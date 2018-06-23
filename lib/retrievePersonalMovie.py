###################################################
###        retrivePersonalMovieHistory.py       ###
###################################################
# This script is to retrieve personal movie watching history information from movie.douban.com.


from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import time
import csv
import numpy as np
import os
from lib import utility

###################  auxiliary function  ####################
def catUrl(userID, startNum):
    '''
    Concatenate user movie history pages
    :param userID: user id
    :param startNum: history page number
    :return: url
    '''
    url = 'https://movie.douban.com/people/{}/collect?start={}&sort=time&rating=all&filter=all&mode=list'.format(str(userID), str(startNum))
    return url

def getHTML(url):
    '''
    Retrieve html
    :param url: url
    :return: bsObj
    '''
    try:
        request = urlopen(url)
        bsObj = BeautifulSoup(request, 'lxml')
    except HTTPError:
        return None
    return bsObj

def getMovie(html):
    '''
    Extract movie list from watched history.
    :param html: bsObj
    :return: movie id list
    '''
    movieList = []
    urlList = html.find('ul', {'class': 'list-view'}).findAll('a')
    for url in urlList:
        movie_id = url['href'].strip('/').split('/')[-1]
        utility.relexPrint(url.get_text().strip())
        movieList.append(movie_id)
    return movieList


def catHistoryTempFile(userID):
    '''
    Concatename temp file to store personal movie history information
    :param userID: user id
    :return: temp file name
    '''
    tmp_dir = utility.checkTempFolder()
    tmp_filename = 'movie.' + str(userID) + '.viewed.txt'
    tmp_path = os.path.join(tmp_dir, tmp_filename)
    return tmp_path


##################  main function  ######################
def getUserMovieHistory(userID):
    '''
    Get user movie view history
    :param userID: user id
    :return: movie id list
    '''
    startNum = 0
    movieList = []
    pageExists = True

    print('Retrieving {} movie history'.format(userID))
    while pageExists:
        url = catUrl(userID=userID, startNum=startNum)
        bsObj = getHTML(url=url)
        if len(movieList) == 0 or len(newMovieList) == 30:      # first page or the page has 30 movies (next page exist)
            print('\nMovie list from #{} \n-------------'.format(str(startNum + 1)))
            newMovieList = getMovie(html=bsObj)
            movieList = movieList + newMovieList
            startNum = startNum + 30
        else:
            pageExists = False

        utility.sleepAfterRequest()         # randomly sometime before next retrieving

    print(movieList)
    return movieList

def retrieveHistory(userID):
    '''
    Retrieve personal movie history, and write to temp file.
    :param userID: user id
    :return:
    '''
    tmp_path = catHistoryTempFile(userID=userID)
    movieList = getUserMovieHistory(userID=userID)
    with open(tmp_path, 'w') as f:
        for movie in movieList:
            f.write(movie)
            f.write('\n')


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

# userID = 63634081
#
#
# csvPath = 'data/movieHistory.{}.csv'.format(str(userID))
# csvFile = open(csvPath, 'wt')
# writer = csv.writer(csvFile)
# for movie in movieList:
#     writer.writerow(movie)
#
# csvFile.close()