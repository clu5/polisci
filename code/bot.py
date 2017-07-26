#!/usr/bin/python

import requests
import os, sys, time, random, csv, functools
import socks
import socket
import getpass
import stem.socket
import stem.connection
from stem import StreamStatus, CircStatus, Signal
from stem.control import EventType, Controller
from bs4 import BeautifulSoup

PORT = 9051
TIME = 30
random.seed(5)

def main():

	# print('What youtube url to scrape?')
	# url_to_scrape = input()
	# if not url_to_scrape:
	# 	url_to_scrape ='https://www.youtube.com/watch?v=60Dz35QvxhU'
	# base_url = 'https://www.youtube.com'

	with Controller.from_port(port = 9051) as controller:
		controller.authenticate()  # provide the password here if set
		controller.set_options({'ExitNodes':'{US}'})
		print(get_ip_address())

		stream_listener = functools.partial(stream_event, controller)
		controller.add_event_listener(stream_listener, EventType.STREAM)

		input()
		# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9050)
		# socket.socket = socks.socksocket

def stream_event(controller, event):
	if event.status == StreamStatus.SUCCEEDED and event.circ_id:
		circ = controller.get_circuit(event.circ_id)
		exit_fingerprint = circ.path[-1][0]
		exit_relay = controller.get_network_status(exit_fingerprint)
		print('Exit relay for  connection to %s' % event.target)
		print(' address: %s    %i' % (exit_relay.address, exit_relay.or_port))
		print(' fingerprint: %s' % exit_relay.fingerprint)
		print(' nickname: %s' % exit_relay.nickname)
		print(' locale: %s' % controller.get_info('ip-to-country/%s' % 
										exit_relay.address, 'unknown'))

def get_html(url):
	response = requests.get(url)
	return response

def parse_html(html):
	vid_stat = []
	soup = BeautifulSoup(html,'lxml')		
	rec = soup.find('ul', {'id':'watch-related'})
	for i,v in enumerate(rec.find_all(attrs={'class':'content-wrapper'})):
		stat = []
		for span in v.find_all('span'):
			s = span.text
			s = s.lstrip().rstrip()
			stat.append(s)
		stat.append(base_url+v.a.get('href'))
		vid_stat.append(stat)
	return vid_stat

def get_ip_address():
	return requests.get('http://ipv4.icanhazip.com/').text

def get_new_address(controller):
	controller.signal(Signal.NEWNYM)
	time.sleep(controller.get_newnym_wait())

def choose_random_rec(vids):
	url = vids[random.randint(1,19)]
	return url

def csv_writer(filename,first=True):
	if os.path.exists(filename):
		with open(filename, 'r') as f:
			botid = int(f.readlines()[-1].split(',')[0])+1
	else:
		botid = 1
	with open(csv_filename, 'a') as f:
		writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
		if not csv_exists:
			headers = ['botid', 'date', 'time', 
					   'step', 'ipaddress', 'recid']
			headers += ['rec' + str(x) for x in range(1,20)]
			writer.writerow(headers)
	recid = ['channel', 'title', 'views', 'url']

	video_stats = parse_html(get_html(choose_random_rec(vids)))
	for rec in recid:
		row = []
		row.append(str(botid))
		row.append(time.strftime('%m%d%y'))
		row.append(time.strftime('%H:%M'))
		row.append(step)
		row.append(ipaddr)
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

if __name__ == '__main__':
	main()

#	 for circ in sorted(controller.get_circuits()):
# 		if circ.status != CircStatus.BUILT:
# 			continue # skip circuits that aren't yet usable
# 		for i, entry in enumerate(circ.path):
# 			div = '+' if(i == len(circ.path)-1) else '|'
# 			fingerprint, nickname = entry
# 			entry_descriptor = controller.get_network_status(fingerprint, None)
# 			if entry_descriptor:
# 				print("Circuit %s (%s) starts with %s" % (circ.id, 
# 														  circ.purpose,
#														  entry_descriptor.address))
# 			else:
# 				print("Unable to determine the address belonging to circuit %s" % circ.id)
# 
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
