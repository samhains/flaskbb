# -*- coding: utf-8 -*-
"""
    flaskbb.cli.plugins
    ~~~~~~~~~~~~~~~~~~~

    This module contains all plugin commands.

    :copyright: (c) 2016 by the FlaskBB Team.
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
import shutil
import random
import json

import click
from flask import current_app

import markovify
from flaskbb.forum.models import Topic, Post, Forum
from flaskbb.user.models import User
from flaskbb.cli.main import flaskbb
from flaskbb.cli.utils import check_cookiecutter, validate_plugin
from flaskbb.extensions import plugin_manager
from flaskbb.plugins.data.models import RawData
import csv

MARKOV_MODEL_DIR = "markov_models"
DATA_DIR = "markov_data"
THREAD_CORPUS_MIN = 14
THREAD_TO_POST_RATIO = 0.9

try:
    from cookiecutter.main import cookiecutter
except ImportError:
    pass


@flaskbb.group()
def data():
    """Plugins command sub group."""
    pass

@data.command("generate_user_corpus")
def user_markov_model():
    unique_users = RawData.query.distinct(RawData.username).group_by(RawData.username).all()
    f = open('users.txt', 'w')
    for user in unique_users:
        user = [p.split(')')[0] for p in user.username.split('(') if ')' in p]
        if(len(user)> 0):
            print(user[0])
            f.write(user[0].encode('utf-8').strip()+"\n")


@data.command("generate_post_corpus")
def generate_post_corpus():
    posts = RawData.query.all()
    f = open('{}/posts.txt'.format(DATA_DIR), 'w')
    for post in posts:
        print(post.message)
        f.write(post.message.encode('utf-8').strip()+"\n")

@data.command("generate_thread_corpus")
def generate_thread_corpus():
    unique_threads = RawData.query.distinct(RawData.thread_name).all()
    # f = open('posts.txt', 'w')
    for thread in unique_threads:
        print(thread.thread_name)
        # f.write(post.message.encode('utf-8').strip()+"\n")


@data.command("generate_user")
def generate_user():
    with open("{}/users.txt".format(DATA_DIR)) as f:
        text = f.read().split('\n')

    for username in text:
        try: 
            username = username.decode('ascii')
            user = User.query.filter(User.username==username).all()
            if len(user) == 0:
                user = User(username=username, email="{}@gmail.com".format(username), _password="password", primary_group_id=4, activated=1)
                user.save()
        except:
            print('not asciiable')

def map_forum_to_raw_data_forum_id(forum):
    id = forum.id
    if(id == 2):
        return 40
    else:
        return 41

def map_raw_data_forum_id_to_forum(forum_id):
    if(forum_id == 40):
        id = 2
    else:
        id = 1
    return Forum.query.filter(Forum.id==id).one()

def create_model_from_text(text, output_fname):
    # Build the model.
    print(text)
    text_model = markovify.Text(text)
    model_json = text_model.to_json()
    with open(output_fname, "w") as f:
        json.dump(model_json, f)

    return text_model

def create_model_from_file(data_fname, output_fname):
    with open(data_fname, "r") as f:
        text = f.read()
    # Build the model.
    text_model = markovify.Text(text)
    model_json = text_model.to_json()
    with open(output_fname, "w") as f:
        json.dump(model_json, f)

    return text_model

def create_base_ilxor_model(forum_id):
    data_objects = RawData.query.filter(RawData.forum_id == forum_id)
    data_str = get_data_from_threads(data_objects)
    forum = map_raw_data_forum_id_to_forum(forum_id)
    create_model_from_text(data_str, get_base_model_url(forum))

@data.command("create_base_ilm_model")
def create_base_ilm_model():
    create_base_ilxor_model(41)

@data.command("create_base_ile_model")
def create_base_ile_model():
    create_base_ilxor_model(40)

def load_model(data_fname):
    with open(data_fname) as data_file:    
        model_json = json.load(data_file)

    return markovify.Text.from_json(model_json)

def generate_thread_name(forum):
    raw_data_forum_id = map_forum_to_raw_data_forum_id(forum)
    unique_threads = RawData.query.filter(RawData.forum_id==raw_data_forum_id).distinct(RawData.thread_name).group_by(RawData.thread_name).all()
    unique_thread = random.choice(unique_threads)

    topic = Topic.query.filter(Topic.thread_id==unique_thread.thread_id).all()
    if(len(topic) > 0):
        unique_threads = RawData.query.filter(RawData.forum_id==raw_data_forum_id).distinct(RawData.thread_name).group_by(RawData.thread_name).all()
        unique_thread = random.choice(unique_threads)

    return unique_thread.thread_name, unique_thread.thread_id
    

def save_thread(user, forum):

    thread_name, thread_id = generate_thread_name(forum)
    text_model = get_thread_model(forum, thread_id)

    post_content = text_model.make_sentence()
    post = Post(content=post_content)
    thread = Topic(title=thread_name)
    thread.save(user=user, forum=forum, post=post, thread_id=thread_id)

def get_data_from_threads(threads_arr):
    data_str = ""
    for data in threads_arr:
        try:
            data_str += data.message.encode('ascii')
            data_str += "\n"
        except:
            print("not ascii")
    return data_str

def load_thread_model(thread_id):

    if os.path.exists(thread_fname(thread_id)):
        return load_model(thread_fname(thread_id))
    else: 
        data_objects = RawData.query.filter(RawData.thread_id==thread_id).all()
        data_str = get_data_from_threads(data_objects)
        print("new one created!", thread_fname(thread_id))
        return create_model_from_text(data_str, thread_fname(thread_id))


def thread_fname(thread_id):
    return "{}/thread_{}.json".format(MARKOV_MODEL_DIR, thread_id)

def get_combined_model_for_thread(base_model_url, thread_id):
    model_a = load_model(base_model_url)
    model_b = load_thread_model(thread_id)
    print('combining models')
    return markovify.combine([ model_a, model_b ], [ 1, 2 ])

def get_base_model_url(forum):
    if (forum.id == 2):
        model_name = 'ile'
    else:
        model_name = 'ilm'

    return '{}/base_{}.json'.format(MARKOV_MODEL_DIR, model_name)

def generate_post(forum, user, topic, text_model):
    # Print three randomly-generated sentences of no more than 140 characters
    post_content = text_model.make_sentence()
    post = Post(content=post_content)
    post.save(user=user, topic=topic)

def get_thread_model(forum, thread_id):
    thread_corpus_size = RawData.query.filter(RawData.thread_id==thread_id).count()
    base_model_url = get_base_model_url(forum)

    if thread_corpus_size > THREAD_CORPUS_MIN:
        thread_model = get_combined_model_for_thread(base_model_url, thread_id)
    else:
        thread_model = load_model(base_model_url)

    return thread_model

@data.command("run")
def run():
    for i in range(0, 1000):
        r1 = random.random()
        if r1 > 0.5:
            forum_id = 1
        else:
            forum_id = 2

        forums = Forum.query.filter(Forum.id==forum_id).all()
        forum = random.choice(forums)
        users = User.query.all()
        user = random.choice(users)
        rand_val = random.random()

        if rand_val > THREAD_TO_POST_RATIO:

            save_thread(user, forum)
        else:
            threads = Topic.query.filter(Topic.forum_id==forum.id).all()
            thread = random.choice(threads)
            thread_model = get_thread_model(forum, thread.id)
            generate_post(forum, user, thread, thread_model)

def seed_ilxor(fname):
    with open('{}/{}.csv'.format(DATA_DIR,fname), 'rb') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader, None)
        for row in csvreader:
            unicode_row = [x.decode('utf8') for x in row]
            if (len(row) > 1):
                thread_id = unicode_row[0]
                thread_name = unicode_row[1]
                post_num = unicode_row[2]
                username = unicode_row[3]
                message = unicode_row[4]
                forum_id = unicode_row[5]
                raw_data = RawData(thread_id=thread_id, thread_name=thread_name, post_num=post_num, username=username, message=message, forum_id=forum_id)
                raw_data.save()

@data.command("seed_forums")
def seed_forums():
    forum = Forum(title="Everything", description="general discussion", category_id=1, position=2)
    forum = Forum(title="Memiverse", description="culture spreading like virus", category_id=1, position=3)
    forum.save()



@data.command("seed_ile")
def seed_ilm():
    seed_ilxor('ile')

@data.command("seed_ilm")
def seed_ilm():
    seed_ilxor('ilm')
