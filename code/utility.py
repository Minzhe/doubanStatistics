###################################################
###                 utility.py                  ###
###################################################
# This python module contains utility functions.

import os
import sys
from urllib.request import urlretrieve
from urllib.request import URLError
from configparser import ConfigParser

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
        return 'https://api.douban.com/v2/movie/subject/' + id
    elif category == 'book':
        return 'https://api.douban.com/v2/book/' + id
    else:
        raise ValueError('Cannot parse item url, currently only support movie and book.')


def catAPItempfile(url):
    '''
    Parse api url, subtract identification information to name file for downloading.
    :param url: api url
    :return: filename
    '''
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
    if not os.path.exists(target_path):
        try:
            urlretrieve(url, target_path)
        except URLError:
            print('Fetching api url failed, check internet connection.', sys.exc_info())

def parseAPImovie(file):
    '''
    Parse api movie information and return from json file.
    :param file: api temp json file
    :return: movie attribute dict
    '''



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
        db_congif_dict = {}
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
    print(getProjectDir())
    print(catAPItempfile('https://api.douban.com/v2/movie/subject/1764796'))
    print(catAPItempfile('https://api.douban.com/v2/book/1003078'))
    APIdownloadJson('https://api.douban.com/v2/movie/subject/1764796')
    print(parseDBconfig('/home/minzhe/dbincloc/doubanStatistics.db'))
    print(catHTML('movie', '1764796'))

