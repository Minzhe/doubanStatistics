from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import time
import csv



'''
This script is to retrieve personal movie watching history information from movie.douban.com.
'''

def concatUrl(userID, startNum):
    url = 'https://movie.douban.com/people/{}/collect?start={}&sort=time&rating=all&filter=all&mode=grid'.format(str(userID), str(startNum))
    return url

def getHTML(url):
    try:
        request = urlopen(url)
        bsObj = BeautifulSoup(request, 'lxml')
    except HTTPError:
        return None
    return bsObj

def getMovie(html):
    movieList = []
    nameList = html.find('div', {'class': 'grid-view'}).findAll('em')
    for name in nameList:
        movie = name.get_text().split('/')[0].strip()
        print(movie)
        time.sleep(0.2)
        movieList.append(movie)
    return movieList


userID = 63634081
startNum = 0
movieList = []
pageExists = True

while pageExists:
    url = concatUrl(userID=userID, startNum=startNum)
    bsObj = getHTML(url=url)
    if bsObj is None:
        pageExists = False
    else:
        print('\nMovie list from #{} to ...\n------------'.format(str(startNum+1)))
        newMovieList = getMovie(html=bsObj)
        movieList.append(newMovieList)
        startNum = startNum + 15

csvPath = 'data/movieHistory.{}.csv'.format(str(userID))
csvFile = open(csvPath, 'wt')
writer = csv.writer(csvFile)
for movie in movieList:
    writer.writerow(movie)

csvFile.close()