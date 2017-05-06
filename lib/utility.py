###################################################
###                 utility.py                  ###
###################################################
# This python module contains utility functions.

import os
import sys
from urllib.request import urlretrieve
from urllib.request import URLError
import json
from bs4 import BeautifulSoup
import re
import time




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
        return 'https://' + category + '.douban.com/subject/' + str(id)
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

            ### <h1>
            title = bsObj.find('span', {'property': 'v:itemreviewed'}).get_text().strip()
            if 'Season' in title:           # tv
                # title
                movie_info['title'] = re.match('.+第.+季', title).group()
                movie_info['original_title'] = title.replace(movie_info['title'], '').strip()
            else:                           # movie
                # title
                movie_info['title'] = title.split(' ')[0]
                # original title
                movie_info['original_title'] = ' '.join(title.split(' ')[1:])
                if movie_info['original_title'] == '':  # if Chinese movie (no original name)
                    movie_info['original_title'] = 'Null'

            # year
            year = bsObj.find('span', {'class': 'year'}).get_text().strip('(').strip(')')
            movie_info['year'] = int(year)

            ### <div class="subject-others-interests-ft">
            bsObj_others = bsObj.find('div', {'class': 'subject-others-interests-ft'})
            ## tv
            if '在看' in bsObj_others.findAll('a')[0].get_text():
                movie_info['subtype'] = 'tv'
                # viewed count
                viewed_count = bsObj_others.find('a', text=re.compile('.*人看过')).get_text().strip('人看过')
                movie_info['viewed_count'] = int(viewed_count)
                # wish_count
                wish_count = bsObj_others.findAll('a')[2].get_text().strip('人想看')
                movie_info['wish_count'] = int(wish_count)
            ## movie
            elif '看过' in bsObj_others.findAll('a')[0].get_text():
                movie_info['subtype'] = 'movie'
                # viewed count
                viewed_count = bsObj_others.findAll('a')[0].get_text().strip('人看过')
                movie_info['viewed_count'] = int(viewed_count)
                # wish_count
                wish_count = bsObj_others.findAll('a')[1].get_text().strip('人想看')
                movie_info['wish_count'] = int(wish_count)
            else:
                raise ValueError('Cannot figure out item type (movie or tv), check original website of movie {}.'.format(id))


            ### <div id="info">
            bsObj_info = bsObj.find('div', {'id': 'info'})
            # director
            director = bsObj_info.find('a', {'rel': 'v:directedBy'})['href'].strip('/').split('/')[-1]
            movie_info['director'] = int(director)
            # country
            movie_info['country'] = bsObj_info.find('span', text=re.compile('.*国家.*')).next_sibling.strip()
            # pubdate
            pubdate = bsObj_info.find('span', {'property': 'v:initialReleaseDate'}).get_text()      # find the first
            movie_info['pubdate'] = re.sub('\(.*\)', '', pubdate)
            # duration
            if movie_info['subtype'] == 'movie':
                duration = bsObj_info.find('span', {'property': 'v:runtime'}).get_text().split(' ')[0].strip('分钟')
                movie_info['episode'] = -1
            elif movie_info['subtype'] == 'tv':
                duration = bsObj_info.find('span', text=re.compile('.*单集片长.*')).next_sibling.strip().strip('分钟')
                episode = bsObj_info.find('span', text=re.compile('.*集数.*')).next_sibling.strip()
                movie_info['episode'] = int(episode)
            movie_info['duration'] = int(duration)


            ### <div class="rating_self clearfix">
            # rating_ave
            rating_ave = bsObj.find('strong', {'class': 'll rating_num'}).get_text()
            movie_info['rating_ave'] = float(rating_ave)
            # rating_count
            rating_count = bsObj.find('span', {'property': 'v:votes'}).get_text()
            movie_info['rating_count'] = int(rating_count)

            ### <div class="ratings-on-weight">
            # rating_5-1
            i = 5
            for rating in bsObj.findAll('span', {'class': 'rating_per'}):
                rating_per = float('{0:.3f}'.format(float(rating.get_text().strip('%'))/100))
                exec("movie_info['rating_{}'] = rating_per".format(i))
                i -= 1

            ### <div id="comments-section">
            # comment_count
            comment_count = bsObj.find('div', {'id': 'comments-section'}).h2.span.a.get_text().split(' ')[1]
            movie_info['comment_count'] = int(comment_count)

            ### <section class="reviews mod movie-content">
            # review_count
            review_count = bsObj.find('section', {'class': 'reviews mod movie-content'}).header.h2.span.a.get_text().split(' ')[1]
            movie_info['review_count'] = int(review_count)

        # change date
        temp_file_mtime = os.path.getmtime(temp_path)
        movie_info['update_date'] = time.strftime('%Y-%m-%d', time.localtime(temp_file_mtime))

        if len(movie_info) == 21:
            return movie_info
        else:
            raise KeyError('Incorrect number of keys of movie dict!')





if __name__ == '__main__':
    print('1.', getProjectDir())
    url_1 = catAPIurl('movie', '1764796')
    url_2 = catHTML('movie', '1764796')
    print('2.', url_1, '\n', url_2)
    tempfile_1 = catAPItempfile(url_1)
    tempfile_2 = catHTMLtempfile(url_2)
    print('3.', tempfile_1, '\n', tempfile_2)
    print(APIdownloadJson('https://api.douban.com/v2/movie/subject/1764796'))
    print('movie', downloadHTML('https://movie.douban.com/subject/1764796'))
    print('tv', downloadHTML('https://movie.douban.com/subject/10748120'))
    # print('5.', parseJsonMovie('1764796'))
    print('6.movie', parseHTML('1764796'))
    print('6.tv', parseHTML('10748120'))



