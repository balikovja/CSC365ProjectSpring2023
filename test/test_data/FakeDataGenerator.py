import faker.providers.internet as internetGen
import faker.providers.misc as miscGen
import sqlalchemy
from faker import Faker
import random
import decimal
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel
import bcrypt
import src.api.users
import src.database as db


class UserJson(BaseModel):
    username: str
    password: str

def partition(x, max_block):
    for i in range(0, len(x), max_block):
        yield x[i:i+max_block]

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
            conn.execute(sqlalchemy.text("DELETE FROM budgets;"))
            conn.execute(sqlalchemy.text("DELETE FROM tags;"))
            conn.execute(sqlalchemy.text("DELETE FROM users;"))

    # def generate_user_data(self, num_rows):
    #     self.userData = []
    #     data = []
    #     for _ in range(num_rows):
    #         user = UserJson(username=self.fake.email(), password=self.fake.password())
    #         data.append(user)
    #         self.userData.append(user)
    #     return data

    # def insert_user_data(self, num_rows):
    #     self.users = []
    #     data = self.generate_user_data(num_rows)
    #     print(f"User data generated ({num_rows} rows)")
    #     for userEntry in data:
    #         self.users.append(src.api.users.add_user(userEntry))

    def generate_user_data(self, num_rows):
        self.userData = []
        data = []
        passwords = []

        for _ in range(10):
            pw = self.fake.password()
            pwsalt = bcrypt.gensalt()
            pwhash = bcrypt.hashpw(pw.encode(), pwsalt)
            passwords.append({
                "pw" : pw,
                "salt" : pwsalt.decode(),
                "hash" : pwhash.decode()
            })
        
        data = []
        for _ in range(num_rows):
            pw = random.choice(passwords)
            data.append({
                "username" : self.fake.unique.user_name(),
                "password_hash" : pw["hash"],
                "password_salt" : pw["salt"]
            })
        self.userData = data
        return data

    def insert_user_data(self, num_rows):
        data = self.generate_user_data(num_rows)
        print(f"User data generated ({num_rows} rows)")
        with db.engine.begin() as conn:
            result = conn.execute(sqlalchemy.insert(db.users).values(data).returning(db.users.c.id))
            self.users = [row.id for row in result]

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
        print(f"Tag data generated ({num_rows} rows)")
        with db.engine.begin() as conn:
            conn.execute(sqlalchemy.insert(db.tags).values(data))

    def generate_transaction_data(self, num_rows):
        data = []
        today = datetime.today()
        min_date = today - timedelta(365)
        companies = [self.fake.company() for _ in range(100)]
        for user in self.users:
            with db.engine.begin() as conn:
                result = conn.execute(sqlalchemy.select(db.tags).where(db.tags.c.user_id == user))
                tags = [row.id for row in result]
                if len(tags) == 0:
                    tags = [None]
            for y in range(int(num_rows/len(self.users))):
                transaction_date = self.fake.date_between_dates(min_date, today)
                # created_at = self.fake.date_time_between_dates(datetime_start=transaction_date, datetime_end='now')

                row = {
                    # 'created_at': created_at,
                    'user_id': user,
                    'category_id': random.choice(self.categories),
                    'transaction_date': transaction_date,
                    'place': random.choice(companies),
                    'amount': decimal.Decimal(random.randrange(1000, 100000)) / 100,  # Example amount range
                    'tag_id': random.choice(tags),
                    'note': self.fake.sentence(),
                }
                data.append(row)
        return data

    def insert_transaction_data(self, num_rows):
        data = self.generate_transaction_data(num_rows)
        print(f"Transaction data generated ({num_rows} rows)")
        with db.engine.begin() as conn:
            for data_part in partition(data, 50000):
                conn.execute(sqlalchemy.insert(db.transactions).values(data_part))
                print(".", end="", flush=True)
        print("")

    
    def generate_budget_data(self, num_rows):
        periods = {
            1: relativedelta(weeks=1),
            2: relativedelta(weeks=2),
            3: relativedelta(months=1),
            4: relativedelta(months=3),
            5: relativedelta(years=1)
        }
        data = []
        for user in self.users:
            for category in self.categories:
                # work backwards
                end_date = self.fake.date_between('-30d', '+30d')                
                for _ in range(int(num_rows/len(self.users)/len(self.categories))):
                    p_id = random.choice(list(periods.keys()))
                    start_date = end_date - periods[p_id]
                    row = {
                        'user_id' : user,
                        'budget_amount' : decimal.Decimal(random.randrange(10000, 100000)) / 100 * p_id,
                        'category_id' : category,
                        'start_date' : start_date + relativedelta(days=1),
                        'end_date' : end_date,
                        'period_type_id' : p_id
                    }
                    data.append(row)
                    end_date = start_date
        return data

    def insert_budget_data(self, num_rows):
        data = self.generate_budget_data(num_rows)
        print(f"Budget data generated ({num_rows} rows)")
        with db.engine.begin() as conn:
            for data_part in partition(data, 50000):
                conn.execute(sqlalchemy.insert(db.budgets).values(data_part))
                print(".", end="", flush=True)
        print("")

