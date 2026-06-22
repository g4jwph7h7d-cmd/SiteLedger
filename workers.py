from flask import Blueprint, render_template_string, request, redirect, url_for
from .db import get_db

bp = Blueprint('workers', __name__)


@bp.route('/workers')
def list_workers():
    db = get_db()
    cur = db.execute('SELECT id, worker_name, category, mobile, daily_wage FROM workers ORDER BY id DESC')
    workers = cur.fetchall()

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Workers - SiteLedger</title>
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
            .category-badge { font-size: 12px; font-weight: 600; }
            .btn-primary-custom { background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%); border: none; }
            .btn-primary-custom:hover { background: var(--primary-color); }
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
                        <li class="nav-item"><a class="nav-link" href="/workers"><i class="fas fa-users me-1"></i>Workers</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container-fluid py-5">
            <div class="container">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1 class="section-title mb-0"><i class="fas fa-users me-2"></i>Workers Management</h1>
                    <a href="/workers/add" class="btn btn-primary-custom"><i class="fas fa-user-plus me-2"></i>Add Worker</a>
                </div>

                <div class="card border-0 shadow-sm">
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th><i class="fas fa-hashtag me-2"></i>ID</th>
                                        <th><i class="fas fa-user me-2"></i>Worker Name</th>
                                        <th><i class="fas fa-briefcase me-2"></i>Category</th>
                                        <th><i class="fas fa-phone me-2"></i>Mobile</th>
                                        <th><i class="fas fa-money-bill me-2"></i>Daily Wage</th>
                                    </tr>
                                </thead>
                                <tbody>
                                {% for w in workers %}
                                    <tr>
                                        <td><span class="badge bg-primary">{{ w['id'] }}</span></td>
                                        <td><strong>{{ w['worker_name'] }}</strong></td>
                                        <td><span class="badge bg-info">{{ w['category'] or '-' }}</span></td>
                                        <td>{{ w['mobile'] or '-' }}</td>
                                        <td><span class="text-success">₹{{ w['daily_wage'] or 0 }}</span></td>
                                    </tr>
                                {% else %}
                                    <tr><td colspan="5" class="text-center py-4"><i class="fas fa-inbox me-2"></i>No workers yet.</td></tr>
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

    return render_template_string(template, workers=workers)


@bp.route('/workers/add', methods=['GET', 'POST'])
def add_worker():
    if request.method == 'POST':
        worker_name = request.form.get('worker_name')
        category = request.form.get('category')
        mobile = request.form.get('mobile')
        daily_wage = request.form.get('daily_wage')

        db = get_db()
        db.execute(
            'INSERT INTO workers (worker_name, category, mobile, daily_wage) VALUES (?,?,?,?)',
            (worker_name, category, mobile, daily_wage)
        )
        db.commit()
        return redirect(url_for('workers.list_workers'))

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Worker - SiteLedger</title>
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
                        <li class="nav-item"><a class="nav-link" href="/workers"><i class="fas fa-users me-1"></i>Workers</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-lg-6 col-md-8">
                    <div class="form-card">
                        <div class="form-header">
                            <h2><i class="fas fa-user-plus me-2"></i>Register New Worker</h2>
                        </div>
                        <div class="card-body p-4">
                            <form method="post">
                                <div class="mb-3">
                                    <label for="worker_name" class="form-label"><i class="fas fa-user me-2"></i>Worker Name</label>
                                    <input type="text" class="form-control form-control-lg" id="worker_name" name="worker_name" required placeholder="Full name">
                                </div>

                                <div class="mb-3">
                                    <label for="category" class="form-label"><i class="fas fa-briefcase me-2"></i>Category</label>
                                    <input type="text" class="form-control form-control-lg" id="category" name="category" placeholder="e.g., Mason, Labourer, Carpenter">
                                </div>

                                <div class="mb-3">
                                    <label for="mobile" class="form-label"><i class="fas fa-phone me-2"></i>Mobile Number</label>
                                    <input type="text" class="form-control form-control-lg" id="mobile" name="mobile" placeholder="10-digit mobile number">
                                </div>

                                <div class="mb-4">
                                    <label for="daily_wage" class="form-label"><i class="fas fa-money-bill me-2"></i>Daily Wage (₹)</label>
                                    <input type="number" step="0.01" class="form-control form-control-lg" id="daily_wage" name="daily_wage" placeholder="Enter daily wage amount">
                                </div>

                                <div class="d-grid gap-2 d-md-flex">
                                    <button type="submit" class="btn btn-submit btn-lg flex-grow-1"><i class="fas fa-save me-2"></i>Add Worker</button>
                                    <a href="/workers" class="btn btn-secondary btn-lg"><i class="fas fa-arrow-left me-2"></i>Back</a>
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

    return render_template_string(template)
