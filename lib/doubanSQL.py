################################################################
###                        doubanSQL.py                      ###
################################################################
'''
This python script is to write information into mysql database.

1. ##### utility
└── parseDBconfig(config_file)
2. ##### connect to databse
└── doubanCursor(self)                  pymysql.connections.Connection.doubanCursor
    └── connect(host, user, passwd, db)
3. ##### write to databse
├── ifUpdate(self, id, cleanTemp=False, force=False)        pymysql.cursors.Cursor.ifUpdate
├── InsertUpdateMovie(self, movie, cleanTemp=False)         pymysql.cursors.Cursor.InsertUpdateMovie
    ├── 
    └── InsertUpdateMovieSQL(movie)
4. ##### search database information
├── getIdList(subject)

'''

from configparser import ConfigParser
import sys
import re
import pymysql
import datetime
from lib import utility as u
from lib.retrievePersonalMovie import catHistoryTempFile

###############     1. utility function      ###############
def parseDBconfig(config_file):
    '''
    Read database configuration information
    :param config_file: configuration file path
    :return: list of host, user, password, db information
    '''
    parser = ConfigParser()
    try:
        parser.read(config_file)
        db_config_dict = dict()
        if parser.has_section('db_config'):
            db_config_dict['host'] = parser.get('db_config', 'host')
            db_config_dict['username'] = parser.get('db_config', 'username')
            db_config_dict['passwd'] = parser.get('db_config', 'password')
            db_config_dict['db'] = parser.get('db_config', 'database')
            return db_config_dict
        else:
            raise ValueError('Configuration file dose not contain the required information, please check it.')
    except:
        print('Parsing database configuration failed.\n', sys.exc_info())



###############     2. connect to database      ###############
def connect(host, user, passwd, db):
    conn = pymysql.connect(host=host, user=user, passwd=passwd, db=db, charset='utf8')
    return conn


def doubanCursor(self):
    cur = self.cursor(pymysql.cursors.DictCursor)
    cur.execute('USE doubanStatistics')
    return cur

### Add method to pymysql.connections.Connection class
pymysql.connections.Connection.doubanCursor = doubanCursor


###############     3. write movie info to database      ###############
def ifUpdate(self, id, cleanTemp=False, force=False):
    '''
    Check if certain movie if exist in database, if not then write,
    if exist but haven't been updated for a while, then update, otherwise skip
    @param cur: database cursor
    @param id: movie id
    @param cleanTemp: if remove temp file
    @return: status
    '''
    if force:
        return True
    else:
        sql = 'SELECT id, update_date FROM `movie_subject` WHERE id = {}'.format(id)
        self.execute(sql)
        data = self.fetchone()
        if data is None:
            print('Movie id {} does not exist in database, need to be updated.'.format(id))
            return True
        elif datetime.date.today() - data['update_date'] > datetime.timedelta(90):
            print('Movie id {} exist, but data is outdated, need to be updated.'.format(id))
            return True
        else:
            print('Movie id {} exist, data is new, do not need to be updated.'.format(id))
            if cleanTemp == True:
                u.rmTemp(category='movie', id=id)
            return False

### Add method to pymysql.cursors.Cursor class
pymysql.cursors.Cursor.ifUpdate = ifUpdate

