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
            'title':'About Us',
            'year':datetime.now().year,
        })
    )

def user(request):
    context = RequestContext(request, 
    {
        'title':'Music',
    })
    return render(request, 'app/user.html', context)

def update_playlist(request, do_work):
    song_list = []
    artist_list = []
    genre_list = []
    country_list = []
    language_list = []

    session_songs = []
    artist_songs = []
    genre_songs = []
    country_songs = []
    language_songs = []
    top_songs = []

    final_songs = []
    #check for session vars
    if request.session.__contains__('songList'):
        song_list = request.session['songList']
    if request.session.__contains__('artistList'):
        artist_list = request.session['artistList']
    if request.session.__contains__('genreList'):
        genre_list = request.session['genreList']
    if request.session.__contains__('countryList'):
        country_list = request.session['countryList']
    if request.session.__contains__('languageList'):
        language_list = request.session['languageList']


    #Logic Part
    max_from_category = 25

    if song_list:
        session_songs = get_songs_from_session(song_list)

    if artist_list:
        artist_songs = get_artist_songs_from_session(artist_list, max_from_category)

    if genre_list:
        genre_songs = get_genre_songs_from_session(genre_list, max_from_category)

    if country_list:
        country_songs = get_country_songs_from_session(country_list, max_from_category)

    if language_list:
        language_songs = get_language_songs_from_session(language_list, max_from_category)

    
    if not artist_list and not genre_list and not country_list and not language_list:
        top_songs = Songs.objects.order_by('-crawlDelta')[:max_from_category]
    
    final_songs = combine_querysets(session_songs, artist_songs, genre_songs, country_songs, language_songs, top_songs)

    #Save to session, current playlist
    final_list = []
    for s in final_songs:
        final_list.append(s.youtubeId)
    request.session['playlist'] = final_list
    
    context = RequestContext(request, {
        'final_songs': final_songs,
    })

        
    return render(request, 'app/playlistPartial.html', context)

def combine_querysets(q1, q2, q3, q4, q5, q6):

    lis = list(set(chain(q1, q2, q3, q4, q5, q6)))
    return sorted(chain(lis), key=attrgetter('crawlDelta'), reverse=True)


def get_songs_from_session(song_list):
    return Songs.objects.filter(youtubeId__in=song_list).order_by('-crawlDelta')

def get_artist_songs_from_session(artist_list, max_results):
    q = []
    for i in artist_list:
        q = list(chain(q, Songs.objects.filter(artistId__exact=i).order_by('-crawlDelta')[:max_results]))
    return q

def get_genre_songs_from_session(genre_list, max_results):
    q = []
    for i in genre_list:
        song_list = Genres.objects.filter(name__exact=i).values_list('songId', flat=True)
        q = list(chain(q, Songs.objects.filter(youtubeId__in=song_list).order_by('-crawlDelta')[:25]))
    return q

def get_country_songs_from_session(country_list, max_results):
    return Songs.objects.filter(songCountry__in=country_list).order_by('-crawlDelta')[:max_results]

def get_language_songs_from_session(language_list, max_results):
    return Songs.objects.filter(songLanguage__in=language_list).order_by('-crawlDelta')[:max_results]

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

#Country Part
def country_filter(request):
    print "in country filter"
    search_text = ''
    if request.method == 'POST':
        search_text = request.POST['search_text']
        print search_text
    suggs = get_countries(search_text)
    context = RequestContext(request, {
        'suggs': suggs,
    })
    return render(request, 'app/countriesFilterPartial.html', context)

def get_countries(starts_with=''):
    countries_name_list = []
    if starts_with is not '':
        countries_name_list = Songs.objects.filter(songCountry__icontains=starts_with).values_list('songCountry', flat=True).distinct()
    print countries_name_list
    return countries_name_list

#Language Part
def language_filter(request):
    print "in language filter"
    search_text = ''
    if request.method == 'POST':
        search_text = request.POST['search_text']
        print search_text
    suggs = get_languages(search_text)
    context = RequestContext(request, {
        'suggs': suggs,
    })
    return render(request, 'app/languagesFilterPartial.html', context)

