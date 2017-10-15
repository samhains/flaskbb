import flaskbb.generate.utils as utils
import flaskbb.generate.process_reddit as process
import flaskbb.scrapers.google_scraper as google_scraper
from flaskbb.forum.models import Topic, Post, Forum
from flaskbb.user.models import User
import random

JSON_PATH = 'markov_data/donald_latest_json'
MARKOV_MODEL_DIR = "markov_models"
THREAD_TO_POST_RATIO = 0.84

def model_fname(subreddit_name, model_type):
    return "{}/{}_{}.json".format(MARKOV_MODEL_DIR, model_type, subreddit_name)

def generate_title(subreddit):
    text_model = utils.load_model(model_fname(subreddit, 'title'))
    title = text_model.make_sentence(tries=100)
    return title 


# def parse_json(fname):
def create_reddit_post_model(subreddit):
    json_path = "flaskbb/scrapers/{}".format(subreddit)
    text = process.get_posts_text(json_path)
    utils.create_model_from_text(text, model_fname(subreddit, "post"))

def create_reddit_title_model(subreddit):
    json_path = "flaskbb/scrapers/{}".format(subreddit)
    text = process.get_titles_text(json_path)
    utils.create_model_from_text(text, model_fname(subreddit, "title"))

def save_thread(user, forum, subreddit):

    thread_name = generate_title(subreddit)

    text_model = utils.load_model(model_fname(subreddit, 'post')) 
    post_content = utils.generate_body(text_model)

    post = Post(content=post_content)
    thread = Topic(title=thread_name)
    thread.save(user=user, forum=forum, post=post)

def seed_users():
    subreddits = ["politics"]
    text = ""
    for subreddit in subreddits:
        json_path = "flaskbb/scrapers/{}".format(subreddit)
        text = text + process.get_usernames_text(json_path)
        text += "\n"

    utils.save_user(text)

    return 


def generate_post(user, forum):
    rand_val = random.random()
    subreddits = ["politics", "The_Donald"]
    subreddit = random.choice(subreddits)
    topics = Topic.query.filter(Topic.forum_id == forum.id).all()
    topic = random.choice(topics)
    url = google_scraper.run(100, topic.title)

    if rand_val > THREAD_TO_POST_RATIO:
        save_thread(user, forum, subreddit)
    else:
        rand_val = random.random()
        topics = Topic.query.filter(Topic.forum_id == forum.id).all()
        topic = random.choice(topics)
        text_model = utils.load_model(model_fname(subreddit, 'post')) 

        if rand_val > 0.7 and rand_val < 0.85:
            utils.save_image_post_markov(forum, user, topic, text_model, url)
        elif rand_val >= 0.85:
            utils.save_image_post_caption(forum, user, topic, text_model, url)
        else:
            utils.save_post(forum, user, topic, text_model)
