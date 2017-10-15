import json
import random
import markovify
from flaskbb.user.models import User
from flaskbb.generate.microsoft_azure import analyse_image


def caption_img(image_url):
    try: 
        return analyse_image(image_url)["description"]["captions"][0]["text"]
    except:
        print("problem captioning image!")
        return ""

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
        post_content += text_model.make_sentence()
        post_content += " "


    post_content += "\n"
    post_content += "\n"

    return post_content

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
