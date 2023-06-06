import faker.providers.internet as internetGen
import faker.providers.misc as miscGen
import sqlalchemy
from faker import Faker
import random
import decimal
from datetime import datetime
from pydantic import BaseModel

import src.api.users
import src.database as db


class UserJson(BaseModel):
    username: str
    password: str


# Example usage
# generator = FakeDataGenerator()
# generator.insert_data_into_database(1000000)
class FakeDataGenerator:
    def __init__(self):
        self.fake = Faker()
        self.categories = [1, 2, 3, 4, 5, 6, 7, 8]  # Example category IDs
        self.users = []
        self.userData = []

    def clear_tables(self):
        with db.engine.begin() as conn:
            conn.execute(sqlalchemy.text("DELETE FROM transactions;"))
            conn.execute(sqlalchemy.text("DELETE FROM tags;"))
            conn.execute(sqlalchemy.text("DELETE FROM users;"))

    def generate_user_data(self, num_rows):
        self.userData = []
        data = []
        for _ in range(num_rows):
            user = UserJson(username=self.fake.email(), password=self.fake.password())
            data.append(user)
            self.userData.append(user)
        return data

    def insert_user_data(self, num_rows):
        self.users = []
        data = self.generate_user_data(num_rows)
        for userEntry in data:
            self.users.append(src.api.users.add_user(userEntry))

    def generate_tag_data(self, num_rows):
        data = []
        for _ in range(num_rows):
            tag = {
                "name": self.fake.word(),
                "user_id": random.choice(self.users)
            }
            data.append(tag)
        return data

    def insert_tag_data(self, num_rows):
        data = self.generate_tag_data(num_rows)
        with db.engine.begin() as conn:
            conn.execute(sqlalchemy.insert(db.tags).values(data))

    def generate_transaction_data(self, num_rows):
        data = []
        for x in range(len(self.users)):
            with db.engine.begin() as conn:
                result = conn.execute(sqlalchemy.select(db.tags).where(db.tags.c.user_id == self.users[x]))
                tags = [row.id for row in result]
                if len(tags) == 0:
                    tags = [None]
            for y in range(int(num_rows/len(self.users))):
                transaction_date = self.fake.date_between(start_date='-1y', end_date='today')
                created_at = self.fake.date_time_between_dates(datetime_start=transaction_date, datetime_end='now')

                row = {
                    'created_at': created_at,
                    'user_id': self.users[x],
                    'category_id': random.choice(self.categories),
                    'transaction_date': transaction_date,
                    'place': self.fake.company(),
                    'amount': decimal.Decimal(random.randrange(1000, 100000)) / 100,  # Example amount range
                    'tag_id': random.choice(tags),
                    'note': self.fake.sentence(),
                }
                data.append(row)
        return data

    def insert_transaction_data(self, num_rows):
        data = self.generate_transaction_data(num_rows)
        with db.engine.begin() as conn:
            conn.execute(sqlalchemy.insert(db.transactions).values(data))
