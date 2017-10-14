import flaskbb.generate.utils as utils
import flaskbb.generate.process_reddit as process
import flaskbb.scrapers.google_scraper as google_scraper
from flaskbb.forum.models import Topic, Post, Forum
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

def generate_body(subreddit):
    text_model = utils.load_model(model_fname(subreddit, 'post')) 
    post_content = text_model.make_sentence()
    return post_content 

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
    post_content = generate_body(subreddit)

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

def save_image_post(forum, user, topic, subreddit, image_url):
    # Print three randomly-generated sentences of no more than 140 characters
    post_content = "![]({})".format(image_url)
    # post_content = generate_body(subreddit)
    post = Post(content=post_content)
    post.save(user=user, topic=topic)

def save_post(forum, user, topic, subreddit):
    # Print three randomly-generated sentences of no more than 140 characters
    post_content = generate_body(subreddit)
    post = Post(content=post_content)
    post.save(user=user, topic=topic)

def generate_post(user, forum):
    rand_val = random.random()
    subreddits = ["politics", "The_Donald"]
    subreddit = random.choice(subreddits)
    topics = Topic.query.filter(Topic.forum_id == forum.id).all()
    topic = random.choice(topics)
    url = google_scraper.run(100, topic.title)
    save_image_post(forum, user, topic, subreddit, url)

    # if rand_val > THREAD_TO_POST_RATIO:
        # save_thread(user, forum, subreddit)
    # else:
        # topics = Topic.query.filter(Topic.forum_id == forum.id).all()
        # topic = random.choice(topics)
        # save_post(forum, user, topic, subreddit)
