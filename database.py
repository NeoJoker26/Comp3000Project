from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from models import Banana

Base = declarative_base()


# this is where all the crud happens, i initialise the db with the url, i then have the option to call on the CRUD
# with main.py from models
class DatabaseHandler:
    def __init__(self, db_url):
        self.engine = create_engine(db_url, echo=True)
        self.Session = Session
        Base.metadata.create_all(self.engine)

    def create_banana(self, size, weight, sweetness, softness, harvest_time, ripeness, acidity, quality):
        with self.Session(self.engine) as session:
            banana = Banana(
                size=size,
                weight=weight,
                sweetness=sweetness,
                softness=softness,
                harvest_time=harvest_time,
                ripeness=ripeness,
                acidity=acidity,
                quality=quality
            )
            session.add(banana)
            session.commit()
            session.refresh(banana)  # Refresh the object to get the generated banana_id
            return banana.banana_id

    def read_banana(self, banana_id):
        with self.Session(self.engine) as session:
            return session.get(Banana, banana_id)

    def update_banana(self, banana_id, **kwargs):
        with self.Session(self.engine) as session:
            banana = session.get(Banana, banana_id)
            if banana:
                for key, value in kwargs.items():
                    setattr(banana, key, value)
                session.commit()
            return banana

    def delete_banana(self, banana_id):
        with self.Session(self.engine) as session:
            banana = session.get(Banana, banana_id)
            if banana:
                session.delete(banana)
                session.commit()
                return True
            return False
