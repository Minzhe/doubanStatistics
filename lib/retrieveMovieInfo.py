####################################################################################
###                            retriveMovieInfo.py                               ###
####################################################################################
'''
This python script contains the function and class to retrieve and store movie
subject information from movie.douban.com.

Function structure:
Movie()
├── __init__(self, id)                          | create instance
├── readAPI(self)                               | get movie information from douban api
├── readHTML(self)                              | get movie information from html file
│   └── parseHTML(id)                           | parse movie html content
├── infoComplete(self, verbose, cleanTemp)      | check if movie information is complete
├── getid(self)                                 | return movie id
└── getMovieInfo(self)                          | return movie informaiton
'''

import os
import re
import time
import sys
from urllib.request import urlretrieve
from urllib.request import URLError
from bs4 import BeautifulSoup
from . import utility as u
from pprint import pprint


##################################  function  ###################################
def parseHTML(id):
    """
    This is the core function to parse website movie information from html file and return
    @param id: movie id
    @return: movie attribute dict
    """
    temp_dir = u.checkTempFolder()
    temp_path = os.path.join(temp_dir, 'movie.subject.' + str(id) + '.html')
    if os.path.exists(temp_path):
        with open(temp_path, encoding='utf-8') as html_file:
            data = html_file.read()
            bsObj = BeautifulSoup(data, 'lxml')
            movie_info = dict()

            ### ------------------------ content in <h1> tag ------------------------ ###
            title = bsObj.find('span', {'property': 'v:itemreviewed'}).get_text().strip()
            title = re.sub('\'', '', title)
            if 'Season' in title:           # this item is a tv series
                ### title
                movie_info['title'] = re.match('.+第.+季', title).group()
                movie_info['original_title'] = title.replace(movie_info['title'], '').strip()
            else:                           # this item is a movie
                ### title
                movie_info['title'] = title.split(' ')[0]
                ### original title
                movie_info['original_title'] = ' '.join(title.split(' ')[1:])
                if movie_info['original_title'] == '':  # if Chinese movie (no original name)
                    movie_info['original_title'] = 'Null'
                # elif len(movie_info['original_title'].split(' ')) % 2 == 1:
                #     movie_info['title'] = movie_info['title'] + ' ' + movie_info['original_title'].split(' ')[0].strip()
                #     movie_info['original_title'] = ' '.join(movie_info['original_title'].split(' ')[1:])

            ### year
            year = bsObj.find('span', {'class': 'year'}).get_text().strip('(').strip(')')
            movie_info['year'] = int(year)

            ### ---------------------- content in <div class="subject-others-interests-ft"> ---------------------- ###
            bsObj_others = bsObj.find('div', {'class': 'subject-others-interests-ft'})
            ### tv series
            if '在看' in bsObj_others.findAll('a')[0].get_text():
                movie_info['subtype'] = 'tv'
                ### viewed count
                viewed_count = bsObj_others.find('a', text=re.compile('.*人看过')).get_text().strip('人看过')
                movie_info['viewed_count'] = int(viewed_count)
                ### wish_count
                wish_count = bsObj_others.findAll('a')[2].get_text().strip('人想看')
                movie_info['wish_count'] = int(wish_count)
            ### movie
            elif '看过' in bsObj_others.findAll('a')[0].get_text():
                movie_info['subtype'] = 'movie'
                ### viewed count
                viewed_count = bsObj_others.findAll('a')[0].get_text().strip('人看过')
                movie_info['viewed_count'] = int(viewed_count)
                ### wish_count
                wish_count = bsObj_others.findAll('a')[1].get_text().strip('人想看')
                movie_info['wish_count'] = int(wish_count)
            else:
                raise ValueError('Cannot figure out item type (movie or tv), check original website of movie {}.'.format(id))

            ### ------------------ content in <div id="info"> ---------------------- ###
            bsObj_info = bsObj.find('div', {'id': 'info'})
            ### director
            director = bsObj_info.find('a', {'rel': 'v:directedBy'})['href'].strip('/').split('/')[-1]
            try:
                movie_info['director'] = int(director)
            except:
                movie_info['director'] = 'Null'
                print('Warning: movie director id cannot be parsed!')
            ### country
            movie_info['country'] = bsObj_info.find('span', text=re.compile('.*国家.*')).next_sibling.strip().split('/')[0].strip()
            ### pubdate
            pubdate = [date_.get_text() for date_ in bsObj_info.findAll('span', {'property': 'v:initialReleaseDate'})]
            pubdate = list(map(lambda x: re.sub('\(.*\)', '', x), pubdate))
            if len(pubdate) == 1:
                movie_info['pubdate'] = pubdate[0]
            else:
                try:
                    movie_info['pubdate'] = [date_ for date_ in pubdate if str(movie_info['year']) in date_][0]
                except:
                    movie_info['pubdate'] = sorted(pubdate)[0]
            movie_info['pubdate'] = u.cleanDate(movie_info['pubdate'])
            ### duration
            if movie_info['subtype'] == 'movie':
                duration = bsObj_info.find('span', {'property': 'v:runtime'}).get_text().strip()
                duration = re.findall('([0-9]+)\s*分钟', duration)[0]
                movie_info['episode'] = 'Null'
            elif movie_info['subtype'] == 'tv':
                duration = bsObj_info.find('span', text=re.compile('.*单集片长.*')).next_sibling.strip()
                duration = re.findall('([0-9]+)\s*分钟', duration)[0]
                episode = bsObj_info.find('span', text=re.compile('.*集数.*')).next_sibling.strip()
                movie_info['episode'] = int(episode)
            movie_info['duration'] = int(duration)

            ### ---------------------- content in <div class="rating_self clearfix"> ---------------------- ###
            ### rating_ave
            rating_ave = bsObj.find('strong', {'class': 'll rating_num'}).get_text()
            movie_info['rating_ave'] = float(rating_ave)
            ### rating_count
            rating_count = bsObj.find('span', {'property': 'v:votes'}).get_text()
            movie_info['rating_count'] = int(rating_count)

            ### ---------------------- content in <div class="ratings-on-weight"> ------------------------ ###
            ### rating_5 to 1
            i = 5
            for rating in bsObj.findAll('span', {'class': 'rating_per'}):
                rating_per = float('{0:.3f}'.format(float(rating.get_text().strip('%'))/100))
                exec("movie_info['rating_{}'] = rating_per".format(i))
                i -= 1

            ### ----------------------- content in <div id="comments-section"> -------------------------- ###
            # comment_count
            comment_count = bsObj.find('div', {'id': 'comments-section'}).h2.span.a.get_text().split(' ')[1]
            movie_info['comment_count'] = int(comment_count)

            ### ----------------------- content in <section class="reviews mod movie-content"> ---------- ###
            # review_count
            review_count = bsObj.find('section', {'class': 'reviews mod movie-content'}).header.h2.span.a.get_text().split(' ')[1]
            movie_info['review_count'] = int(review_count)

            ### -------------------------- content in <span class="all hidden"> ------------------------- ###
            movie_intro = bsObj.find('span', {'class': 'all hidden'})
            if movie_intro is not None:
                movie_info['intro'] = ''.join(list(map(lambda x: x.strip(), movie_intro.get_text().strip().split('\n'))))
            else:
                movie_intro = bsObj.find('span', {'property': 'v:summary'})
                if movie_intro is not None:
                    movie_info['intro'] = ''.join(list(map(lambda x: x.strip(), movie_intro.get_text().strip().split('\n'))))

        ### set updated date
        temp_file_mtime = os.path.getmtime(temp_path)
        movie_info['update_date'] = time.strftime('%Y-%m-%d', time.localtime(temp_file_mtime))

        ### final check
        if movie_info['subtype'] == 'movie':
            movie_info['subtype'] = 1
        elif movie_info['subtype'] == 'tv':
            movie_info['subtype'] = 2
        if len(movie_info) == 22:
            print('... Movie {} information parsed.'.format(id))
            return movie_info
        else:
            raise KeyError('Incorrect number of keys of movie dict!')
    else:
        raise ValueError('Cannot find the html file {}.'.format(temp_path))


