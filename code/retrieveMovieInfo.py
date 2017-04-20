###################################################
###        retrivePersonalMovieHistory.py       ###
###################################################
# This python script is to retrieve movie subject information from movie.douban.com.

import sys
import os
import pprint
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import utility


class Movie(object):
    def __init__(self, id):
        self.__id = id
        self.__title = None
        self.__original_title = None
        self.__ave_rating = None
        self.__rating_count = None
        self.__rating_5 = None
        self.__rating_4 = None
        self.__rating_3 = None
        self.__rating_2 = None
        self.__rating_1 = None
        self.__wish_count = None
        self.__viewed_count = None
        self.__watching_count = None
        self.__comment_count = None
        self.__review_count = None
        self.__subtype = None
        self.__directors = None
        self.__writers = None
        self.__pubdates = None
        self.__mainland_pubdate = None
        self.__year = None
        self.__durations = None
        self.__countries = None
        self.__update_date = None

    def infoComplete(self, verbose=False):
        attrs_vals = list(vars(self).values())
        if all(attrs_vals):
            # remove temp api file if exists and return true
            curdir = os.path.dirname(os.path.realpath(__file__))
            tmpfile = os.path.abspath(os.path.join(curdir, '../temp/api.movie.subject.' + str(self.__id) + '.json'))
            if os.path.exists(tmpfile):
                os.remove(tmpfile)
            return True
        else:
            if verbose:
                none_attrs = [attr for attr in dir(self) if '_Movie' in attr and self.__getattribute__(attr) is None]
                print('Following information is lacking:', *none_attrs, sep='\n')
            return False

    def readAPI(self):
        api_url = utility.catAPIurl(self.__id)
        utility.APIdownloadJson(api_url)


    def getid(self):
        return self.__id



robots_9 = Movie(1764796)
print(robots_9.getid())
print(robots_9.infoComplete())
print(robots_9.__getattribute__('_Movie__year'))
print(len(robots_9.__dict__))
