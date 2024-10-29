# FOH_PSE
FOH allows users to trade, sell, and adjust stocks whilst managing and viewing their own stock portfolio. FOH will simulate a stock trading platform whilst implementing multi-user login and an administration account.

# Team Members & Roles
Manila Aryal: Activity Log & Password Hashing Lead

Grace Frizzell: Database & Transaction Lead

Tamsyn Evezard: Authentication & API Lead

Ngoc Bui: Visualization & CAPTCHA Lead

Berkan Guven: Facial Recognition Lead

## Accomplished Work
- Username and password authentication for users and admin that maintains session (functionality included in the register, login, and logout pages)​

- Password hashing for account security​

- Working database with user, portfolio, and eventLog tables​

- Portfolio page ​

    - displaying the specific user and their initial balance of $100,000​

    - other hardcoded UI elements for functional visualization​

- Trade page ​

    - displaying updated stock prices for 5 stocks, ​

    - ability to search for a specific stock and display its details​

    - ability to search for a stock and buy or sell an amount of it​

    - graph of a default stock's performance over the last 30 days​

- Log page​

    - Hardcoded UI elements for initial visualization
 
# Developing the product to ensure compatibility:​

Python & Flask (backend)​

SQL (database schema)​

Frontend (HTML, CSS, JavaScript)​

API: yahoo finance

## Running backend
export FLASK_APP=backend/app

flask init-db

flask --app backend/server.py run

## Running frontend
python frontend/interface.py

## MIDSEMESTER DEMO
https://www.youtube.com/watch?v=jCZ426may-Q 

## The final product deliverable should include:

• Source code with compilation instructions (if any) and a list of required libraries.

• Installer script (for Unix/Linux) or installer program (for MS-Windows)

• All document artifacts generated during the software engineering lifecycle

• An Installation Guide

• A User’s Guide (with screen shots)

• A Programmer’s Guide