##################################  movie class  ###################################
class Movie(object):

    def __init__(self, id):
        '''
        Initialize the movie class with item's id
        @ param id: item id
        '''
        self.__id = id                          # item's id
        self.__title = None                     # Chinese name
        self.__original_title = None            # original name
        self.__rating_ave = None                # average rating
        self.__rating_count = None              # number of people rated the movie
        self.__rating_5 = None                  # percentage of 5 star rating
        self.__rating_4 = None                  # percentage of 4 star rating
        self.__rating_3 = None                  # percentage of 3 star rating
        self.__rating_2 = None                  # percentage of 2 star rating
        self.__rating_1 = None                  # percentage of 1 star rating
        self.__wish_count = None                # number of people wish to watch the movie
        self.__viewed_count = None              # number of people viewed the movie
        self.__comment_count = None             # number of short comment on the movie
        self.__review_count = None              # number of review on the movie
        self.__subtype = None                   # movie or tv
        self.__director = None                  # director id of the movie
        self.__pubdate = None                   # the date the movie first released
        self.__year = None                      # year the movie released
        self.__duration = None                  # duration of the movie
        self.__episode = None                   # which episode (only applied when item is a tv series, null for movie)
        self.__country = None                   # country the movie released
        self.__intro = None                     # movie introduction
        self.__update_date = None               # when is this information is updated

    # Because the pubilc api only return limited information, currently the function download the whole webpage
    # def readAPI(self):
    #     '''
    #     Parse json file, and store information to movie instance
    #     @return: no return
    #     '''
    #     # download api json file
    #     api_url = u.catAPIurl('movie', self.__id)
    #     status = u.APIdownloadJson(api_url)
    #     # parse api json file
    #     if status:
    #         movie_info = u.parseJsonMovie(self.__id)
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
        @return: noreturn
        '''
        ### download html file
        html_url = u.catHTML('movie', self.__id)
        status = u.downloadHTML(html_url)
        ### parse html file
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
            self.__intro = movie_info['intro']
            self.__update_date = movie_info['update_date']
        else:
            raise URLError('Fetching {} failed.'.format(html_url))



    def infoComplete(self, verbose=False, cleanTemp=False):
        '''
        Check if movie instance has complete information
        @param verbose: set to True will print unfound attributes of the movie
        @param cleanTemp: whether to delete temp file after the information is stored
        :return: True or False
        '''
        ### information is already complete
        if hasattr(self, 'status') and self.__status == True:
            return self.__status
        ### check if information is complete for new item
        else:
            attrs_vals = list(vars(self).values())
            if all(attrs_vals):
                ### remove temp api file if exists and return true
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
        @return: movie id
        '''
        return self.__id


    def getMovieInfo(self):
        '''
        Return Movie information as dictionary.
        @return: dict of all movie attributes
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
                          ('intro', self.__intro),
                          ('update_date', self.__update_date)])
        return movie_dict


if __name__ == '__main__':
    print('Following is the result to test if this script works\n' + '-'*50)
    # test_movie = Movie(id=1764796)
    test_movie = Movie(id=26416062)
    test_movie.readHTML()
    test_movie.infoComplete(verbose=True, cleanTemp=False)
    print(test_movie.getMovieInfo())