#!/usr/bin/python

import os, sys, time, random, csv, functools
import requests
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
STEP = 0
REC_VIDS = []
random.seed(5)
YOUTUBE = 'https://www.youtube.com'
CUR_PATH = os.path.dirname(os.path.realpath(__file__))
OUTPUT_PATH = os.path.abspath(os.path.join(CUR_PATH, os.pardir))+'/data/'
FILE = OUTPUT_PATH+'output.csv'

##########################################################################

def main():

	if len(sys.argv) == 2:
		url_to_scrape = sys.argv[1]
	else:
		url_to_scrape ='https://www.youtube.com/watch?v=60Dz35QvxhU'

	with Controller.from_port(port = 9051) as controller:

		# provide the password here if set
		controller.authenticate()  
		controller.set_options({'ExitNodes':'{US}'})
		print('IPv4:', get_ip_address())

		# stream_listener = functools.partial(stream_event, controller)
		# controller.add_event_listener(stream_listener, EventType.STREAM)

		csv_writer(FILE,parse_html(get_html(url_to_scrape)))

		for i in range(100):
			
			if STEP == 0:
				REC_VIDS = parse_html(get_html(url_to_scrape))
				STEP = 1

			if get_step() == 1:
				REC_VIDS = parse_html(get_html(choose_random_rec()))
				STEP = 2
			elif get_step() == 2:
				get_new_address(controller)
				print(i, get_ip_address())
				_ = parse_html(get_html(choose_random_rec(REC_VIDS)))
				csv_writer(FILE, _)
				STEP = 1

###########################################################################

def stream_event(controller, event):
	if event.status == StreamStatus.SUCCEEDED and event.circ_id:
		circ = controller.get_circuit(event.circ_id)
		exit_fingerprint = circ.path[-1][0]
		exit_relay = controller.get_network_status(exit_fingerprint)
		print('Exit relay for  connection to %s' % event.target)
		print(' address: %s (%i)' % (exit_relay.address,exit_relay.or_port))
		print(' fingerprint: %s' % exit_relay.fingerprint)
		print(' nickname: %s' % exit_relay.nickname)
		print(' locale: %s' % controller.get_info('ip-to-country/%s' % 
										exit_relay.address, 'unknown'))

def get_html(url):
	response = requests.get(url).text
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
		stat.append(YOUTUBE+v.a.get('href'))
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

def get_step(prev_step):
	return STEP

def csv_writer(file,video_stats,first=True):
	file_exists = os.path.exists(file)
	if file_exists:
		with open(file, 'r') as f:
			botid = int(f.readlines()[-1].split(',')[0])+1
	else:
		botid = 1
	with open(file, 'a') as f:
		writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
		if not file_exists:
			headers = ['botid', 'date', 'time', 
					   'step', 'ipaddress', 'recid']
			headers += ['rec' + str(x) for x in range(1,20)]
			writer.writerow(headers)
	recid = ['channel', 'title', 'views', 'url']

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
