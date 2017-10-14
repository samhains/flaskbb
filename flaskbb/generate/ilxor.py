from flaskbb.plugins.data.models import RawData
from flaskbb.forum.models import Topic, Post, Forum
import flaskbb.generate.utils as utils

import markovify
import os
import random

THREAD_TO_POST_RATIO = 0.94
MARKOV_MODEL_DIR = "markov_models"
DATA_DIR = "markov_data"
THREAD_CORPUS_MIN = 14

def get_data_from_threads(threads_arr):
    data_str = ""
    for data in threads_arr:
        try:
            data_str += data.message.encode('ascii')
            data_str += "\n"
        except:
            print("not ascii")
    return data_str

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

def load_thread_model(thread_id):

    if os.path.exists(thread_fname(thread_id)):
        return utils.load_model(thread_fname(thread_id))
    else: 
        data_objects = RawData.query.filter(RawData.thread_id == thread_id).all()
        data_str = get_data_from_threads(data_objects)
        print("new one created!", thread_fname(thread_id))
        return utils.create_model_from_text(data_str, thread_fname(thread_id))


def thread_fname(thread_id):
    return "{}/thread_{}.json".format(MARKOV_MODEL_DIR, thread_id)


def get_combined_model_for_thread(base_model_url, thread_id):
    model_a = utils.load_model(base_model_url)
    model_b = load_thread_model(thread_id)
    print('combining models')
    return markovify.combine([model_a, model_b], [1, 2])

def get_thread_model(forum, thread_id):
    thread_corpus_size = RawData.query.filter(RawData.thread_id==thread_id).count()
    base_model_url = get_base_model_url(forum)

    if thread_corpus_size > THREAD_CORPUS_MIN:
        thread_model = get_combined_model_for_thread(base_model_url, thread_id)
    else:
        thread_model = utils.load_model(base_model_url)

    return thread_model

def generate_thread_name(forum):
    raw_data_forum_id = map_forum_to_raw_data_forum_id(forum)
    unique_threads = RawData.query.filter(RawData.forum_id==raw_data_forum_id).distinct(RawData.thread_name).group_by(RawData.thread_name).all()
    unique_thread = random.choice(unique_threads)

    topic = Topic.query.filter(Topic.thread_id==unique_thread.thread_id).all()
    if(len(topic) > 0):
        unique_threads = RawData.query.filter(RawData.forum_id==raw_data_forum_id).distinct(RawData.thread_name).group_by(RawData.thread_name).all()
        unique_thread = random.choice(unique_threads)

    return unique_thread.thread_name, unique_thread.thread_id

def get_base_model_url(forum):
    if (forum.id == 2):
        model_name = 'ile'
    else:
        model_name = 'ilm'

    return '{}/base_{}.json'.format(MARKOV_MODEL_DIR, model_name)

def save_thread(user, forum):

    thread_name, thread_id = generate_thread_name(forum)
    text_model = get_thread_model(forum, thread_id)

    post_content = text_model.make_sentence()
    post = Post(content=post_content)
    thread = Topic(title=thread_name)
    thread.save(user=user, forum=forum, post=post, thread_id=thread_id)

def generate_post(forum, user, topic, text_model):
    # Print three randomly-generated sentences of no more than 140 characters
    post_content = text_model.make_sentence()
    post = Post(content=post_content)
    post.save(user=user, topic=topic)

def ilxor_post(user, forum):
    rand_val = random.random()

    if rand_val > THREAD_TO_POST_RATIO:

        save_thread(user, forum)
    else:
        threads = Topic.query.filter(Topic.forum_id==forum.id).all()
        thread = random.choice(threads)
        thread_model = get_thread_model(forum, thread.id)
        generate_post(forum, user, thread, thread_model)

