# Fakespot Bot
Fakespot Bot is a Reddit bot ([/u/fakespot_bot](https://www.reddit.com/user/fakespot_bot/)) that posts information about the authenticity of an Amazon product's reviews directly from [Fakespot](https://fakespot.com) on request. This bot is currently inactive. If you wish, you may run this bot on a private subreddit for testing purposes. 	
### How to Request on Reddit
On a subreddit that is being listened to by Fakespot Bot, if a user wishes to view a brief Fakespot overview of a submission that links to an Amazon product, comment with  `!fs_bot`, and the bot will reply with the product's information.
**Note**: Once Fakespot Bot has replied to a comment for a submission, it will not respond to further calls to `!fs_bot` on that particular submission. 
###  Technical Information
The bot is coded for Python 3 and uses PRAW, a Python wrapper for the Reddit API, to listen indefinitely to a stream of comments of subreddit(s) for any call to `!fs_bot`. It uses Selenium's Firefox webdriver and regex to extract information from Fakespot's webpages.
### Setup and Configuration
Running bot requires a Python installation (either Python 2.7 or Python 3 is fine) and Selenium's Firefox webdriver. The bot requires several packages, including PRAW and Selenium. These packages are outlined at the top of the `main.py` file. `pip` is ideal for installing the necessary packages. The `praw.ini` file with proper credentials is necessary to access the Reddit API.  
