from bs4 import BeautifulSoup
import requests
import re
import urllib2
import os
import argparse
import sys
import json
import random
import imghdr

# adapted from http://stackoverflow.com/questions/20716842/python-download-images-from-google-image-search


def delete_files(folder):
  for the_file in os.listdir(folder):
      file_path = os.path.join(folder, the_file)
      try:
          if os.path.isfile(file_path):
              os.unlink(file_path)
          #elif os.path.isdir(file_path): shutil.rmtree(file_path)
      except Exception as e:
          print(e)


def get_soup(url,header):
    return BeautifulSoup(urllib2.urlopen(urllib2.Request(url,headers=header)),'html.parser')

def run(max_images, query):
	whitelist = set('abcdefghijklmnopqrstuvwxy ABCDEFGHIJKLMNOPQRSTUVWXYZ')
	query = ''.join(filter(whitelist.__contains__, query))
	arr = query.split()
	query='+'.join(arr)
	header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
	url="https://www.google.co.in/search?q="+query+"&source=lnms&tbm=isch"
	soup = get_soup(url,header)
	ActualImages=[] # contains the link for Large original images, type of  image
	for a in soup.find_all("div",{"class":"rg_meta"}):
	    link , Type =json.loads(a.text)["ou"]  ,json.loads(a.text)["ity"]
	    ActualImages.append((link,Type))
	random.shuffle(ActualImages)
	
	type = ''

	for (url, type) in ActualImages:
	  print(url, type)
	  if type == 'jpg' or type == 'jpeg':
	    return url



if __name__ == '__main__':
    from sys import argv
    try:
        main(argv)
    except KeyboardInterrupt:
        pass
    sys.exit()
