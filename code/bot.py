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

random.seed(5)
YOUTUBE = 'https://www.youtube.com'
CUR_PATH = os.path.dirname(os.path.realpath(__file__))
OUTPUT_PATH = os.path.abspath(os.path.join(CUR_PATH, os.pardir))+'/data/'
FILE = OUTPUT_PATH+'output.csv'
STEP = 0

################################################################################
def main():
	global STEP

	if len(sys.argv) == 2:
		url_to_scrape = sys.argv[1]
	else:
		url_to_scrape ='https://www.youtube.com/watch?v=60Dz35QvxhU'

	with Controller.from_port(port = 9051) as controller:
		controller.authenticate() # password here if set
		controller.set_options({'ExitNodes':'{US}'})
		socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9050)
		socket.socket = socks.socksocket	
		for i in range(100):
			print('\n###############\tIteration:',
				   i+1,'\taddress:', get_ip_address(controller),
				   '\t###############')
			recs_before = parse_html(get_html(url_to_scrape))
			STEP = 0
			csv_writer(FILE, recs_before, controller)
			get_html(choose_random_rec(recs_before)) #throwaway
			recs_after = parse_html(get_html(url_to_scrape))
			STEP = 1
			csv_writer(FILE, recs_after, controller)
			controller.signal(Signal.NEWNYM) # new ip address
			time.sleep(10)
################################################################################

def get_html(url):
	response = requests.get(url)
	if not response.status_code == 200: 
		print(response.status_code)
	return response.text

def parse_html(html):
	vid_stat = []
	soup = BeautifulSoup(html,'lxml')		
	try:
		rec = soup.find('ul', {'id':'watch-related'})
		for i, v in enumerate(rec.find_all(attrs={'class':'content-wrapper'})):
			stat = []
			for span in v.find_all('span'):
				s = span.text
				s = s.lstrip().rstrip()
				stat.append(s)
			stat.append(YOUTUBE+v.a.get('href'))
			vid_stat.append(stat)
	except:
		print(soup.prettify())
	return vid_stat

def get_bot_id(file, exists=True):
	if exists:
		with open(file, 'r') as f:
			last_line = f.readlines()[-1].split(',')
			if int(last_line[3]) == 1:
				bid = int(last_line[0])+1
			elif int(last_line[3]) == 0:
				bid = int(last_line[0])
	else:
		bid = 1
	return bid

def get_ip_address(controller):
	for circuit in controller.get_circuits():
		if circuit.status != CircStatus.BUILT: continue
		exit, name = circuit.path[-1]
		exit_desc = controller.get_network_status(exit, None)
		address = exit_desc.address if exit_desc else 'Unknown'
		# print(exit, name, address)
	return address

def choose_random_rec(vids):
	# print('\n', len(vids), '\n', vids, '\n')
	url = vids[random.randint(0,19-1)][-1]
	print('\tRandomly chose', url, '\n')
	return url

def csv_writer(file, video_stats, controller):
	file_exists = os.path.exists(file)
	bid = get_bot_id(file, file_exists)
	recid = ['channel','title','views','url']
	headers = ['botid','date','time','step','ipaddress','recid']
	headers += ['rec' + str(x) for x in range(1,20)]
	with open(file, 'a') as f:
		writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
		if not file_exists:
			writer.writerow(headers)
		for x in recid:
			row = []
			row.append(bid)
			row.append(time.strftime('%m%d%y'))
			row.append(time.strftime('%H:%M'))
			row.append(STEP)
			row.append(str(get_ip_address(controller)))
			row.append(x)
			for i, v in enumerate(video_stats):
				if x == 'title':
					row.append(v[0])
				elif x == 'channel':
					row.append(v[2])
				elif x == 'views':
					views = v[4].split(' ')[0]
					views = views.replace(',', '')
					row.append(views)
				elif x == 'url':
					row.append(v[-1])
			writer.writerow(row)

if __name__ == '__main__':
	main()
