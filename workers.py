from flask import Blueprint, render_template_string, request, redirect, url_for
from db import get_db

bp = Blueprint('workers', __name__)


@bp.route('/workers')
def list_workers():
    db = get_db()
    cur = db.execute('SELECT id, worker_name, category, mobile, daily_wage FROM workers ORDER BY id DESC')
    workers = cur.fetchall()

    template = """
    <html>
    <head>
        <title>Workers - SiteLedger</title>
        <style>
            body{ font-family: Arial; background:#f4f6f8; padding:30px }
            .card{ background:white; padding:20px; margin:10px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1); }
            table{ width:100%; border-collapse:collapse }
            th,td{ padding:8px 12px; border-bottom:1px solid #eee }
            a.button{ display:inline-block; padding:8px 12px; background:#0d47a1; color:white; border-radius:6px; text-decoration:none }
        </style>
    </head>
    <body>
    <h1>Workers</h1>
    <p><a class="button" href="/workers/add">Add Worker</a> <a href="/">Back to Dashboard</a></p>

    <div class="card">
        <table>
            <thead>
                <tr><th>ID</th><th>Name</th><th>Category</th><th>Mobile</th><th>Daily Wage</th></tr>
            </thead>
            <tbody>
            {% for w in workers %}
                <tr>
                    <td>{{ w['id'] }}</td>
                    <td>{{ w['worker_name'] }}</td>
                    <td>{{ w['category'] }}</td>
                    <td>{{ w['mobile'] }}</td>
                    <td>{{ w['daily_wage'] }}</td>
                </tr>
            {% else %}
                <tr><td colspan="5">No workers yet.</td></tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
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
    <html>
    <head>
        <title>Add Worker - SiteLedger</title>
        <style>
            body{ font-family: Arial; background:#f4f6f8; padding:30px }
            form{ background:white; padding:20px; border-radius:8px; box-shadow:0 0 8px rgba(0,0,0,0.08); max-width:600px }
            label{ display:block; margin-top:10px }
            input, textarea, select{ width:100%; padding:8px; margin-top:6px }
            button{ margin-top:12px; padding:8px 12px; background:#0d47a1; color:white; border:none; border-radius:6px }
        </style>
    </head>
    <body>
    <h1>Add Worker</h1>
    <form method="post">
        <label>Worker Name<input name="worker_name" required></label>
        <label>Category<input name="category"></label>
        <label>Mobile<input name="mobile"></label>
        <label>Daily Wage<input type="number" step="0.01" name="daily_wage"></label>
        <button type="submit">Create Worker</button>
    </form>
    <p><a href="/workers">Back to Workers</a></p>
    </body>
    </html>
    """

    return render_template_string(template)
