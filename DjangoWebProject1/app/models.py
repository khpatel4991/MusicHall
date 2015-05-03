"""
Definition of models.
"""
from __future__ import unicode_literals

import pickle
import base64

from django.contrib import admin
from django.contrib.auth.models import User

from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField

from django.db import models


# Create your models here.

class Artists(models.Model):
    artistId = models.IntegerField(db_column='artistId', primary_key=True)  # Field name made lowercase.
    artistName = models.CharField(db_column='artistName', max_length=200, blank=True, null=True)  # Field name made lowercase.
    artistPopularityAll = models.IntegerField(db_column='artistPopularityAll', blank=True, null=True)  # Field name made lowercase.
    artistPopularityRecent = models.IntegerField(db_column='artistPopularityRecent', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Artists'


class Genres(models.Model):
    id = models.IntegerField(db_column='genreId', primary_key=True)
    level = models.IntegerField()
    name = models.CharField(max_length=30)
    songId = models.ForeignKey('Songs', db_column='songId')  # Field name made lowercase.

    class Meta:
        db_table = 'Genres'
        unique_together = (('level', 'name', 'songId'),)


class Songs(models.Model):
    youtubeId = models.CharField(db_column='youtubeId', primary_key=True, max_length=100)  # Field name made lowercase.
    artistId = models.ForeignKey(Artists, db_column='artistId')  # Field name made lowercase.
    songName = models.CharField(db_column='songName', max_length=150, blank=True, null=True)  # Field name made lowercase.
    youtubeName = models.CharField(db_column='youtubeName', max_length=350, blank=True, null=True)  # Field name made lowercase.
    url = models.CharField(max_length=255, blank=True, null=True)
    releaseDate = models.IntegerField(db_column='releaseDate', blank=True, null=True)  # Field name made lowercase.
    decade = models.IntegerField(blank=True, null=True)
    youtubeDate = models.DateField(db_column='youtubeDate', blank=True, null=True)  # Field name made lowercase.
    crawlDate = models.DateField(db_column='crawlDate', blank=True, null=True)  # Field name made lowercase.
    viewCount = models.IntegerField(db_column='viewCount', blank=True, null=True)  # Field name made lowercase.
    crawlDelta = models.IntegerField(db_column='crawlDelta', blank=True, null=True)  # Field name made lowercase.
    rating = models.FloatField(blank=True, null=True)
    viewCountRate = models.FloatField(db_column='viewCountRate', blank=True, null=True)  # Field name made lowercase.
    duration = models.CharField(max_length=40, blank=True, null=True)
    songLanguage = models.CharField(db_column='songLanguage', max_length=40)  #Field name made lowercase.
    songCountry = models.CharField(db_column='songCountry', max_length=40)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Songs'
