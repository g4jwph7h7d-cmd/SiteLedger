from flask import Blueprint, render_template_string, request, redirect, url_for
from .db import get_db

bp = Blueprint('expenses', __name__)


def get_sites():
    db = get_db()
    return db.execute('SELECT id, site_name FROM sites ORDER BY site_name').fetchall()


@bp.route('/expenses')
def list_expenses():
    db = get_db()
    cur = db.execute(
        '''
        SELECT e.id, e.date, s.site_name, e.category, e.amount, e.remarks
        FROM expenses e
        JOIN sites s ON e.site_id = s.id
        ORDER BY e.date DESC, e.id DESC
        '''
    )
    expenses = cur.fetchall()

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Expenses - SiteLedger</title>
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
            .btn-primary-custom { background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%); border: none; }
            .btn-primary-custom:hover { background: var(--primary-color); }
            .footer-custom { background: var(--primary-color); color: white; }
            .category-badge { font-size: 11px; }
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
                        <li class="nav-item"><a class="nav-link" href="/expenses"><i class="fas fa-receipt me-1"></i>Expenses</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container-fluid py-5">
            <div class="container">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1 class="section-title mb-0"><i class="fas fa-receipt me-2"></i>Expense Management</h1>
                    <a href="/expenses/add" class="btn btn-primary-custom"><i class="fas fa-plus me-2"></i>Add Expense</a>
                </div>

                <div class="card border-0 shadow-sm">
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th><i class="fas fa-hashtag me-2"></i>ID</th>
                                        <th><i class="fas fa-calendar me-2"></i>Date</th>
                                        <th><i class="fas fa-map-pin me-2"></i>Site</th>
                                        <th><i class="fas fa-tag me-2"></i>Category</th>
                                        <th><i class="fas fa-money-bill me-2"></i>Amount</th>
                                        <th><i class="fas fa-note-sticky me-2"></i>Remarks</th>
                                    </tr>
                                </thead>
                                <tbody>
                                {% for e in expenses %}
                                    <tr>
                                        <td><span class="badge bg-primary">{{ e['id'] }}</span></td>
                                        <td>{{ e['date'] }}</td>
                                        <td><strong>{{ e['site_name'] }}</strong></td>
                                        <td>
                                            {% if e['category'] == 'Labour' %}
                                                <span class="badge bg-danger category-badge">{{ e['category'] }}</span>
                                            {% elif e['category'] == 'Material' %}
                                                <span class="badge bg-warning text-dark category-badge">{{ e['category'] }}</span>
                                            {% elif e['category'] == 'Transport' %}
                                                <span class="badge bg-info category-badge">{{ e['category'] }}</span>
                                            {% else %}
                                                <span class="badge bg-secondary category-badge">{{ e['category'] }}</span>
                                            {% endif %}
                                        </td>
                                        <td><span class="text-danger fw-bold">₹{{ "%.2f"|format(e['amount']) }}</span></td>
                                        <td>{{ e['remarks'] or '-' }}</td>
                                    </tr>
                                {% else %}
                                    <tr><td colspan="6" class="text-center py-4"><i class="fas fa-inbox me-2"></i>No expenses yet.</td></tr>
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

    return render_template_string(template, expenses=expenses)


@bp.route('/expenses/add', methods=['GET', 'POST'])
def add_expense():
    sites = get_sites()

    if request.method == 'POST':
        date = request.form.get('date')
        site_id = request.form.get('site_id')
        category = request.form.get('category')
        amount = request.form.get('amount')
        remarks = request.form.get('remarks')

        db = get_db()
        db.execute(
            'INSERT INTO expenses (date, site_id, category, amount, remarks) VALUES (?,?,?,?,?)',
            (date, site_id, category, amount, remarks)
        )
        db.commit()
        return redirect(url_for('expenses.list_expenses'))

    template = """
    <html>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Expense - SiteLedger</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {
                --primary-color: #0d47a1;
                --secondary-color: #1565c0;
                --accent-color: #ff6f00;
            }
            body { background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 100%); min-height: 100vh; }
            .navbar-custom { background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%); }
            .nav-link { color: rgba(255,255,255,0.8) !important; }
            .nav-link:hover { color: white !important; }
            .form-card { background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            .form-header { background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%); color: white; padding: 24px; border-radius: 12px 12px 0 0; }
            .form-header h2 { margin: 0; font-weight: 700; }
            .form-label { font-weight: 600; color: var(--primary-color); }
            .form-control:focus { border-color: var(--secondary-color); box-shadow: 0 0 0 0.2rem rgba(21, 101, 192, 0.25); }
            .btn-submit { background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%); border: none; font-weight: 600; }
            .btn-submit:hover { background: var(--primary-color); }
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
                        <li class="nav-item"><a class="nav-link" href="/expenses"><i class="fas fa-receipt me-1"></i>Expenses</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-lg-6 col-md-8">
                    <div class="form-card">
                        <div class="form-header">
                            <h2><i class="fas fa-receipt me-2"></i>Record New Expense</h2>
                        </div>
                        <div class="card-body p-4">
                            <form method="post">
                                <div class="mb-3">
                                    <label for="date" class="form-label"><i class="fas fa-calendar me-2"></i>Date</label>
                                    <input type="date" class="form-control form-control-lg" id="date" name="date" required>
                                </div>

                                <div class="mb-3">
                                    <label for="site_id" class="form-label"><i class="fas fa-map-pin me-2"></i>Site</label>
                                    <select class="form-select form-select-lg" id="site_id" name="site_id" required>
                                        {% for s in sites %}
                                            <option value="{{ s['id'] }}">{{ s['site_name'] }}</option>
                                        {% endfor %}
                                    </select>
                                </div>

                                <div class="mb-3">
                                    <label for="category" class="form-label"><i class="fas fa-tag me-2"></i>Category</label>
                                    <select class="form-select form-select-lg" id="category" name="category" required>
                                        <option value="Labour">Labour</option>
                                        <option value="Material">Material</option>
                                        <option value="Transport">Transport</option>
                                        <option value="Machinery">Machinery</option>
                                        <option value="Miscellaneous">Miscellaneous</option>
                                    </select>
                                </div>

                                <div class="mb-3">
                                    <label for="amount" class="form-label"><i class="fas fa-money-bill me-2"></i>Amount (₹)</label>
                                    <input type="number" step="0.01" class="form-control form-control-lg" id="amount" name="amount" required>
                                </div>

                                <div class="mb-4">
                                    <label for="remarks" class="form-label"><i class="fas fa-note-sticky me-2"></i>Remarks</label>
                                    <textarea class="form-control" id="remarks" name="remarks" rows="3" placeholder="Optional notes..."></textarea>
                                </div>

                                <div class="d-grid gap-2 d-md-flex">
                                    <button type="submit" class="btn btn-submit btn-lg flex-grow-1"><i class="fas fa-save me-2"></i>Save Expense</button>
                                    <a href="/expenses" class="btn btn-secondary btn-lg"><i class="fas fa-arrow-left me-2"></i>Back</a>
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
    </body>
    </html>
    """

    return render_template_string(template, sites=sites)
