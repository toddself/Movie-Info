#!/usr/bin/env python
import json

from urllib2 import urlopen
from urllib import quote_plus

from movie import Movie, connect
from sqlobject import SQLObjectNotFound

class TMDBNotFoundError(Exception):
    pass

class TMDBUrls():
    base = 'http://api.themoviedb.org'
    apikey = '32143db63692aa6a5cb01336cc06211b'
    version = '2.1'
    output = 'json'
    lang = 'en-US'
    
    def __init__(self, lang = '', version=''):
        if lang:
            self.lang = lang           
        
        if version:
            self.version = version

    def generateURL(self, domain, action, auth=False):
        self._calledAPI = "%(domain)s.%(action)s" % \
                            {'domain': domain.capitalize(), 'action': action}

        url = "%(base)s/%(version)s/%(api)s/%(lang)s/%(output)s/%(apikey)s/" % \
                              {'base': self.base,
                               'version': self.version,
                               'api': self._calledAPI,
                               'lang': self.lang,
                               'output': self.output,
                               'apikey': self.apikey,}

        if auth:
            url = ''.join(url.split('/'+self.lang))

        self._baseURL = url
        return self._baseURL                         

class TMDB():
    token = ''
    connection = None

    def __init__(self, apikey = '', output = 'json'):
        if apikey:
            self.apikey = apikey
        
        self.urls = TMDBUrls()
        
        connection = connect()
        
    def getMovieInfoByName(self, name):
        this_id = self.getMovieIDByName(name)
        return self.getMovieInfoByTMDB_ID(this_id)

    def getMovieIDByName(self, name):
        self.domain = 'movie'
        self.action = 'search'
        self.searchTerm = quote_plus(name)
        
        try:
            movie_list = Movie.select("""movie.title LIKE '%s'""" % name)
            if movie_list.count() == 1:
                self.tmdb_id = movie_list[0].tmdb_id
            else:
                raise SQLObjectNotFound
        except SQLObjectNotFound:
            self.url = "%s%s" % (self.urls.generateURL(self.domain, self.action), self.searchTerm)

            movie_info = self._getResponse(self.url)
            self.tmdb_id = movie_info['id']
        
        return self.tmdb_id
        
    def getMovieInfoByTMDB_ID(self, tmdb_id=''):
        self.domain = 'movie'
        self.action = 'getInfo'
        if tmdb_id:
            self.tmdb_id = tmdb_id
        
        try:    
            movie_list = Movie.select(Movie.q.tmdb_id==self.tmdb_id)
            if movie_list.count() == 1:
                oMovie = movie_list[0]
            elif movie_list.count() == 0:
                raise SQLObjectNotFound
            else:
                raise AttributeError
        except SQLObjectNotFound:
        
            self.url = "%s%s" % (self.urls.generateURL(self.domain, self.action), self.tmdb_id)
        
            movie_info = self._getResponse(self.url)
        
            oMovie = Movie(tmdb_id = movie_info['id'],
                           imdb_id = movie_info['imdb_id'],
                           title = movie_info['name'],
                           year = int(movie_info['released'].split('-')[0]),
                           genre = self._getPrimaryGenre(movie_info['genres']),
                           mpaa = Movie.ratings.index(movie_info['certification']),
                           director = self._getDirector(movie_info['cast']),
                           actors = self._getPrimaryActors(movie_info['cast']),
                           description = movie_info['overview'],
                           length = int(movie_info['runtime']),
                           poster_URL = self._getPosterURL(movie_info['posters']),
                           )
        
        return oMovie
        
    def _getPosterURL(self, posterDict):
        for poster in posterDict:
            try:
                if poster['image']['size'] == "cover":
                    return poster['image']['url']
            except KeyError:
                if poster['image']['size'] == 'mid':
                    return poster['image']['url']
        
        return ''
                    
    
    def _getPrimaryGenre(self, genreDict):
        mainGenre = genreDict[0]['name']
        return mainGenre
    
    def _getDirector(self, castDict):
        for member in castDict:
            if member['job'] == 'Director':
                return member['name']
    
    def _getPrimaryActors(self, castDict):
        actors = []
        for member in castDict:
            if member['job'] == 'Actor':
                actors.append(member['name'])
        
        return '  '.join(actors[:3])
    
    def _getResponse(self, url):
        self._server_response = urlopen(url)
        self._server_msg = self._server_response.msg
        if "OK" not in self._server_msg:
            raise TMDBNotFoundError
        else:
            self._response_data = json.loads(self._server_response.read())[0]
            if "Nothing found" in self._response_data:
                raise TMDBNotFoundError
            else:
                return self._response_data
        
if __name__ == '__main__':
    connect()
    t = TMDB()
    this_id = t.getMovieIDByName('Aliens')
    print "ID: ", this_id
    this_movie = t.getMovieInfoByTMDB_ID(this_id)
    print this_movie.toxml()