def get_languages(starts_with=''):
    languages_name_list = []
    if starts_with is not '':
        languages_name_list = Songs.objects.filter(songLanguage__icontains=starts_with).values_list('songLanguage', flat=True).distinct()
    print languages_name_list
    return languages_name_list


def add_song(request):
    print 'in song add'
    song_to_add = ''
    song_list = []
    playlist = []
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

    suggs = get_songs_from_session(song_list)
    context = RequestContext(request, {
        'suggs': suggs,
    })
    return render(request, 'app/songPanelPartial.html', context)    

def add_artist(request):
    print 'in artist add'
    artist_to_add = ''
    artist_list = []

    if request.session.__contains__('artistList'):
        artist_list = request.session['artistList']

    if request.method == 'POST':
        artist_to_add = request.POST['artist_to_add']
        if artist_to_add not in artist_list:
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
    
    suggs = get_songs_from_session(request.session['songList'])
    context = RequestContext(request, {
        'suggs': suggs,
    })
    return render(request, 'app/songPanelPartial.html', context)


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


#Country Part
def add_country(request):
    print "in country add"
    country_to_add = ''
    country_list = []
    #Check if Session is there
    if request.session.__contains__('countryList'):
        country_list = request.session['countryList']
    if request.method == 'POST':
        country_to_add = request.POST['country_to_add']
        if country_to_add not in country_list:
            country_list.append(country_to_add)
            request.session['countryList'] = country_list
    
    context = RequestContext(request, {
        'suggs': country_list,
    })
    return render(request, 'app/countryPanelPartial.html', context)


def remove_country(request):
    print "in country remove"
    country_to_remove = ''
    if request.method == 'POST':
        country_to_remove = request.POST['country_to_remove']
        print country_to_remove
    if request.session.__contains__('countryList'):
        lis = request.session['countryList']
        if country_to_remove in lis:
            lis.remove(country_to_remove)
            request.session['countryList'] = lis
    else:
        new_list = []
        new_list.append(country_to_remove)
        request.session['countryList'] = new_list
    
    context = RequestContext(request, {
        'suggs': request.session['countryList'],
    })
    return render(request, 'app/countryPanelPartial.html', context)

#Language Part
def add_language(request):
    print "in language add"
    language_to_add = ''
    language_list = []
    #Check if Session is there
    if request.session.__contains__('languageList'):
        language_list = request.session['languageList']
    if request.method == 'POST':
        language_to_add = request.POST['language_to_add']
        if language_to_add not in language_list:
            language_list.append(language_to_add)
            request.session['languageList'] = language_list
    
    context = RequestContext(request, {
        'suggs': language_list,
    })
    return render(request, 'app/languagePanelPartial.html', context)


def remove_language(request):
    print "in language remove"
    language_to_remove = ''
    if request.method == 'POST':
        language_to_remove = request.POST['language_to_remove']
        print language_to_remove
    if request.session.__contains__('languageList'):
        lis = request.session['languageList']
        if language_to_remove in lis:
            lis.remove(language_to_remove)
            request.session['languageList'] = lis
    else:
        new_list = []
        new_list.append(language_to_remove)
        request.session['languageList'] = new_list
    
    context = RequestContext(request, {
        'suggs': request.session['languageList'],
    })
    return render(request, 'app/languagePanelPartial.html', context)




def yplayer(request, shuffle):
    print(type(int(shuffle)))
    ids = get_sorted_ids_from_session(request.session['playlist'], int(shuffle))
    context = RequestContext(request, {
        'ids': ids,
    })
    return render(request, 'app/yplayer.html', context)


def get_sorted_ids_from_session(song_list, shuffle):
    if shuffle:
        ids = Songs.objects.filter(youtubeId__in=song_list).values_list('youtubeId', flat=True).order_by('?')
    else:
        ids = Songs.objects.filter(youtubeId__in=song_list).values_list('youtubeId', flat=True).order_by('-crawlDelta')
    ids2 = list(ids)
    data = json.dumps(ids2)
    return data