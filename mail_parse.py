#!/usr/bin/env python

import imaplib
import email
import re
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import MySQLdb

# Connect to news database
conn = MySQLdb.connect(host= "localhost", user="root", passwd="password", db="databasename")
x = conn.cursor()                   

# Connect to mailbox containing Google News emails
mail = imaplib.IMAP4_SSL('server')
mail.login('emailaddress', 'password')

# Connect to inbox
mail.select("inbox") 

# Search and return mail uids
result, data = mail.uid('search', None, "UNSEEN") 

urls = []
summarys = []
headlines = []
fromLocs = []

for latest_email_uid in data[0].split():
  # Get most recent email
  result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')

  # Remove all '=\r\n' from email text
  raw_email = data[0][1].replace("=\r\n", "")

  # Get all HTML tags from email, this removes the extra email only text (ie. header, sender addresses, etc)
  only_html_tags = SoupStrainer("html")
  html = BeautifulSoup(raw_email, "html.parser", parse_only=only_html_tags)

  # Extract each summary
  for summary in html.find_all('div', attrs={'style':'3D"color:#222"'}):
    summarys.append(summary.text)

  # Extract each headline text and article URL
  for headline in html.find_all('a', attrs={'style':'3D"color:#1111CC;display:inline;font:normal'}):
    headlines.append(headline.text)
    url = headline['href']
    url = url.replace('3D"https://www.google.com/url?q=3D', '')
    url = re.sub(r'&[\w\-=_"]*', '', str(url))
    urls.append(url)

  # Extract the article source (ie. Newsweek, WSJ, etc)
  for fromLoc in html.find_all('span', attrs={'style':'3D"text-decoration:none;color:#777777"'}):
    fromLocs.append(fromLoc.text)

for cnt in xrange(len(urls)):
  # Print article information
  print "***"
  print headlines[cnt]
  print fromLocs[cnt]
  print urls[cnt]
  print summarys[cnt]
  print "***"
  
  # Insert article information into news database
  try:
     x.execute("""INSERT INTO articles (title, author, link, description) VALUES (%s,%s,%s,%s)""",(headlines[cnt],fromLocs[cnt],urls[cnt],summarys[cnt]))
     conn.commit()
  except:
     conn.rollback()

conn.close()
       
