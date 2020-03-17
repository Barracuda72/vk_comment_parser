#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base

class Connections(Base):
    __tablename__ = "connections"
    id = Column(Integer, primary_key=True)
    skype = Column(String)
    facebook = Column(String)
    twitter = Column(String)
    livejournal = Column(String)
    instagram = Column(String)

    def __init__(self, id, conns):
        self.id = id

        self.skype = conns.get('skype')
        self.facebook = conns.get('facebook')
        self.twitter = conns.get('twitter')
        self.livejournal = conns.get('livejournal')
        self.instagram = conns.get('instagram')

    def __repr__(self):
        return "<Connections '%d'>" % (self.id,)
