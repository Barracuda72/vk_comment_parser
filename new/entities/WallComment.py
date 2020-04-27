#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base
from entities.Comment import Comment

class WallComment(Comment):
    __tablename__ = "wall_comment"
    unique_id = Column(Integer, ForeignKey("comment.unique_id"), primary_key=True)
    
    post_id = Column(Integer, ForeignKey('post.unique_id'))
    post = relationship('Post')

    __mapper_args__ = {
        'polymorphic_identity':'wall_comment',
    }

    def __init__(self, comment):
        super().__init__(self, comment)
        self.post_id = comment.get('post_id')

    def __repr__(self):
        return "<WallComment '%d' '%s'>" % (self.id, self.text,)
