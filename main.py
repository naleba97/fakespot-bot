import praw
import prawcore
import os
import re
import json
import urllib2
import requests
import time
import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from urllib import urlencode

reddit = None
subreddit = None
posts_replied_to = None
driver = None

def setup():
	global reddit, subreddit, posts_replied_to, driver

	reddit = praw.Reddit('fs_bot')
	subreddit = reddit.subreddit("buildapcsales")

	options = Options()
	options.add_argument("--headless")
	driver = webdriver.Firefox(firefox_options = options)

	if not os.path.isfile("posts_replied_to.txt"):
		posts_replied_to = []
	else:
		with open("posts_replied_to.txt", "r") as f:
			posts_replied_to = f.read()
			posts_replied_to = posts_replied_to.split()



def run():
	global posts_replied_to
	print("Listening for the command !fs_bot...")
	try:
		for comment in subreddit.stream.comments():
			print(datetime.datetime.fromtimestamp(comment.created))
			if comment.submission.id not in posts_replied_to:
				submission = comment.submission
				if re.search("!fs_bot", comment.body, re.IGNORECASE):
					if re.search("amazon.com", submission.url, re.IGNORECASE):
						reply = search(submission.url)
						print("Generating reply... \n" + reply)
						
						comment.reply(reply)

						posts_replied_to.append(submission.id)
						mark_post_as_replied(submission.id)	
	except prawcore.exceptions.RequestException:
		print("Reddit API has a problem. Restarting bot...")
		run()
	except praw.exceptions.APIException as e:
		print(e.message + "\n")
		reg_sec = re.search("second", e.message)
		reg_min = re.search("minute", e.message)
		if reg_min:
			reg = re.search("try again in ([0-9]*)", e.message)
			print("Waiting" + reg.group(1) + " minutes...\n")
			time.sleep(int(reg.group(1))*60 + 60)
		elif reg_sec:
			reg = re.search("try again in ([0-9]*)", e.message)
			print("Waiting" + reg.group(1) + " seconds...\n")
			time.sleep(int(reg.group(1)) + 60)
		else:
			print("Waiting for 10 minutes...\n")
			time.sleep(600)
		print("Restarting bot...")
		run()
			






def search(url):
	"""
	Searches the Fakespot website for the requested Amazon product.
	Returns the correct reply depending on the result. 
	"""
	global driver
	
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
		comment = make_comment(final_html, driver.current_url)
		return comment
	else:
		return "Not enough reviews for analysis"


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


def make_comment(html, url):
	"""
	Creates and concatenate the parts of the reply.
	"""
	header = create_header(html)
	grade = get_grade(html)
	total_reviews = get_total_reviews(html)
	amazon_rating = get_amazon_rating(html)
	company_grade = get_company_grade(html)
	redirect = get_redirect(url)
	footer = create_footer()

	return header+grade+total_reviews+amazon_rating+company_grade+redirect+footer


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
	if reg:
		return "**" + reg.group(1) + "**\n\n"
	else:
		return "Could not create header.\n\n"

def create_footer():
	"""
	Creates the footer of the comment and returns it.
	Includes link to source code and page to report bugs/errors.
	"""
	code_url = "https://github.com/naleba97/fakespot-bot"
	error_url = "https://github.com/naleba97/fakespot-bot/issues"
	return "> [Source Code](" + code_url + ") | " + "[Report Errors](" + error_url + ")\n\n" 


def get_redirect(url):
	"""
	Creates a hyperlink to the original Fakespot review and returns it.
	"""
	return "> [Full Fakespot Review](" + url + " \"" + url + "\")\n\n"

def get_total_reviews(html):
	"""
	Searches and returns the current total amount of reviews.
	"""
	reg = re.search("Total Reviews</div><p>([0-9]*)", html)
	if reg:
		return "Total number of reviews: " + reg.group(1) + "\n\n"
	else:
		return "Could not locate total number of reviews.\n\n"

def get_grade(html):
	"""
	Searches and returns the current Fakespot grade.
	"""
	reg = re.search("Fakespot Grade</div><p>(A|B|C|D|F)",html)
	if reg:
		return "Product Fakespot Grade: " + reg.group(1) + "\n\n"
	else:
		return "Could not locate Product Fakespot Grade.\n\n"

def get_amazon_rating(html):
	"""
	Searches and returns the current Amazon score.
	"""
	reg = re.search("rating=\"([\w.]*)\"", html)
	if reg:
		return "Amazon Product Star Rating: " + reg.group(1) + "\n\n"
	else:
		return "Could not locate Amazon Product Star Rating.\n\n"


def get_company_grade(html):
	"""
	Searches and returns the company name and grade.
	"""
	reg_name = re.search("Sold by[\s&nbsp]*;<[\w\s=\"\-\/]*>([\w\s]*)<", html)
	reg_grade = re.search("font-grade-(\w+)", html)
	if reg_name and reg_grade:
		return "Company Name: " + reg_name.group(1) + "\n\n" + "Company Grade: " + reg_grade.group(1).upper() + "\n\n"
	else:
		return "Could not locate Company Name or Grade.\n\n"


def mark_post_as_replied(submission_id):
	"""
	Adds the original submission's ID to the text file.
	"""
	with open("posts_replied_to.txt", "a+") as f:
		f.write(submission_id + "\n")

if __name__ == '__main__':
	setup()
	run()
	
