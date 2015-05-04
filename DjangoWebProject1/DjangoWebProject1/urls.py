"""
Definition of urls for DjangoWebProject1.
"""
import os
from datetime import datetime
from django.conf.urls import patterns, url
from app.forms import BootstrapAuthenticationForm

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'app.views.home', name='home'),
    url(r'^user', 'app.views.user', name='user'),
    url(r'^updateplaylist/(?P<do_work>\d+)', 'app.views.update_playlist', name='updatePlaylist'),
    url(r'^filtersong', 'app.views.song_filter', name='filterSongs'),
    url(r'^filterartists', 'app.views.artist_filter', name='filterArtists'),
    url(r'^filtergenres', 'app.views.genre_filter', name='filterGenres'),
    url(r'^filtercountries', 'app.views.country_filter', name='filterCountries'),
    url(r'^addsong', 'app.views.add_song', name='addSong'),
    url(r'^addartist', 'app.views.add_artist', name='addArtist'),
    url(r'^addgenre', 'app.views.add_genre', name='addGenre'),
    url(r'^addcountry', 'app.views.add_country', name='addCountry'),
    url(r'^removesong', 'app.views.remove_song', name='removeSong'),
    url(r'^removeartist', 'app.views.remove_artist', name='removeArtist'),
    url(r'^removegenre', 'app.views.remove_genre', name='removeGenre'),
    url(r'^removecountry', 'app.views.remove_country', name='removeCountry'),
    url(r'^yplayer/(?P<shuffle>\d+)', 'app.views.yplayer', name='yPlayer'),
    url(r'^contact$', 'app.views.contact', name='contact'),
    url(r'^about', 'app.views.about', name='about'),
    url(r'^login/$',
        'django.contrib.auth.views.login',
        {
            'template_name': 'app/login.html',
            'authentication_form': BootstrapAuthenticationForm,
            'extra_context':
            {
                'title':'Log in',
                'year':datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        'django.contrib.auth.views.logout',
        {
            'next_page': '/',
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
