# Technical Specifications for Our API, iBudgetlyify365

User stories/User requirements. Describe the flows that users will go through and how they will interact with the application.
-  As a budgeteer, can record transactions and label those transactions under specific budgetting categories
-  As a budgeteer, can remove existing transactions that they've created
-  As a budgeteer, can enter total monthly income, and split this income into category limits
-  As a budgeteer, can view a summary of all of their budgetting categories
-  As a budgeteer, can view specific budget categories
-  As a budgeteer, can view previous month's budgets


Documentation on what endpoints you will create. This should be at the same level of detail as what I provided in Assignment 1.  
**[POST] /add_transaction**
- categoryID: int
- location: str
- date: date
- amount: decimal

**[DELETE] /remove_transaction**
- transactionID

**[PUT] /define_income**
- income: int
- pay_date: date

**[POST] /define_budgets**
- This endpoint adds budget instances for each specified category.
    * `start_date`: The start of this budget period.
    * `end_date`: The end of this budget period.
    * `amount`: How much money.
    * `period_id`: The period id defined for this budget (1: Weekly, 4: Quarterly, etc.)
    

**[GET] /transactions/{optional params: transactionID, category, location, timespan, amount, sort}**
- list of [
    - transactionID: int
    - category: int
    - location: str
    - date: date
    - amount: decimal
]
- total: decimal

**[GET] /categories/**
- list of [
   - id: int
   - name: str
]

**[GET] /budget_summary/{params: month/year}**
- list of [
    - category_name: str
    - budget: decimal
    - spent: decimal
]

**[GET] /my_current_budget/**
- This endpoint returns your configured budgeting categories. For each category it returns:
    * `category_name`: The name of the category.
    * `allotment`: This category's budget allotment.
    * `spent`: How much of the allotment has already been spent.
    * `start_date`: The start date of the curent period for this category.
    * `end_date`: The end date of the curent period for this category.
    * `period`: The period defined for this budget (Weekly, Quarterly, etc.)


Detailed descriptions of edge cases and transaction flows. For example, if the app has a credit card checkout, describe what happens if the credit card transaction fails, what happens if the user tries to cancel mid-way through, etc.

- If someone attempts to add a transaction with an invalid category it will not add it and will give an error message 
- If someone attempts to remove a transaction with an invalid transactionID it won't remove anything and will give an error message
- If someone defines a budget where the sum of category values exceeds their income, an error message will appear, if it's
  less than their income, a warning message will appear
