###################################################
###        retrivePersonalMovieHistory.py       ###
###################################################
# This python script contains the function and class to retrieve and store movie subject information from movie.douban.com.

import os
from . import utility


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
        html_url = utility.catHTML('movie', self.__id)
        status = utility.downloadHTML(html_url)
        # parse html file
        if status:
            movie_info = utility.parseHTML(self.__id)
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
        attrs_vals = list(vars(self).values())
        if all(attrs_vals):
            # remove temp api file if exists and return true
            curdir = os.path.dirname(os.path.realpath(__file__))
            tmpfile_api = os.path.abspath(os.path.join(curdir, '../temp/api.movie.subject.' + str(self.__id) + '.json'))
            tmpfile_html = os.path.abspath(os.path.join(curdir, '../temp/movie.subject.' + str(self.__id) + '.html'))
            if cleanTemp:
                os.remove(tmpfile_api) if os.path.exists(tmpfile_api) else None
                os.remove(tmpfile_html) if os.path.exists(tmpfile_html) else None
            return True
        elif verbose:
            none_attrs = [attr for attr in dir(self) if '_Movie' in attr and self.__getattribute__(attr) is None]
            print('Following information is lacking:', *none_attrs, sep='\n')
            return False

    def prepareDataForDB(self):
        '''
        Prepare movie information data for database insertion. First check if all data is ready (no None value),
        then convert some preset None value back to None.
        :return: True or False
        '''
        if self.infoComplete():
            self.__episode = None if self.__episode == -1 else None
            self.__original_title = None if self.__original_title == 'Null' else None
            return True
        else:
            print('Information not complete!')
            return self.infoComplete(verbose=True)


    def getid(self):
        '''
        Return attribute movie id
        :return: movie id
        '''
        return self.__id


if __name__ == '__main__':
    print('This script')