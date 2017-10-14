import json
import uuid
import csv
from pprint import pprint

from os import listdir
from os.path import isfile, join
data_path = "The_donald 12-10-2017 13-10-2017"
csv_path = data_path+'.csv'
board_id = 'The_Donald'

fnames = [join(data_path, f) for f in listdir(data_path) if isfile(join(data_path, f)) and join(data_path, f).endswith('.json')]

def get_csv_writer(filename):
    f  =  open(filename, 'wb')
    return csv.writer(f)

def encode_arr(arr):
 return [s.encode('utf-8') for s in arr]

def get_data(fname, csvwriter):
    with open(fname) as data_file:    
        data = json.load(data_file)

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
                    args = [str(thread_id), title, str(post_num), username, body, board_id]
                    csvwriter.writerow(encode_arr(args))

                else:
                    print('data', post["kind"])

csvwriter = get_csv_writer(csv_path)
csvwriter.writerow(['thread_id', 'thread_name', 'post_num', 'username', 'message', 'forum_id'])
for fname in fnames:
    get_data(fname, csvwriter)
