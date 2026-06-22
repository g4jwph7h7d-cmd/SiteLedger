from flask import Blueprint, render_template_string, request, redirect, url_for
from db import get_db

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
    <html>
    <head>
        <title>Expenses - SiteLedger</title>
        <style>
            body{ font-family: Arial; background:#f4f6f8; padding:30px }
            .card{ background:white; padding:20px; margin:10px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1); }
            table{ width:100%; border-collapse:collapse }
            th,td{ padding:8px 12px; border-bottom:1px solid #eee }
            a.button{ display:inline-block; padding:8px 12px; background:#0d47a1; color:white; border-radius:6px; text-decoration:none }
        </style>
    </head>
    <body>
    <h1>Expenses</h1>
    <p><a class="button" href="/expenses/add">Add Expense</a> <a href="/">Back to Dashboard</a></p>

    <div class="card">
        <table>
            <thead>
                <tr><th>ID</th><th>Date</th><th>Site</th><th>Category</th><th>Amount</th><th>Remarks</th></tr>
            </thead>
            <tbody>
            {% for e in expenses %}
                <tr>
                    <td>{{ e['id'] }}</td>
                    <td>{{ e['date'] }}</td>
                    <td>{{ e['site_name'] }}</td>
                    <td>{{ e['category'] }}</td>
                    <td>₹{{ e['amount'] }}</td>
                    <td>{{ e['remarks'] }}</td>
                </tr>
            {% else %}
                <tr><td colspan="6">No expenses yet.</td></tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
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
    <head>
        <title>Add Expense - SiteLedger</title>
        <style>
            body{ font-family: Arial; background:#f4f6f8; padding:30px }
            form{ background:white; padding:20px; border-radius:8px; box-shadow:0 0 8px rgba(0,0,0,0.08); max-width:600px }
            label{ display:block; margin-top:10px }
            input, select, textarea{ width:100%; padding:8px; margin-top:6px }
            button{ margin-top:12px; padding:8px 12px; background:#0d47a1; color:white; border:none; border-radius:6px }
        </style>
    </head>
    <body>
    <h1>Add Expense</h1>
    <form method="post">
        <label>Date<input type="date" name="date" required></label>
        <label>Site<select name="site_id" required>
            {% for s in sites %}
                <option value="{{ s['id'] }}">{{ s['site_name'] }}</option>
            {% endfor %}
        </select></label>
        <label>Category<select name="category" required>
            <option value="Labour">Labour</option>
            <option value="Material">Material</option>
            <option value="Transport">Transport</option>
            <option value="Machinery">Machinery</option>
            <option value="Miscellaneous">Miscellaneous</option>
        </select></label>
        <label>Amount<input type="number" step="0.01" name="amount" required></label>
        <label>Remarks<textarea name="remarks"></textarea></label>
        <button type="submit">Save Expense</button>
    </form>
    <p><a href="/expenses">Back to Expenses</a></p>
    </body>
    </html>
    """

    return render_template_string(template, sites=sites)
