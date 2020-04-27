#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base

class Comment(Base):
    __tablename__ = "comment"
    unique_id = Column(Integer, primary_key=True)
    id = Column(Integer)
    text = Column(String)
    date = Column(Integer)
    
    from_id = Column(Integer, ForeignKey('user.id'))
    from_ = relationship('User', foreign_keys=[from_id])
    
    reply_to_comment_id = Column(Integer, ForeignKey('comment.unique_id'))
    reply_to_comment = relationship('Comment')

    __mapper_args__ = {
        'polymorphic_identity':'comment',
        'polymorphic_on':type
    }

    def __init__(self, comment):
        self.id = comment.get('id')
        self.text = comment.get('text')
        self.date = comment.get('date')
        self.from_id = comment.get('from_id')
        self.reply_to_comment_id = comment.get('reply_to_comment')

    def __repr__(self):
        return "<Comment '%d' '%s'>" % (self.id, self.text,)
