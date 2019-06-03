#!/usr/bin/env python

import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Sequence, \
    Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

path = os.path.join(os.getcwd(), 'markers.db')
engine = create_engine('sqlite:///' + path)
Base = declarative_base()

session = None

class InlineClass(object):
    def __init__(self, dict): self.__dict__ = dict

def set_session():
    global session
    Base.metadata.create_all(engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()


def make_marker_tables():

    class Markervalues(Base):
        __tablename__ = 'markers_info'
        id = Column(Integer, Sequence('id'), primary_key=True)
        name = Column(String(10001))
        status = Column(String(10001))
        dt = Column(DateTime)

        def __init__(self, name, status):
            self.name = name
            self.status = status
            self.dt = datetime.now()

        def __repr__(self): return "<Markervalues(%d, '%s', '%s')>" % \
                                   (self.name, self.status, self.dt)

    set_session()

    class Copymarker(object):
        def __init__(self): self.last_rec = None

        def __iter__(self): return session.query(Markervalues).all().__iter__()

        def __len__(self): return session.query(Markervalues).count()

        def __contains__(self, i):
            return session.query(Markervalues).filter_by(name=i).count()

        def set_rec_no_commit(self, rec):
            session.add(Markervalues(*rec))
            self.last_rec = rec

        def set_rec(self, rec):
            session.add(Markervalues(*rec))
            session.commit()
            self.last_rec = rec

        def get_rec(self): return self.last_rec

        rec = property(get_rec, set_rec)

    return InlineClass({'copy_marker': Copymarker()})
