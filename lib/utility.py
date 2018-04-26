############################################################################
###                              utility.py                              ###
############################################################################
# This python module contains utility functions.

import os
import sys
import json
import time
import numpy as np
from urllib.request import urlretrieve
from urllib.request import URLError


###########################     0. utility function      ###########################
def sleepAfterRequest():
    time.sleep(np.random.uniform(5, 20))

def relexPrint(content):
    print(content)
    time.sleep(0.15)


########################     1. working with directory      ###########################
def getProjectDir():
    '''
    get the top absolute path of this project
    @return: path
    '''
    file_path = os.path.realpath(__file__)
    end_idx = file_path.find('doubanStatistics')
    proj_dir = file_path[0:end_idx] + 'doubanStatistics'
    return proj_dir


def checkTempFolder():
    '''
    Check if temp folder exist, and create it if not.
    @return: no return
    '''
    proj_dir = getProjectDir()
    temp_dir = os.path.join(proj_dir, 'temp')
    if not os.path.isdir(temp_dir):
        os.makedirs(temp_dir)
    return temp_dir


def rmTemp(category, id):
    '''
    Remove temp files
    @param category: Movie, movie_person or book
    @param id: movie id, user id or book id
    @return: no return
    '''
    proj_dir = getProjectDir()
    temp_dir = os.path.join(proj_dir, 'temp')
    if category == 'movie':
        tmp_path = os.path.join(temp_dir, 'movie.subject.' + str(id) + '.html')
    elif category == 'personal_movie':
        tmp_path = os.path.join(temp_dir, 'movie.' + id + '.viewed.txt')
    elif category == 'book':
        tmp_path = os.path.join(temp_dir, 'book.subject.' + id + '.html')
    else:
        raise ValueError('category should be "movie", "movie_history" or "book".')
    if os.path.exists(tmp_path):
        os.remove(tmp_path)


###############################     2. working with api      ################################
def catAPIurl(category, id):
    '''
    Concatenate item api url from its category and id.
    @param category: movie or book
    @param id: item id
    @return: url
    '''
    if category == 'movie':
        return 'https://api.douban.com/v2/movie/subject/' + str(id)
    elif category == 'book':
        return 'https://api.douban.com/v2/book/' + str(id)
    else:
        raise ValueError('Cannot parse item url, currently only support movie and book.')


def catAPItempfile(url):
    '''
    Parse api url, subtract identification information to name file for downloading.
    @param url: api url
    @return: filename
    '''
    url = url.strip('/')
    if '/movie/' in url:      # if movie
        start_idx = url.find('movie')
        name_list = ['api'] + url[start_idx:].split('/') + ['json']
        temp_filename = '.'.join(name_list)
        return temp_filename
    elif '/book/' in url:     # if book
        start_idx = url.find('book')
        name_list = ['api'] + url[start_idx:].split('/') + ['json']
        temp_filename = '.'.join(name_list)
        return temp_filename
    else:
        raise ValueError('Cannot parse api url, currently only support movie and book.')


def APIdownloadJson(url):
    '''
    Download API json file to temp folder.
    @param url: json url.
    @return: no return.
    '''
    temp_dir = checkTempFolder()
    temp_filename = catAPItempfile(url)
    target_path = os.path.join(temp_dir, temp_filename)
    if os.path.exists(target_path):
        return True
    else:
        try:
            urlretrieve(url, target_path)
            return True
        except URLError:
            print('Fetching {} failed, check internet connection.'.format(url), sys.exc_info())
            return False


def parseJsonMovie(id):
    '''
    Parse api movie information and return from json file.
    @param id: movie id
    @return: movie attribute dict
    '''
    temp_dir = checkTempFolder()
    temp_path = os.path.join(temp_dir, 'api.movie.subject.' + str(id) + '.json')
    if os.path.exists(temp_path):
        with open(temp_path, encoding='utf-8') as json_file:
            data = json.load(json_file)
            movie_info = dict()
            movie_info['id'] = data['id']
            movie_info['title'] = data['title']
            movie_info['original_title'] = data['original_title']
            movie_info['rating_ave'] = data['rating']['average']
            movie_info['rating_count'] = data['ratings_count']
            movie_info['wish_count'] = data['wish_count']
            movie_info['viewed_count'] = data['collect_count']
            movie_info['comment_count'] = data['comments_count']
            movie_info['review_count'] = data['reviews_count']
            movie_info['subtype'] = data['subtype']
            movie_info['director'] = data['directors'][0]['id']
            movie_info['year'] = data['year']
            movie_info['country'] = data['countries']
            return movie_info



if __name__ == '__main__':
    print('This script.')



