"""
Definition of views.
"""
import httplib2
import os
import sys
import logging
import json

from django.shortcuts import render, render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.template import RequestContext, loader
from datetime import datetime
from .models import *
from django.core import serializers

#For combining QuerySets
from itertools import chain
from operator import attrgetter

#For youtube
from django.contrib.auth.decorators import login_required
from DjangoWebProject1 import settings
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from oauth2client import xsrfutil
from oauth2client.django_orm import Storage

CLIENT_SECRETS_FILE = CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '..', 'client_secrets.json')
FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/plus.me',
    redirect_uri='http://localhost:8000/oauth2callback')

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        context_instance = RequestContext(request,
        {
            'title':'Home Page',
            'year':datetime.now().year,
        })
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        context_instance = RequestContext(request,
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        })
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        context_instance = RequestContext(request,
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        })
    )

def user(request):
    context = RequestContext(request)
    return render(request, 'app/user.html', context)

def update_playlist(request, do_work):
    print 'in playlist with do_work = ' + do_work
    song_list = []
    artist_list = []
    genre_list = []

    session_songs = []
    artist_songs = []
    genre_songs = []

    final_songs = []
    #check for session vars
    if request.session.__contains__('songList'):
        song_list = request.session['songList']
    if request.session.__contains__('artistList'):
        artist_list = request.session['artistList']
    if request.session.__contains__('genreList'):
        genre_list = request.session['genreList']

    if song_list:
        session_songs = get_songs_from_session(song_list)

    if not artist_list and not genre_list:
        print 'no cached genre or artist'
        top_songs = Songs.objects.order_by('-crawlDelta')[:25]
        if song_list:
            final_songs = combine_querysets(top_songs, session_songs)
        else:
            final_songs = top_songs
    #Artist OR Genre List is available
    else:
        if artist_list:
            artist_songs = get_artist_songs_from_session(artist_list)
            final_songs = artist_songs
        if genre_list:
            genre_songs = get_genre_songs_from_session(genre_list)
            final_songs = genre_songs

        if artist_list and genre_list:
            final_songs = combine_querysets(artist_songs, genre_songs)
        
        if song_list:
            final_songs = combine_querysets(final_songs, session_songs)

    #Save to session, current playlist

    final_list = []
    for s in final_songs:
        final_list.append(s.youtubeId)
    request.session['playlist'] = final_list

    print  request.session['playlist']
    context = RequestContext(request, {
        'final_songs': final_songs,
    })

        
    return render(request, 'app/playlistPartial.html', context)

def combine_querysets(q1, q2):
    return sorted(chain(q1, q2), key=attrgetter('crawlDelta'), reverse=True)


def get_songs_from_session(song_list):
    return Songs.objects.filter(youtubeId__in=song_list).order_by('-crawlDelta')[:25]

def get_artist_songs_from_session(artist_list):
    return Songs.objects.filter(artistId__in=artist_list).order_by('-crawlDelta')[:25]

def get_genre_songs_from_session(genre_list):
    genre_songs_list = Genres.objects.filter(name__in=genre_list).values_list('songId')
    return get_songs_from_session(genre_songs_list)

def song_filter(request):
    print "in song filter"
    search_text = ''
    if request.method == 'POST':
        search_text = request.POST['search_text']
    suggs = get_songs(20, search_text)
    context = RequestContext(request, {
        'suggs': suggs,
    })
    return render(request, 'app/songsFilterPartial.html', context)


def get_songs(max_results = 0, starts_with=''):
    songs_list = []
    if starts_with is not '' and max_results > 0:
        songs_list = Songs.objects.filter(songName__istartswith=starts_with).order_by('-crawlDelta')[:max_results]
    print songs_list
    return songs_list

def artist_filter(request):
    print "in artist filter"
    search_text = ''
    if request.method == 'POST':
        search_text = request.POST['search_text']
    suggs = get_recent_artists(20, search_text)
    context = RequestContext(request, {
        'suggs': suggs,
    })
    return render(request, 'app/artistsFilterPartial.html', context)


