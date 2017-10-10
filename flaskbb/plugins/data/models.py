# -*- coding: utf-8 -*-
"""
    flaskbb.raw_data.models
    ~~~~~~~~~~~~~~~~~~~~~~

    The models for the conversations and raw_datas are located here.

    :copyright: (c) 2014 by the FlaskBB Team.
    :license: BSD, see LICENSE for more details.
"""
from sqlalchemy_utils import UUIDType

from flaskbb.extensions import db
from flaskbb.utils.helpers import time_utcnow
from flaskbb.utils.database import CRUDMixin, UTCDateTime


class RawData(db.Model, CRUDMixin):
    __tablename__ = "rawdata"

    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, nullable=False)
    thread_name = db.Column(db.String, nullable=False)
    post_num = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)

    date_created = db.Column(UTCDateTime(timezone=True), default=time_utcnow,
                             nullable=False)


    def save(self):
        """Saves a raw_data and returns the saved raw_data object.

        :param raw_data: If given, it will also save the raw_data for the
                        raw_data. It expects a Message object.
        """

        db.session.add(self)
        db.session.commit()
        return self
