import json
from urllib.request import urlopen
import pprint

url = 'https://api.douban.com/v2/movie/subject/1764796'
response = urlopen(url=url).read().decode('utf-8')
responseJson = json.loads(response)
pprint.pprint(responseJson)