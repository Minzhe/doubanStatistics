#####################################################
###                retrivelMovie.py               ###
#####################################################
# This python script is to retrieve movie information.

import sys
from os.path import join, dirname, abspath
sys.path.append(join(dirname(abspath(__file__)), '..'))
from lib.retrieveMovieInfo import Movie
from lib.retrievePersonalMovie import retrieveHistory
from lib import mysqlDouban
from lib import utility


# robots_9 = Movie(1764796)
# print('1.', robots_9.getid())
# print('2.', robots_9.infoComplete(verbose=True))
# print('3.', robots_9.__getattribute__('_Movie__year'))
# print('4.', robots_9.__dict__)
# print('5.')
# robots_9.readHTML()
# print('6.', vars(robots_9))
# print('7.', robots_9.infoComplete(verbose=True))
# print('\n')
#
# detective = Movie(10748120)
# print('1.', detective.getid())
# print('5.')
# detective.readHTML()
# print('6.', vars(detective))
# print('7.', detective.infoComplete(verbose=True))
# print('\n')
#
# green_snake = Movie(1303394)
# print('1.', green_snake.getid())
# print('5.')
# green_snake.readHTML()
# print('6.', vars(green_snake))
# print('7.', green_snake.infoComplete(verbose=True))
# print('8.', vars(green_snake))
# print('9.', green_snake.getMovieInfo())

# retrieveHistory(userID=63634081)

###############    1. connect to database    #################
db_config = mysqlDouban.parseDBconfig('/home/minzhe/dbincloc/doubanStatistics.db')
print('1.', db_config)
conn = mysqlDouban.connect(host=db_config['host'], user=db_config['username'], passwd=db_config['passwd'], db=db_config['db'])
cur = conn.movieCursor()


##############     2. write movie to mysql      ###############
id_list = mysqlDouban.getPersonlMovie(userID='luorumo')
print('--------------------------------------------------')
print('Prepare to writing {} movies to mysql database.'.format(len(id_list)))
print('--------------------------------------------------')
for movie_id in id_list:
    if cur.ifUpdate(id=movie_id, cleanTemp=True):           # will print check information if this movie should be created
        movie_obj = Movie(id=movie_id)
        movie_obj.readHTML()
        if movie_obj.infoComplete(verbose=True):
            movie_info = movie_obj.getMovieInfo()
            cur.InsertUpdate(movie=movie_info, cleanTemp=True)
        else:
            print('...... Movie {} information not stored!')
            continue
        utility.sleepAfterRequest()

##############     3. close database connection      ###############
cur.close()
conn.close()

