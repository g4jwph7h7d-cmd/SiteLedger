from flask import Blueprint, render_template_string, request, redirect, url_for
from db import get_db

bp = Blueprint('sites', __name__)


@bp.route('/sites')
def list_sites():
    db = get_db()
    cur = db.execute('SELECT id, site_name, client_name, address, status FROM sites ORDER BY id DESC')
    sites = cur.fetchall()

    template = """
    <html>
    <head>
        <title>Sites - SiteLedger</title>
        <style>
            body{ font-family: Arial; background:#f4f6f8; padding:30px }
            .card{ background:white; padding:20px; margin:10px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1); }
            table{ width:100%; border-collapse:collapse }
            th,td{ padding:8px 12px; border-bottom:1px solid #eee }
            a.button{ display:inline-block; padding:8px 12px; background:#0d47a1; color:white; border-radius:6px; text-decoration:none }
        </style>
    </head>
    <body>
    <h1>Sites</h1>
    <p><a class="button" href="/sites/add">Add Site</a> <a href="/">Back to Dashboard</a></p>

    <div class="card">
        <table>
            <thead>
                <tr><th>ID</th><th>Site Name</th><th>Client</th><th>Address</th><th>Status</th></tr>
            </thead>
            <tbody>
            {% for s in sites %}
                <tr>
                    <td>{{ s['id'] }}</td>
                    <td>{{ s['site_name'] }}</td>
                    <td>{{ s['client_name'] }}</td>
                    <td>{{ s['address'] }}</td>
                    <td>{{ s['status'] }}</td>
                </tr>
            {% else %}
                <tr><td colspan="5">No sites yet.</td></tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
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
    <html>
    <head>
        <title>Add Site - SiteLedger</title>
        <style>
            body{ font-family: Arial; background:#f4f6f8; padding:30px }
            form{ background:white; padding:20px; border-radius:8px; box-shadow:0 0 8px rgba(0,0,0,0.08); max-width:600px }
            label{ display:block; margin-top:10px }
            input, textarea, select{ width:100%; padding:8px; margin-top:6px }
            button{ margin-top:12px; padding:8px 12px; background:#0d47a1; color:white; border:none; border-radius:6px }
        </style>
    </head>
    <body>
    <h1>Add Site</h1>
    <form method="post">
        <label>Site Name<input name="site_name" required></label>
        <label>Client Name<input name="client_name"></label>
        <label>Address<textarea name="address"></textarea></label>
        <label>Status<select name="status">
            <option value="Planned">Planned</option>
            <option value="Active">Active</option>
            <option value="Completed">Completed</option>
        </select></label>
        <button type="submit">Create Site</button>
    </form>
    <p><a href="/sites">Back to Sites</a></p>
    </body>
    </html>
    """

    return render_template_string(template)
