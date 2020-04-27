#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base
from entities.Comment import Comment

class PhotoComment(Comment):
    __tablename__ = "photo_comment"
    unique_id = Column(Integer, ForeignKey("comment.unique_id"), primary_key=True)
    
    photo_id = Column(Integer, ForeignKey('photo.unique_id'))
    photo = relationship('Photo')

    __mapper_args__ = {
        'polymorphic_identity':'photo_comment',
    }

    def __init__(self, comment):
        super().__init__(comment)
        self.photo_id = comment.get('pid')

    def __repr__(self):
        return "<PhotoComment '%d' '%s'>" % (self.id, self.text,)
