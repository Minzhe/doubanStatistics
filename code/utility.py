###################################################
###                 utility.py                  ###
###################################################
# This python module contains utility functions.

import os
import sys
from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.request import URLError
from configparser import ConfigParser
import json
from bs4 import BeautifulSoup


###############     1. working with directory      ###############
def getProjectDir():
    '''
    get the top absolute dirname of the project
    :return: dirname
    '''
    file_path = os.path.realpath(__file__)
    end_idx = file_path.find('doubanStatistics')
    proj_dir = file_path[0:end_idx] + 'doubanStatistics'
    return proj_dir


def checkTempFolder():
    '''
    Check if temp folder exist, and create it if not.
    :return: no return
    '''
    proj_dir = getProjectDir()
    temp_dir = os.path.join(proj_dir, 'temp')
    if not os.path.isdir(temp_dir):
        os.makedirs(temp_dir)
    return temp_dir


###############     2. working with api      ###############
def catAPIurl(category, id):
    '''
    Concatenate item api url from its category and id.
    :param category: movie or book
    :param id: item id
    :return: url
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
    :param url: api url
    :return: filename
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
    :param url: json url.
    :return: no return.
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
    :param id: movie id
    :return: movie attribute dict
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



###############     3. working with html      ###############
def catHTML(category, id):
    '''
    Concatenate item url from its category and id.
    :param category: movie or book
    :param id: item id
    :return: url
    '''
    if category in ['movie', 'book']:
        return 'https://' + category + '.douban.com/subject/' + id
    else:
        raise ValueError('Cannot parse item url, currently only support movie and book.')


def catHTMLtempfile(url):
    '''
    Parse html url, subtract identification information to name file for downloading.
    :param url: api url
    :return: filename
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
    :param url:
    :return: no return
    '''
    temp_dir = checkTempFolder()
    temp_filename = catHTMLtempfile(url)
    target_path = os.path.join(temp_dir, temp_filename)
    if os.path.exists(target_path):
        return True
    else:
        try:
            urlretrieve(url, target_path)
            return True
        except URLError:
            print('Fetching {} failed.'.format(url), sys.exc_info())
            return False


def parseHTML(id):
    '''
    Parse website movie information from html file and return .
    :param id: movie id
    :return: movie attribute dict
    '''
    temp_dir = checkTempFolder()
    temp_path = os.path.join(temp_dir, 'movie.subject.' + str(id) + '.html')
    if os.path.exists(temp_path):
        with open(temp_path, encoding='utf-8') as html_file:
            data = html_file.read()
            bsObj = BeautifulSoup(data, 'lxml')
            movie_info = dict()
            # extract 5 stars rating distribution
            i = 5
            for rating in bsObj.findAll('span', {'class': 'rating_per'}):
                rating_per = float(rating.get_text().strip('%'))/100
                rating_per = float('{0:.3f}'.format(rating_per))
                exec("movie_info['rating_{}'] = rating_per".format(i))
                i -= 1
            # extract pubdate
            movie_info['pubdate'] = bsObj.find('span', {'class': 'comment-time'}).get_text().strip()
            print(movie_info)



###############     4. connect to database      ###############
def parseDBconfig(config_file):
    '''
    Read database configuration information
    :param config_file: configuration file path
    :return: list of host, user, password, db information
    '''
    parser = ConfigParser()
    try:
        parser.read(config_file)
        db_congif_dict = dict()
        if parser.has_section('db_config'):
            db_congif_dict['host'] = parser.get('db_config', 'host')
            db_congif_dict['username'] = parser.get('db_config', 'username')
            db_congif_dict['passwd'] = parser.get('db_config', 'password')
            db_congif_dict['db'] = parser.get('db_config', 'database')
            return db_congif_dict
        else:
            raise ValueError('Configuration file dose not contain the required information, please check it.')
    except:
        print('Parsing database configuration failed.\n', sys.exc_info())


if __name__ == '__main__':
    print('1.', getProjectDir())
    url_1 = catAPIurl('movie', '1764796')
    url_2 = catHTML('movie', '1764796')
    print('2.', url_1, '\n', url_2)
    tempfile_1 = catAPItempfile(url_1)
    tempfile_2 = catHTMLtempfile(url_2)
    print('3.', tempfile_1, '\n', tempfile_2)
    print(APIdownloadJson('https://api.douban.com/v2/movie/subject/1764796'))
    print(downloadHTML('https://movie.douban.com/subject/1764796/'))
    print('5.', parseJsonMovie('1764796'))
    print('6.', parseHTML('1764796'))
    print('7.', parseDBconfig('/home/minzhe/dbincloc/doubanStatistics.db'))


