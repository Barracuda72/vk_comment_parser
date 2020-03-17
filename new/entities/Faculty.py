#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base

class Faculty(Base):
    __tablename__ = "faculty"
    id = Column(Integer, primary_key=True)
    faculty_name = Column(String)

    def __init__(self, id, faculty_name):
        self.id = id
        self.faculty_name = faculty_name

    def __repr__(self):
        return "<Faculty '%d' '%s'>" % (self.id, self.faculty_name,)
