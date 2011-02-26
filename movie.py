#!/usr/bin/env python

from SQLObject import *

class Movie():
    tmdb_id = ''
    imdb_id = ''
    title = ''
    year = ''
    genre = ''
    mpaa = ''
    director = ''
    actors = ''
    description = ''
    length = ''
    
    def __init__(self, **kwargs):
        for k,v in kwargs.iteritems():
            # print k, v
            setattr(self, k, v)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.title
