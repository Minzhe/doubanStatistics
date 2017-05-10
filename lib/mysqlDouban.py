###################################################
###                connectDB.py                 ###
###################################################
# This python script is to write information into mysql database.


from configparser import ConfigParser
import sys
import pymysql
import datetime
from lib import utility
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


def getPersonlMovie(userID):
    '''
    Parse personal movie history movie information temp file, get all viewed movie id.
    :param userID: userID
    :return: movie id list
    '''
    tmp_path = catHistoryTempFile(userID=userID)
    with open(tmp_path, 'r') as f:
        id_list = f.readlines()
    id_list = [int(movie_id.strip()) for movie_id in id_list]

    return id_list


###############     2. connect to database      ###############
def connect(host, user, passwd, db):
    conn = pymysql.connect(host=host, user=user, passwd=passwd, db=db, charset='utf8')
    return conn


def movieCursor(self):
    cur = self.cursor(pymysql.cursors.DictCursor)
    cur.execute('USE doubanStatistics')
    return cur

### Add method to pymysql.connections.Connection class
pymysql.connections.Connection.movieCursor = movieCursor


###############     3. write movie info to database      ###############
def ifUpdate(self, id, cleanTemp=False):
    '''
    Check if certain movie if exist in database, if not then write,
    if exist but haven't been updated for a while, then update, otherwise skip
    :param cur: database cursor
    :param id: movie id
    :param cleanTemp: if remove temp file
    :return: status
    '''
    sql = 'SELECT id, update_date FROM `movie_subject` WHERE id = {}'.format(id)
    self.execute(sql)
    data = self.fetchone()
    if data is None:
        print('Movie id {} does not exist, need to be stored.'.format(id))
        return True
    elif datetime.date.today() - data['update_date'] > datetime.timedelta(90):
        print('Movie id {} exist, but data is old, need to be updated.'.format(id))
        return True
    else:
        print('Movie id {} exist, data is new, do not need to be updated.'.format(id))
        if cleanTemp == True:
            utility.rmTemp(category='movie', id=id)
        return False

### Add method to pymysql.cursors.Cursor class
pymysql.cursors.Cursor.ifUpdate = ifUpdate

def InsertUpdateSQL(movie):
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
              'update_date) ' \
              'VALUES ({}, \'{}\', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, \'{}\', \'{}\', {}, {}, \'{}\', \'{}\') ' \
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
              'update_date) ' \
              'VALUES ({}, \'{}\', \'{}\', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, \'{}\', \'{}\', {}, {}, \'{}\', \'{}\') ' \
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

def InsertUpdate(self, movie, cleanTemp=False):
    '''
    Write movie objects data into database.
    :param conn: database connection
    :param movie_list: movie objects to write
    :param cleanTemp: if remove temp file
    :return: no return
    '''
    print('... Writing movie {} {} to database.'.format(movie['id'], movie['title']))
    sql = InsertUpdateSQL(movie)
    try:
        self.execute(sql)
        if cleanTemp:
            utility.rmTemp(category='movie', id=movie['id'])
    except:
        print('Writing to mysql failed! SQL:', sql, sys.exc_info(), sep='\n')
        sys.exit()
    self.connection.commit()

### Add method to pymysql.cursors.Cursor class
pymysql.cursors.Cursor.InsertUpdate = InsertUpdate




if __name__ == '__main__':
    print('This script.')
