from flask import Blueprint, render_template_string, request, redirect, url_for
from .db import get_db

bp = Blueprint('sites', __name__)


@bp.route('/sites')
def list_sites():
    db = get_db()
    cur = db.execute('SELECT id, site_name, client_name, address, status FROM sites ORDER BY id DESC')
    sites = cur.fetchall()

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sites - SiteLedger</title>
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
            .status-badge { font-size: 12px; font-weight: 600; }
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
                        <li class="nav-item"><a class="nav-link" href="/sites"><i class="fas fa-map-location-dot me-1"></i>Sites</a></li>
                        <li class="nav-item"><a class="nav-link" href="/workers"><i class="fas fa-users me-1"></i>Workers</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container-fluid py-5">
            <div class="container">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1 class="section-title mb-0"><i class="fas fa-map-pin me-2"></i>Construction Sites</h1>
                    <a href="/sites/add" class="btn btn-primary-custom"><i class="fas fa-plus me-2"></i>Add New Site</a>
                </div>

                <div class="card border-0 shadow-sm">
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th><i class="fas fa-hashtag me-2"></i>ID</th>
                                        <th><i class="fas fa-house-building me-2"></i>Site Name</th>
                                        <th><i class="fas fa-user me-2"></i>Client</th>
                                        <th><i class="fas fa-location-dot me-2"></i>Address</th>
                                        <th><i class="fas fa-circle-dot me-2"></i>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                {% for s in sites %}
                                    <tr>
                                        <td><span class="badge bg-primary">{{ s['id'] }}</span></td>
                                        <td><strong>{{ s['site_name'] }}</strong></td>
                                        <td>{{ s['client_name'] or '-' }}</td>
                                        <td>{{ s['address'] or '-' }}</td>
                                        <td>
                                            {% if s['status'] == 'Active' %}
                                                <span class="badge bg-success">{{ s['status'] }}</span>
                                            {% elif s['status'] == 'Planned' %}
                                                <span class="badge bg-info">{{ s['status'] }}</span>
                                            {% else %}
                                                <span class="badge bg-secondary">{{ s['status'] }}</span>
                                            {% endif %}
                                        </td>
                                    </tr>
                                {% else %}
                                    <tr><td colspan="5" class="text-center py-4"><i class="fas fa-inbox me-2"></i>No sites yet.</td></tr>
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

    return render_template_string(template, sites=sites)


@bp.route('/sites/add', methods=['GET', 'POST'])
def add_site():
    if request.method == 'POST':
        site_name = request.form.get('site_name')
        client_name = request.form.get('client_name')
        address = request.form.get('address')
        status = request.form.get('status')

        db = get_db()
        db.execute('INSERT INTO sites (site_name, client_name, address, status) VALUES (?,?,?,?)',
                   (site_name, client_name, address, status))
        db.commit()
        return redirect(url_for('sites.list_sites'))

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Site - SiteLedger</title>
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
                        <li class="nav-item"><a class="nav-link" href="/sites"><i class="fas fa-map-location-dot me-1"></i>Sites</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-lg-6 col-md-8">
                    <div class="form-card">
                        <div class="form-header">
                            <h2><i class="fas fa-plus-circle me-2"></i>Add New Construction Site</h2>
                        </div>
                        <div class="card-body p-4">
                            <form method="post">
                                <div class="mb-3">
                                    <label for="site_name" class="form-label"><i class="fas fa-house-building me-2"></i>Site Name</label>
                                    <input type="text" class="form-control form-control-lg" id="site_name" name="site_name" required placeholder="e.g., ABC Tower, Mumbai">
                                </div>

                                <div class="mb-3">
                                    <label for="client_name" class="form-label"><i class="fas fa-user me-2"></i>Client Name</label>
                                    <input type="text" class="form-control form-control-lg" id="client_name" name="client_name" placeholder="e.g., ABC Construction Co.">
                                </div>

                                <div class="mb-3">
                                    <label for="address" class="form-label"><i class="fas fa-location-dot me-2"></i>Address</label>
                                    <textarea class="form-control" id="address" name="address" rows="3" placeholder="Enter site address"></textarea>
                                </div>

                                <div class="mb-4">
                                    <label for="status" class="form-label"><i class="fas fa-circle-dot me-2"></i>Status</label>
                                    <select class="form-select form-select-lg" id="status" name="status">
                                        <option value="Planned">Planned</option>
                                        <option value="Active" selected>Active</option>
                                        <option value="Completed">Completed</option>
                                    </select>
                                </div>

                                <div class="d-grid gap-2 d-md-flex">
                                    <button type="submit" class="btn btn-submit btn-lg flex-grow-1"><i class="fas fa-save me-2"></i>Create Site</button>
                                    <a href="/sites" class="btn btn-secondary btn-lg"><i class="fas fa-arrow-left me-2"></i>Back</a>
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
