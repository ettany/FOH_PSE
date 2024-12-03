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

- Password hashing, CAPTCHA and optional face recognition login for account security​

- Working database with user, portfolio, and eventLog tables​

- Separate administration dashboard with privileges for creating and deleting user accounts

- <b>Portfolio page ​</b>

    - displays user balance and stock portfolio

    - graph of profit

- <b>Trade page </b>

  - displaying updated stock prices for 5 stocks with a table and graph​

  - ability to search for a specific stock and display its details​

  - ability to buy, sell, or adjust stock​s

  - graph of searched stock's performance over the last 30 days
 <img width="500" alt="Screenshot 2024-10-29 at 11 25 47 AM" src="https://github.com/user-attachments/assets/f0ba1be4-36a2-49d3-adcc-21b5caa0a401">
    

- <b>Log page​ </b>

    - table log of activities with details for: buy, sell, scheduled buy/sell, logging on, logging out
 
# Developing the product to ensure compatibility:​

Python & Flask (backend)​

SQL (database schema)​

Frontend (HTML, CSS, JavaScript)​

API: yahoo finance
## Install dependencies

See requirements.txt files in frontend and backend for libraries and dependencies


## Running backend
export FLASK_APP=backend/app

flask init-db

flask --app backend/server.py run

## Running frontend
python frontend/interface.py

## MIDSEMESTER DEMO
https://www.youtube.com/watch?v=jCZ426may-Q 

## FINAL DEMO
TBC
