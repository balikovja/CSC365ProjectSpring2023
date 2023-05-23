import sqlalchemy as sa

def load_csv(engine : sa.Engine, filename, table_and_cols):
	with open(filename, "r") as file:
		conn = engine.raw_connection()
		cursor = conn.cursor()
		cmd = f"COPY {table_and_cols} FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
		cursor.copy_expert(cmd, file)
		conn.commit()

def load_transactions(engine):
	tc = "transactions (user_id, category_id, transaction_date, place, amount, tag_id, note)"
	load_csv(engine, "test/test_data/transactions.csv", tc)


def load_budgets(engine):
	tc = "budgets (user_id, budget_amount, category_id, start_date, end_date, period_type_id)"
	load_csv(engine, "test/test_data/budgets.csv", tc)