def get_recent_artists(max_results = 0, starts_with=''):
    artists_list = []
    if starts_with is not '' and max_results > 0:
        artists_list = Artists.objects.filter(artistName__istartswith=starts_with).order_by('-artistPopularityRecent')[:max_results]
    print artists_list
    return artists_list

def genre_filter(request):
    print "in genre filter"
    search_text = ''
    if request.method == 'POST':
        search_text = request.POST['search_text']
        print search_text
    suggs = get_genres(20, search_text)
    context = RequestContext(request, {
        'suggs': suggs,
    })
    return render(request, 'app/genresFilterPartial.html', context)


def get_genres(max_results = 0, starts_with=''):
    genres_name_list = []
    genres_id_list = []
    if starts_with is not '' and max_results > 0:
        genres_name_list = Genres.objects.filter(name__icontains=starts_with).values_list('name', flat=True).order_by('level').distinct()[:max_results]
    print genres_name_list
    return genres_name_list

def add_song(request):
    print 'in song add'
    song_to_add = ''
    song_list = []
    if request.session.__contains__('songList'):
        song_list = request.session['songList']
        playlist = request.session['playlist']
        if request.method == 'POST':
            song_to_add = request.POST['song_to_add']
            if song_to_add not in song_list:
                song_list.append(song_to_add)
                playlist.append(song_to_add)
                request.session['songList'] = song_list
                request.session['playlist'] = playlist
    print "check this"
    print request.session['songList']
    return HttpResponse(status=200)
    

def add_artist(request):
    print 'in artist add'
    artist_to_add = ''
    artist_list = []
    #CHeck if session is there
    if request.session.__contains__('artistList'):
        artist_list = request.session['artistList']
        #Check if post request
        if request.method == 'POST':
            artist_to_add = request.POST['artist_to_add']
            if artist_to_add not in artist_list:
                artist_list.append(artist_to_add)
                request.session['artistList'] = artist_list
            else:
                artist_list.append(artist_to_add)
                request.session['artistList'] = artist_list

    suggs = get_artists_from_session(artist_list)
    context = RequestContext(request, {
        'suggs': suggs,
    })
    return render(request, 'app/artistPanelPartial.html', context)

def remove_song(request):
    print 'in song remove'
    song_to_remove = ''
    song_list = []
    if request.session.__contains__('songList'):
        song_list = request.session['songList']
        playlist = request.session['playlist']
        if request.method == 'POST':
            song_to_remove = request.POST['song_to_remove']
            if song_to_remove in song_list:
                song_list.remove(song_to_remove)
                playlist.remove(song_to_remove)
                request.session['songList'] = song_list
                request.session['playlist'] = playlist
    return HttpResponse(status=200)


def remove_artist(request):
    print "in artist remove"
    artist_to_remove = ''
    if request.method == 'POST':
        artist_to_remove = request.POST['artist_to_remove']
        print artist_to_remove
    if request.session.__contains__('artistList'):
        lis = request.session['artistList']
        if artist_to_remove in lis:
            lis.remove(artist_to_remove)
            request.session['artistList'] = lis

    suggs = get_artists_from_session(request.session['artistList'])
    context = RequestContext(request, {
        'suggs': suggs,
    })
    return render(request, 'app/artistPanelPartial.html', context)

def get_artists_from_session(artistList):
    return Artists.objects.filter(artistId__in=artistList)

def add_genre(request):
    print "in genre add"
    genre_to_add = ''
    genre_list = []
    #Check if Session is there
    if request.session.__contains__('genreList'):
        genre_list = request.session['genreList']
    if request.method == 'POST':
        genre_to_add = request.POST['genre_to_add']
        if genre_to_add not in genre_list:
            genre_list.append(genre_to_add)
            request.session['genreList'] = genre_list
        else:
            genre_list.append(genre_to_add)
            request.session['genreList'] = genre_list
    
    context = RequestContext(request, {
        'suggs': genre_list,
    })
    return render(request, 'app/genrePanelPartial.html', context)


