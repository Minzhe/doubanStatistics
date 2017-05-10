###################################################
###        retrivePersonalMovieHistory.py       ###
###################################################
'''
This python script contains the function and class to retrieve and store movie
subject information from movie.douban.com.

Demo:
------------------
new_movie = Movie(id=)
new_movie.readHTML()
    catHTML()
    downloadHTML()
        catHTMLtempfile()
    parseHTML()
new_movie.infoComplete(verbose=True)
info_dict = new_movie.getMovieInfo()
'''

import os
from urllib.request import urlretrieve
from urllib.request import URLError
from bs4 import BeautifulSoup
import re
import time
import sys
from . import utility



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
    :param url: movie subject html url
    :return: status
    '''
    temp_dir = utility.checkTempFolder()
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
            print('... Fetching {} failed.'.format(url), sys.exc_info())
            return False


def parseHTML(id):
    '''
    Parse website movie information from html file and return .
    :param id: movie id
    :return: movie attribute dict
    '''
    temp_dir = utility.checkTempFolder()
    temp_path = os.path.join(temp_dir, 'movie.subject.' + str(id) + '.html')
    if os.path.exists(temp_path):
        with open(temp_path, encoding='utf-8') as html_file:
            data = html_file.read()
            bsObj = BeautifulSoup(data, 'lxml')
            movie_info = dict()

            ### <h1>
            title = bsObj.find('span', {'property': 'v:itemreviewed'}).get_text().strip()
            title = re.sub('\'', '', title)
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
                # elif len(movie_info['original_title'].split(' ')) % 2 == 1:
                #     movie_info['title'] = movie_info['title'] + ' ' + movie_info['original_title'].split(' ')[0].strip()
                #     movie_info['original_title'] = ' '.join(movie_info['original_title'].split(' ')[1:])

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
            try:
                movie_info['director'] = int(director)
            except:
                movie_info['director'] = 'Null'
                print('Warning: movie director id cannot be parsed!')
            # country
            movie_info['country'] = bsObj_info.find('span', text=re.compile('.*国家.*')).next_sibling.strip().split('/')[0].strip()
            # pubdate
            pubdate = bsObj_info.find('span', {'property': 'v:initialReleaseDate'}).get_text()      # find the first
            movie_info['pubdate'] = re.sub('\(.*\)', '', pubdate)
            # duration
            if movie_info['subtype'] == 'movie':
                duration = bsObj_info.find('span', {'property': 'v:runtime'}).get_text().split(' ')[0].strip('分钟')
                movie_info['episode'] = 'Null'
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

        # final check
        if movie_info['subtype'] == 'movie':
            movie_info['subtype'] = 1
        elif movie_info['subtype'] == 'tv':
            movie_info['subtype'] = 2

        if len(movie_info) == 21:
            print('... Movie {} information parsed.'.format(id))
            return movie_info
        else:
            raise KeyError('Incorrect number of keys of movie dict!')


class Movie(object):
    def __init__(self, id):
        self.__id = id
        self.__title = None                     # Chinese name
        self.__original_title = None            # original name
        self.__rating_ave = None
        self.__rating_count = None
        self.__rating_5 = None
        self.__rating_4 = None
        self.__rating_3 = None
        self.__rating_2 = None
        self.__rating_1 = None
        self.__wish_count = None
        self.__viewed_count = None
        self.__comment_count = None
        self.__review_count = None
        self.__subtype = None
        self.__director = None
        self.__pubdate = None
        self.__year = None
        self.__duration = None
        self.__episode = None
        self.__country = None
        self.__update_date = None


    # def readAPI(self):
    #     '''
    #     Parse json file, and store information to movie instance
    #     :return: no return
    #     '''
    #     # download api json file
    #     api_url = utility.catAPIurl('movie', self.__id)
    #     status = utility.APIdownloadJson(api_url)
    #     # parse api json file
    #     if status:
    #         movie_info = utility.parseJsonMovie(self.__id)
    #         self.__title = movie_info['title']
    #         self.__original_title = movie_info['original_title']
    #         self.__rating_ave = movie_info['rating_ave']
    #         self.__rating_count = movie_info['rating_count']
    #         self.__wish_count = movie_info['wish_count']
    #         self.__viewed_count = movie_info['viewed_count']
    #         self.__comment_count = movie_info['comment_count']
    #         self.__review_count = movie_info['review_count']
    #         self.__subtype = movie_info['subtype']
    #         self.__director = movie_info['director']
    #         self.__year = movie_info['year']
    #         self.__country = movie_info['country']

    def readHTML(self):
        '''
        Parse html file, and store information to movie instance
        :return: noreturn
        '''
        # download html file
        html_url = catHTML('movie', self.__id)
        status = downloadHTML(html_url)
        # parse html file
        if status:
            movie_info = parseHTML(self.__id)
            self.__title = movie_info['title']
            self.__original_title = movie_info['original_title']
            self.__rating_ave = movie_info['rating_ave']
            self.__rating_count = movie_info['rating_count']
            self.__rating_5 = movie_info['rating_5']
            self.__rating_4 = movie_info['rating_4']
            self.__rating_3 = movie_info['rating_3']
            self.__rating_2 = movie_info['rating_2']
            self.__rating_1 = movie_info['rating_1']
            self.__wish_count = movie_info['wish_count']
            self.__viewed_count = movie_info['viewed_count']
            self.__comment_count = movie_info['comment_count']
            self.__review_count = movie_info['review_count']
            self.__subtype = movie_info['subtype']
            self.__director = movie_info['director']
            self.__pubdate = movie_info['pubdate']
            self.__year = movie_info['year']
            self.__duration = movie_info['duration']
            self.__episode = movie_info['episode']
            self.__country = movie_info['country']
            self.__update_date = movie_info['update_date']


    def infoComplete(self, verbose=False, cleanTemp=False):
        '''
        Check if movie instance has complete information
        :param verbose: if print vacumn
        :return: True or False
        '''
        if hasattr(self, 'status') and self.__status == True:
            return self.__status
        else:
            attrs_vals = list(vars(self).values())
            if all(attrs_vals):
                # remove temp api file if exists and return true
                curdir = os.path.dirname(os.path.realpath(__file__))
                tmpfile_api = os.path.abspath(os.path.join(curdir, '../temp/api.movie.subject.' + str(self.__id) + '.json'))
                tmpfile_html = os.path.abspath(os.path.join(curdir, '../temp/movie.subject.' + str(self.__id) + '.html'))
                if cleanTemp:
                    os.remove(tmpfile_api) if os.path.exists(tmpfile_api) else None
                    os.remove(tmpfile_html) if os.path.exists(tmpfile_html) else None
                self.__status = True
                return self.__status
            elif verbose:
                none_attrs = [attr for attr in dir(self) if '_Movie' in attr and self.__getattribute__(attr) is None]
                print('Following information is lacking:', *none_attrs, sep='\n......')
                return False
            else:
                return False


    def getid(self):
        '''
        Return attribute movie id
        :return: movie id
        '''
        return self.__id


    def getMovieInfo(self):
        '''
        Return Movie information as dictionary.
        :return: dict
        '''
        movie_dict = dict([('id', self.__id),
                          ('title', self.__title),
                          ('original_title', self.__original_title),
                          ('rating_ave', self.__rating_ave),
                          ('rating_count', self.__rating_count),
                          ('rating_5', self.__rating_5),
                          ('rating_4', self.__rating_4),
                          ('rating_3', self.__rating_3),
                          ('rating_2', self.__rating_2),
                          ('rating_1', self.__rating_1),
                          ('wish_count', self.__wish_count),
                          ('viewed_count', self.__viewed_count),
                          ('comment_count', self.__comment_count),
                          ('review_count', self.__review_count),
                          ('subtype', self.__subtype),
                          ('director', self.__director),
                          ('pubdate', self.__pubdate),
                          ('year', self.__year),
                          ('duration', self.__duration),
                          ('episode', self.__episode),
                          ('country', self.__country),
                          ('update_date', self.__update_date)])
        return movie_dict


if __name__ == '__main__':
    print('This script')