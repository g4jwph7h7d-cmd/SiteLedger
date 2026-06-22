from flask import Blueprint, render_template_string, request, redirect, url_for, jsonify
from db import get_db

bp = Blueprint('labour_payment', __name__)


def get_workers():
    db = get_db()
    return db.execute('SELECT id, worker_name, daily_wage FROM workers ORDER BY worker_name').fetchall()


def calculate_worker_wages(worker_id, end_date=None):
    """Calculate total wages earned by worker from attendance records"""
    db = get_db()
    
    if end_date:
        rows = db.execute(
            '''SELECT a.status, a.overtime_hours, w.daily_wage FROM attendance a
               JOIN workers w ON a.worker_id = w.id
               WHERE a.worker_id = ? AND a.date <= ? 
               ORDER BY a.date DESC''',
            (worker_id, end_date)
        ).fetchall()
    else:
        rows = db.execute(
            '''SELECT a.status, a.overtime_hours, w.daily_wage FROM attendance a
               JOIN workers w ON a.worker_id = w.id
               WHERE a.worker_id = ? 
               ORDER BY a.date DESC''',
            (worker_id,)
        ).fetchall()
    
    total_wages = 0
    for row in rows:
        wage = row['daily_wage'] or 0
        if row['status'] == 'Present':
            base = wage
        elif row['status'] == 'Half Day':
            base = wage * 0.5
        else:
            base = 0
        overtime = (wage / 8.0) * (row['overtime_hours'] or 0)
        total_wages += base + overtime
    
    return round(total_wages, 2)


def calculate_payments_sum(worker_id, end_date=None):
    """Calculate total amount paid to worker"""
    db = get_db()
    
    if end_date:
        result = db.execute(
            'SELECT IFNULL(SUM(amount_paid), 0) FROM labour_payment WHERE worker_id = ? AND date <= ?',
            (worker_id, end_date)
        ).fetchone()
    else:
        result = db.execute(
            'SELECT IFNULL(SUM(amount_paid), 0) FROM labour_payment WHERE worker_id = ?',
            (worker_id,)
        ).fetchone()
    
    return round(result[0], 2) if result else 0


def calculate_advance_sum(worker_id, end_date=None):
    """Calculate total advance deductions for worker"""
    db = get_db()
    
    if end_date:
        result = db.execute(
            'SELECT IFNULL(SUM(advance_deduction), 0) FROM labour_payment WHERE worker_id = ? AND date <= ?',
            (worker_id, end_date)
        ).fetchone()
    else:
        result = db.execute(
            'SELECT IFNULL(SUM(advance_deduction), 0) FROM labour_payment WHERE worker_id = ?',
            (worker_id,)
        ).fetchone()
    
    return round(result[0], 2) if result else 0


def calculate_balance(worker_id, end_date=None):
    """Calculate balance payable"""
    total_wages = calculate_worker_wages(worker_id, end_date)
    total_paid = calculate_payments_sum(worker_id, end_date)
    total_advance = calculate_advance_sum(worker_id, end_date)
    
    balance = total_wages - total_paid - total_advance
    return round(balance, 2)


