#!/usr/bin/python3
import os, sys, time, random, datetime
import re
import json
import functools
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

random.seed(0) 
WEBSITE  = 'http://www.presidency.ucsb.edu/'
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
# OUTPUT_PATH = os.path.abspath(os.path.join(CURRENT_PATH, os.pardir)) 
FILE = CURRENT_PATH + '/' + 'election_speeches_data.json'
# print(OUTPUT_PATH)

def get_html(url):
    response = requests.get(url)
    if not response.status_code == 200: 
        print(response.status_code)
    return response.text


def get_election_page_links(url):
	soup = BeautifulSoup(get_html(url), 'lxml')
	table_urls = [td.a.get('href') 
				  for td in soup.find_all(attrs={'class':'tah11'}) 
				  if td.a != None]
	regex = re.compile('\D\D\D\D')
	date_urls = list(filter(regex.search, table_urls))
	return sorted([link for link in date_urls if '_election.php' in link])


def make_soup(url):
	return BeautifulSoup(get_html(url), 'lxml')

def split_date(string_m_d_y, strip_comma=True):
	if strip_comma:
		string_m_d_y = string_m_d_y.replace(',', '')
	return datetime.datetime.strptime(string_m_d_y, '%B %d %Y')

def write_to_json(outfile, all_speeches_data): 
	"""
	`all_speeches_data` should be list of lists of speechs in this format:
	['Name', 'Party', 'Title', 'Year', 'Month', 'Day', 'Text']
	 """
	data = {}
	data['speech'] = []
	for speech in all_speeches_data:
		data['speech'].append({
								'Name':speech[0],
								# 'Party':speech[1],
								'Title':speech[1],
								'Year':speech[2],
								'Month':speech[3],
								'Day':speech[4],
								'Text':speech[5]
								})

	with open(outfile, 'a+') as f:
		json.dump(data, f)

		
def main():
	election_links = get_election_page_links(WEBSITE + 'data.php')
	print(election_links) # 1960, 1968, 1996, etc

	for year, election in enumerate(election_links[:2]):
		year *= 4; year += 1960
		print('############################################################\n')
		print(year, 'election')
		soup1 = make_soup(election)

		# main table with candidates
		table1 = soup1.find('table', attrs={'width':'680', 'bgcolor':'#FFFFFF'})
		
		# get links to campaign speechs
		# usually first link but 2012 Obama is second link for some reason
		candidate_links = [a.get('href') for a in table1.find_all('a')] 

		for candidate in candidate_links:

			# page of speeches
			soup2 = make_soup(WEBSITE + candidate)

			# table of candidate, date, and links to speeches 
			table2 = soup2.find('table', attrs={'width':'700', 
											    'border':'0', 
											    'align':'center'})

		

			# List of Lists of speeches
			# First list is empty for some reason
			candidate_speeches = [tr.find_all('td', attrs={'class':'listdate'}) 
								  for tr in table2.find_all('tr')]
	

			for i, speech in enumerate(candidate_speeches[1:]):
				i += 1 # because the first list is empty for some reason
				# ['Barack Obama', 'July 27, 2004, 'Keynote at...]
				current_speech = [td.text for td in speech] 

				speech_date = split_date(current_speech[1])

				# link to speech is the third/last one in list
				speech_relative_path = [a.get('href') 
										for a in candidate_speeches[i][-1]]

				# remove '../' part i.e. first three chars of relative path
				link_to_speech = urljoin(WEBSITE, speech_relative_path[0][2:]) 
				soup3 = make_soup(link_to_speech)
				speech_text = soup3.find('span', attrs={'class':'displaytext'}).text

				speech_info = []
				speech_info.append(current_speech[0])
				speech_info.append(current_speech[2])
				speech_info.append(speech_date.year)
				speech_info.append(speech_date.month)
				speech_info.append(speech_date.day)
				speech_info.append(speech_text)
				
				all_speeches_info = []
				all_speeches_info.append(speech_info)
				# print(all_speeches_info)
				# print(candidate_speech_info)

				write_to_json(FILE, all_speeches_info)

				if i == 1: 
					print(len(candidate_speeches),'speeches for',current_speech[0])

				print(i, current_speech[2])
			

if __name__ == '__main__':
    main()

