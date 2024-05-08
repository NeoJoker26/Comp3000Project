import datetime
import os
import subprocess

from sqlalchemy import create_engine, func, text, inspect, column, alias, MetaData, Table, select
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from models import Banana
from models import RDM

Base = declarative_base()

""" this is where all the crud happens, i initialise the db with the url, i then have the option to call on the CRUD
with main.py from models
This class basically provides different methods to interact with the database, it will
create, read, update, delete, get table name, get column names, get bottom/top 100 fields from a column
count the records, calc the average, find the min and max value in a column
Seems simple but this took TIME, the documentation for SQLAlchemy is really awful and i dont wish the pain of trying
to understand it from 1.4 to 2.0 
Hand written scripts may be easier for someone who has never used SQL before or doesnt know how to exectue scripts or 
simply is just lazy
More scripts can be written if the code ever becomes a large scale application 
"""


class DatabaseHandler:
    def __init__(self, db_url):
        # init the database handler with the url in windowmaker
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

    def setup_replication(self):
        # high availability
        try:
            # create db command
            subprocess.run(["createdb", "replicated_database"])
            with open("postgresql.conf", "a") as conf_file:
                # open conf file and set to replica (enable replication basically)
                conf_file.write("\n# Replication settings\n")
                conf_file.write("wal_level = replica\n")
                conf_file.write("max_wal_senders = 10\n")
                conf_file.write("wal_keep_size = 1GB\n")

            with self.engine.connect() as conn:
                # postgres replication
                conn.execute(text("SELECT * FROM pg_create_physical_replication_slot('replicated_database');"))

            subprocess.run(["pg_ctl", "-D", "/path/to/standby/data", "start"])

            print("Database replication setup completed.")
        except Exception as e:
            print(f"Error setting up database replication: {str(e)}")

    def perform_backup(self):
        try:
            # Execute pg_dump command to create a dump of the dissertation database
            backup_file = "dissertation_backup.sql"
            subprocess.run(["pg_dump", "dissertation", "-f", backup_file])

            compressed_file = "dissertation_backup.tar.gz"
            subprocess.run(["tar", "-czvf", compressed_file, backup_file])

            # Generate a random encryption key
            encryption_key = os.urandom(32)

            # Encrypt the backup file using AES-256-GCM
            encrypted_file = f"{compressed_file}.enc"
            subprocess.run(
                ["openssl", "enc", "-aes-256-gcm", "-salt", "-in", compressed_file, "-out", encrypted_file,
                 "-pass", f"pass:{encryption_key.hex()}"]
            )

            # Generate a checksum of the encrypted backup file
            checksum = subprocess.check_output(["sha256sum", encrypted_file]).decode().split()[0]

            secure_location = "/path/to/secure/backup/location"
            subprocess.run(["mv", encrypted_file, secure_location])

            # Store the encryption key and checksum securely
            key_location = "/path/to/secure/key/location"
            with open(os.path.join(key_location, "encryption_key.txt"), "w") as key_file:
                key_file.write(encryption_key.hex())
            with open(os.path.join(key_location, "backup_checksum.txt"), "w") as checksum_file:
                checksum_file.write(checksum)

            print("Database backup completed.")
        except Exception as e:
            print(f"Error performing database backup: {str(e)}")

    def create_rdm(self, service_name, ip_address, port, service_type, resource_availability):
        with self.Session() as session:
            rdm = RDM(
                service_name=service_name,
                ip_address=ip_address,
                port=port,
                service_type=service_type,
                resource_availability=resource_availability
            )
            session.add(rdm)
            session.commit()
            return rdm.id

    def get_rdm_by_id(self, rdm_id):
        with self.Session() as session:
            return session.query(RDM).filter_by(id=rdm_id).first()

    def get_all_rdms(self):
        with self.Session() as session:
            return session.query(RDM).all()

    def update_rdm(self, rdm_id, **kwargs):
        with self.Session() as session:
            rdm = session.query(RDM).filter_by(id=rdm_id).first()
            if rdm:
                for key, value in kwargs.items():
                    setattr(rdm, key, value)
                rdm.timestamp = datetime.datetime.now()
                session.commit()
                return True
            return False

    def delete_rdm(self, rdm_id):
        with self.Session() as session:
            rdm = session.query(RDM).filter_by(id=rdm_id).first()
            if rdm:
                session.delete(rdm)
                session.commit()
                return True
            return False