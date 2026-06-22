from flask import Blueprint, render_template_string, request, redirect, url_for
from db import get_db

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
    <head>
        <title>Attendance - SiteLedger</title>
        <style>
            body{ font-family: Arial; background:#f4f6f8; padding:30px }
            .card{ background:white; padding:20px; margin:10px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1); }
            table{ width:100%; border-collapse:collapse }
            th,td{ padding:8px 12px; border-bottom:1px solid #eee }
            a.button{ display:inline-block; padding:8px 12px; background:#0d47a1; color:white; border-radius:6px; text-decoration:none }
        </style>
    </head>
    <body>
    <h1>Attendance</h1>
    <p><a class="button" href="/attendance/add">Add Attendance</a> <a href="/">Back to Dashboard</a></p>

    <div class="card">
        <table>
            <thead>
                <tr><th>ID</th><th>Date</th><th>Site</th><th>Worker</th><th>Status</th><th>Overtime</th><th>Cost</th></tr>
            </thead>
            <tbody>
            {% for r in records %}
                <tr>
                    <td>{{ r['id'] }}</td>
                    <td>{{ r['date'] }}</td>
                    <td>{{ r['site_name'] }}</td>
                    <td>{{ r['worker_name'] }}</td>
                    <td>{{ r['status'] }}</td>
                    <td>{{ r['overtime_hours'] or 0 }}</td>
                    <td>₹{{ r['cost'] }}</td>
                </tr>
            {% else %}
                <tr><td colspan="7">No attendance records yet.</td></tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
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
    <head>
        <title>Add Attendance - SiteLedger</title>
        <style>
            body{ font-family: Arial; background:#f4f6f8; padding:30px }
            form{ background:white; padding:20px; border-radius:8px; box-shadow:0 0 8px rgba(0,0,0,0.08); max-width:600px }
            label{ display:block; margin-top:10px }
            input, select{ width:100%; padding:8px; margin-top:6px }
            button{ margin-top:12px; padding:8px 12px; background:#0d47a1; color:white; border:none; border-radius:6px }
        </style>
    </head>
    <body>
    <h1>Add Attendance</h1>
    <form method="post">
        <label>Date<input type="date" name="date" required></label>
        <label>Site<select name="site_id" required>
            {% for s in sites %}
                <option value="{{ s['id'] }}">{{ s['site_name'] }}</option>
            {% endfor %}
        </select></label>
        <label>Worker<select name="worker_id" required>
            {% for w in workers %}
                <option value="{{ w['id'] }}">{{ w['worker_name'] }}</option>
            {% endfor %}
        </select></label>
        <label>Status<select name="status" required>
            <option value="Present">Present</option>
            <option value="Absent">Absent</option>
            <option value="Half Day">Half Day</option>
        </select></label>
        <label>Overtime Hours<input type="number" step="0.25" name="overtime_hours" value="0"></label>
        <button type="submit">Save Attendance</button>
    </form>
    <p><a href="/attendance">Back to Attendance</a></p>
    </body>
    </html>
    """

    return render_template_string(template, sites=sites, workers=workers)
