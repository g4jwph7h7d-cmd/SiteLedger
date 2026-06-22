import os
from flask import Flask, render_template_string
from .db import init_db, close_db, get_db
from .sites import bp as sites_bp
from .workers import bp as workers_bp
from .attendance import bp as attendance_bp
from .expenses import bp as expenses_bp
from .material_register import bp as material_register_bp
from .labour_payment import bp as labour_payment_bp

app = Flask(__name__)
# database path placed at workspace root
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
app.register_blueprint(labour_payment_bp)

@app.route('/')
def home():
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SiteLedger - Construction Site Management</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {
                --primary-color: #0d47a1;
                --secondary-color: #1565c0;
                --accent-color: #ff6f00;
                --light-bg: #f8f9fa;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--light-bg);
            }
            
            /* Navbar */
            .navbar-custom {
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .navbar-brand {
                font-size: 24px;
                font-weight: 700;
                color: white !important;
            }
            
            .nav-link {
                color: rgba(255,255,255,0.8) !important;
                transition: all 0.3s ease;
                margin: 0 5px;
            }
            
            .nav-link:hover {
                color: white !important;
                transform: translateY(-2px);
            }
            
            /* Dashboard Cards */
            .dashboard-card {
                background: white;
                border: none;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
                overflow: hidden;
            }
            
            .dashboard-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.12);
            }
            
            .card-icon {
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 28px;
                margin-bottom: 15px;
            }
            
            .card-title-small {
                font-size: 14px;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 8px;
            }
            
            .card-value {
                font-size: 32px;
                font-weight: 700;
                color: var(--primary-color);
            }
            
            .card-value.accent {
                color: var(--accent-color);
            }
            
            /* Footer */
            .footer-custom {
                background: var(--primary-color);
                color: white;
                padding: 30px 0;
                margin-top: 50px;
                text-align: center;
            }
            
            .footer-custom a {
                color: rgba(255,255,255,0.8);
                text-decoration: none;
            }
            
            .footer-custom a:hover {
                color: white;
            }
            
            /* Section Title */
            .section-title {
                color: var(--primary-color);
                font-weight: 700;
                margin-bottom: 30px;
                padding-bottom: 15px;
                border-bottom: 3px solid var(--accent-color);
            }
        </style>
    </head>
    <body>
        <!-- Navbar -->
        <nav class="navbar navbar-expand-lg navbar-custom sticky-top">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">
                    <i class="fas fa-building me-2"></i>SiteLedger
                </a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item"><a class="nav-link" href="/sites"><i class="fas fa-map-location-dot me-1"></i>Sites</a></li>
                        <li class="nav-item"><a class="nav-link" href="/workers"><i class="fas fa-users me-1"></i>Workers</a></li>
                        <li class="nav-item"><a class="nav-link" href="/attendance"><i class="fas fa-clipboard-check me-1"></i>Attendance</a></li>
                        <li class="nav-item"><a class="nav-link" href="/expenses"><i class="fas fa-receipt me-1"></i>Expenses</a></li>
                        <li class="nav-item"><a class="nav-link" href="/material-register"><i class="fas fa-boxes me-1"></i>Materials</a></li>
                        <li class="nav-item"><a class="nav-link" href="/labour-payment"><i class="fas fa-money-bill me-1"></i>Payments</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <!-- Main Content -->
        <div class="container-fluid py-5">
            <div class="container">
                <div class="mb-5">
                    <h1 class="section-title"><i class="fas fa-chart-line me-3"></i>Dashboard</h1>
                </div>

                <!-- Dashboard Stats Row -->
                <div class="row g-4 mb-5">
                    <div class="col-lg-3 col-md-6">
                        <div class="dashboard-card p-4">
                            <div class="card-icon">
                                <i class="fas fa-map-pin"></i>
                            </div>
                            <div class="card-title-small">Active Sites</div>
                            <div class="card-value">{{ active_sites }}</div>
                        </div>
                    </div>

                    <div class="col-lg-3 col-md-6">
                        <div class="dashboard-card p-4">
                            <div class="card-icon">
                                <i class="fas fa-user-check"></i>
                            </div>
                            <div class="card-title-small">Workers Today</div>
                            <div class="card-value">{{ workers_today }}</div>
                        </div>
                    </div>

                    <div class="col-lg-3 col-md-6">
                        <div class="dashboard-card p-4">
                            <div class="card-icon">
                                <i class="fas fa-calendar-day"></i>
                            </div>
                            <div class="card-title-small">Today's Expense</div>
                            <div class="card-value accent">₹{{ todays_expense }}</div>
                        </div>
                    </div>

                    <div class="col-lg-3 col-md-6">
                        <div class="dashboard-card p-4">
                            <div class="card-icon">
                                <i class="fas fa-chart-pie"></i>
                            </div>
                            <div class="card-title-small">Total Expenses</div>
                            <div class="card-value">₹{{ total_expenses }}</div>
                        </div>
                    </div>
                </div>

                <!-- Additional Stats Row -->
                <div class="row g-4">
                    <div class="col-lg-3 col-md-6">
                        <div class="dashboard-card p-4">
                            <div class="card-icon">
                                <i class="fas fa-hand-holding-usd"></i>
                            </div>
                            <div class="card-title-small">Wages Paid</div>
                            <div class="card-value">₹{{ total_wages_paid }}</div>
                        </div>
                    </div>

                    <div class="col-lg-3 col-md-6">
                        <div class="dashboard-card p-4">
                            <div class="card-icon">
                                <i class="fas fa-balance-scale"></i>
                            </div>
                            <div class="card-title-small">Balance Payable</div>
                            <div class="card-value accent">₹{{ total_balance_payable }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <footer class="footer-custom mt-5">
            <div class="container">
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <h5><i class="fas fa-building me-2"></i>SiteLedger</h5>
                        <p>Construction Site Management System</p>
                    </div>
                    <div class="col-md-4 mb-3">
                        <h5>Quick Links</h5>
                        <p>
                            <a href="/sites">Sites</a> | 
                            <a href="/workers">Workers</a> | 
                            <a href="/attendance">Attendance</a>
                        </p>
                    </div>
                    <div class="col-md-4 mb-3">
                        <h5>Support</h5>
                        <p><a href="/">Contact Us</a></p>
                    </div>
                </div>
                <hr class="bg-light">
                <p class="mb-0">&copy; 2024 SiteLedger. All rights reserved.</p>
            </div>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
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
    total_wages_paid = db.execute(
        "SELECT IFNULL(SUM(amount_paid), 0) FROM labour_payment"
    ).fetchone()[0]
    
    # Calculate total balance payable across all workers
    from .labour_payment import calculate_balance
    workers = db.execute('SELECT id FROM workers').fetchall()
    total_balance_payable = sum(calculate_balance(w['id']) for w in workers)

    return render_template_string(template,
                                 active_sites=active_sites,
                                 workers_today=workers_today,
                                 todays_expense=todays_expense,
                                 total_expenses=total_expenses,
                                 total_wages_paid=total_wages_paid,
                                 total_balance_payable=total_balance_payable)

if __name__ == "__main__":
    app.run(debug=True)
