import os
from flask import Flask, render_template_string
from db import init_db, close_db, get_db
from sites import bp as sites_bp
from workers import bp as workers_bp
from attendance import bp as attendance_bp
from expenses import bp as expenses_bp
from material_register import bp as material_register_bp

app = Flask(__name__)
# database path placed at workspace root (one level above this folder)
app.config['DATABASE'] = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'siteledger.db')
)

# Initialize database (creates file and tables if missing)
init_db(app)

# Register teardown to close DB connections
app.teardown_appcontext(close_db)

# Register blueprints
app.register_blueprint(sites_bp)
app.register_blueprint(workers_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(expenses_bp)
app.register_blueprint(material_register_bp)

@app.route('/')
def home():
    template = """
    <html>
    <head>
        <title>SiteLedger</title>
        <style>
            body{
                font-family: Arial;
                background:#f4f6f8;
                padding:30px;
            }

            .card{
                background:white;
                padding:20px;
                margin:10px;
                border-radius:10px;
                box-shadow:0 0 10px rgba(0,0,0,0.1);
            }

            h1{
                color:#0d47a1;
            }
        </style>
    </head>

    <body>

    <h1>🏗 SiteLedger</h1>
    <p><a href="/sites">View Sites</a> | <a href="/workers">View Workers</a> | <a href="/attendance">View Attendance</a> | <a href="/expenses">View Expenses</a> | <a href="/material-register">Material Register</a></p>

    <div class="card">
        <h3>Active Sites</h3>
        <h2>{{ active_sites }}</h2>
    </div>

    <div class="card">
        <h3>Workers Today</h3>
        <h2>{{ workers_today }}</h2>
    </div>

    <div class="card">
        <h3>Today's Expense</h3>
        <h2>₹{{ todays_expense }}</h2>
    </div>

    <div class="card">
        <h3>Total Expenses</h3>
        <h2>₹{{ total_expenses }}</h2>
    </div>

    </body>
    </html>
    """

    db = get_db()
    active_sites = db.execute('SELECT COUNT(*) FROM sites').fetchone()[0]
    workers_today = db.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = date('now') AND status = 'Present'"
    ).fetchone()[0]
    todays_expense = db.execute(
        "SELECT IFNULL(SUM(amount), 0) FROM expenses WHERE date = date('now')"
    ).fetchone()[0]
    total_expenses = db.execute(
        "SELECT IFNULL(SUM(amount), 0) FROM expenses"
    ).fetchone()[0]

    return render_template_string(template,
                                 active_sites=active_sites,
                                 workers_today=workers_today,
                                 todays_expense=todays_expense,
                                 total_expenses=total_expenses)

if __name__ == "__main__":
    app.run(debug=True)
    