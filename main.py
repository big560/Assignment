from fastapi import FastAPI, HTTPException
from helper import generateUserAgent
import time
import json
import requests
import csv
import sqlite3


app = FastAPI()


conn = sqlite3.connect("finance_data.db")
c = conn.cursor()


c.execute("""
    CREATE TABLE IF NOT EXISTS finance_data (
        company TEXT,
        date TEXT,
        open TEXT,
        high REAL,
        low REAL,
        close REAL,
        adj_close REAL,
        volume REAL,
        PRIMARY KEY (company, date)
    );
""")
conn.commit()


header = generateUserAgent()
period2 = time.time()
url = lambda name, period2 : f"https://query1.finance.yahoo.com/v7/finance/download/{name}?period1=1649033696&period2={period2}&interval=1d&events=history&includeAdjustedClose=true"


with open("config.json", 'r') as f:
    config = json.load(f)
    

for company in config['companies']:
    download_url = url(company['name'], int(period2))
    response = requests.get(download_url, headers=header)
    reader = csv.reader(response.content.decode('utf-8').splitlines())
    headers = next(reader)

    for row in reader:
        data = [company['name']] + row
        c.execute("""
            INSERT OR REPLACE INTO finance_data
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
    conn.commit()



@app.get('/api/stocks')
def get_all_stocks(date: str):
    conn = sqlite3.connect('finance_data.db')
    c = conn.cursor()
    c.execute(
        """
        SELECt * FROM finance_data WHERE date=?
        """, (date,)
    )

    data = c.fetchall()
    if not data:
        raise HTTPException(status_code=404, detail="Data not found")
    c.close()
    return [dict(zip(['Date', 'Open', 'High', 'Low', 'Close', 'AdjClose', 'Volume'], row)) for row in data]



@app.get("/api/stocks/{company}")
def get_stocks_by_company(company: str):
    conn = sqlite3.connect('finance_data.db')
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM finance_data WHERE company = ?", (company,))
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(['Date', 'Open', 'High', 'Low', 'Close', 'AdjClose', 'Volume'], row)) for row in rows]


@app.get("/api/stocks/{company}/{date}")
def get_stocks_by_company_and_date(company: str, date: str):
    conn = sqlite3.connect('finance_data.db')
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM finance_data WHERE company = ? AND date = ?", (company, date))
    rows = cur.fetchall()
    conn.close()   
    return [dict(zip(['Date', 'Open', 'High', 'Low', 'Close', 'AdjClose', 'Volume'], row)) for row in rows]


@app.post("/api/stocks/{company}/{date}")
def update_by_date(company: str, date: str, data: dict):
    conn = sqlite3.connect('finance_data.db')
    c = conn.cursor()
    fields = ["open", "high", "low", "close", "adj_close", "volume"]
    values = [data.get(field) for field in fields]
    values = [company, date] + values + [date, company]
    breakpoint()
    c.execute("""
        UPDATE  finance_data SET company = ? , date = ?, open = ?, high = ?, low = ?, close = ?, adj_close = ?, volume = ? WHERE date= ? AND company= ?
    """, values,)
    conn.commit()
    conn.close()
    return {"message": "Data added successfully"}
