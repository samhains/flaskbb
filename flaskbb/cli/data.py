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
    f = open('posts.txt', 'w')
    for post in posts:
        print(post.message)
        f.write(post.message.encode('utf-8').strip()+"\n")

@data.command("generate_thread_corpus")
def generate_thread_corpus():
    unique_threads = RawData.query.distinct(RawData.thread_name).all()
    f = open('posts.txt', 'w')
    for thread in unique_threads:
        print(thread.thread_name)
        # f.write(post.message.encode('utf-8').strip()+"\n")


@data.command("generate_user")
def generate_user():
    with open("users.txt") as f:
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


    # print(markovify)
    # # Print five randomly-generated sentences
    # for i in range(5):
        # print(text_model.make_sentence(tries=100))

    # # Print three randomly-generated sentences of no more than 140 characters
    # for i in range(3):
        # print(text_model.make_short_sentence(1, test_output=False))

# @data.command("create_base_ilxor_model")

def generate_thread(user, forum):
    with open("posts.txt", "r") as f:
        text = f.read()

    # Build the model.
    text_model = markovify.Text(text)

    # Print three randomly-generated sentences of no more than 140 characters
    post_content = text_model.make_sentence()
    post = Post(content=post_content)
    thread_name = text_model.make_short_sentence(100)
    thread = Topic(title=thread_name)
    thread.save(user=user, forum=forum, post=post)


def generate_post(forum, user, topic):
    with open("posts.txt", "r") as f:
        text = f.read()

    # Build the model.
    text_model = markovify.Text(text)

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

    if rand_val > 0.95:
        generate_thread(user, forum)
    else:
        topics = Topic.query.all()
        topic = random.choice(topics)
        generate_post(forum, user, topic)

    # topic = Topic.query.all()[0]

    # # topic = Topic(title="hello")
    # post = Post(content="okokokok")
    # post.save(user=user, topic=topic)

    # with open("posts.txt") as f:
        # text = f.read()

    # # Build the model.
    # text_model = markovify.Text(text)

    # # Print five randomly-generated sentences
    # for i in range(5):
        # print(text_model.make_sentence())

    # # Print three randomly-generated sentences of no more than 140 characters
    # for i in range(3):
        # print(text_model.make_short_sentence(140))

                 

@data.command("seed_ilxor")
def seed_ilxor():
    """Installs a new plugin."""

    with open('ilxor.csv', 'rb') as csvfile:
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
                raw_data = RawData(thread_id=thread_id, thread_name=thread_name, post_num=post_num, username=username, message=message)
                raw_data.save()
             
