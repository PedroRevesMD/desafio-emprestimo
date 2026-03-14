import sqlite3
import json
from datetime import datetime
from app.models.schemas import CustomerInput, LoanResponse

DB_PATH = "loans.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            request_body TEXT,
            response_body TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_request_response(request: CustomerInput, response: LoanResponse):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO loan_logs (request_body, response_body)
        VALUES (?, ?)
    ''', (
        request.model_dump_json(),
        response.model_dump_json()
    ))
    conn.commit()
    conn.close()
