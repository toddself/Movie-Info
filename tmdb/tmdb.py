#!/usr/bin/env python

from urllib2 import urlopen
from urllib import quote_plus
import json

from movie import Movie, connect
from sqlobject import SQLObjectNotFound

class TMDBNotFoundError(Exception):
    pass

class TMDBUrls():
    available_outputs = ['xml', 'yaml', 'json']
    base = 'http://api.themoviedb.org'
    version = '2.1'
    output = 'json'
    lang = 'en-US'
    
    def __init__(self, output = '', lang = ''):
        if output and output in self.available_outputs:
            self.output = output
        
        if lang:
            self.lang = lang           
                     

class TMDB():
    apikey = '32143db63692aa6a5cb01336cc06211b'
    token = ''
    connection = None

    def __init__(self, apikey = '', output = 'json'):
        if apikey:
            self.apikey = apikey
        
        self.urls = TMDBUrls(output=output)
        
        connection = connect()
        
    def getMovieInfoByName(self, name):
        this_id = self.getMovieIDByName(name)
        return self.getMovieInfoByTMDB_ID(this_id)

    def getMovieIDByName(self, name):
        self.domain = 'movie'
        self.action = 'search'
        self.searchTerm = quote_plus(name)
        
        self.url = "%s%s" % (self._generateURL(self.domain, self.action), self.searchTerm)
        
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
        
            self.url = "%s%s" % (self._generateURL(self.domain, self.action), self.tmdb_id)
        
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
        poster = posterDict[0]
        return poster['image']['url']
    
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
        
        return ' '.join(actors[:3])
    
    def _getResponse(self, url):
        print url
        self._server_response = urlopen(url)
        self._server_msg = self._server_response.msg
        if "OK" not in self._server_msg:
            raise TMDBNotFoundError
        else:
            self._response_data = self._server_response.read()
        
            self._json = json.loads(self._response_data)
            if 'Nothing found' in self._json[0]:
                raise TMDBNotFoundError
            else:
                self.resp_dict = self._json[0]
        
            return self.resp_dict

    def _generateURL(self, domain, action, auth=False):
        self._calledAPI = "%(domain)s.%(action)s" % \
                            {'domain': domain.capitalize(), 'action': action}
        
        url = "%(base)s/%(version)s/%(api)s/%(lang)s/%(output)s/%(apikey)s/" % \
                              {'base': self.urls.base,
                               'version': self.urls.version,
                               'api': self._calledAPI,
                               'lang': self.urls.lang,
                               'output': self.urls.output,
                               'apikey': self.apikey,}

        if auth:
            url = ''.join(url.split('/'+self.urls.lang))
        
        self._baseURL = url
        return self._baseURL
        
if __name__ == '__main__':
    connect()
    t = TMDB()
    this_id = t.getMovieIDByName('Aliens')
    print "ID: ", this_id
    this_movie = t.getMovieInfoByTMDB_ID(this_id)
    print this_movie.toxml()