import flaskbb.scrapers.google_scraper as google_scraper

import flaskbb.generate.process_reddit as process
from flaskbb.forum.models import Topic, Post, Forum
import flaskbb.generate.utils as utils
from flaskbb.user.models import User
import random
import os

DATA_DIR = "markov_data"
MEME_FORUM_ID = 4
MARKOV_MODEL_DIR = "markov_models"
MODEL_NAME = "dankmemes"
PROJECT_DIR = os.environ["FLASKBB_DIR"]

def model_fname():
    return "{}/{}/{}.json".format(PROJECT_DIR, MARKOV_MODEL_DIR, MODEL_NAME)

def seed_topics():
    f = open("{}/{}/meme_threads.txt".format(PROJECT_DIR, DATA_DIR), 'r')
    memes = f.read().split('\n')

    forum = Forum.query.filter(Forum.id==MEME_FORUM_ID).all()[0]
    text_model = utils.load_model(model_fname()) 
    users = User.query.all()

    for meme in memes[48:]:
        user = random.choice(users)
        if len(meme) > 1:
            title = meme
            url = google_scraper.run(100, title + " meme")
            post_content = "![]({})".format(url)
            post_content += "\n"
            post_content += "\n"
            post_content += text_model.make_sentence()
            rand_val = random.random()
            if rand_val > 0.6:
                title += " meme"

            post = Post(content=post_content)
            topic = Topic(title=title)
            topic.save(user=user, forum=forum, post=post)

def memes_post(user, forum):
    topics = Topic.query.filter(Topic.forum_id == forum.id).all()
    topic = random.choice(topics)
    text_model = utils.load_model(model_fname()) 
    rand_val = random.random()
    title = topic.title

    if not title.endswith('meme'):
        title += "meme"
    print(title)


    if rand_val < 0.2:
        utils.save_post(forum, user, topic, text_model)
    elif rand_val >= 0.12 and rand_val <= 0.92:
        if random.random() > 0.5:
            gan_path_prefix = "{}/{}/memes_gan/".format(PROJECT_DIR, DATA_DIR)
            meme_files = [gan_path_prefix+fname for fname in os.listdir(gan_path_prefix)]
            meme_file = random.choice(meme_files)
            url = utils.upload_image(meme_file).link
        else:
            url = google_scraper.run(100, topic.title)
        utils.save_image_post_markov(forum, user, topic, text_model, url)
    else:
        url = google_scraper.run(100, topic.title)
        utils.save_image_post_caption(forum, user, topic, text_model, url)


def create_memes_model():
    json_path = "{}/flaskbb/scrapers/dankmemes".format(PROJECT_DIR)
    text = process.get_posts_text(json_path)
    utils.create_model_from_text(text, model_fname())
