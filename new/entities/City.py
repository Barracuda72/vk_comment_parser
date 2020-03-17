#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base

class City(Base):
    __tablename__ = "city"
    id = Column(Integer, primary_key=True)
    title = Column(String)

    def __init__(self, id, title):
        self.id = id
        self.title = title

    def __repr__(self):
        return "<City '%d' '%s'>" % (self.id, self.title,)
