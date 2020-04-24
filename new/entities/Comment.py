#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base

class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    date = Column(Integer)
    
    from_id = Column(Integer, ForeignKey('user.id'))
    from_ = relationship('User')
    
    post_id = Column(Integer, ForeignKey('post.id'))
    post = relationship('Post')

    photo_id = Column(Integer, ForeignKey('photo.id'))
    photo = relationship('Photo')

    reply_to_comment_id = Column(Integer, ForeignKey('comment.id'))
    reply_to_comment = relationship('Comment')

    def __init__(self, id, comment):
        self.id = id
        self.text = comment.get('text')
        self.from_id = comment.get('from_id')
        self.post_id = comment.get('post_id')
        self.photo_id = comment.get('pid')
        self.date = comment.get('date')
        self.reply_to_comment_id = comment.get('reply_to_comment')

    def __repr__(self):
        return "<Comment '%d' '%s'>" % (self.id, self.text,)
