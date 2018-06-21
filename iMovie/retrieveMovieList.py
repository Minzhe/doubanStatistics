#####################################################################
###                     retrivelMovieList.py                      ###
#####################################################################

import os
from lib import utility as u

def getRecommandIDs(id):
    '''
    Given a movie id, get the 10 recommanded movie id
    @param id: movie id
    @return: list of ids
    '''
    html_url = u.catHTML('movie', id)
    status = u.downloadHTML(html_url)
    if status:
        temp_dir = u.checkTempFolder()
        temp_path = os.path.join(temp_dir, 'movie.subject.' + str(id) + '.html')
        if os.path.exists(temp_path):


movieIDs = list()