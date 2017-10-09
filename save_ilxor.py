import csv
from flask import Flask
from flaskbb.plugins.data.models import RawData
from flaskbb.extensions import db
from flaskbb.utils.database import UTCDateTime

# user_instance = User.query.filter_by(id=user_id).first()
print(RawData)

from datetime import date
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from alembic import op
import click
from flask import Flask

app = Flask(__name__)

@app.cli.command()
def initdb():
    """Initialize the database."""
    click.echo('Init the db')

# Create an ad-hoc table to use for the insert statement.
# rawdata_table = table('rawdata',
    # sa.Column("id", sa.Integer),
    # sa.Column("thread_id", sa.Integer, nullable=False),
    # sa.Column("thread_name", sa.String, nullable=False),
    # sa.Column("post_num", sa.Integer, nullable=False),
    # sa.Column("username", sa.String, nullable=False),
    # sa.Column("message", sa.String, nullable=False),
    # sa.Column("date_created", UTCDateTime(timezone=True), nullable=True )
# )

# # thread_id,thread_name,post_num,username,message
# with open('ilxor.csv', 'rb') as csvfile:
    # ilxor_data = []
    # csvreader = csv.reader(csvfile)
    # for row in csvreader:
        # print(row)
        # if (len(row) > 1):
            # thread_id = row[0]
            # thread_name = row[1]
            # post_num = row[2]
            # username = row[3]
            # message = row[4]
            # ilxor_data.append({'thread_id': thread_id, 'thread_name': thread_name, 'post_num':post_num, 'username':username, 'message': message})
    # op.bulk_insert(rawdata_table, ilxor_data)

