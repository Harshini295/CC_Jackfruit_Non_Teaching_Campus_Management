import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import configparser
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime, timedelta
from decimal import Decimal

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Load MySQL configuration
config = configparser.ConfigParser()
config.read('config.ini')

app.config['MYSQL_HOST'] = config.get('mysql', 'host')
app.config['MYSQL_USER'] = config.get('mysql', 'user')
app.config['MYSQL_PASSWORD'] = config.get('mysql', 'password')
app.config['MYSQL_DB'] = config.get('mysql', 'database')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Helper functions
def execute_query(query, params=None, fetch_one=False):
    cur = mysql.connection.cursor()
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        if fetch_one:
            result = cur.fetchone()
        else:
            result = cur.fetchall()
            
        mysql.connection.commit()
        return result
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cur.close()

def get_contractor_name(contractor_id):
    query = "SELECT name FROM contractors WHERE contractor_id = %s"
    result = execute_query(query, (contractor_id,), fetch_one=True)
    return result['name'] if result else "Unknown"

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Dashboard
@app.route('/')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    active_contractors = execute_query("SELECT COUNT(*) as count FROM contractors WHERE status = 'active'", fetch_one=True)['count']
    active_contracts = execute_query("SELECT COUNT(*) as count FROM contracts WHERE status = 'active'", fetch_one=True)['count']
    today_orders = execute_query("SELECT COUNT(*) as count FROM orders WHERE DATE(order_date) = CURDATE()", fetch_one=True)['count']
    low_inventory = execute_query("SELECT COUNT(*) as count FROM inventory WHERE quantity <= threshold_level", fetch_one=True)['count']
    
    recent_orders = execute_query("""
        SELECT o.order_id, o.customer_name, o.order_date, o.status, SUM(oi.quantity * oi.price_at_order) as total 
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY o.order_id
        ORDER BY o.order_date DESC
        LIMIT 5
    """)
    
    return render_template('dashboard.html', 
                         active_contractors=active_contractors,
                         active_contracts=active_contracts,
                         today_orders=today_orders,
                         low_inventory=low_inventory,
                         recent_orders=recent_orders)

@app.route('/reports/export')
def export_reports():
    flash('Export functionality will be implemented in next version', 'info')
    return redirect(url_for('dashboard'))

# Contractor Management
@app.route('/contractors')
def list_contractors():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    contractors = execute_query("""
        SELECT c.*, COUNT(ct.contract_id) as contract_count 
        FROM contractors c
        LEFT JOIN contracts ct ON c.contractor_id = ct.contractor_id
        GROUP BY c.contractor_id
        ORDER BY c.name
    """)
    return render_template('contractors/list.html', contractors=contractors)

