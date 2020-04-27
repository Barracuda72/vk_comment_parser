#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base

class Photo(Base):
    __tablename__ = "photo"
    id = Column(Integer, primary_key=True)
    date = Column(Integer)

    #owner_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship('User', foreign_keys=[owner_id])

    comments_count = Column(Integer)
    likes_count = Column(Integer)
    reposts_count = Column(Integer)

    def __init__(self, id, photo):
        self.id = id
        self.text = photo.get('text')
        self.owner_id = photo.get('owner_id')
        self.date = photo.get('date')
        self.comments_count = photo.get('comments', {}).get('count')
        self.likes_count = photo.get('likes', {}).get('count')
        self.reposts_count = photo.get('reposts', {}).get('count')
        # Geo?

    def __repr__(self):
        return "<photo '%d' '%s'>" % (self.id, self.text,)
