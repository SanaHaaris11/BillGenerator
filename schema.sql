DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS bill_items;

CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT,
    phone TEXT,
    email TEXT UNIQUE NOT NULL
);

CREATE TABLE bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    bill_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'unpaid',
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE bill_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_item_price REAL NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(id)
);