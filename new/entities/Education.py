#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base

class Education(Base):
    __tablename__ = "education"
    id = Column(Integer, primary_key=True)

    university_id = Column(Integer, ForeignKey('university.id'))
    university = relationship('University')

    faculty_id = Column(Integer, ForeignKey('faculty.id'))
    faculty = relationship("Faculty")

    graduation = Column(Integer)

    def __init__(self, id, educ):
        self.id = id

        self.university_id = educ.get('university')
        self.faculty_id = educ.get('faculty')
        self.graduation = educ.get('graduation')

    def __repr__(self):
        return "<Education '%d'>" % (self.id,)
