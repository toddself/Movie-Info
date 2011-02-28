#!/usr/bin/env python

import os
import sys
import codecs
from os.path import join as fjoin
from urllib2 import urlopen
from optparse import OptionParser

from tmdb.tmdb import TMDB, TMDBNotFoundError

__version__ = '0.50'
allowed_extensions = ['m4v', 'mp4', 'mov', 'wmv']

def get_video_filelist(basepath):
    videos = []
    for root, dirs, files in os.walk(basepath):
        for name in files:
            if name.split('.')[-1] in allowed_extensions:
                videos.append(fjoin(root,name))
    
    return videos
    
def file_exists(fn_xml):
    try:
        os.stat(fn_xml)
    except OSError:
        return False
    else:
        return True
        
def generate_xml(fn_xml, movie_xml):
    try:
        out = file(fn_xml, 'w')
        out.write(codecs.BOM_UTF8)
        out.write(movie_xml.encode('utf-8'))
        out.close()
    except OSError:
        return False
    else:
        return True

def generate_image(fn_image, image_url):
    if len(image_url) < 1:
        return False
    try:
        fh = open(fn_image, 'wb')
        fh.write(urlopen(image_url).read())
        fh.close()
    except OSError:
        return False
    else:
        return True

def make_filename(movie_path, movie_name, extn):
    return fjoin(movie_path, "%s.%s" % (movie_name, extn))

def main(argv):
    usage = "usage: %prog [options] URL"
    version = __version__
    parser = OptionParser(usage=usage, version="%prog "+version)
    
    parser.add_option("-r", "--rename-files", action='store_true', dest="rename", 
            default=True, help="Rename media files to match titles from TMDB")
    (options, args) = parser.parse_args()    
    
    basepath = os.getcwd()
    videos = get_video_filelist(basepath)
    
    for fn_video in videos:
        tmdb = TMDB()
        (movie_path, movie_fn) = fn_video.rsplit('/', 1)
        (movie_fn_base, movie_fn_extn) = movie_fn.rsplit('.', 1)
        movie_name = movie_fn_base.replace('_', ' ')
        try:
            movie = tmdb.getMovieInfoByName(movie_fn_base)
            if options.rename:
                new_movie_fn_base = movie.title
                os.rename(fn_video, make_filename(movie_path, new_movie_fn_base, movie_fn_extn))
                movie_fn_base = new_movie_fn_base

            fn_xml = make_filename(movie_path, movie_fn_base, 'xml')
            fn_image = make_filename(movie_path, movie_fn_base, 'jpg')            
        except TMDBNotFoundError:
            print movie_name, "not found"
        else:            
            if not file_exists(fn_xml):
                if not generate_xml(fn_xml, movie.toxml()):
                    print "ERROR: Couldn't create file: %s" % fn_xml
                    sys.exit(1)
            if not file_exists(fn_image):
                if not generate_image(fn_image, movie.poster_URL):
                    print "ERROR: Couldn't create file: %s" % fn_image
                    sys.exit(2)            

if __name__ == '__main__':
    main(sys.argv[1:])