def remove_genre(request):
    print "in genre remove"
    genre_to_remove = ''
    if request.method == 'POST':
        genre_to_remove = request.POST['genre_to_remove']
        print genre_to_remove
    if request.session.__contains__('genreList'):
        lis = request.session['genreList']
        if genre_to_remove in lis:
            lis.remove(genre_to_remove)
            request.session['genreList'] = lis
    else:
        new_list = []
        new_list.append(genre_to_remove)
        request.session['genreList'] = new_list
    
    context = RequestContext(request, {
        'suggs': request.session['genreList'],
    })
    return render(request, 'app/genrePanelPartial.html', context)

def yplayer(request):
    context = RequestContext(request, {
        'ids': get_sorted_ids_from_session(request.session['playlist']),
    })
    return render(request, 'app/yplayer.html', context)


def get_sorted_ids_from_session(song_list):
    ids = Songs.objects.filter(youtubeId__in=song_list).values_list('youtubeId', flat=True).order_by('-crawlDelta')
    ids2 = list(ids)
    data = json.dumps(ids2)
    return data
#@login_required
#def youtube_thingy(request):
#    print '340'
#    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
#    credential = storage.get()
#    if credential is None or credential.invalid == True:
#        print 'if 344 bad'
#        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, request.user)
#        authorize_url = FLOW.step1_get_authorize_url()
#        return HttpResponseRedirect(authorize_url)
#    else:
#        print 'else 349 good'
#        http = httplib2.Http()
#        http = credential.authorize(http)
#        service = build("plus", "v1", http=http)
#        activities = service.activities()
#        activitylist = activities.list(collection='public',
#                                       userId='me').execute()
#        logging.info(activitylist)
#        print activitylist
#        return render_to_response('plus/welcome.html', {
#                'activitylist': activitylist,
#                })

#@login_required
#def auth_return(request):
#    if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'],
#                                 request.user):
#        return  HttpResponseBadRequest()
#    credential = FLOW.step2_exchange(request.REQUEST)
#    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
#    storage.put(credential)
#    return HttpResponseRedirect("/")

    #print '330'
    #CLIENT_SECRETS_FILE = CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '..', 'client_secrets.json')

    ## This variable defines a message to display if the CLIENT_SECRETS_FILE is
    ## missing.
    #MISSING_CLIENT_SECRETS_MESSAGE = """
   
    #To make this sample run you will need to populate the client_secrets.json file
    #found at:

    #   %s

    #with information from the Developers Console
    #https://console.developers.google.com/

    #For more information about the client_secrets.json file format, please visit:
    #https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
    #""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
    #                                   CLIENT_SECRETS_FILE))

    ## This OAuth 2.0 access scope allows for full read/write access to the
    ## authenticated user's account.
    #YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
    #YOUTUBE_API_SERVICE_NAME = "youtube"
    #YOUTUBE_API_VERSION = "v3"
    
    #flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    #  message=MISSING_CLIENT_SECRETS_MESSAGE,
    #  scope=YOUTUBE_READ_WRITE_SCOPE,
    #  redirect_uri='http://localhost:8000/oauth2callback')

    #storage = Storage("%s-oauth2.json" % sys.argv[0])
    #credentials = storage.get()

    #if credentials is None or credentials.invalid:
    #  flags = argparser.parse_args()
    #  credentials = run_flow(flow, storage, flags)

    #youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    #  http=credentials.authorize(httplib2.Http()))

    ## This code creates a new, private playlist in the authorized user's channel.
    #playlists_insert_response = youtube.playlists().insert(
    #  part="snippet,status",
    #  body=dict(
    #    snippet=dict(
    #      title="Test Playlist",
    #      description="A private playlist created with the YouTube API v3"
    #    ),
    #    status=dict(
    #      privacyStatus="private"
    #    )
    #  )
    #).execute()

    #print "New playlist id: %s" % playlists_insert_response["id"]
    #return HttpResponse(status=200)