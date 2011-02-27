#!/usr/bin/env python

import os
import sys
from os.path import fjoin
from urllib2 import urlopen

from tmdb import TMDB

allowed_extensions = ['m4v', 'mp4', 'mov', 'wmv']

def get_image():
    pass
    
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
    try:
        fh = open(fn_image, 'wb')
        fh.write(urlopen(image_url).read())
        fh.close()
    except OSError:
        return False
    else:
        return True

def get_filename(movie_path, movie_name, extn):
    return "%(path)s/%(name)s.%(extn)s" % {'path': movie_path, 'name': movie_name, 'extn': extn}

if __name__ == '__main__':
    basepath = os.getcwd()
    videos = get_video_filelist(basepath)
    tmdb = TMDB()
    
    for fn_video in videos:
        (movie_path, movie_fn) = fn_video.rsplit('/', 1)
        movie_name = '.'.join(movie_fn.split('.')[:-1]).capitalize()
        fn_xml = get_filename(movie_path, movie_name, 'xml')
        fn_image = get_filename(movie_path, movie_name, 'jpg')
        movie = tmdb.getMovieInfoByName(movie_name)
        if not file_exists(fn_xml):
            if not generate_xml(fn_xml, movie.toxml()):
                print "ERROR: Couldn't create file: %s" % fn_xml
                sys.exit(1)
        if not file_exist(fn_image):
            if not generate_image(fn_image, movie.poster_URL)
                print "ERROR: Couldn't create file: %s" % fn_image
                sys.exit(2)
        
        
            