import praw
import prawcore
import os
import re
import json
import urllib2
import requests
from urllib import urlencode

reddit = None
subreddit = None
posts_replied_to = None

def setup():
	global reddit, subreddit, posts_replied_to

	reddit = praw.Reddit('fs_bot');
	subreddit = reddit.subreddit("testingground4bots");



def search():
	global posts_replied_to
	'''
	print("Listening for posts from amazon.com")
	try:
		for post in subreddit.stream.submissions():
			if submission.id not in posts_replied_to:
				if re.search("amazon.com", submission.url, re.IGNORECASE):

					url = "https://www.amazon.com/Asmodee-60522QNG-Chicago-Express/dp/B001LPGS1S?SubscriptionId=AKIAJ7T5BOVUVRD2EFYQ&tag=camelproducts-20&linkCode=xm2&camp=2025&creative=165953&creativeASIN=B001LPGS1S"

					fakespot_url = "https://www.fakespot.com/analyze/?"

					params = {'url' : url}

					req = requests.get(fakespot_url + urlencode(params)) 
					print(req.status_code)
					try:
						page = urllib2.urlopen(req.url)
						raw_html = page.read()
						print(raw_html)
					except urllib2.URLError:
						print("error")
	except prawcore.exceptions.RequestException:
		print("Reddit API has a problem. Restart the bot.")
		search()
	'''

	#Test code
	url="https://www.amazon.com/Creativity-Kids-Grow-Glow-Terrarium/dp/B00I9KDFK0/ref=pd_bxgy_21_img_3?_encoding=UTF8&pd_rd_i=B00I9KDFK0&pd_rd_r=ZHGGDTNC69H473QA2HX3&pd_rd_w=byV4x&pd_rd_wg=af1pw&psc=1&refRID=ZHGGDTNC69H473QA2HX3"

	fakespot_url = "https://www.fakespot.com/analyze/?"

	params = {'url' : url}

	req = requests.get(fakespot_url + urlencode(params)) 

	try:
		page = urllib2.urlopen(req.url)
		
		html = page.read()

		if check_reanalyze(page, html):
			html = page.read()

		grade = get_grade(html)

		total_reviews = get_total_reviews(html)

		print(total_reviews)
		print(grade)
		
		

	except urllib2.URLError:
		print("error")

'''
Checks whether the currently displayed analysis is old. If so, make a GET request to reanalyze the site.
'''
def check_reanalyze(page, html):
	fakespot_url = "https://www.fakespot.com/reanalyze/"
	if re.search("This analysis is quite old", html):
		reg = re.search("/reanalyze/([0-9A-Za-z]*)\"", html)
		fakespot_url = fakespot_url + reg.group(1)
		req = requests.get(fakespot_url)
		while re.search("reanalyze",page.read()):
			pass
		return True
	else:
		return False

def get_total_reviews(html):
	reg = re.search("Total Reviews</div><p>([0-9]*)", html)
	return reg.group(1)

def get_grade(html):
	reg = re.search("Fakespot Grade</div><p>(A|B|C|D|F)",html)
	return reg.group(1)

def comment_grade(grade):
	return "Fakespot Grade: " + grade + "\n"


def print_grade():	
	print()

if __name__ == '__main__':
	search()
