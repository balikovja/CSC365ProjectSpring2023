<h1 align="center">
  💲💸 iBudgetlyify365 💸💲
</h1>

<div align="center">
  DEPRECATED: This project was hosted for free on Vercel but is no longer in use. This Github remains available to showcase the code.
</div>

<div align="center">
  <a href="https://github.com/balikovja/iBudgetlyify365/issues/new?assignees=&labels=bug&template=01_BUG_REPORT.md&title=bug%3A+">Report a Bug</a>
  ·
  <a href="https://github.com/balikovja/iBudgetlyify365/issues/new?assignees=&labels=enhancement&template=02_FEATURE_REQUEST.md&title=feat%3A+">Request a Feature</a>
</div>

<div align="center">
<br />

![Website](https://img.shields.io/website?down_message=offline&up_message=online&url=https%3A%2F%2Fibudgetlyify365.vercel.app%2Fdocs)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/balikovja/iBudgetlyify365?color=0ec0ac)
![GitHub Sponsors](https://img.shields.io/github/sponsors/balikovja?color=blueviolet)

</div>

<details open="open">
<summary>Table of Contents</summary>

- [About](#about)
  - [Built By](#built-by)
- [Getting Started](#getting-started)
  - [Usage](#usage)
    - [API Link/URL](#api-linkurl)
    - [API Endpoints](#endpoints)
  - [Development](#development)
- [Acknowledgements/Resources](#acknowledgementsresources)

</details>

---

## About

<table>
<tr>
<td>

This API provides users with a way to manage their finances and budgets. With functionalities for account creation and login, budget creation, transaction tracking, and tag creation users are able to neatly manage the amounts of money they want to spend in certain categories during certain time periods, all while keeping track of what they have already spent in the past. The API is designed to be simple to use and support automatic population of transactions without user interaction.
  
</td>
</tr>
</table>

The API is built with FastAPI and SqlAlchemy and connects to a postgres database for persistence. It is hosted on Vercel.

### Built By

Jacob Balikov - jbalikov@calpoly.edu  
Jake Alt - joalt@calpoly.edu
  
## Getting Started

Create a user with the accounts endpoint and then log in. Use the access token provided at login when querying other endpoints. The token will expire in 15 minutes or less.


### Usage
 
The iBudgetlyify API is available [HERE](https://ibudgetlyify365.vercel.app)
for free use and is open to developers (through PRs)

#### API Link/URL

The link for the iBudgetlyify API is available at the top right of this GitHub repository and also [HERE](https://ibudgetlyify365.vercel.app)

#### Endpoints
There are 4 categories of endpoints in the API:
- Access Control: Create users and log in or out.
- Transactions: Enter, edit, and search for your transactions
- Tags: Add tags for personalized categorization of transactions
- Budgets: Define budgets specifying the target spending amounts for certain time periods. Budgets are defined per-category and can be repeated on a weekly, fortnightly, monthly, quarterly, or annual basis.


#### Documentation

Further documentation on the iBudgetlyify API is available [HERE](https://ibudgetlyify365.vercel.app/docs)

## Development

This project is open to outside developers using GitHub's pull request feature. If you plan to contribute, we recommend creation of a local database mimicking the iBudgetlyify database as we will not make any key/.env available for security reasons. You can do that for free through [Supabase](https://supabase.com).

### DB Migrations
Database migrations are performend with alembic. Install alembic, run `alembic upgrade head`, and enter an admin connection URL to bring up the schema.

### Testing
Tests are run with the pytest package. This requires a backing database connection.


## Acknowledgements/Resources

This project was created using a multitude of resources:
- [Supabase](https://supabase.com)
- [Pycharm](https://www.jetbrains.com/pycharm/)
- [Docker](https://www.docker.com)
- [Vercel](https://vercel.com)
- [GitHub README.md Template](https://github.com/dec0dOS/amazing-github-template)
- [Shields.io](https://shields.io)
- [Faker](https://fakerjs.dev)

Built for the CSC 365 databases course at Cal Poly SLO. 🌴

We'd also like to thank Lucas Pierce for his help/mentoring in the creation of this API
