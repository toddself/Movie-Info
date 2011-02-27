#!/usr/bin/env python

import os
import sys
from os.path import join as fjoin
from urllib2 import urlopen

from tmdb.tmdb import TMDB, TMDBNotFoundError

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
        fh = open(fn_xml, 'w')
        fh.write(movie_xml)
        fh.close()
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
    return "%(path)s/%(name)s.%(extn)s" % {'path': movie_path, 'name': movie_name, 'extn': extn}

if __name__ == '__main__':
    basepath = os.getcwd()
    videos = get_video_filelist(basepath)
    
    for fn_video in videos:
        tmdb = TMDB()
        (movie_path, movie_fn) = fn_video.rsplit('/', 1)
        movie_fn_root = '.'.join(movie_fn.split('.')[:-1])
        movie_name = movie_fn_root.capitalize().replace('_', ' ')
        fn_xml = make_filename(movie_path, movie_fn_root, 'xml')
        fn_image = make_filename(movie_path, movie_fn_root, 'jpg')
        print "For file:", fn_video
        print "Looking up:", movie_name
        try:
            movie = tmdb.getMovieInfoByName(movie_name)
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