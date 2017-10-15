# -*- coding: utf-8 -*-
import time
import datetime
import shutil
import praw
import os
import traceback
import requests
b = "timestamp:"
d = ".."

#Config Details-
r = praw.Reddit(client_id='azpMBTKkazvXoA',
                     client_secret='zhIE_X0GtoFqWylpN-Ls8JFpMug',
                     user_agent='python:plutoboards:1.0.0 (by /u/sam_hains)')

def resume():
        if os.path.exists('config.txt'):
                line = file('config.txt').read()
                startStamp,endStamp,step,subName=line.split(',')
                startStamp,endStamp,step=int(startStamp),int(endStamp),int(step)
                return startStamp,endStamp,step,subName
        else:
                return 0

# sdate=datetime.datetime.fromtimestamp(int(startStamp)).strftime('%d-%m-%Y')
# edate=datetime.datetime.fromtimestamp(int(endStamp)).strftime('%d-%m-%Y')
# folderName=str(subName+' '+str(sdate)+' '+str(edate))

    
def scrape(hours,step,folderName,subName):
    time_now = datetime.datetime.now()
    twelve_earlier = time_now - datetime.timedelta(hours=hours)

    endStamp= int(time.mktime(time_now.timetuple()))
    startStamp= int(time.mktime(twelve_earlier.timetuple()))
    print(startStamp, endStamp)
    c=1
    print(range(startStamp, endStamp, step))

    for currentStamp in range(startStamp,endStamp,step):
        e=' --'
        if(c%2==0):
            e=' |'
        f = str(currentStamp)
        g = str(currentStamp+step)
        search_results = r.subreddit(subName).search(b+f+d+g, syntax='cloudsearch')

        for post in search_results:
            print("---I found a post! It\'s called:" + str(post))
            url= "https://reddit.com" + (post.permalink).replace('?ref=search_posts','')
            data= {'user-agent':'archive by /u/healdb'}
            #manually grabbing this file is much faster than loading the individual json files of every single comment, as this json provides all of it
            response = requests.get(url+'.json',headers=data)
            #Create a folder called dogecoinArchive before running the script
            filename=folderName+"/"+post.name+'.json'
            obj=open(filename, 'w')
            obj.write(response.text)
            obj.close()
            #print post_json
            #print("I saved the post and named it " + str(post.name) + " .---")
            time.sleep(1)
        obj=open(folderName+"/lastTimestamp.txt", 'w')
        obj.write(str(currentStamp))
        obj.close()
        c+=1

def run(subreddit, hours, delete_old=True):

    folderName = "flaskbb/scrapers/{}".format(subreddit)

    if not os.path.exists(folderName):
        os.makedirs(folderName)
    else:
        if delete_old:
            shutil.rmtree(folderName)
            os.makedirs(folderName)

    try:
        step = 30
        scrape(hours, step, folderName, subreddit)
        print("Succesfully got all posts within parameters.")
    except KeyboardInterrupt:
        exit()
    except SystemExit:
        exit()
