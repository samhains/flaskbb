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

def create_model_from_text(text, output_fname):
    # Build the model.
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
    data_objects = RawData.query.filter(RawData.forum_id==forum_id)
    data_str = get_data_from_threads(data_objects)
    create_model_from_text(data_str, "{}/base_ilxor.json".format(MARKOV_MODEL_DIR))

@data.command("create_base_ilm_model")
def create_base_ilm_model():
    create_base_ilxor_model(41)

def load_model(data_fname):
    with open(data_fname) as data_file:    
        model_json = json.load(data_file)

    return markovify.Text.from_json(model_json)

def generate_thread_name():
    unique_threads = RawData.query.distinct(RawData.thread_name).group_by(RawData.thread_name).all()
    unique_thread = random.choice(unique_threads)

    topic = Topic.query.filter(Topic.thread_id==unique_thread.thread_id).all()
    if(len(topic) > 0):
        unique_threads = RawData.query.distinct(RawData.thread_name).group_by(RawData.thread_name).all()
        unique_thread = random.choice(unique_threads)

    return unique_thread.thread_name, unique_thread.thread_id
    

def generate_thread(user, forum):
    text_model = load_model('{}/base_ilxor.json'.format(MARKOV_MODEL_DIR))
    # Print three randomly-generated sentences of no more than 140 characters
    post_content = text_model.make_sentence()
    post = Post(content=post_content)
    thread_name, thread_id = generate_thread_name()
    print('got thread', thread_name, thread_id)
    # thread = Topic(title=thread_name, thread_id=thread_id)
    # thread.save(user=user, forum=forum, post=post)

def get_data_from_threads(threads_arr):
    data_str = ""
    for data in threads_arr:
        data_str += data.message.encode('utf-8')
        data_str += "\n"
    return data_str

def load_thread_model(thread_id):
    if os.path.exists(thread_fname(thread_id)):
        return load_model(thread_fname(thread_id))
    else: 
        data_objects = RawData.query.filter(RawData.thread_id==thread_id)
        data_str = get_data_from_threads(data_objects)
        create_model_from_text(data_str, thread_fname(thread_id))
        print("new one created!", thread_fname(thread_id))


def thread_fname(thread_id):
    return "{}/thread_{}.json".format(MARKOV_MODEL_DIR, thread_id)

def merge_thread_with_base(thread_id):
    model_a = load_model('{}/base_ilxor.json'.format(MARKOV_MODEL_DIR))
    model_b = load_thread_model(thread_id)

    model_combo = markovify.combine([ model_a, model_b ], [ 1, 2 ])

    for i in range(0, 10):
        print(model_combo.make_sentence(tries=10))


@data.command("generate_post_with_thread_weighting")
def generate_post_with_thread_weighting():
    merge_thread_with_base(10258)

def generate_post(forum, user, topic):

    text_model = load_model()
    # Print three randomly-generated sentences of no more than 140 characters
    post_content = text_model.make_sentence()
    post = Post(content=post_content)
    post.save(user=user, topic=topic)

@data.command("generate_post")
def post():
    forum = Forum.query.all()[0]
    users = User.query.all()
    user = random.choice(users)
    rand_val = random.random()


    generate_thread(user, forum)
    # if rand_val > 0.95:
        # generate_thread(user, forum)
    # else:
        # topics = Topic.query.all()
        # topic = random.choice(topics)
        # generate_post(forum, user, topic)

@data.command("seed_ilm")
def seed_ilm():
    """Installs a new plugin."""

    with open('{}/ilm.csv'.format(DATA_DIR), 'rb') as csvfile:
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
             
