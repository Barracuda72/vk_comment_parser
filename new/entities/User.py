#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    deactivated = Column(Boolean, nullable=False, default=False)
    is_closed = Column(Boolean, nullable=False, default=False)

    nickname = Column(String)
    about = Column(String)
    bdate = Column(DateTime)
    sex = Column(Integer)

    city_id = Column(Integer, ForeignKey('city.id'))
    city = relationship("City")

    country_id = Column(Integer, ForeignKey("country.id"))
    country = relationship("Country")

    education_id = Column(Integer, ForeignKey('education.id'))
    education = relationship("Education")

    connections_id = Column(Integer, ForeignKey("connections.id"))
    connections = relationship("Connections")

    counters_id = Column(Integer, ForeignKey("counters.id"))
    counters = relationship("Counters")

    updated = Column(DateTime, nullable=False)

    def __init__(self, id, user):
        self.id = int(id)

        self.first_name = user.get('first_name')
        self.last_name = user.get('last_name')
        self.deactivated = user.get('deactivated')
        self.is_closed = user.get('is_closed')
        self.nickname = user.get('nickname')
        self.about = user.get('about')
        self.bdate = user.get('bdate')
        self.sex = user.get('sex')
        self.city_id = user.get('city', {}).get('id')
        self.country_id = user.get('country', {}).get('id')
        # TODO: connections, counter, updated!

    def __repr__(self):
        return "<User('id%d', '%s','%s')>" % (self.vk_id, self.firstname, self.lastname)
