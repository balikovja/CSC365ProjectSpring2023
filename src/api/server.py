from fastapi import FastAPI
from src.api import pkg_util, budget, transactions, tags, users

description = """
iBudgetlyify365 API allows for the development of personal budgets
along with analytics on budgeting trends.

## Budgets

You can:
* **Define an income**
* **Define a budget**
* **Add transactions**
* **Remove Transactions**
* **Get transactions (with filtering options)**
* **View budgeting categories**
* **View budget summaries**
"""
tags_metadata = [
    {
        "name": "transactions",
        "description": "Access/Edit/Upload information on transactions in our database.",
    },
    {
        "name": "tags",
        "description": "Access/Edit/Create information on tags in our database",
    },
]

app = FastAPI(
    title="iBudgetlyify365 API",
    description=description,
    version="0.0.1",
    contact={
        "name": "Jacob Balikov, Jake Alt",
        "email": "jbalikov@calpoly.edu, joalt@calpoly.edu",
    },
    openapi_tags=tags_metadata,
)
app.include_router(budget.router)
app.include_router(transactions.router)
app.include_router(tags.router)
app.include_router(users.router)
app.include_router(pkg_util.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the iBudgetlyify365 API. See /docs for more information."}
