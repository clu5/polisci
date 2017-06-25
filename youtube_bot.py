"""
1. Create bots (different users), that click on the following link 100 times: https://www.youtube.com/watch?v=60Dz35QvxhU

2. Each time the link is clicked by a bot, I would like the following information recorded in a CSV sheet for each bot:
       botid- an id # for the bot, this can be 1,2,3 etc.
       date - the date that the bot clicked on the link.
       time - the time that the bot clicked on the link.
       city - the city of the bot (connected to the IP address)
       state -  the state of the bot (connected to the IP address)
       recid - recommendation id. Values for this will either be "channel", "title", "views" or "url" 
       recommendation (channel, video title, # of views, link) 1-19 - 19 columns containing information about the first visible 19 recommendations in rank order (ie 1 = first visible recommendation on the right hand side bar, 2 = second visible recommendation etc.)  this should be obvious from the html.
"""

import requests
import os
import time
import csv
from bs4 import BeautifulSoup

print('What youtube url to scrape?')
url_to_scrape = input()

if not url_to_scrape:
	url_to_scrape ='https://www.youtube.com/watch?v=60Dz35QvxhU'

base_url = 'https://www.youtube.com'

csv_filename = 'youtube_scraper.csv'
csv_exists = os.path.exists(csv_filename)

if csv_exists:
	with open(csv_filename, 'r') as f:
		botid = int(f.readlines()[-1].split(',')[0]) + 1
else:
	botid = 1
city = '-'
state = '-'
recid = ['channel', 'title', 'views', 'url']

response = requests.get(url_to_scrape)
html = response.text
soup = BeautifulSoup(html, 'lxml')
related_videos = soup.find('ul', {'id': 'watch-related'})

with open(csv_filename, 'a') as f:

	writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)

	if not csv_exists:
		headers = ['botid', 'date', 'time', 'city', 'state', 'recid']
		headers += ['rec' + str(x) for x in range(1,20)]
		writer.writerow(headers)

	video_stats = []
	for i, video in enumerate(related_videos.find_all(attrs={'class':'content-wrapper'})):
		stats = []		
		for span in video.find_all('span'):
			s = span.text
			s = s.lstrip()
			s = s.rstrip()
			stats.append(s)
		stats.append(base_url + video.a.get('href'))
		video_stats.append(stats)

		print('recommended video:', i+1)
		print(stats)

	for rec in recid:
		row = []
		row.append(str(botid))
		row.append(time.strftime('%m%d%y'))
		row.append(time.strftime('%H:%M'))
		row.append(city)
		row.append(state)
		row.append(rec)

		for i, v in enumerate(video_stats):
			if rec == 'title':
				row.append(v[0])
			elif rec == 'channel':
				row.append(v[2])
			elif rec == 'views':
				views = v[4].split(' ')[0]
				views = views.replace(',', '')
				row.append(views)
			elif rec == 'url':
				row.append(v[-1])


		writer.writerow(row)
