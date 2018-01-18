import praw
import prawcore
import os
import re
import json
import urllib2
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from urllib import urlencode

reddit = None
subreddit = None
posts_replied_to = None
driver = None

def setup():
	global reddit, subreddit, posts_replied_to, driver

	reddit = praw.Reddit('fs_bot')
	subreddit = reddit.subreddit("testingground4bots")
	driver = webdriver.Firefox()



def run():
	global posts_replied_to, driver
	driver = webdriver.Firefox()
	print("Listening for posts from amazon.com")
	try:
		for post in subreddit.stream.submissions():
			if submission.id not in posts_replied_to:
				if re.search("amazon.com", submission.url, re.IGNORECASE):
					search(submission.url)
					
	except prawcore.exceptions.RequestException:
		print("Reddit API has a problem. Restart the bot.")
		run()



def search(url):
	print("Searching for reviews for " + url)		
	
	fakespot_url = "https://www.fakespot.com/analyze/?"

	params = {'url' : url}

	full_url = fakespot_url + urlencode(params)

	driver.get(full_url)

	wait_rendering("loading-text")
	wait_rendering("analysis-status")

	final_html = driver.page_source

	if not check_class_name("alert-danger"):
		result = check_reanalyze(driver.page_source, driver.current_url, driver)

		if result:
			wait_rendering("analysis-status")

			final_html = driver.page_source

		else:
			pass 
		comment = make_comment(final_html)
		print(comment)
	else:
		print("Not enough reviews for analysis")

	driver.close()

def check_class_name(class_name):
	"""
	Checks whether an element with the class name exists in the DOM.
	"""
	global driver
	try:
		if driver.find_element_by_class_name(class_name):
			return True
	except NoSuchElementException:
		return False
	return False

def wait_rendering(class_name):
	"""
	Waits for a page to finish rendering by checking whether an element
	with the class name still exists.
	"""
	global driver
	try:
		while driver.find_element_by_class_name(class_name):
			time.sleep(5)
			pass
	except NoSuchElementException:
		pass


def make_comment(html):
	header = create_header(html)
	grade = get_grade(html)
	total_reviews = get_total_reviews(html)

	return header+grade+total_reviews


def check_reanalyze(html, url, driver):
	"""
	Checks whether the currently displayed analysis is old. 
	If so, make a GET request to reanalyze the site and return True.
	"""

	if re.search("This analysis is quite old", html):
		fakespot_url = "https://www.fakespot.com/reanalyze/"
		reg = re.search("/reanalyze/(\w*)\"", html)
		fakespot_url = fakespot_url + reg.group(1)
		req = requests.get(fakespot_url)
		driver.get(url)
		time.sleep(5)
		return True
	else:
		return False

def create_header(html):
	"""
	Creates the header of the comment and returns it.
	"""

	reg = re.search("<title>([\w\s|]*)", html)
	return "**" + reg.group(1) + "**\n"

def get_total_reviews(html):
	"""
	Searches and returns the current total amount of reviews.
	"""

	reg = re.search("Total Reviews</div><p>([0-9]*)", html)
	return "Total number of reviews: " + reg.group(1) + "\n"

def get_grade(html):
	"""
	Searches and returns the current Fakespot grade.
	"""
	reg = re.search("Fakespot Grade</div><p>(A|B|C|D|F)",html)
	return "Fakespot Grade: " + reg.group(1) + "\n"


def print_grade():	
	print()

if __name__ == '__main__':
	#setup()
	search()
