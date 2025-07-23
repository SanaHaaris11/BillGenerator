from flask import Flask, render_template, request, redirect, url_for, flash, g
import database # Import your database module
import os
import sqlite3 # Needed for specific database error handling

app = Flask(__name__)
# A secret key is required for Flask's session management (used by flash messages)
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize the database when the app starts
database.init_app(app)

# --- ROUTES (URL Endpoints) ---

@app.route('/')
def index():
    """Renders the homepage."""
    return render_template('index.html')

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    """Handles adding new customer details to the database."""
    if request.method == 'POST':
        # Get data from the submitted form
        name = request.form['name']
        address = request.form.get('address', '') # .get() is safer for optional fields
        phone = request.form.get('phone', '')
        email = request.form['email']

        # Basic server-side validation
        if not name or not email:
            flash('Customer name and email are required!', 'danger')
            return render_template('add_customer.html')

        db = database.get_db() # Get a database connection
        cursor = db.cursor() # Get a cursor to execute SQL commands
        try:
            # Execute the INSERT statement to add the customer
            cursor.execute("INSERT INTO customers (name, address, phone, email) VALUES (?, ?, ?, ?)",
                           (name, address, phone, email))
            db.commit() # Save the changes to the database
            flash('Customer added successfully!', 'success')
            return redirect(url_for('view_customers')) # Redirect to the customer list page
        except sqlite3.IntegrityError:
            # Catches error if an email (which must be unique) is duplicated
            flash('Error: Customer with this email already exists.', 'danger')
        except Exception as e:
            # Catches any other general database errors
            flash(f'Error adding customer: {e}', 'danger')
            db.rollback() # Undo any partial changes if an error occurs

    return render_template('add_customer.html') # Render the form for GET requests or if POST fails

@app.route('/view_customers')
def view_customers():
    """Displays a list of all registered customers."""
    db = database.get_db()
    customers = db.execute("SELECT * FROM customers ORDER BY name").fetchall()
    return render_template('view_customers.html', customers=customers)

@app.route('/generate_bill', methods=['GET', 'POST'])
def generate_bill():
    """Handles the creation of new bills and their associated items."""
    db = database.get_db()
    # Fetch all customers to populate the dropdown in the form
    customers = db.execute("SELECT id, name FROM customers ORDER BY name").fetchall()

    if request.method == 'POST':
        customer_id = request.form['customer_id']
        # .getlist() is used for form fields with multiple values (like item_name[])
        item_names = request.form.getlist('item_name[]')
        quantities = request.form.getlist('quantity[]')
        unit_prices = request.form.getlist('unit_price[]')

        # --- Server-side validation for the bill form ---
        if not customer_id:
            flash('Please select a customer.', 'danger')
            return render_template('generate_bill.html', customers=customers)

        processed_items = []
        total_bill_amount = 0.0

        # Iterate through each submitted item row
        for i in range(len(item_names)):
            item_name_val = item_names[i].strip()
            quantity_val = quantities[i].strip()
            unit_price_val = unit_prices[i].strip()

            # Skip completely empty rows (if user added and then left blank)
            if not item_name_val and not quantity_val and not unit_price_val:
                continue

            # Validate individual item fields
            if not item_name_val:
                flash(f'Item name for row {i+1} cannot be empty.', 'danger')
                return render_template('generate_bill.html', customers=customers)

            try:
                quantity = int(quantity_val)
                unit_price = float(unit_price_val)
            except ValueError:
                flash(f'Quantity and Unit Price for row {i+1} must be valid numbers.', 'danger')
                return render_template('generate_bill.html', customers=customers)

            if quantity <= 0:
                flash(f'Quantity for item "{item_name_val}" must be a positive number.', 'danger')
                return render_template('generate_bill.html', customers=customers)
            if unit_price < 0:
                flash(f'Unit price for item "{item_name_val}" cannot be negative.', 'danger')
                return render_template('generate_bill.html', customers=customers)

            # Calculate total price for this item and add to overall bill total
            total_item_price = quantity * unit_price
            total_bill_amount += total_item_price
            processed_items.append((item_name_val, quantity, unit_price, total_item_price))

        # Ensure at least one valid item was provided for the bill
        if not processed_items:
            flash('Please add at least one valid item to the bill.', 'danger')
            return render_template('generate_bill.html', customers=customers)

        # --- Database Transaction for Bill and Items ---
        try:
            cursor = db.cursor()

            # 1. Insert the main bill record into the 'bills' table
            cursor.execute("INSERT INTO bills (customer_id, total_amount) VALUES (?, ?)",
                           (customer_id, total_bill_amount))
            bill_id = cursor.lastrowid # Get the ID of the newly inserted bill

            # 2. Insert each processed item into the 'bill_items' table
            for item in processed_items:
                cursor.execute("INSERT INTO bill_items (bill_id, item_name, quantity, unit_price, total_item_price) VALUES (?, ?, ?, ?, ?)",
                               (bill_id, item[0], item[1], item[2], item[3]))

            db.commit() # Save all changes to the database as a single transaction
            flash(f'Bill #{bill_id} successfully added!', 'success')
            # Redirect to view the details of the newly created bill
            return redirect(url_for('view_bill', bill_id=bill_id))

        except Exception as e:
            db.rollback() # If any error occurs during the insertions, undo all changes
            flash(f'An error occurred while adding the bill: {e}', 'danger')

    # For GET requests (when you first load the page), just render the form
    return render_template('generate_bill.html', customers=customers)

@app.route('/view_bills')
def view_bills():
    """Displays a summary list of all generated bills."""
    db = database.get_db()
    bills = db.execute("""
        SELECT
            b.id,
            c.name AS customer_name,
            b.bill_date,
            b.total_amount,
            b.status
        FROM
            bills b
        JOIN
            customers c ON b.customer_id = c.id
        ORDER BY
            b.bill_date DESC
    """).fetchall()
    return render_template('view_bills.html', bills=bills)

@app.route('/view_bill/<int:bill_id>')
def view_bill(bill_id):
    """Displays detailed information for a specific bill."""
    db = database.get_db()
    # Fetch bill details along with customer information
    bill = db.execute("""
        SELECT
            b.id,
            c.name AS customer_name,
            c.address,
            c.phone,
            c.email,
            b.bill_date,
            b.total_amount,
            b.status
        FROM
            bills b
        JOIN
            customers c ON b.customer_id = c.id
        WHERE b.id = ?
    """, (bill_id,)).fetchone() # .fetchone() gets one row

    if bill is None:
        flash('Bill not found.', 'danger')
        return redirect(url_for('view_bills'))

    # Fetch all items associated with this bill
    items = db.execute("SELECT * FROM bill_items WHERE bill_id = ?", (bill_id,)).fetchall()

    return render_template('bill_details.html', bill=bill, items=items)

# This block runs the Flask development server when you execute app.py directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
