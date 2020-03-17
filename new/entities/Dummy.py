#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base

class Dummy(Base):
    __tablename__ = "dummy"
    id = Column(Integer, primary_key=True)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "<Dummy '%d'>" % (self.id,)
