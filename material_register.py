from flask import Blueprint, render_template_string, request, redirect, url_for
from .db import get_db

bp = Blueprint('material_register', __name__)


def get_sites():
    db = get_db()
    return db.execute('SELECT id, site_name FROM sites ORDER BY site_name').fetchall()


@bp.route('/material-register')
def material_register():
    db = get_db()
    cur = db.execute(
        '''
        SELECT m.id, m.date, s.site_name, m.material, m.unit, m.quantity_received, m.quantity_used, m.balance
        FROM material_register m
        JOIN sites s ON m.site_id = s.id
        ORDER BY m.date DESC, m.id DESC
        '''
    )
    records = cur.fetchall()

    template = """
    <html>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Material Register - SiteLedger</title>
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
                        <li class="nav-item"><a class="nav-link" href="/material-register"><i class="fas fa-boxes me-1"></i>Materials</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container-fluid py-5">
            <div class="container">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1 class="section-title mb-0"><i class="fas fa-boxes me-2"></i>Material Register</h1>
                    <a href="/material-register/add" class="btn btn-primary-custom"><i class="fas fa-plus me-2"></i>Add Material</a>
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
                                        <th><i class="fas fa-box me-2"></i>Material</th>
                                        <th><i class="fas fa-ruler me-2"></i>Unit</th>
                                        <th><i class="fas fa-arrow-down me-2"></i>Received</th>
                                        <th><i class="fas fa-arrow-up me-2"></i>Used</th>
                                        <th><i class="fas fa-balance-scale me-2"></i>Balance</th>
                                    </tr>
                                </thead>
                                <tbody>
                                {% for r in records %}
                                    <tr>
                                        <td><span class="badge bg-primary">{{ r['id'] }}</span></td>
                                        <td>{{ r['date'] }}</td>
                                        <td><strong>{{ r['site_name'] }}</strong></td>
                                        <td>{{ r['material'] }}</td>
                                        <td><span class="badge bg-secondary">{{ r['unit'] }}</span></td>
                                        <td><span class="text-success">{{ r['quantity_received'] }}</span></td>
                                        <td><span class="text-warning">{{ r['quantity_used'] }}</span></td>
                                        <td><span class="text-info fw-bold">{{ r['balance'] }}</span></td>
                                    </tr>
                                {% else %}
                                    <tr><td colspan="8" class="text-center py-4"><i class="fas fa-inbox me-2"></i>No material records yet.</td></tr>
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


@bp.route('/material-register/add', methods=['GET', 'POST'])
def add_material():
    sites = get_sites()
    materials = ['Cement', 'Steel', 'Sand', 'Bricks', 'Aggregate']

    if request.method == 'POST':
        date = request.form.get('date')
        site_id = request.form.get('site_id')
        material = request.form.get('material')
        unit = request.form.get('unit')
        quantity_received = float(request.form.get('quantity_received') or 0)
        quantity_used = float(request.form.get('quantity_used') or 0)
        balance = float(request.form.get('balance') or 0)

        db = get_db()
        db.execute(
            'INSERT INTO material_register (date, site_id, material, unit, quantity_received, quantity_used, balance) VALUES (?,?,?,?,?,?,?)',
            (date, site_id, material, unit, quantity_received, quantity_used, balance)
        )
        db.commit()
        return redirect(url_for('material_register.material_register'))

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Material - SiteLedger</title>
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
                        <li class="nav-item"><a class="nav-link" href="/material-register"><i class="fas fa-boxes me-1"></i>Materials</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-lg-6 col-md-8">
                    <div class="form-card">
                        <div class="form-header">
                            <h2><i class="fas fa-plus-circle me-2"></i>Record Material</h2>
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
                                    <label for="material" class="form-label"><i class="fas fa-box me-2"></i>Material</label>
                                    <select class="form-select form-select-lg" id="material" name="material" required>
                                        {% for m in materials %}
                                            <option value="{{ m }}">{{ m }}</option>
                                        {% endfor %}
                                    </select>
                                </div>

                                <div class="mb-3">
                                    <label for="unit" class="form-label"><i class="fas fa-ruler me-2"></i>Unit</label>
                                    <input type="text" class="form-control form-control-lg" id="unit" name="unit" placeholder="e.g., Bags, Kg, Tons">
                                </div>

                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="quantity_received" class="form-label"><i class="fas fa-arrow-down me-2"></i>Received</label>
                                        <input type="number" step="0.01" class="form-control" id="quantity_received" name="quantity_received" value="0">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label for="quantity_used" class="form-label"><i class="fas fa-arrow-up me-2"></i>Used</label>
                                        <input type="number" step="0.01" class="form-control" id="quantity_used" name="quantity_used" value="0">
                                    </div>
                                </div>

                                <div class="mb-4">
                                    <label for="balance" class="form-label"><i class="fas fa-balance-scale me-2"></i>Balance</label>
                                    <input type="number" step="0.01" class="form-control form-control-lg" id="balance" name="balance" value="0">
                                </div>

                                <div class="d-grid gap-2 d-md-flex">
                                    <button type="submit" class="btn btn-submit btn-lg flex-grow-1"><i class="fas fa-save me-2"></i>Save Record</button>
                                    <a href="/material-register" class="btn btn-secondary btn-lg"><i class="fas fa-arrow-left me-2"></i>Back</a>
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

    return render_template_string(template, sites=sites, materials=materials)