def InsertUpdateMovieSQL(movie):
    '''
    Prepare sql for writting movie information to MySQL database.
    :param movie: Dict contain movie information
    :return:
    '''
    if movie['original_title'] == 'Null':
        sql = 'INSERT INTO movie_subject (' \
              'id, ' \
              'title, ' \
              'original_title, ' \
              'rating_ave, ' \
              'rating_count,' \
              'rating_5, ' \
              'rating_4, ' \
              'rating_3, ' \
              'rating_2, ' \
              'rating_1, ' \
              'wish_count, ' \
              'viewed_count, ' \
              'comment_count, ' \
              'review_count, ' \
              'subtype, ' \
              'director, ' \
              'pubdate, ' \
              'year, ' \
              'duration, ' \
              'episode, ' \
              'country, ' \
              'intro, ' \
              'update_date) ' \
              'VALUES ({}, \'{}\', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, \'{}\', \'{}\', {}, {}, \'{}\', \'{}\', \'{}\') ' \
              'ON DUPLICATE KEY UPDATE ' \
              'rating_ave = {}, ' \
              'rating_count = {}, ' \
              'rating_5 = {}, ' \
              'rating_4 = {}, ' \
              'rating_3 = {}, ' \
              'rating_2 = {}, ' \
              'rating_1 = {}, ' \
              'wish_count = {}, ' \
              'viewed_count = {}, ' \
              'comment_count = {}, ' \
              'review_count = {}, ' \
              'update_date = \'{}\'' \
              .format(  # following insert content
                      movie['id'],
                      movie['title'],
                      movie['original_title'],
                      movie['rating_ave'],
                      movie['rating_count'],
                      movie['rating_5'],
                      movie['rating_4'],
                      movie['rating_3'],
                      movie['rating_2'],
                      movie['rating_1'],
                      movie['wish_count'],
                      movie['viewed_count'],
                      movie['comment_count'],
                      movie['review_count'],
                      movie['subtype'],
                      movie['director'],
                      movie['pubdate'],
                      movie['year'],
                      movie['duration'],
                      movie['episode'],
                      movie['country'],
                      movie['intro'],
                      movie['update_date'],
                        # following update content
                      movie['rating_ave'],
                      movie['rating_count'],
                      movie['rating_5'],
                      movie['rating_4'],
                      movie['rating_3'],
                      movie['rating_2'],
                      movie['rating_1'],
                      movie['wish_count'],
                      movie['viewed_count'],
                      movie['comment_count'],
                      movie['review_count'],
                      movie['update_date'])
    else:   # movie['original_title'] != 'Null'
        sql = 'INSERT INTO movie_subject (' \
              'id, ' \
              'title, ' \
              'original_title, ' \
              'rating_ave, ' \
              'rating_count,' \
              'rating_5, ' \
              'rating_4, ' \
              'rating_3, ' \
              'rating_2, ' \
              'rating_1, ' \
              'wish_count, ' \
              'viewed_count, ' \
              'comment_count, ' \
              'review_count, ' \
              'subtype, ' \
              'director, ' \
              'pubdate, ' \
              'year, ' \
              'duration, ' \
              'episode, ' \
              'country, ' \
              'intro, ' \
              'update_date) ' \
              'VALUES ({}, \'{}\', \'{}\', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, \'{}\', \'{}\', {}, {}, \'{}\', \'{}\', \'{}\') ' \
              'ON DUPLICATE KEY UPDATE ' \
              'rating_ave = {}, ' \
              'rating_count = {}, ' \
              'rating_5 = {}, ' \
              'rating_4 = {}, ' \
              'rating_3 = {}, ' \
              'rating_2 = {}, ' \
              'rating_1 = {}, ' \
              'wish_count = {}, ' \
              'viewed_count = {}, ' \
              'comment_count = {}, ' \
              'review_count = {}, ' \
              'update_date = \'{}\'' \
              .format(  # following insert content
                      movie['id'],
                      movie['title'],
                      movie['original_title'],
                      movie['rating_ave'],
                      movie['rating_count'],
                      movie['rating_5'],
                      movie['rating_4'],
                      movie['rating_3'],
                      movie['rating_2'],
                      movie['rating_1'],
                      movie['wish_count'],
                      movie['viewed_count'],
                      movie['comment_count'],
                      movie['review_count'],
                      movie['subtype'],
                      movie['director'],
                      movie['pubdate'],
                      movie['year'],
                      movie['duration'],
                      movie['episode'],
                      movie['country'],
                      movie['intro'],
                      movie['update_date'],
                        # following update content
                      movie['rating_ave'],
                      movie['rating_count'],
                      movie['rating_5'],
                      movie['rating_4'],
                      movie['rating_3'],
                      movie['rating_2'],
                      movie['rating_1'],
                      movie['wish_count'],
                      movie['viewed_count'],
                      movie['comment_count'],
                      movie['review_count'],
                      movie['update_date'])
    return sql


def InsertUpdateMovie(self, movie, cleanTemp=False):
    '''
    Write movie objects data into database.
    @param self: doubanCursor()
    @param movie: movie dict
    @param cleanTemp: if remove temp file
    @return: no return
    '''
    print('... Writing movie {} {} to database.'.format(movie['id'], movie['title']))
    movie['intro'] = u.cleanSQL(movie['intro'])
    sql = InsertUpdateMovieSQL(movie)
    try:
        self.execute(sql)
        if cleanTemp:
            u.rmTemp(category='movie', id=movie['id'])
    except:
        print('Writing to mysql failed! SQL:', sql, sys.exc_info(), sep='\n')
        sys.exit()
    self.connection.commit()

### Add method to pymysql.cursors.Cursor class
pymysql.cursors.Cursor.InsertUpdateMovie = InsertUpdateMovie


###############     3. write movie info to database      ###############s
def getIdList(self, subject):
    '''
    Function to get all subject ids:
    @subject: movie or book
    @return: id list
    '''
    if subject == 'movie':
        sql = 'SELECT id from `movie_subject`'
    elif subject == 'book':
        sql = 'SELECT id from `book_subject`'
    else:
        raise ValueError('Incorrect subject type, support book or movie.')
    self.execute(sql)
    data = self.fetchall()
    return list(map(lambda x: x['id'], data))

### Add method to pymysql.cursors.Cursor class
pymysql.cursors.Cursor.getIdList = getIdList

if __name__ == '__main__':
    print('This script.')
