import json
import uuid
import csv
from pprint import pprint

from os import listdir
from os.path import isfile, join
data_path = "The_donald 12-10-2017 13-10-2017"
csv_path = data_path+'.csv'
board_id = 'The_Donald'


def get_csv_writer(filename):
    f  =  open(filename, 'wb')
    return csv.writer(f)

def encode_arr(arr):
 return [s.encode('utf-8') for s in arr]

def get_title_str(fname):
    with open(fname) as data_file:    
        data = json.load(data_file)
        str = ""

        for item in data:
            posts = item["data"]["children"]
            for post in posts:
                kind = post["kind"]
                data = post["data"]
                if kind == "t3":
                    title = post["data"]["title"]
                    str += title.encode('utf-8')
                    str += '\n'
        return str

        return str

def get_username_str(fname):
    with open(fname) as data_file:    
        data = json.load(data_file)
        user_set = []

        for item in data:
            posts = item["data"]["children"]
            for post in posts:
                kind = post["kind"]
                data = post["data"]
                if kind == "t3":
                    username = data["author"]
                    user_set.append(username)
                elif kind == "t1":
                    username = data["author"]
                    user_set.append(username)

        return '\n'.join(user_set)

                    # args = [str(thread_id), title, str(post_num), username, body, board_id]
                    # csvwriter.writerow(encode_arr(args))

        # return str

def get_post_str(fname):
    with open(fname) as data_file:    
        data = json.load(data_file)
        str = ""

        for item in data:
            posts = item["data"]["children"]
            for post in posts:
                kind = post["kind"]
                data = post["data"]
                if kind == "t3":
                    username = data["author"]
                    post_num = 0
                    title = post["data"]["title"]
                    thread_id = uuid.uuid4()
                elif kind == "t1":
                    post_num = post_num + 1
                    username = data["author"]
                    body = post["data"]["body"]
                    str += body.encode('utf-8')
                    str += '\n'

                    # args = [str(thread_id), title, str(post_num), username, body, board_id]
                    # csvwriter.writerow(encode_arr(args))

        return str


def get_data_fnames(data_path):
    return [join(data_path, f) for f in listdir(data_path) if isfile(join(data_path, f)) and join(data_path, f).endswith('.json')]

def get_usernames_text(data_path):
    fnames = get_data_fnames(data_path)
    str = ""
    for fname in fnames:
        str += get_username_str(fname)
    return str

def get_titles_text(data_path):
    fnames = get_data_fnames(data_path)
    str = ""
    for fname in fnames:
        str += get_title_str(fname)
    return str

def get_posts_text(data_path):
    fnames = get_data_fnames(data_path)
    str = ""
    for fname in fnames:
        str += get_post_str(fname)
    return str
