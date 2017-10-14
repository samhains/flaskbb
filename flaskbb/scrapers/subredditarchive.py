# -*- coding: utf-8 -*-
import time
import datetime
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

# if not os.path.exists(folderName):
    # os.makedirs(folderName)
    
def getNew(subName,folderName):
    subreddit_comment = r.get_comments(subName, limit=1000)
    subreddit_posts = r.get_submissions(subName, limit=1000)
    for comment in subreddit_comment:
        print comment
        url= "https://reddit.com" + comment.permalink
        data= {'user-agent':'archive by /u/healdb'}
        #manually grabbing this file is much faster than loading the individual json files of every single comment, as this json provides all of it
        response = requests.get(url+'.json',headers=data)
        #Create a folder called dogecoinArchive before running the script
        filename=folderName+"/"+comment.name
        obj=open(filename, 'w')
        obj.write(response.text)
        obj.close()
        #print post_json
    for post in subreddit_posts:
        print post
        url1= "https://reddit.com" + post.permalink
        #pprint(vars(post))
        data= {'user-agent':'archive by /u/healdb'}
        #manually grabbing this file is much faster than loading the individual json files of every single comment, as this json provides all of it
        if submission.id not in already_done:
            response = requests.get(url1+'.json',headers=data)
            #Create a folder called dogecoinArchive before running the script
            filename=folderName+"/"+post.name
            obj=open(filename, 'w')
            obj.write(response.text)
            obj.close()
            #print post_json
            already_done.add(submission.id)
        else:
            continue

def scrape(startStamp,endStamp,step,folderName,subName):
    startStamp= int(time.mktime(datetime.datetime.strptime(startStamp, "%d/%m/%Y").timetuple()))
    endStamp= int(time.mktime(datetime.datetime.strptime(endStamp, "%d/%m/%Y").timetuple()))
    c=1
    print(startStamp, endStamp, step)

    for currentStamp in range(startStamp,endStamp,step):
        e=' --'
        if(c%2==0):
            e=' |'
        f = str(currentStamp)
        g = str(currentStamp+step)
        search_results = r.subreddit(subName).search(b+f+d+g, syntax='cloudsearch')

        for post in search_results:
            print(post)
            #print("---I found a post! It\'s called:" + str(post))
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

while True:
    try:
        startStamp = "01/01/2016"
        endStamp = "02/01/2016"
        step = 30
        folderName = "politics 01-07-2017 02-07-2017"
        subName = "politics"
        scrape(startStamp, endStamp, step, folderName, subName)
        print("Succesfully got all posts within parameters.")
    except KeyboardInterrupt:
        exit()
    except SystemExit:
        exit()
