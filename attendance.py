from flask import Blueprint, render_template_string, request, redirect, url_for
from .db import get_db

bp = Blueprint('attendance', __name__)


def get_sites():
    db = get_db()
    return db.execute('SELECT id, site_name FROM sites ORDER BY site_name').fetchall()


def get_workers():
    db = get_db()
    return db.execute('SELECT id, worker_name, daily_wage FROM workers ORDER BY worker_name').fetchall()


@bp.route('/attendance')
def list_attendance():
    db = get_db()
    cur = db.execute(
        '''
        SELECT a.id, a.date, s.site_name, w.worker_name, a.status, a.overtime_hours, w.daily_wage
        FROM attendance a
        JOIN sites s ON a.site_id = s.id
        JOIN workers w ON a.worker_id = w.id
        ORDER BY a.date DESC, a.id DESC
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
        <title>Attendance - SiteLedger</title>
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
                        <li class="nav-item"><a class="nav-link" href="/attendance"><i class="fas fa-clipboard-check me-1"></i>Attendance</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container-fluid py-5">
            <div class="container">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1 class="section-title mb-0"><i class="fas fa-clipboard-check me-2"></i>Attendance Records</h1>
                    <a href="/attendance/add" class="btn btn-primary-custom"><i class="fas fa-plus me-2"></i>Add Attendance</a>
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
                                        <th><i class="fas fa-user me-2"></i>Worker</th>
                                        <th><i class="fas fa-circle-dot me-2"></i>Status</th>
                                        <th><i class="fas fa-hourglass me-2"></i>Overtime</th>
                                        <th><i class="fas fa-money-bill me-2"></i>Cost</th>
                                    </tr>
                                </thead>
                                <tbody>
                                {% for r in records %}
                                    <tr>
                                        <td><span class="badge bg-primary">{{ r['id'] }}</span></td>
                                        <td>{{ r['date'] }}</td>
                                        <td><strong>{{ r['site_name'] }}</strong></td>
                                        <td>{{ r['worker_name'] }}</td>
                                        <td>
                                            {% if r['status'] == 'Present' %}
                                                <span class="badge bg-success">{{ r['status'] }}</span>
                                            {% elif r['status'] == 'Half Day' %}
                                                <span class="badge bg-warning text-dark">{{ r['status'] }}</span>
                                            {% else %}
                                                <span class="badge bg-danger">{{ r['status'] }}</span>
                                            {% endif %}
                                        </td>
                                        <td>{{ r['overtime_hours'] or 0 }} h</td>
                                        <td><span class="text-success fw-bold">₹{{ "%.2f"|format(r['cost']) }}</span></td>
                                    </tr>
                                {% else %}
                                    <tr><td colspan="7" class="text-center py-4"><i class="fas fa-inbox me-2"></i>No attendance records yet.</td></tr>
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

    processed = []
    for row in records:
        wage = row['daily_wage'] or 0
        if row['status'] == 'Present':
            base = wage
        elif row['status'] == 'Half Day':
            base = wage * 0.5
        else:
            base = 0
        overtime = (wage / 8.0) * (row['overtime_hours'] or 0)
        cost = round(base + overtime, 2)
        row = dict(row)
        row['cost'] = cost
        processed.append(row)

    return render_template_string(template, records=processed)


@bp.route('/attendance/add', methods=['GET', 'POST'])
def add_attendance():
    if request.method == 'POST':
        date = request.form.get('date')
        site_id = request.form.get('site_id')
        worker_id = request.form.get('worker_id')
        status = request.form.get('status')
        overtime_hours = request.form.get('overtime_hours') or 0

        db = get_db()
        db.execute(
            'INSERT INTO attendance (date, site_id, worker_id, status, overtime_hours) VALUES (?,?,?,?,?)',
            (date, site_id, worker_id, status, overtime_hours)
        )
        db.commit()
        return redirect(url_for('attendance.list_attendance'))

    sites = get_sites()
    workers = get_workers()

    template = """
    <html>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Attendance - SiteLedger</title>
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
                        <li class="nav-item"><a class="nav-link" href="/attendance"><i class="fas fa-clipboard-check me-1"></i>Attendance</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-lg-6 col-md-8">
                    <div class="form-card">
                        <div class="form-header">
                            <h2><i class="fas fa-check-circle me-2"></i>Record Attendance</h2>
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
                                    <label for="worker_id" class="form-label"><i class="fas fa-user me-2"></i>Worker</label>
                                    <select class="form-select form-select-lg" id="worker_id" name="worker_id" required>
                                        {% for w in workers %}
                                            <option value="{{ w['id'] }}">{{ w['worker_name'] }}</option>
                                        {% endfor %}
                                    </select>
                                </div>

                                <div class="mb-3">
                                    <label for="status" class="form-label"><i class="fas fa-circle-dot me-2"></i>Status</label>
                                    <select class="form-select form-select-lg" id="status" name="status" required>
                                        <option value="Present">Present</option>
                                        <option value="Absent">Absent</option>
                                        <option value="Half Day">Half Day</option>
                                    </select>
                                </div>

                                <div class="mb-4">
                                    <label for="overtime_hours" class="form-label"><i class="fas fa-hourglass me-2"></i>Overtime Hours</label>
                                    <input type="number" step="0.25" class="form-control form-control-lg" id="overtime_hours" name="overtime_hours" value="0" placeholder="Leave empty for no overtime">
                                </div>

                                <div class="d-grid gap-2 d-md-flex">
                                    <button type="submit" class="btn btn-submit btn-lg flex-grow-1"><i class="fas fa-save me-2"></i>Save Attendance</button>
                                    <a href="/attendance" class="btn btn-secondary btn-lg"><i class="fas fa-arrow-left me-2"></i>Back</a>
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

    return render_template_string(template, sites=sites, workers=workers)
