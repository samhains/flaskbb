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

@data.command("user_markov_model")
def user_markov_model():
    unique_users = RawData.query.distinct(RawData.username).group_by(RawData.username).all()
    f = open('users.txt', 'w')
    for user in unique_users:
        user = [p.split(')')[0] for p in user.username.split('(') if ')' in p]
        if(len(user)> 0):
            print(user[0])
            f.write(user[0].encode('utf-8').strip()+"\n")

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


@data.command("post")
def post():
    """Installs a new plugin."""
    # forum = Forum.query.all()[0]
    # user = User.query.all()[0]
    # topic = Topic.query.all()[0]

    # # topic = Topic(title="hello")
    # post = Post(content="okokokok")
    # post.save(user=user, topic=topic)

    with open("test.txt") as f:
        text = f.read()

    # Build the model.
    text_model = markovify.Text(text)

    # Print five randomly-generated sentences
    for i in range(5):
        print(text_model.make_sentence())

    # Print three randomly-generated sentences of no more than 140 characters
    for i in range(3):
        print(text_model.make_short_sentence(140))

                 

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
             
