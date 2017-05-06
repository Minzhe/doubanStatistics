import json
from urllib.request import urlopen
import pprint

# url = 'https://api.douban.com/v2/movie/subject/1764796'
# response = urlopen(url=url).read().decode('utf-8')
# responseJson = json.loads(response)
# pprint.pprint(responseJson)

file = '/home/minzhe/Project/doubanStatistics/temp/api.movie.subject.1764796.json'
with open(file, encoding='utf-8') as json_file:
    data = json.load(json_file)

print(data)