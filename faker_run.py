from test.test_data import FakeDataGenerator as f
import time

def main():
	gen = f.FakeDataGenerator()
	start = time.time()
	gen.clear_tables()
	tc1 = time.time()
	print(f"Tables cleared in {tc1 - start} s")

	gen.insert_user_data(10000)
	tc2 = time.time()
	print(f"Users added in {tc2 - tc1} s")

	gen.insert_tag_data(50000)
	tc3 = time.time()
	print(f"Tags added in {tc3 - tc2} s")

	gen.insert_budget_data(500000)
	tc4 = time.time()
	print(f"Budgets added in {tc4 - tc3} s")

	gen.insert_transaction_data(1000000)
	tc5 = time.time()
	print(f"Transactions added in {tc5 - tc4} s")

	print(f"\nTotal time: {tc5 - start} s\n")

if __name__ == "__main__":
	main()
