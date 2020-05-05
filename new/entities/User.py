#!/usr/bin/env false

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from entities.Base import Base

from datetime import datetime

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
        self.deactivated = bool(user.get('deactivated'))
        self.is_closed = user.get('is_closed')
        self.nickname = user.get('nickname')
        self.about = user.get('about')
        self.sex = user.get('sex')
        self.city_id = user.get('city', {}).get('id')
        self.country_id = user.get('country', {}).get('id')
        bdate = user.get('bdate')
        if (bdate):
            if (bdate.count(".") == 1):
                # Append fake year
                bdate = bdate + ".6000"
            try:
                self.bdate = datetime.strptime(bdate, "%d.%m.%Y")
            except ValueError as e:
                print ("Error parsing date {}, leaving empty".format(bdate))
                self.bdate = None
        # TODO: connections, counter, updated!

    def __repr__(self):
        return "<User('id%d', '%s','%s')>" % (self.id, self.first_name, self.last_name)