@bp.route('/labour-payment')
def list_payments():
    db = get_db()
    cur = db.execute(
        '''
        SELECT lp.id, lp.date, w.worker_name, lp.amount_paid, lp.advance_deduction, lp.remarks
        FROM labour_payment lp
        JOIN workers w ON lp.worker_id = w.id
        ORDER BY lp.date DESC, lp.id DESC
        '''
    )
    records = cur.fetchall()

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Labour Payment - SiteLedger</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {
                --primary-color: #0d47a1;
                --secondary-color: #1565c0;
                --accent-color: #ff6f00;
            }
            body { background-color: #f8f9fa; }
            .navbar-custom { background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%); }
            .nav-link { color: rgba(255,255,255,0.8) !important; }
            .nav-link:hover { color: white !important; }
            .section-title { color: var(--primary-color); font-weight: 700; border-bottom: 3px solid var(--accent-color); }
            table { border-collapse: collapse; }
            tbody tr { transition: background-color 0.2s ease; }
            tbody tr:hover { background-color: #f0f4ff; }
            .btn-primary-custom { background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%)); border: none; }
            .btn-primary-custom:hover { background: var(--primary-color); }
            .btn-report { background: #28a745; border: none; }
            .btn-report:hover { background: #218838; }
            .footer-custom { background: var(--primary-color); color: white; }
        </style>
    </head>
    <body>
        <!-- Navbar -->
        <nav class="navbar navbar-expand-lg navbar-custom sticky-top">
            <div class="container-fluid">
                <a class="navbar-brand" href="/"><i class="fas fa-building me-2"></i>SiteLedger</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item"><a class="nav-link" href="/"><i class="fas fa-home me-1"></i>Dashboard</a></li>
                        <li class="nav-item"><a class="nav-link" href="/labour-payment"><i class="fas fa-money-bill me-1"></i>Payments</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container-fluid py-5">
            <div class="container">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1 class="section-title mb-0"><i class="fas fa-money-bill-wave me-2"></i>Labour Payments</h1>
                    <div>
                        <a href="/labour-payment/add" class="btn btn-primary-custom me-2"><i class="fas fa-plus me-2"></i>Add Payment</a>
                        <a href="/labour-payment/report" class="btn btn-report"><i class="fas fa-chart-bar me-2"></i>View Report</a>
                    </div>
                </div>

                <div class="card border-0 shadow-sm">
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th><i class="fas fa-hashtag me-2"></i>ID</th>
                                        <th><i class="fas fa-calendar me-2"></i>Date</th>
                                        <th><i class="fas fa-user me-2"></i>Worker</th>
                                        <th><i class="fas fa-hand-holding-usd me-2"></i>Amount Paid</th>
                                        <th><i class="fas fa-percent me-2"></i>Advance Deduction</th>
                                        <th><i class="fas fa-note-sticky me-2"></i>Remarks</th>
                                    </tr>
                                </thead>
                                <tbody>
                                {% for r in records %}
                                    <tr>
                                        <td><span class="badge bg-primary">{{ r['id'] }}</span></td>
                                        <td>{{ r['date'] }}</td>
                                        <td><strong>{{ r['worker_name'] }}</strong></td>
                                        <td><span class="text-success fw-bold">₹{{ "%.2f"|format(r['amount_paid']) }}</span></td>
                                        <td><span class="text-warning">₹{{ "%.2f"|format(r['advance_deduction']) }}</span></td>
                                        <td>{{ r['remarks'] or '-' }}</td>
                                    </tr>
                                {% else %}
                                    <tr><td colspan="6" class="text-center py-4"><i class="fas fa-inbox me-2"></i>No payment records yet.</td></tr>
                                {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="footer-custom text-center py-4 mt-5">
            <p class="mb-0">&copy; 2024 SiteLedger. All rights reserved.</p>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

    return render_template_string(template, records=records)


@bp.route('/labour-payment/add', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        date = request.form.get('date')
        worker_id = request.form.get('worker_id')
        amount_paid = request.form.get('amount_paid') or 0
        advance_deduction = request.form.get('advance_deduction') or 0
        remarks = request.form.get('remarks')

        db = get_db()
        db.execute(
            '''INSERT INTO labour_payment (date, worker_id, amount_paid, advance_deduction, remarks) 
               VALUES (?,?,?,?,?)''',
            (date, worker_id, amount_paid, advance_deduction, remarks)
        )
        db.commit()
        return redirect(url_for('labour_payment.list_payments'))

    workers = get_workers()

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Labour Payment - SiteLedger</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {
                --primary-color: #0d47a1;
                --secondary-color: #1565c0;
                --accent-color: #ff6f00;
            }
            body { background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 100%); min-height: 100vh; }
            .navbar-custom { background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%)); }
            .nav-link { color: rgba(255,255,255,0.8) !important; }
            .nav-link:hover { color: white !important; }
            .form-card { background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            .form-header { background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%)); color: white; padding: 24px; border-radius: 12px 12px 0 0; }
            .form-header h2 { margin: 0; font-weight: 700; }
            .form-label { font-weight: 600; color: var(--primary-color); }
            .form-control:focus, .form-select:focus { border-color: var(--secondary-color); box-shadow: 0 0 0 0.2rem rgba(21, 101, 192, 0.25); }
            .btn-submit { background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%)); border: none; font-weight: 600; }
            .btn-submit:hover { background: var(--primary-color); }
            .worker-summary { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)); border-left: 5px solid var(--secondary-color); border-radius: 8px; }
            .summary-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(0,0,0,0.1); }
            .summary-row:last-child { border-bottom: none; }
            .summary-label { font-weight: 600; color: #555; }
            .summary-value { font-size: 18px; font-weight: 700; color: var(--primary-color); }
            .balance-value { color: #d32f2f; font-size: 20px; }
            .footer-custom { background: var(--primary-color); color: white; }
        </style>
    </head>
    <body>
        <!-- Navbar -->
        <nav class="navbar navbar-expand-lg navbar-custom sticky-top">
            <div class="container-fluid">
                <a class="navbar-brand" href="/"><i class="fas fa-building me-2"></i>SiteLedger</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item"><a class="nav-link" href="/"><i class="fas fa-home me-1"></i>Dashboard</a></li>
                        <li class="nav-item"><a class="nav-link" href="/labour-payment"><i class="fas fa-money-bill me-1"></i>Payments</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-lg-7 col-md-9">
                    <div class="form-card">
                        <div class="form-header">
                            <h2><i class="fas fa-money-bill-wave me-2"></i>Record Labour Payment</h2>
                        </div>
                        <div class="card-body p-4">
                            <form method="post" id="paymentForm">
                                <div class="mb-4">
                                    <label for="worker_id" class="form-label"><i class="fas fa-user me-2"></i>Select Worker *</label>
                                    <select class="form-select form-select-lg" id="workerSelect" name="worker_id" required onchange="updateWorkerInfo()">
                                        <option value="">-- Choose a Worker --</option>
                                        {% for w in workers %}
                                            <option value="{{ w['id'] }}" data-wage="{{ w['daily_wage'] }}">{{ w['worker_name'] }}</option>
                                        {% endfor %}
                                    </select>
                                </div>

                                <!-- Worker Summary -->
                                <div id="workerInfo" class="worker-summary p-4 mb-4" style="display:none">
                                    <h5 class="mb-3"><i class="fas fa-chart-pie me-2"></i>Worker Payment Summary</h5>
                                    <div class="summary-row">
                                        <span class="summary-label"><i class="fas fa-coins me-2"></i>Total Wages Earned:</span>
                                        <span class="summary-value">₹<span id="totalWages">0.00</span></span>
                                    </div>
                                    <div class="summary-row">
                                        <span class="summary-label"><i class="fas fa-check-circle me-2"></i>Total Already Paid:</span>
                                        <span class="summary-value">₹<span id="totalPaid">0.00</span></span>
                                    </div>
                                    <div class="summary-row">
                                        <span class="summary-label"><i class="fas fa-minus-circle me-2"></i>Total Advances:</span>
                                        <span class="summary-value">₹<span id="totalAdvance">0.00</span></span>
                                    </div>
                                    <div class="summary-row">
                                        <span class="summary-label"><i class="fas fa-balance-scale me-2"></i>Balance Payable:</span>
                                        <span class="summary-value balance-value">₹<span id="balance">0.00</span></span>
                                    </div>
                                </div>

                                <hr>

                                <div class="mb-3">
                                    <label for="date" class="form-label"><i class="fas fa-calendar me-2"></i>Payment Date</label>
                                    <input type="date" class="form-control form-control-lg" id="date" name="date" required>
                                </div>

                                <div class="mb-3">
                                    <label for="amount_paid" class="form-label"><i class="fas fa-money-bill me-2"></i>Amount Paid (₹)</label>
                                    <input type="number" step="0.01" class="form-control form-control-lg" id="amount_paid" name="amount_paid" required placeholder="Enter payment amount">
                                </div>

                                <div class="mb-3">
                                    <label for="advance_deduction" class="form-label"><i class="fas fa-minus me-2"></i>Advance Deduction (₹)</label>
                                    <input type="number" step="0.01" class="form-control form-control-lg" id="advance_deduction" name="advance_deduction" value="0" placeholder="Leave empty if no advance">
                                </div>

                                <div class="mb-4">
                                    <label for="remarks" class="form-label"><i class="fas fa-note-sticky me-2"></i>Remarks</label>
                                    <textarea class="form-control" id="remarks" name="remarks" rows="3" placeholder="Optional notes..."></textarea>
                                </div>

                                <div class="d-grid gap-2 d-md-flex">
                                    <button type="submit" class="btn btn-submit btn-lg flex-grow-1"><i class="fas fa-save me-2"></i>Save Payment</button>
                                    <a href="/labour-payment" class="btn btn-secondary btn-lg"><i class="fas fa-arrow-left me-2"></i>Back</a>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="footer-custom text-center py-4 mt-5">
            <p class="mb-0">&copy; 2024 SiteLedger. All rights reserved.</p>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            function updateWorkerInfo() {
                const workerSelect = document.getElementById('workerSelect');
                const workerId = workerSelect.value;
                
                if (!workerId) {
                    document.getElementById('workerInfo').style.display = 'none';
                    return;
                }
                
                fetch('/labour-payment/worker-info/' + workerId)
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('totalWages').textContent = data.total_wages.toFixed(2);
                        document.getElementById('totalPaid').textContent = data.total_paid.toFixed(2);
                        document.getElementById('totalAdvance').textContent = data.total_advance.toFixed(2);
                        document.getElementById('balance').textContent = data.balance.toFixed(2);
                        document.getElementById('workerInfo').style.display = 'block';
                    });
            }
        </script>
    </body>
    </html>
    """

    return render_template_string(template, workers=workers)


@bp.route('/labour-payment/worker-info/<int:worker_id>')
def get_worker_info(worker_id):
    total_wages = calculate_worker_wages(worker_id)
    total_paid = calculate_payments_sum(worker_id)
    total_advance = calculate_advance_sum(worker_id)
    balance = calculate_balance(worker_id)
    
    return jsonify({
        'total_wages': total_wages,
        'total_paid': total_paid,
        'total_advance': total_advance,
        'balance': balance
    })


@bp.route('/labour-payment/report')
def payment_report():
    workers = get_workers()
    db = get_db()
    
    report_data = []
    for worker in workers:
        worker_id = worker['id']
        total_wages = calculate_worker_wages(worker_id)
        total_paid = calculate_payments_sum(worker_id)
        total_advance = calculate_advance_sum(worker_id)
        balance = calculate_balance(worker_id)
        
        # Get payment history
        payments = db.execute(
            '''SELECT date, amount_paid, advance_deduction, remarks 
               FROM labour_payment WHERE worker_id = ? 
               ORDER BY date DESC''',
            (worker_id,)
        ).fetchall()
        
        report_data.append({
            'worker_name': worker['worker_name'],
            'total_wages': total_wages,
            'total_paid': total_paid,
            'total_advance': total_advance,
            'balance': balance,
            'payments': payments
        })

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Labour Payment Report - SiteLedger</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {
                --primary-color: #0d47a1;
                --secondary-color: #1565c0;
                --accent-color: #ff6f00;
            }
            body { background-color: #f8f9fa; }
            .navbar-custom { background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%)); }
            .nav-link { color: rgba(255,255,255,0.8) !important; }
            .nav-link:hover { color: white !important; }
            .section-title { color: var(--primary-color); font-weight: 700; border-bottom: 3px solid var(--accent-color); }
            .worker-card { background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); overflow: hidden; margin-bottom: 24px; }
            .worker-card-header { background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%)); color: white; padding: 20px; }
            .worker-card-header h5 { margin: 0; font-weight: 700; }
            .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; padding: 20px; }
            .summary-box { background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%)); padding: 16px; border-radius: 8px; border-left: 4px solid var(--primary-color); }
            .summary-label { font-size: 12px; font-weight: 600; color: #666; text-transform: uppercase; margin-bottom: 6px; }
            .summary-value { font-size: 20px; font-weight: 700; color: var(--primary-color); }
            .summary-box.balance .summary-value { color: #d32f2f; }
            .payments-table { margin: 0; }
            tbody tr { transition: background-color 0.2s ease; }
            tbody tr:hover { background-color: #f0f4ff; }
            thead { background-color: #f8f9fa; }
            .no-data { text-align: center; color: #999; padding: 30px; }
            .footer-custom { background: var(--primary-color); color: white; }
        </style>
    </head>
    <body>
        <!-- Navbar -->
        <nav class="navbar navbar-expand-lg navbar-custom sticky-top">
            <div class="container-fluid">
                <a class="navbar-brand" href="/"><i class="fas fa-building me-2"></i>SiteLedger</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item"><a class="nav-link" href="/"><i class="fas fa-home me-1"></i>Dashboard</a></li>
                        <li class="nav-item"><a class="nav-link" href="/labour-payment"><i class="fas fa-money-bill me-1"></i>Payments</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container-fluid py-5">
            <div class="container">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1 class="section-title mb-0"><i class="fas fa-chart-bar me-2"></i>Labour Payment Report</h1>
                    <a href="/labour-payment" class="btn btn-primary" style="background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%)); border: none;"><i class="fas fa-arrow-left me-2"></i>Back to Payments</a>
                </div>

                {% if report_data %}
                    {% for worker in report_data %}
                    <div class="worker-card">
                        <div class="worker-card-header">
                            <h5><i class="fas fa-user-circle me-2"></i>{{ worker['worker_name'] }}</h5>
                        </div>

                        <div class="summary-grid">
                            <div class="summary-box">
                                <div class="summary-label"><i class="fas fa-coins me-1"></i>Total Wages</div>
                                <div class="summary-value">₹{{ "%.2f"|format(worker['total_wages']) }}</div>
                            </div>
                            <div class="summary-box">
                                <div class="summary-label"><i class="fas fa-check-circle me-1"></i>Total Paid</div>
                                <div class="summary-value">₹{{ "%.2f"|format(worker['total_paid']) }}</div>
                            </div>
                            <div class="summary-box">
                                <div class="summary-label"><i class="fas fa-minus-circle me-1"></i>Total Advance</div>
                                <div class="summary-value">₹{{ "%.2f"|format(worker['total_advance']) }}</div>
                            </div>
                            <div class="summary-box balance">
                                <div class="summary-label"><i class="fas fa-balance-scale me-1"></i>Balance Payable</div>
                                <div class="summary-value">₹{{ "%.2f"|format(worker['balance']) }}</div>
                            </div>
                        </div>

                        {% if worker['payments'] %}
                        <div class="px-4 pb-3">
                            <h6 class="mb-3"><i class="fas fa-history me-2"></i>Payment History</h6>
                            <div class="table-responsive">
                                <table class="table table-hover payments-table mb-0">
                                    <thead>
                                        <tr>
                                            <th><i class="fas fa-calendar me-2"></i>Date</th>
                                            <th><i class="fas fa-hand-holding-usd me-2"></i>Amount Paid</th>
                                            <th><i class="fas fa-percent me-2"></i>Advance Deduction</th>
                                            <th><i class="fas fa-note-sticky me-2"></i>Remarks</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                    {% for payment in worker['payments'] %}
                                        <tr>
                                            <td>{{ payment['date'] }}</td>
                                            <td><span class="badge bg-success">₹{{ "%.2f"|format(payment['amount_paid']) }}</span></td>
                                            <td><span class="badge bg-warning">₹{{ "%.2f"|format(payment['advance_deduction']) }}</span></td>
                                            <td>{{ payment['remarks'] or '-' }}</td>
                                        </tr>
                                    {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        {% else %}
                        <div class="no-data">
                            <i class="fas fa-inbox fa-3x mb-3" style="color: #ccc;"></i>
                            <p>No payment records yet.</p>
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                {% else %}
                <div class="alert alert-info text-center py-4">
                    <i class="fas fa-info-circle me-2"></i>No worker data available.
                </div>
                {% endif %}
            </div>
        </div>

        <footer class="footer-custom text-center py-4 mt-5">
            <p class="mb-0">&copy; 2024 SiteLedger. All rights reserved.</p>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

    return render_template_string(template, report_data=report_data)
