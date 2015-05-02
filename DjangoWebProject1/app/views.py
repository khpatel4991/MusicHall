"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template import RequestContext, loader
from datetime import datetime
from .models import *
from django.core import serializers

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

def update_playlist(request):
    print 'in playlist'
    song_list = []
    artist_list = []
    genre_list = []
    top_songs = []
    #check for session vars
    if request.session.__contains__('songList'):
        song_list = request.session['songList']
    if request.session.__contains__('artistList'):
        artist_list = request.session['artistList']
    if request.session.__contains__('genreList'):
        genre_list = request.session['genreList']

    if not artist_list and not genre_list:
        print 'no cached genre or artist'
        #top_songs = Songs.objects.order_by('-crawlDelta')[:25]
        if song_list:
            #top_songs.extend(get_songs_from_session(song_list))
            top_songs = get_songs_from_session(song_list)

    context = RequestContext(request, {
        'top_songs': top_songs,
    })
    
    return render(request, 'app/playlistPartial.html', context)

def get_songs_from_session(songList):
    return Songs.objects.filter(youtubeId__in=songList)


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
        if request.method == 'POST':
            song_to_add = request.POST['song_to_add']
            if song_to_add not in song_list:
                song_list.append(song_to_add)
                request.session['songList'] = song_list
        else:
            song_list.append(song_to_add)
            request.session['songList'] = song_list
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