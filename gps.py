import cookielib as cl
import urllib2 as ul
from bs4 import BeautifulSoup
from selenium import webdriver
import yaml
import re
import time
import datetime
import calendar

# Some constants
gp_url = 'http://passthepopcorn.me/torrents.php?\
		action=advanced&grouping=0&scene=2&order_by=gptime'

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

def downloadGPs():
	br.get(gp_url)
	soup = BeautifulSoup(br.page_source)
	movies = soup.find_all('tr', class_='group_torrent')
	for m in movies: 
		t = m.find('span', class_='time').get('title')
		created = time.strptime(t, '%b %d %Y, %H:%M')
		if (time.time() - calendar.timegm(created)) / 60 < cfg['interval']:
			title = m.find_previous(class_='basic-movie-list__movie__title').get_text().replace(' ', '-')
			year = m.find_previous(class_='basic-movie-list__movie__year').get_text()
			target = m.find('a', title='Download').get('href')
			f = opener.open('http://passthepopcorn.me/' + target)
			with open(title + '-' + year + '.torrent', 'wb') as local:
				local.write(f.read())
		else: 
			break

downloadGPs()
