#!/usr/bin/env python

from urllib2 import urlopen
import webbrowser
import json

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

    def __init__(self, apikey = '', output = 'json'):
        if apikey:
            self.apikey = apikey
        
        self.urls = TMDBUrls(output=output)

    def getMovieIDFromName(self, name):
        self.domain = 'movie'
        self.action = 'search'
        self.searchTerm = name
        
        self.url = "%s%s" % (self._generateURL(self.domain, self.action), self.searchTerm)
        
        movie_info = self._getResponse(self.url)
        self.tmdb_id = movie_info['id']
        return self.tmdb_id
        
    def getMovieInfoByTMDB_ID(self, tmdb_id=''):
        self.domain = 'movie'
        self.action = 'getInfo'
        if tmdb_id:
            self.tmdb_id = tmdb_id
        
        self.url = "%s%s" % (self._generateURL(self.domain, self.action), self.tmdb_id)
        
        movie_info = self._getResponse(self.url)
        
        oMovie = Movie(tmdb_id = movie_info['id'],
                       imdb_id = movie_info['imdb_id'],
                       title = movie_info['name'],
                       year = movie_info['released'].split('-')[0],
                       genre = self._getPrimaryGenre(movie_info['genres']),
                       mpaa = movie_info['certification'],
                       director = self._getDirector(movie_info['cast']),
                       actors = self._getPrimaryActors(movie_info['cast']),
                       description = movie_info['overview'],
                       length = movie_info['runtime'])
        
        return oMovie
    
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
        self._server_response = urlopen(url)
        self._json = json.load(self._server_response)
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
    t = TMDB()
    this_id = t.getMovieIDFromName('Mallrats')
    print "ID: ", this_id
    this_movie = t.getMovieInfoByTMDB_ID(this_id)
    print "Movie: ", this_movie