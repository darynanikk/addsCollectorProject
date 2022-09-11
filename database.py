import os

from peewee import PostgresqlDatabase, Model, CharField, TextField, DateField


pg_db = PostgresqlDatabase('db', user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'),
                           host=os.getenv('DB_LOCALHOST'), port=5432)


class Add(Model):
    title = CharField()
    image = CharField()
    location = CharField()
    date_posted = DateField()
    description = TextField()
    currency = CharField()
    number_of_beds = CharField()

    class Meta:
        database = pg_db
