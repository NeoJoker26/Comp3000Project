from sqlalchemy import create_engine, func, text, inspect, column, alias, MetaData, Table, select
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
            #  Create a session context manager using the engine
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
        # Method to retrieve a Banana record from the database by its banana_id
        # Create a session context manager using the engine
        with self.Session(self.engine) as session:
            return session.get(Banana, banana_id)

    def update_banana(self, banana_id, **kwargs):
        with self.Session(self.engine) as session:
            banana = session.get(Banana, banana_id)
            if banana:
                for key, value in kwargs.items():
                    # Iterate over the keyword arguments
                    setattr(banana, key, value)
                    # Commit the changes to the database
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

    def get_table_names(self):
        with self.Session(self.engine) as session:
            inspector = inspect(self.engine)
            # Create an inspector object for the engine
            table_names = inspector.get_table_names()
            return table_names

    def get_column_names(self, table_name):
        with self.Session(self.engine) as session:
            inspector = inspect(self.engine)
            column_names = [column['name'] for column in inspector.get_columns(table_name)]
            return column_names

    def show_bottom_100(self, table_name):
        with self.Session(self.engine) as session:
            query = session.query(Banana).order_by(Banana.banana_id.desc()).limit(100)
            result = query.all()
            return result

    def show_top_100(self, table_name):
        with self.Session(self.engine) as session:
            query = session.query(Banana).order_by(Banana.banana_id).limit(100)
            result = query.all()
            return result

    def count_records(self):
        with self.Session(self.engine) as session:
            count = session.query(Banana).count()
            return count

    def calculate_average(self, column_name):
        with self.Session(self.engine) as session:
            column_attr = getattr(Banana, column_name)
            avg = session.query(func.avg(column_attr)).scalar()
            return avg

    def find_max_value(self, column_name):
        with self.Session(self.engine) as session:
            column_attr = getattr(Banana, column_name)
            max_row = session.query(Banana).order_by(column_attr.desc()).first()
            return max_row

    def find_min_value(self, column_name):
        with self.Session(self.engine) as session:
            column_attr = getattr(Banana, column_name)
            min_row = session.query(Banana).order_by(column_attr.asc()).first()
            return min_row


