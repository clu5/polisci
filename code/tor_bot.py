#!/usr/bin/python

import requests
import os, sys, time, csv
import socks
import socket
import getpass
import stem.socket
import stem.connection
from stem import CircStatus
from stem.control import Controller
from stem import Signal
from bs4 import BeautifulSoup

if __name__ == '__main__':

	url_to_scrape ='https://www.youtube.com/watch?v=60Dz35QvxhU'
	base_url = 'https://www.youtube.com'

	with Controller.from_port(port = 9051) as controller:
		controller.authenticate()  # provide the password here if set
		controller.set_options({'ExitNodes':'{US}'})
		socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1",9050)
		socket.socket = socks.socksocket

		# for i in range(10):
		response = requests.get(url_to_scrape)
		html = response.text
		soup = BeautifulSoup(html,'lxml')
		related_videos = soup.find('ul', {'id': 'watch-related'})
		# print(related_videos)
		controller.signal(Signal.NEWNYM)
		time.sleep(controller.get_newnym_wait())

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
	
	# 	for circ in controller.get_circuits():
	# 		if circ.status != CircStatus.BUILT:
	# 			continue # skip circuits that aren't yet usable
	# 		entry_fingerprint = circ.path[0][0]
	# 		entry_descriptor = controller.get_network_status(entry_fingerprint, None)
	# 		if entry_descriptor:
	# 			print("Circuit %s starts with %s" % (circ.id, entry_descriptor.address))
	# 		else:
	# 			print("Unable to determine the address belonging to circuit %s" % circ.id)

	# 	controller.signal(Signal.NEWNYM)


	# r = requests.get(url_to_scrape,
	# 			 proxies={'http', 'socks5://127.0.0.1:9050',
	# 			 		  'https':'socks5://127.0.0.1:9050'})


# print('What youtube url to scrape?')
# url_to_scrape = input()

# if not url_to_scrape:
# 	url_to_scrape ='https://www.youtube.com/watch?v=60Dz35QvxhU'

# base_url = 'https://www.youtube.com'

# csv_filename = 'output.csv'
# csv_exists = os.path.exists(csv_filename)

# if csv_exists:
# 	with open(csv_filename, 'r') as f:
# 		botid = int(f.readlines()[-1].split(',')[0]) + 1
# else:
# 	botid = 1

# city = '-'
# state = '-'
# recid = ['channel', 'title', 'views', 'url']

# response = requests.get(url_to_scrape)
# html = response.text
# soup = BeautifulSoup(html, 'lxml')
# related_videos = soup.find('ul', {'id': 'watch-related'})

# with open(csv_filename, 'a') as f:

# 	writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)

# 	if not csv_exists:
# 		headers = ['botid', 'date', 'time', 'city', 'state', 'recid']
# 		headers += ['rec' + str(x) for x in range(1,20)]
# 		writer.writerow(headers)

# 	video_stats = []
# 	for i, video in enumerate(related_videos.find_all(attrs={'class':'content-wrapper'})):
# 		stats = []		
# 		for span in video.find_all('span'):
# 			s = span.text
# 			s = s.lstrip()
# 			s = s.rstrip()
# 			stats.append(s)
# 		stats.append(base_url + video.a.get('href'))
# 		video_stats.append(stats)

# 		print('recommended video:', i+1)
# 		# print(stats)

# 	for rec in recid:
# 		row = []
# 		row.append(str(botid))
# 		row.append(time.strftime('%m%d%y'))
# 		row.append(time.strftime('%H:%M'))
# 		row.append(city)
# 		row.append(state)
# 		row.append(rec)

# 		for i, v in enumerate(video_stats):
# 			if rec == 'title':
# 				row.append(v[0])
# 			elif rec == 'channel':
# 				row.append(v[2])
# 			elif rec == 'views':
# 				views = v[4].split(' ')[0]
# 				views = views.replace(',', '')
# 				row.append(views)
# 			elif rec == 'url':
# 				row.append(v[-1])


# 		writer.writerow(row)
