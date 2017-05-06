###################################################
###        retrivePersonalMovieHistory.py       ###
###################################################
# This python script is to retrieve movie information.

import sys
from os.path import join, dirname, abspath
sys.path.append(join(dirname(abspath(__file__)), '..'))
from lib.retrieveMovieInfo import Movie

robots_9 = Movie(1764796)
print('1.', robots_9.getid())
print('2.', robots_9.infoComplete(verbose=True))
print('3.', robots_9.__getattribute__('_Movie__year'))
print('4.', robots_9.__dict__)
print('5.')
robots_9.readHTML()
print('6.', vars(robots_9))
print('7.', robots_9.infoComplete(verbose=True))
print('\n')

detective = Movie(10748120)
print('1.', detective.getid())
print('5.')
detective.readHTML()
print('6.', vars(detective))
print('7.', detective.infoComplete(verbose=True))
print('\n')

green_snake = Movie(1303394)
print('1.', green_snake.getid())
print('5.')
green_snake.readHTML()
print('6.', vars(green_snake))
print('7.', green_snake.infoComplete(verbose=True))
green_snake.prepareDataForDB()
print('8.', vars(green_snake))