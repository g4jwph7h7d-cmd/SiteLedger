from app import app
from db import get_db

with app.app_context():
    db = get_db()
    active_sites = db.execute('SELECT COUNT(*) FROM sites').fetchone()[0]
    workers_today = db.execute("SELECT COUNT(*) FROM attendance WHERE date = date('now') AND status = 'Present'").fetchone()[0]
    todays_expense = db.execute("SELECT IFNULL(SUM(amount), 0) FROM expenses WHERE date = date('now')").fetchone()[0]
    total_expenses = db.execute('SELECT IFNULL(SUM(amount), 0) FROM expenses').fetchone()[0]
    print('active_sites', active_sites)
    print('workers_today', workers_today)
    print('todays_expense', todays_expense)
    print('total_expenses', total_expenses)
