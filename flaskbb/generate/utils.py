import json
import random
import uuid
import pyimgur
import markovify
from flaskbb.user.models import User
from flaskbb.forum.models import Topic, Post, Forum
from flaskbb.generate.microsoft_azure import analyse_image
import flaskbb.scrapers.google_scraper as google_scraper

IMGUR_CLIENT_ID = "435f67c1a9fb655"

def caption_img(image_url):
    try: 
        return analyse_image(image_url)["description"]["captions"][0]["text"]
    except:
        print("problem captioning image!")
        return ""

def generate_body(text_model):
    max_paragraphs = 2
    max_paragraph_size = 4
    post_content = generate_paragraphs(text_model, max_paragraphs, max_paragraph_size)
    return post_content 

def save_image_post_markov(forum, user, topic, text_model, image_url):
    post_content = generate_body(text_model)
    post_content += "![]({})".format(image_url)
    post = Post(content=post_content)
    post.save(user=user, topic=topic)

def save_image_post_caption(forum, user, topic, text_model, image_url):
    caption = caption_img(image_url)
    save_post_with_image_and_text(user, topic, image_url, caption)
    users = User.query.all()
    range_int = random.randint(0, 2)

    for i in range(0, range_int):
        # post caption of previous image
        user = random.choice(users)
        post_content = generate_body(text_model)
        image_url = google_scraper.run(2, caption)
        text = caption_img(image_url)
        post_content += text
        save_post_with_image_and_text(user, topic, image_url, post_content)

def save_post_with_image_and_text(user, topic, image_url, text):
    post_content = ""
    post_content += text
    post_content += "\n"
    post_content += "\n"
    post_content += "![]({})".format(image_url)
    post = Post(content=post_content)
    post.save(user=user, topic=topic)



def save_post(forum, user, topic, text_model):
    # Print three randomly-generated sentences of no more than 140 characters
    post_content = generate_body(text_model)
    post = Post(content=post_content)
    post.save(user=user, topic=topic)

def generate_paragraphs(text_model, max_paragraphs, max_paragraph_size):
    post_content = ""
    max_paragraphs = random.randint(1, max_paragraphs)
    for i in range(0, max_paragraphs):
        post_content += generate_paragraph(text_model, max_paragraph_size)

    return post_content


def generate_paragraph(text_model, max_paragraph_size):
    post_content = ""
    max_paragraph_size = random.randint(1, max_paragraph_size)

    for i in range(0, max_paragraph_size):
        post_content += text_model.make_sentence(test_output=False)
        post_content += " "


    post_content += "\n"
    post_content += "\n"

    return post_content

def upload_image(image_url):

    title = uuid.uuid4()
    im = pyimgur.Imgur(IMGUR_CLIENT_ID)
    uploaded_image = im.upload_image(image_url, title=title)
    return uploaded_image

def load_model(data_fname):
    with open(data_fname) as data_file:    
        model_json = json.load(data_file)

    return markovify.Text.from_json(model_json)


def create_model_from_text(text, output_fname):
    # Build the model.
    text_model = markovify.Text(text)
    model_json = text_model.to_json()
    print('saving model', output_fname)
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


def post_or_image(forum, user, topic, text_model):
    rand_val = random.random()
    topics = Topic.query.filter(Topic.forum_id == forum.id).all()
    topic = random.choice(topics)

    if rand_val > 0.50 and rand_val < 0.85:
        url = google_scraper.run(50, topic.title)
        save_image_post_markov(forum, user, topic, text_model, url)
    elif rand_val >= 0.85:
        url = google_scraper.run(50, topic.title)
        save_image_post_caption(forum, user, topic, text_model, url)
    else:
        save_post(forum, user, topic, text_model)

def save_user(text):
    text = text.split("\n")
    for username in text:
        # print('saving', username)
        try: 
            username = username.decode('ascii')
            user = User.query.filter(User.username==username).all()
            if len(user) == 0 and len(username) > 1:
                user = User(username=username, email="{}@gmail.com".format(username), _password="password", primary_group_id=4, activated=1)
                user.save()
        except:
            print('not asciiable')
