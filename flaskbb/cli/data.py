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
import flaskbb.generate.reddit as reddit
import flaskbb.generate.ilxor as ilxor
import flaskbb.generate.memes as memes
import flaskbb.generate.utils as generate_utils
import flaskbb.scrapers.reddit_scraper as reddit_scraper
import datetime
from flaskbb.extensions import db

import csv

MARKOV_MODEL_DIR = "markov_models"
DATA_DIR = "markov_data"
PROJECT_DIR = os.environ[ "FLASKBB_DIR" ]

try:
    from cookiecutter.main import cookiecutter
except ImportError:
    pass


@flaskbb.group()
def data():
    """Plugins command sub group."""
    pass

@data.command("delete_old_posts")
def user_markov_model():
    current_time = datetime.datetime.utcnow()
    d = current_time - datetime.timedelta(hours=23)
    posts = Topic.query.filter(Topic.date_created < d).delete()
    # print(len(posts))


    db.session.commit()
    # print(Topic.query.filter(Post.date_created < d).count())

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
    f = open('{}/{}/posts.txt'.format(PROJECT_DIR, DATA_DIR), 'w')
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


@data.command("generate_ilxor_user")
def generate_user():
    with open("{}/{}/users.txt".format(PROJECT_DIR, DATA_DIR)) as f:
        text = f.read().split('\n')

    generate_utils.save_users(text)


@data.command("create_base_ilm_model")
def create_base_ilm_model():
    ilxor.create_base_ilxor_model(41)

@data.command("create_base_ile_model")
def create_base_ile_model():
    ilxor.create_base_ilxor_model(40)


@data.command("run")
def run():
    for i in range(0, 1):
        # r1 = random.random()
        forum_id = random.randint(1,4)
        forum = Forum.query.filter(Forum.id==forum_id).all()[0]
        users = User.query.all()
        user = random.choice(users)

        if forum_id == 3:
            reddit.reddit_post(user, forum)
        elif forum_id == 4:
            memes.memes_post(user, forum)
        else:
            ilxor.ilxor_post(user, forum)


@data.command("seed_meme_topics")
def seed_meme_topics():
    memes.seed_topics()


def seed_ilxor(fname):
    with open('{}/{}/{}.csv'.format(PROJECT_DIR, DATA_DIR, fname), 'rb') as csvfile:
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


@data.command("create_memes_model")
def update_reddit_models():
    memes.create_memes_model()


@data.command("update_reddit_models")
def update_reddit_models():
    subreddits = ["The_Donald", "politics"]
    hours = 24
    for subreddit in subreddits:
        reddit_scraper.run(subreddit, hours, delete_old=False)
        reddit.create_reddit_post_model(subreddit)
        reddit.create_reddit_title_model(subreddit)

@data.command("recalculate_forums")
def seed_forums():
    forums = Forum.query.all()
    for forum in forums:
        forum.recalculate()

# @data.command("seed_forums")
# def seed_forums():
    # forum = Forum(title="Everything", description="general discussion", category_id=1, position=2)
    # forum = Forum(title="Memiverse", description="culture spreading like virus", category_id=1, position=4)
    # forum = Forum(title="Politics", description="please keep it civil", category_id=1, position=3)
    # forum.save()

@data.command("seed_avatars")
def seed_avatars():
    gan_path_prefix = "{}/{}/avatars/".format(PROJECT_DIR, DATA_DIR)
    avatars = [fname for fname in os.listdir(gan_path_prefix)]
    users = User.query.all()
    print(avatars)
# 
    for user in users:
        avatar = random.choice(avatars)
        url = "https://s3-us-west-2.amazonaws.com/avatars-pluto-c/avatars/{}".format(avatar)
        user.avatar = url
        db.session.commit()

@data.command("seed_reddit_users")
def seed_reddit_users():
    reddit.seed_users()

@data.command("seed_ile")
def seed_ilm():
    seed_ilxor('ile')

@data.command("seed_ilm")
def seed_ilm():
    seed_ilxor('ilm')
