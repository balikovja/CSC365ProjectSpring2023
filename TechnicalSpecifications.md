# Technical Specifications for Our API, iBudgetlyify365

User stories/User requirements. Describe the flows that users will go through and how they will interact with the application.
-  Can record transactions and label those transactions under specific budgetting categories
-  Can remove existing transactions that they've created
-  Can enter total monthly income, and split this income into category limits
-  Can view a summary of all of their budgetting categories
-  Can view specific budget categories
-  Can reset their budget for the next month
-  Can view previous month's budgets


Documentation on what endpoints you will create. This should be at the same level of detail as what I provided in Assignment 1.  
**[PUT] /add_transaction**
- categoryID: int
- location: str
- date: date
- amount: decimal

**[PUT] /remove_transaction**
- transactionID

**[PUT] /define_budget**
- income: int
- pay_date: date
- categories: Dictionary where key is category name (str) and value is budget amount for that category (int)

**[GET] /transactions/{optional params: transactionID, category, location, timespan, amount}**
- list of [
    - transactionID: int
    - category: int
    - location: str
    - date: date
    - amount: decimal
]
- total: decimal

**[GET] /budget_categories/**
- list of [
   - categoryID: int
   - category_name: str
]

**[GET] /budget_summary/{params: month/year}**
- list of [
    - category_name: str
    - budget: decimal
    - spent: decimal
]

Detailed descriptions of edge cases and transaction flows. For example, if the app has a credit card checkout, describe what happens if the credit card transaction fails, what happens if the user tries to cancel mid-way through, etc.

- If someone attempts to add a transaction with an invalid category it will not add it and will give an error message 
- If someone attempts to remove a transaction with an invalid transactionID it won't remove anything and will give an error message
- If someone defines a budget where the sum of category values exceeds their income, an error message will appear, if it's
  less than their income, a warning message will appear
