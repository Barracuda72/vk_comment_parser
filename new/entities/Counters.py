#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base

class Counters(Base):
    __tablename__ = "counters"
    id = Column(Integer, primary_key=True)
    albums = Column(Integer)
    videos = Column(Integer)
    audios = Column(Integer)
    photos = Column(Integer)
    notes = Column(Integer)
    friends = Column(Integer)
    groups = Column(Integer)
    user_videos = Column(Integer)
    followers = Column(Integer)
    pages = Column(Integer)

    def __init__(self, id, counts):
        self.id = id

        self.albums = counts.get('albums')
        self.videos = counts.get('videos')
        self.audios = counts.get('audios')
        self.photos = counts.get('photos')
        self.notes = counts.get('notes')
        self.friends = counts.get('friends')
        self.groups = counts.get('groups')
        self.user_videos = counts.get('user_videos')
        self.followers = counts.get('followers')
        self.pages = counts.get('pages')

    def __repr__(self):
        return "<Counters '%d'>" % (self.id,)
