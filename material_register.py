from flask import Blueprint, render_template_string, request, redirect, url_for
from db import get_db

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
    <head>
        <title>Material Register - SiteLedger</title>
        <style>
            body{ font-family: Arial; background:#f4f6f8; padding:30px }
            .card{ background:white; padding:20px; margin:10px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1); }
            table{ width:100%; border-collapse:collapse }
            th,td{ padding:8px 12px; border-bottom:1px solid #eee }
            a.button{ display:inline-block; padding:8px 12px; background:#0d47a1; color:white; border-radius:6px; text-decoration:none }
        </style>
    </head>
    <body>
    <h1>Material Register</h1>
    <p><a class="button" href="/material-register/add">Add Material</a> <a href="/">Back to Dashboard</a></p>

    <div class="card">
        <table>
            <thead>
                <tr><th>ID</th><th>Date</th><th>Site</th><th>Material</th><th>Unit</th><th>Received</th><th>Used</th><th>Balance</th></tr>
            </thead>
            <tbody>
            {% for r in records %}
                <tr>
                    <td>{{ r['id'] }}</td>
                    <td>{{ r['date'] }}</td>
                    <td>{{ r['site_name'] }}</td>
                    <td>{{ r['material'] }}</td>
                    <td>{{ r['unit'] }}</td>
                    <td>{{ r['quantity_received'] }}</td>
                    <td>{{ r['quantity_used'] }}</td>
                    <td>{{ r['balance'] }}</td>
                </tr>
            {% else %}
                <tr><td colspan="8">No material records yet.</td></tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
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
    <html>
    <head>
        <title>Add Material - SiteLedger</title>
        <style>
            body{ font-family: Arial; background:#f4f6f8; padding:30px }
            form{ background:white; padding:20px; border-radius:8px; box-shadow:0 0 8px rgba(0,0,0,0.08); max-width:600px }
            label{ display:block; margin-top:10px }
            input, select{ width:100%; padding:8px; margin-top:6px }
            button{ margin-top:12px; padding:8px 12px; background:#0d47a1; color:white; border:none; border-radius:6px }
        </style>
    </head>
    <body>
    <h1>Add Material Record</h1>
    <form method="post">
        <label>Date<input type="date" name="date" required></label>
        <label>Site<select name="site_id" required>
            {% for s in sites %}
                <option value="{{ s['id'] }}">{{ s['site_name'] }}</option>
            {% endfor %}
        </select></label>
        <label>Material<select name="material" required>
            {% for m in materials %}
                <option value="{{ m }}">{{ m }}</option>
            {% endfor %}
        </select></label>
        <label>Unit<input name="unit"></label>
        <label>Quantity Received<input type="number" step="0.01" name="quantity_received"></label>
        <label>Quantity Used<input type="number" step="0.01" name="quantity_used"></label>
        <label>Balance<input type="number" step="0.01" name="balance"></label>
        <button type="submit">Save Record</button>
    </form>
    <p><a href="/material-register">Back to Material Register</a></p>
    </body>
    </html>
    """

    return render_template_string(template, sites=sites, materials=materials)
