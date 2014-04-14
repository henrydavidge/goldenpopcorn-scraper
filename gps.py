import cookielib as cl
import urllib2 as ul
from bs4 import BeautifulSoup
from selenium import webdriver
import yaml
import re
import time
import datetime
import calendar
import os

# Some constants
gp_url = 'http://passthepopcorn.me/torrents.php?\
		action=advanced&grouping=0&scene=2&order_by=gptime'

bytes_per_gb = 1024*1024*1024

# Load configuration
cfg = yaml.load(open('config.yaml'))
ck = cl.Cookie(version=0, 
		name='session', 
		value=cfg['cookie'], 
		port=None, 
		port_specified=False,
		domain='passthepopcorn.me', 
		domain_specified=True,
		domain_initial_dot=False, 
		path='/', 
		path_specified=True,
		secure=False, 
		expires=None, 
		discard=True, 
		comment=None,
		comment_url=None, 
		rest={'HttpOnly': None}, 
		rfc2109=False)
cj = cl.LWPCookieJar()
cj.set_cookie(ck)
opener = ul.build_opener(ul.HTTPCookieProcessor(cj))

br = webdriver.Firefox()
br.get(gp_url)
br.add_cookie({
	'name': 'session',
	'value': cfg['cookie'],
	'path': '/',
	'domain': 'passthepopcorn.me'
	})

# h/t http://stackoverflow.com/a/1392549/3447412
def getSize(start_path = '.'):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(start_path):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			try:
				total_size += os.path.getsize(fp)
			except: pass
	return total_size

def downloadGPs(size):
	print size
	br.get(gp_url)
	soup = BeautifulSoup(br.page_source)
	movies = soup.find_all('tr', class_='group_torrent')
	for m in movies: 
		t = m.find('span', class_='time').get('title')
		created = time.strptime(t, '%b %d %Y, %H:%M')

		if size > cfg['max_size']:
			print 'Not enough space on disk!'
			print size
			return
		elif (time.time() - calendar.timegm(created)) / 60 < cfg['interval']:
			# No new GP
			return
		else:
			title = m.find_previous(class_='basic-movie-list__movie__title').get_text().replace(' ', '-')
			year = m.find_previous(class_='basic-movie-list__movie__year').get_text()
			torrent_size = m.find_all(class_='nobr')[1].get_text() # Ugly, but this is where to find the size
			print torrent_size
			if 'GiB' in torrent_size:
				size += float(torrent_size.split()[0])
			else: # It's in megabytes
				size += float(torrent_size.split()[0]) / 1024 
			target = m.find('a', title='Download').get('href')
			f = opener.open('http://passthepopcorn.me/' + target)
			try:
				print 'Downloading {}'.format(title.replace('-', ' ') + ' ' + year)
			except:
				print 'Downloading something with unicode in the title'
			with open(os.path.join(cfg['watch_folder'], title + '-' + year + '.torrent'), 'wb+') as local:
				local.write(f.read())

downloadGPs(getSize(start_path=cfg['storage_root']) / bytes_per_gb)
br.quit()
