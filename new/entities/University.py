#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base

class University(Base):
    __tablename__ = "university"
    id = Column(Integer, primary_key=True)
    university_name = Column(String)

    def __init__(self, id, university_name):
        self.id = id
        self.university_name = university_name

    def __repr__(self):
        return "<University '%d' '%s'>" % (self.id, self.university_name,)
