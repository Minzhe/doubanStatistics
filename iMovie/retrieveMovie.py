#################################################################
###                     retrivelMovie.py                      ###
#################################################################
# This python script is to retrieve movie information.

'''
Function structure:
---------------------------------------------------
├── new_movie = Movie(id=)                      | initiate movie entry
├── new_movie.readHTML()                        | get movie info from html
│   ├── catHTML()                               |
│   ├── downloadHTML()                          |
│   │   └── catHTMLtempfile()                   |
│   ├── parseHTML()                             |
├── new_movie.infoComplete(verbose=True)        | check if the class attributes is complete
└── info_dict = new_movie.getMovieInfo()        | store the movie information to a dictionary
'''

import sys
from os.path import join, dirname, abspath
sys.path.append(join(dirname(abspath(__file__)), '..'))
from urllib.request import URLError
from lib.retrieveMovieInfo import Movie
from lib.retrievePersonalMovie import retrieveHistory
from lib import doubanSQL
from lib import utility as u


###############    1. connect to database    #################
db_config = doubanSQL.parseDBconfig('/home/minzhe/dbincloc/doubanStatistics.ini')
conn = doubanSQL.connect(host=db_config['host'], user=db_config['username'], passwd=db_config['passwd'], db=db_config['db'])
cur = conn.doubanCursor()


##############     2. write movie to mysql      ###############
# all movie ids
id_list = u.getIdList('../data/movie_ids.txt')
id_exists = cur.getIdList(subject='movie')
id_invalid = u.getIdList('../data/movie_ids_invalid.txt')
id_list = [id_ for id_ in id_list if id_ not in id_exists and id_ not in id_invalid]
print('--------------------------------------------------')
print('Prepare to writing {} movies to mysql database.'.format(len(id_list)))
print('--------------------------------------------------')
for movie_id in id_list:
    if cur.ifUpdate(id=movie_id, cleanTemp=True):           # will print check information if this movie should be created
        movie_obj = Movie(id=movie_id)
        try:
            movie_obj.readHTML()
        except:
            pass
        if movie_obj.infoComplete(verbose=True):
            movie_info = movie_obj.getMovieInfo()
            cur.InsertUpdateMovie(movie=movie_info, cleanTemp=True)
        else:
            print('...... Movie {} information not stored!'.format(movie_id))
            id_invalid.append(movie_id)
            u.outputIdList(id_invalid, '../data/movie_ids_invalid.txt')
            continue
        u.sleepAfterRequest()

##############     3. close database connection      ###############
cur.close()
conn.close()

