import os
import uuid

from dotenv import load_dotenv
from peewee import PostgresqlDatabase, Model, UUIDField, CharField, TextField, DateField

load_dotenv()

pg_db = PostgresqlDatabase(os.getenv('DB_NAME'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'),
                           host=os.getenv('DB_LOCALHOST'), port=5432)


class Add(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    title = CharField()
    image = CharField()
    location = CharField()
    date_posted = DateField()
    description = TextField()
    currency = CharField()
    number_of_beds = CharField()

    class Meta:
        database = pg_db