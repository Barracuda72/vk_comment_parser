#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from entities.Base import Base
from entities.User import User
from entities.City import City
from entities.Country import Country
from entities.Connections import Connections
from entities.Counters import Counters
from entities.Education import Education
from entities.University import University
from entities.Faculty import Faculty
from entities.Post import Post
from entities.Photo import Photo
from entities.Comment import Comment

engine = create_engine('sqlite:///:memory:', echo=False)
_session = sessionmaker(bind=engine)

session = _session()

Base.metadata.create_all(engine)

