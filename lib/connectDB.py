###################################################
###                connectDB.py                 ###
###################################################
# This python script is to write information into mysql database.


from configparser import ConfigParser
import sys
import pymysql

###############     1. connect to database      ###############
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


def DBconnect(db_config):
    '''
    Connect to database.
    :param db_config: list of host, user, password, db information
    :return: database connection
    '''
    conn = pymysql.connect(host=db_config['host'], user=db_config['username'], passwd=db_config['passwd'], db=db_config['db'], charset='utf8')
    return conn


###############     2. write movie data to database      ###############
def writeMovieToDB(conn, movie_list):
    '''
    Write movie objects data into database.
    :param conn: database connection
    :param movie_list: movie objects to write
    :return: no return
    '''
    cur = conn.cursor()
    cur.execute('USE doubanStatistics')

    for movie in movie_list:
        sql = 'INSERT INTO movie.subject (' \
              'id, ' \
              'title, ' \
              'originial_title, ' \
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
              'VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')' \
              .format(movie['id'],
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
                      movie['update_date'])
        print(sql)

if __name__ == '__main__':
    db_config = parseDBconfig('/home/minzhe/dbincloc/doubanStatistics.db')
    print('1.', db_config)
    conn = DBconnect(db_config)
