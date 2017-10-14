import flaskbb.generate.utils as utils
import flaskbb.generate.process_reddit as process
from flaskbb.forum.models import Topic, Post, Forum
import random

forum_name = "The_Donald"
JSON_PATH = 'markov_data/donald_latest_json'
MARKOV_MODEL_DIR = "markov_models"
THREAD_TO_POST_RATIO = 0.60

def model_fname(model_name):
    return "{}/{}_{}.json".format(MARKOV_MODEL_DIR, model_name, forum_name)

def generate_title():
    text_model = utils.load_model(model_fname('title'))
    title = text_model.make_sentence()
    return title 

def generate_body():
    text_model = utils.load_model(model_fname('post'))
    post_content = text_model.make_sentence()
    return post_content 

# def parse_json(fname):
def create_reddit_post_model():
    text = process.get_posts_text(JSON_PATH)
    utils.create_model_from_text(text, model_fname("post"))

def create_reddit_title_model():
    text = process.get_titles_text(JSON_PATH)
    utils.create_model_from_text(text, model_fname("title"))

def save_thread(user, forum):

    thread_name = generate_title()
    post_content = generate_body()

    post = Post(content=post_content)
    thread = Topic(title=thread_name)
    thread.save(user=user, forum=forum, post=post)

def save_post(forum, user, topic):
    # Print three randomly-generated sentences of no more than 140 characters
    post_content = generate_body()
    post = Post(content=post_content)
    post.save(user=user, topic=topic)

def generate_post(user, forum):
    rand_val = random.random()

    if rand_val > THREAD_TO_POST_RATIO:
        save_thread(user, forum)
    else:
        topics = Topic.query.filter(Topic.forum_id == forum.id).all()
        topic = random.choice(topics)
        save_post(forum, user, topic)