@app.route('/contractors/add', methods=['GET', 'POST'])
def add_contractor():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        contact_person = request.form['contact_person']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        service_type = request.form['service_type']
        contract_start_date = request.form['contract_start_date']
        contract_end_date = request.form['contract_end_date']
        status = request.form['status']
        
        query = """
            INSERT INTO contractors 
            (name, contact_person, phone, email, address, service_type, contract_start_date, contract_end_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        execute_query(query, (name, contact_person, phone, email, address, service_type, 
                             contract_start_date, contract_end_date, status))
        
        flash('Contractor added successfully!', 'success')
        return redirect(url_for('list_contractors'))
    
    return render_template('contractors/add.html')

@app.route('/contractors/edit/<int:contractor_id>', methods=['GET', 'POST'])
def edit_contractor(contractor_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        contact_person = request.form['contact_person']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        service_type = request.form['service_type']
        contract_start_date = request.form['contract_start_date']
        contract_end_date = request.form['contract_end_date']
        status = request.form['status']
        
        query = """
            UPDATE contractors SET 
            name = %s, contact_person = %s, phone = %s, email = %s, address = %s, 
            service_type = %s, contract_start_date = %s, contract_end_date = %s, status = %s
            WHERE contractor_id = %s
        """
        execute_query(query, (name, contact_person, phone, email, address, service_type, 
                             contract_start_date, contract_end_date, status, contractor_id))
        
        flash('Contractor updated successfully!', 'success')
        return redirect(url_for('list_contractors'))
    
    contractor = execute_query("SELECT * FROM contractors WHERE contractor_id = %s", (contractor_id,), fetch_one=True)
    return render_template('contractors/edit.html', contractor=contractor)

# Contract Management
@app.route('/contracts')
def list_contracts():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    contracts = execute_query("""
        SELECT ct.*, c.name as contractor_name 
        FROM contracts ct
        JOIN contractors c ON ct.contractor_id = c.contractor_id
        ORDER BY ct.start_date DESC
    """)
    return render_template('contracts/list.html', contracts=contracts)

@app.route('/contracts/add', methods=['GET', 'POST'])
def add_contract():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        contractor_id = request.form['contractor_id']
        contract_title = request.form['contract_title']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        total_amount = request.form['total_amount']
        payment_terms = request.form['payment_terms']
        terms_and_conditions = request.form['terms_and_conditions']
        status = request.form['status']
        
        query = """
            INSERT INTO contracts 
            (contractor_id, contract_title, description, start_date, end_date, total_amount, 
             payment_terms, terms_and_conditions, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        execute_query(query, (contractor_id, contract_title, description, start_date, end_date, 
                             total_amount, payment_terms, terms_and_conditions, status))
        
        flash('Contract added successfully!', 'success')
        return redirect(url_for('list_contracts'))
    
    contractors = execute_query("SELECT contractor_id, name FROM contractors WHERE status = 'active' ORDER BY name")
    return render_template('contracts/add.html', contractors=contractors)

@app.route('/contracts/edit/<int:contract_id>', methods=['GET', 'POST'])
def edit_contract(contract_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        contractor_id = request.form['contractor_id']
        contract_title = request.form['contract_title']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        total_amount = request.form['total_amount']
        payment_terms = request.form['payment_terms']
        terms_and_conditions = request.form['terms_and_conditions']
        status = request.form['status']
        
        query = """
            UPDATE contracts SET 
            contractor_id = %s, 
            contract_title = %s, 
            description = %s, 
            start_date = %s, 
            end_date = %s, 
            total_amount = %s, 
            payment_terms = %s, 
            terms_and_conditions = %s, 
            status = %s
            WHERE contract_id = %s
        """
        execute_query(query, (
            contractor_id, contract_title, description, start_date, end_date,
            total_amount, payment_terms, terms_and_conditions, status, contract_id
        ))
        
        flash('Contract updated successfully!', 'success')
        return redirect(url_for('list_contracts'))
    
    contract = execute_query("SELECT * FROM contracts WHERE contract_id = %s", (contract_id,), fetch_one=True)
    contractors = execute_query("SELECT contractor_id, name FROM contractors WHERE status = 'active' ORDER BY name")
    return render_template('contracts/edit.html', contract=contract, contractors=contractors)
# Staff Management
@app.route('/staff')
def list_staff():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    staff = execute_query("""
        SELECT s.*, c.name as contractor_name 
        FROM canteen_staff s
        LEFT JOIN contractors c ON s.contractor_id = c.contractor_id
        ORDER BY s.name
    """)
    return render_template('staff/list.html', staff=staff)

@app.route('/staff/add', methods=['GET', 'POST'])
def add_staff():
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        contractor_id = request.form.get('contractor_id')
        hire_date = request.form.get('hire_date')
        phone = request.form.get('phone')
        email = request.form.get('email')
        salary = request.form.get('salary')
        status = request.form['status']
        service_type = request.form['service_type']

        query = """
            INSERT INTO canteen_staff (name, role, contractor_id, hire_date, phone, email, salary, status, service_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (name, role, contractor_id, hire_date, phone, email, salary, status, service_type)

        execute_query(query, params)
        return redirect(url_for('list_staff'))

    contractors = execute_query("SELECT contractor_id, name FROM contractors")
    return render_template('staff/add.html', contractors=contractors)

@app.route('/staff/edit/<int:staff_id>', methods=['GET', 'POST'])
def edit_staff(staff_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        service_type = request.form.get('service_type')
        contractor_id = request.form.get('contractor_id') or None
        phone = request.form.get('phone')
        email = request.form.get('email')
        hire_date = request.form.get('hire_date')
        salary = request.form.get('salary')
        status = request.form['status']
        
        query = """
            UPDATE canteen_staff SET 
            name = %s, role = %s, service_type = %s, contractor_id = %s, phone = %s, 
            email = %s, hire_date = %s, salary = %s, status = %s
            WHERE staff_id = %s
        """
        execute_query(query, (name, role, service_type, contractor_id, phone, email, hire_date, salary, status, staff_id))
        
        flash('Staff member updated successfully!', 'success')
        return redirect(url_for('list_staff'))
    
    staff = execute_query("SELECT * FROM canteen_staff WHERE staff_id = %s", (staff_id,), fetch_one=True)
    contractors = execute_query("SELECT contractor_id, name FROM contractors")
    return render_template('staff/edit.html', staff=staff, contractors=contractors)

@app.route('/staff/filter', methods=['GET'])
def staff_filter():
    role = request.args.get('role')
    contractor_id = request.args.get('contractor_id')
    status = request.args.get('status')
    service_type = request.args.get('service_type')

    query = """
    SELECT cs.*, c.name AS contractor_name
    FROM canteen_staff cs
    LEFT JOIN contractors c ON cs.contractor_id = c.contractor_id
    WHERE 1=1
    """

    params = []

    if role:
        query += " AND cs.role = %s"
        params.append(role)
    if contractor_id:
        query += " AND cs.contractor_id = %s"
        params.append(contractor_id)
    if status:
        query += " AND cs.status = %s"
        params.append(status)
    if service_type:
        query += " AND cs.service_type = %s"
        params.append(service_type)

    staff = execute_query(query, tuple(params))
    contractors = execute_query("SELECT contractor_id, name FROM contractors")

    return render_template('staff/staff_filter.html', staff=staff, contractors=contractors)

# Order Management
@app.route('/orders/view/<int:order_id>')
def view_order(order_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    order = execute_query("""
        SELECT o.*, s.name as staff_name 
        FROM orders o
        LEFT JOIN canteen_staff s ON o.staff_id = s.staff_id
        WHERE o.order_id = %s
    """, (order_id,), fetch_one=True)
    
    order_items = execute_query("""
        SELECT oi.* 
        FROM order_items oi
        WHERE oi.order_id = %s
    """, (order_id,))
    
    feedback = execute_query("""
        SELECT * FROM feedback WHERE order_id = %s
    """, (order_id,), fetch_one=True)
    
    return render_template('orders/view.html', 
                         order=order, 
                         order_items=order_items, 
                         feedback=feedback)

@app.route('/orders/update-status/<int:order_id>/<status>')
def update_order_status(order_id, status):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    valid_statuses = ['pending', 'preparing', 'ready', 'delivered', 'cancelled']
    if status not in valid_statuses:
        flash('Invalid status', 'danger')
        return redirect(url_for('list_orders'))
    
    execute_query("UPDATE orders SET status = %s WHERE order_id = %s", (status, order_id))
    
    if status == 'delivered':
        execute_query("UPDATE orders SET payment_status = 'paid' WHERE order_id = %s", (order_id,))
    
    flash(f'Order status updated to {status}', 'success')
    return redirect(request.referrer or url_for('list_orders'))

# Inventory Management
@app.route('/inventory')
def list_inventory():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        inventory = execute_query("SELECT * FROM inventory ORDER BY item_name")
        low_stock = execute_query("""
            SELECT * FROM inventory 
            WHERE quantity <= threshold_level OR threshold_level IS NULL 
            ORDER BY item_name
        """)
        return render_template('inventory/list.html', 
                            inventory=inventory, 
                            low_stock=low_stock)
    except Exception as e:
        flash(f'Error loading inventory: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/inventory/add', methods=['GET', 'POST'])
def add_inventory_item():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            item_name = request.form['item_name']
            category = request.form['category']
            quantity = float(request.form['quantity'])
            unit = request.form['unit']
            threshold_level = float(request.form.get('threshold_level', 0))
            supplier_info = request.form.get('supplier_info', '')
            storage_location = request.form.get('storage_location', '')
            
            execute_query("""
                INSERT INTO inventory 
                (item_name, category, quantity, unit, threshold_level, 
                 supplier_info, storage_location, last_restocked)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_DATE)
            """, (item_name, category, quantity, unit, threshold_level,
                 supplier_info, storage_location))
            
            flash('Inventory item added successfully!', 'success')
            return redirect(url_for('list_inventory'))
        except Exception as e:
            flash(f'Error adding item: {str(e)}', 'danger')
    
    return render_template('inventory/add.html')

@app.route('/inventory/edit/<int:inventory_id>', methods=['GET', 'POST'])
def edit_inventory_item(inventory_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        item = execute_query(
            "SELECT * FROM inventory WHERE inventory_id = %s", 
            (inventory_id,), fetch_one=True)
        
        if not item:
            flash('Inventory item not found', 'danger')
            return redirect(url_for('list_inventory'))
        
        if request.method == 'POST':
            try:
                item_name = request.form['item_name']
                category = request.form['category']
                quantity = float(request.form['quantity'])
                unit = request.form['unit']
                threshold_level = float(request.form.get('threshold_level', 0))
                supplier_info = request.form.get('supplier_info', '')
                storage_location = request.form.get('storage_location', '')
                
                execute_query("""
                    UPDATE inventory SET 
                    item_name = %s, category = %s, quantity = %s, unit = %s, 
                    threshold_level = %s, supplier_info = %s, storage_location = %s
                    WHERE inventory_id = %s
                """, (item_name, category, quantity, unit, 
                     threshold_level, supplier_info, storage_location, inventory_id))
                
                flash('Inventory item updated successfully!', 'success')
                return redirect(url_for('list_inventory'))
            except Exception as e:
                flash(f'Error updating item: {str(e)}', 'danger')
        
        return render_template('inventory/edit.html', item=item)
    except Exception as e:
        flash(f'Error loading item: {str(e)}', 'danger')
        return redirect(url_for('list_inventory'))

@app.route('/inventory/delete/<int:inventory_id>')
def delete_inventory_item(inventory_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        execute_query("DELETE FROM inventory WHERE inventory_id = %s", (inventory_id,))
        flash('Inventory item deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting item: {str(e)}', 'danger')
    
    return redirect(url_for('list_inventory'))

# Menu Management
@app.route('/menu')
def list_menu():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    menu_items = execute_query("""
        SELECT m.*, c.name as category_name 
        FROM menu_items m
        LEFT JOIN food_categories c ON m.canteen_id = c.canteen_id
        ORDER BY m.name
    """)
    return render_template('menu/list.html', menu_items=menu_items)

@app.route('/menu/add', methods=['GET', 'POST'])
def add_menu_item():
    if request.method == 'POST':
        item_name = request.form['item_name']
        price = request.form['price']
        canteen_id = request.form['canteen_id']

        query = "INSERT INTO menu_items (name, price, canteen_id) VALUES (%s, %s, %s)"
        execute_query(query, (item_name, price, canteen_id))

        flash('Menu item added successfully.', 'success')
        return redirect(url_for('add_menu_item'))

    canteens = execute_query("SELECT contractor_id, name FROM contractors WHERE service_type = 'Canteen'")
    return render_template('menu/menu.html', canteens=canteens)

@app.route('/menu/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_menu_item(item_id):
    if request.method == 'POST':
        name = request.form['name']
        canteen_id = request.form.get('canteen_id') or None
        description = request.form.get('description')
        price = request.form['price']
        preparation_time = request.form.get('preparation_time')
        is_available = 1 if 'is_available' in request.form else 0
        
        query = """
            UPDATE menu_items SET 
            name = %s, canteen_id = %s, description = %s, 
            price = %s, preparation_time = %s, is_available = %s
            WHERE item_id = %s
        """
        execute_query(query, (name, canteen_id, description, price, preparation_time, is_available, item_id))
        
        flash('Menu item updated successfully!', 'success')
        return redirect(url_for('list_menu'))
    
    item = execute_query("SELECT * FROM menu_items WHERE item_id = %s", (item_id,), fetch_one=True)
    categories = execute_query("SELECT * FROM food_categories")
    return render_template('menu/edit.html', item=item, categories=categories)

# Order Management
@app.route('/orders')
def list_orders():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    status_filter = request.args.get('status', 'all')
    
    base_query = """
        SELECT o.*, s.name as staff_name 
        FROM orders o
        LEFT JOIN canteen_staff s ON o.staff_id = s.staff_id
    """
    
    if status_filter != 'all':
        base_query += f" WHERE o.status = '{status_filter}'"
    
    base_query += " ORDER BY o.order_date DESC"
    
    orders = execute_query(base_query)
    return render_template('orders/list.html', orders=orders, status_filter=status_filter)

@app.route('/orders/create', methods=['GET', 'POST'])
def create_order():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_phone = request.form['customer_phone']
        payment_method = request.form['payment_method']
        notes = request.form.get('notes', '')
        
        query = """
            INSERT INTO orders 
            (customer_name, customer_phone, payment_method, notes)
            VALUES (%s, %s, %s, %s)
        """
        execute_query(query, (customer_name, customer_phone, payment_method, notes))
        
        order_id = execute_query("SELECT LAST_INSERT_ID() as id", fetch_one=True)['id']
        
        item_ids = request.form.getlist('item_id')
        quantities = request.form.getlist('quantity')
        special_requests = request.form.getlist('special_requests')
        
        subtotal = Decimal('0')
        
        for i in range(len(item_ids)):
            quantity = int(quantities[i])
            if quantity > 0:
                item = execute_query("""
                    SELECT price, name 
                    FROM menu_items 
                    WHERE item_id = %s
                """, (item_ids[i],), fetch_one=True)
                
                if not item:
                    flash(f"Item with ID {item_ids[i]} not found", 'danger')
                    continue
                
                price = Decimal(str(item['price']))
                
                query = """
                    INSERT INTO order_items 
                    (order_id, item_id, item_name, quantity, special_requests, price_at_order)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                execute_query(query, (
                    order_id, 
                    item_ids[i], 
                    item['name'],
                    quantity, 
                    special_requests[i], 
                    float(price)
                ))
                
                subtotal += price * quantity
        
        tax_rate = Decimal('0.05')
        tax_amount = subtotal * tax_rate
        grand_total = subtotal + tax_amount
        
        execute_query("""
            UPDATE orders SET 
            total_amount = %s,
            tax_amount = %s,
            grand_total = %s
            WHERE order_id = %s
        """, (
            float(subtotal),
            float(tax_amount),
            float(grand_total),
            order_id
        ))
        
        flash('Order created successfully!', 'success')
        return redirect(url_for('view_order', order_id=order_id))
    
    menu_items = execute_query("""
        SELECT m.*, c.name as category_name 
        FROM menu_items m
        LEFT JOIN food_categories c ON m.canteen_id = c.canteen_id
        WHERE m.is_available = 1
        ORDER BY c.name, m.name
    """)
    
    categories = {}
    for item in menu_items:
        category = item['category_name'] if item['category_name'] else 'Uncategorized'
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    return render_template('orders/create.html', categories=categories)

# Reports
@app.route('/reports/sales')
def sales_report():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = datetime.now().date() - timedelta(days=30)
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = datetime.now().date()
        
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        daily_sales = execute_query("""
            SELECT DATE(order_date) as date, COUNT(*) as order_count, SUM(total_amount) as total_sales
            FROM orders
            WHERE DATE(order_date) BETWEEN %s AND %s
            GROUP BY DATE(order_date)
            ORDER BY DATE(order_date)
        """, (start_date, end_date))
        
        top_items = execute_query("""
            SELECT m.name, SUM(oi.quantity) as total_quantity, SUM(oi.quantity * oi.price_at_order) as total_sales
            FROM order_items oi
            JOIN menu_items m ON oi.item_id = m.item_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE DATE(o.order_date) BETWEEN %s AND %s
            GROUP BY m.name
            ORDER BY total_sales DESC
            LIMIT 10
        """, (start_date, end_date))
        
        dates = [row['date'].strftime('%Y-%m-%d') for row in daily_sales]
        sales = [float(row['total_sales']) for row in daily_sales]
        
        plt.figure(figsize=(10, 5))
        plt.plot(dates, sales, marker='o')
        plt.title('Daily Sales')
        plt.xlabel('Date')
        plt.ylabel('Sales (₹)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart_bytes = BytesIO()
        plt.savefig(chart_bytes, format='png')
        chart_bytes.seek(0)
        chart_base64 = base64.b64encode(chart_bytes.read()).decode('utf-8')
        plt.close()
        
        return render_template('reports/sales.html', 
                            daily_sales=daily_sales,
                            top_items=top_items,
                            start_date=start_date.strftime('%Y-%m-%d'),
                            end_date=end_date.strftime('%Y-%m-%d'),
                            chart_base64=chart_base64)
    
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

# Contractor Feedback
@app.route('/contractors/<int:contractor_id>/feedback')
def view_contractor_feedback(contractor_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    contractor = execute_query("""
        SELECT * FROM contractors WHERE contractor_id = %s
    """, (contractor_id,), fetch_one=True)
    
    feedback = execute_query("""
        SELECT cf.*, o.order_id, o.customer_name 
        FROM contractor_feedback cf
        LEFT JOIN orders o ON cf.order_id = o.order_id
        WHERE cf.contractor_id = %s
        ORDER BY cf.feedback_date DESC
    """, (contractor_id,))
    
    return render_template('contractors/feedback.html', 
                         contractor=contractor, 
                         feedback=feedback)

@app.route('/contractors/<int:contractor_id>/feedback/add', methods=['GET', 'POST'])
def add_contractor_feedback(contractor_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    contractor = execute_query("""
        SELECT * FROM contractors WHERE contractor_id = %s
    """, (contractor_id,), fetch_one=True)
    
    if request.method == 'POST':
        rating = request.form['rating']
        comments = request.form.get('comments', '')
        order_id = request.form.get('order_id')
        
        execute_query("""
            INSERT INTO contractor_feedback 
            (contractor_id, order_id, rating, comments)
            VALUES (%s, %s, %s, %s)
        """, (contractor_id, order_id, rating, comments))
        
        execute_query("""
            UPDATE contractors c
            SET 
                average_rating = (
                    SELECT AVG(rating) FROM contractor_feedback 
                    WHERE contractor_id = %s
                ),
                feedback_count = (
                    SELECT COUNT(*) FROM contractor_feedback 
                    WHERE contractor_id = %s
                )
            WHERE c.contractor_id = %s
        """, (contractor_id, contractor_id, contractor_id))
        
        flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('view_contractor_feedback', contractor_id=contractor_id))
    
    orders = []
    if contractor['service_type'] == 'canteen':
        orders = execute_query("""
            SELECT o.order_id, o.customer_name, o.order_date
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE o.order_date >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
            ORDER BY o.order_date DESC
            LIMIT 50
        """)
    
    return render_template('contractors/add_feedback.html', 
                         contractor=contractor, 
                         orders=orders)

@app.route('/contractors/performance')
def contractor_performance():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    contractors = execute_query("""
        SELECT c.*, 
               COUNT(cf.feedback_id) as feedback_count,
               AVG(cf.rating) as avg_rating
        FROM contractors c
        LEFT JOIN contractor_feedback cf ON c.contractor_id = cf.contractor_id
        GROUP BY c.contractor_id
        ORDER BY avg_rating DESC
    """)
    
    return render_template('contractors/performance.html', 
                         contractors=contractors)

# API Endpoints
@app.route('/api/menu/available')
def api_available_menu():
    items = execute_query("""
        SELECT m.item_id, m.name, m.price, c.name as category 
        FROM menu_items m
        LEFT JOIN food_categories c ON m.category_id = c.category_id
        WHERE m.is_available = 1
        ORDER BY m.name
    """)
    return jsonify(items)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

