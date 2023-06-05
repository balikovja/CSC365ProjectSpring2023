import sqlalchemy
from faker import Faker
import random
import decimal
from datetime import datetime
import src.database as db


# Example usage
# generator = FakeDataGenerator()
# generator.insert_data_into_database(1000000)
class FakeDataGenerator:
    def __init__(self):
        self.fake = Faker()
        self.categories = [1, 2, 3, 4, 5, 6, 7, 8]  # Example category IDs
        self.tags = [1, 2, 3, None]  # Example tag IDs
        self.users = [1]  # Example user IDs

    def generate_data(self, num_rows):
        data = []
        for _ in range(num_rows):
            transaction_date = self.fake.date_between(start_date='-1y', end_date='today')
            created_at = self.fake.date_time_between_dates(datetime_start=transaction_date, datetime_end='now')

            row = {
                'created_at': created_at,
                'user_id': random.choice(self.users),
                'category_id': random.choice(self.categories),
                'transaction_date': transaction_date,
                'place': self.fake.company(),
                'amount': decimal.Decimal(random.randrange(1000, 100000)) / 100,  # Example amount range
                'tag_id': random.choice(self.tags),
                'note': self.fake.text(),
            }
            data.append(row)
        return data

    def insert_data_into_database(self, num_rows):
        data = self.generate_data(num_rows)
        with db.engine.begin() as conn:
            conn.execute(sqlalchemy.text("TRUNCATE TABLE public.transactions;"))
            conn.execute(sqlalchemy.text("ALTER SEQUENCE transactions_id_seq RESTART WITH 1;"))
            conn.execute(sqlalchemy.text("""
                SELECT setval('transactions_id_seq', (SELECT max(id) FROM public.transactions));
                """))
            conn.execute(
                sqlalchemy.text("""
                INSERT INTO public.transacti1ons 
                (created_at, user_id, category_id, transaction_date, place, amount, tag_id, note) 
                VALUES (%(created_at)s, %(user_id)s, %(category_id)s, 
                %(transaction_date)s, %(place)s, %(amount)s, %(tag_id)s, %(note)s);
                """),
                data)



