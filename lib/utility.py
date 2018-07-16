############################################################################
###                              utility.py                              ###
############################################################################
'''
This python module contains utility functions.

Function/

0. ##### utility
├── sleepAfterRequest()
└── relexPrint()
1. ##### directory and file
├── checkTempFolder()
│   └── getProjectDir()
├── rmTemp(category, id)
├── getIdList(file)
└── outputIdList(id_list, file)
2. ##### api
├── catAPIurl(category, id)
├── catAPItempfile(url)
├── APIdownloadJson(url)
└── parseJsonMovie(id)
3. ##### get book and movie content
├── catHTML(category, id)
└── downloadHTML(url)
    └── catHTMLtempfile(url)
4. ##### work with text
├── cleanSQL(text)
└── cleanDate(pubdate)
'''

import os
import sys
import re
import json
import time
import numpy as np
from urllib.request import urlretrieve
from urllib.request import URLError


###########################     0. utility function      ###########################
def sleepAfterRequest():
    time.sleep(np.random.uniform(10, 60))

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

def getIdList(file):
    '''
    Get movie id list from txt file.
    @file: txt file
    @return: list of ids 
    '''
    with open(file, 'r') as f:
        id_list = f.readlines()
    id_list = [int(movie_id.strip()) for movie_id in id_list]
    return id_list

def outputIdList(id_list, file):
    '''
    Output movie id list to txt file.
    @id_list: movie id list
    @file: txt file
    @return: no return
    '''
    with open(file, 'w') as f:
        for id_ in id_list:
            print(id_, file=f)


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


###############################     3. retrieve book and movie      ################################
def catHTML(category, id):
    '''
    Concatenate item url from its category and id.
    @param category: movie or book
    @param id: item id
    @return: url
    '''
    if category in ['movie', 'book']:
        return 'https://' + category + '.douban.com/subject/' + str(id)
    else:
        raise ValueError('Cannot parse item url, currently only support movie and book.')


def catHTMLtempfile(url):
    '''
    Parse html url, subtract identification information to name file for downloading.
    @param url: api url
    @return: filename
    '''
    url = url.strip('/')
    if 'movie.douban.com/' in url:      # if movie
        id = url.split('/')[-1]
        temp_filename = 'movie.subject.' + id + '.html'
        return temp_filename
    elif 'book.douban.com/' in url:     # if book
        id = url.split('/')[-1]
        temp_filename = 'book.subject.' + id + '.html'
        return temp_filename
    else:
        raise ValueError('Cannot parse html url, currently only support movie and book.')


def downloadHTML(url):
    '''
    Download html file to temp folder
    @param url: movie subject html url
    @return: status (bool)
    '''
    temp_dir = checkTempFolder()
    temp_filename = catHTMLtempfile(url)
    target_path = os.path.join(temp_dir, temp_filename)
    if os.path.exists(target_path):
        print('... Movie html file already exist in temp folder.')
        return True
    else:
        print('... Retrieving movie html file ...')
        try:
            urlretrieve(url, target_path)
            print('... Retrieve succeed!')
            return True
        except URLError:
            print('... Fetching {} failed.'.format(url))
            return False



###############################     4. clean text information      ################################
def cleanSQL(text):
    '''
    Clean apostrophe in sql sentense to prevent error
    @text: text to insert into database
    @return: cleaned text
    '''
    return re.sub('\'', '\'\'', text)

def cleanDate(pubdate):
    '''
    Reformate pubdate to xxxx-xx-xx
    @pubdate: date
    @return: reformated date
    '''
    n_ = re.findall('-', pubdate)
    if len(n_) == 2:
        return pubdate
    elif len(n_) == 1:
        return pubdate + '-01'
    elif len(n_) == 0:
        return pubdate + '-01-01'
    else:
        raise ValueError('pubdate formate error!')

if __name__ == '__main__':
    print('This script contains utility function.\nimport utility')



