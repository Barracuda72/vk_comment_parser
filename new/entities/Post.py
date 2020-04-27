#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base

class Post(Base):
    __tablename__ = "post"
    unique_id = Column(Integer, primary_key=True)
    id = Column(Integer)
    text = Column(String)
    date = Column(Integer)

    #owner_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship('User', foreign_keys=[owner_id])

    from_id = Column(Integer, ForeignKey('user.id'))
    from_ = relationship('User', foreign_keys=[from_id])

    reply_post_id = Column(Integer, ForeignKey('post.unique_id'))
    reply_post = relationship('Post')

    comments_count = Column(Integer)
    likes_count = Column(Integer)
    reposts_count = Column(Integer)
    views_count = Column(Integer)

    def __init__(self, post):
        self.id = post.get('id')
        self.text = post.get('text')
        self.owner_id = post.get('owner_id')
        self.from_id = post.get('from_id')
        self.date = post.get('date')
        self.reply_post_id = post.get('reply_post_id')
        self.comments_count = post.get('comments', {}).get('count')
        self.likes_count = post.get('likes', {}).get('count')
        self.reposts_count = post.get('reposts', {}).get('count')
        self.views_count = post.get('views', {}).get('count')
        # Geo?

    def __repr__(self):
        return "<Post '%d' '%s'>" % (self.id, self.text,)
