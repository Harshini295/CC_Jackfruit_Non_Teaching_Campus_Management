-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS campus_management_final;
USE campus_management_final;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS contractor_feedback;
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS contractor_payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS menu_items;
DROP TABLE IF EXISTS food_categories;
DROP TABLE IF EXISTS inventory_restocks;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS canteen_staff;
DROP TABLE IF EXISTS contracts;


DROP TABLE IF EXISTS contractor_services;
DROP TABLE IF EXISTS contractors;


-- Contractor table with rating columns included
CREATE TABLE contractors (
    contractor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    service_type ENUM('canteen', 'cleaning', 'security', 'maintenance', 'other') NOT NULL,
    contract_start_date DATE,
    contract_end_date DATE,
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    feedback_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Contracts table
CREATE TABLE contracts (
    contract_id INT AUTO_INCREMENT PRIMARY KEY,
    contractor_id INT NOT NULL,
    contract_title VARCHAR(200) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    payment_terms TEXT,
    terms_and_conditions TEXT,
    status ENUM('draft', 'active', 'completed', 'terminated') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id) ON DELETE CASCADE
);

-- Canteen staff
CREATE TABLE canteen_staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    contractor_id INT,
    name VARCHAR(100) NOT NULL,
    role ENUM('manager', 'cashier', 'cook', 'helper', 'cleaner') NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    hire_date DATE,
    salary DECIMAL(10,2),
    status ENUM('active', 'inactive', 'on_leave') DEFAULT 'active',
    FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id) ON DELETE SET NULL
);

-- Food categories
CREATE TABLE food_categories (
    canteen_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

-- Menu items
CREATE TABLE menu_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    canteen_id INT,
    description TEXT,
    price DECIMAL(8,2) NOT NULL,
    preparation_time INT DEFAULT NULL, -- in minutes
    is_available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (canteen_id) REFERENCES contractors(contractor_id) ON DELETE SET NULL
);

-- Inventory
CREATE TABLE inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    category ENUM('vegetable', 'fruit', 'dairy', 'meat', 'grocery', 'beverage', 'other') NOT NULL,
    quantity DECIMAL(8,2) NOT NULL,
    unit ENUM('kg', 'g', 'l', 'ml', 'piece', 'packet') NOT NULL,
    threshold_level DECIMAL(8,2),
    last_restocked DATE,
    supplier_info TEXT,
    storage_location VARCHAR(50)
);

-- Orders
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_phone VARCHAR(20),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'preparing', 'ready', 'delivered', 'cancelled') DEFAULT 'pending',
    total_amount DECIMAL(10,2),
    payment_method ENUM('cash', 'card', 'upi', 'campus_wallet'),
    payment_status ENUM('pending', 'paid', 'refunded') DEFAULT 'pending',
    staff_id INT,
    notes TEXT,
    FOREIGN KEY (staff_id) REFERENCES canteen_staff(staff_id) ON DELETE SET NULL
);

-- Order items
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    special_requests TEXT,
    price_at_order DECIMAL(8,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id) ON DELETE CASCADE
);

-- Payments to contractors
CREATE TABLE contractor_payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    contract_id INT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method ENUM('bank_transfer', 'cheque', 'cash', 'online') NOT NULL,
    reference_number VARCHAR(100),
    description TEXT,
    status ENUM('pending', 'processed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE CASCADE
);

-- Feedback
CREATE TABLE feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    rating TINYINT CHECK (rating BETWEEN 1 AND 5),
    comments TEXT,
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL
);

-- Inventory restocks
CREATE TABLE IF NOT EXISTS inventory_restocks (
    restock_id INT AUTO_INCREMENT PRIMARY KEY,
    inventory_id INT NOT NULL,
    quantity_added DECIMAL(10,2) NOT NULL,
    restock_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    supplier_info VARCHAR(255),
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id)
);

-- Contractor feedback table
CREATE TABLE contractor_feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    contractor_id INT NOT NULL,
    order_id INT,
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comments TEXT,
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL
);


-- Update the order_items table to include item_name
ALTER TABLE order_items
ADD COLUMN item_name VARCHAR(100) NOT NULL AFTER item_id;

-- Add the missing columns to your orders table
ALTER TABLE orders
ADD COLUMN tax_amount DECIMAL(10,2) AFTER total_amount,
ADD COLUMN grand_total DECIMAL(10,2) AFTER tax_amount;
-- View all tables
ALTER TABLE canteen_staff
ADD COLUMN service_type ENUM('Canteen', 'Cleaning', 'Security', 'Other') NOT NULL;

CREATE TABLE contractor_services (
    contractor_id INT NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    PRIMARY KEY (contractor_id, service_type),
    FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


SHOW TABLES;
-- Contractors
INSERT INTO contractors (contractor_id, name, contact_person, phone, email, address, service_type, contract_start_date, contract_end_date, status, average_rating, feedback_count, created_at, updated_at)
VALUES
(1, 'Fresh Bite Ltd', 'Alice Smith', '1234567890', 'alice@freshbite.com', '123 Main Street', 'canteen', '2021-01-01', '2024-12-31', 'active', 4.5, 12, NOW(), NOW()),
(2, 'Campus Eats', 'Bob Johnson', '2345678901', 'bob@campuseats.com', '456 College Ave', 'canteen', '2020-06-01', '2025-05-31', 'active', 4.2, 20, NOW(), NOW()),
(3, 'QuickServe', 'Carol Lee', '3456789012', 'carol@quickserve.com', '789 University Road', 'canteen', '2022-03-15', '2024-11-30', 'active', 4.8, 7, NOW(), NOW()),
(4, 'Tasty Treats', 'David Kim', '4567890123', 'david@tastytreats.com', '101 Student Plaza', 'canteen', '2021-09-01', '2024-08-31', 'active', 4.0, 15, NOW(), NOW()),
(5, 'Food Fusion', 'Emma Brown', '5678901234', 'emma@foodfusion.com', '202 Hostel Lane', 'canteen', '2022-01-10', '2024-12-10', 'active', 4.6, 10, NOW(), NOW());

-- Contracts
INSERT INTO contracts (contract_id, contractor_id, contract_title, description, start_date, end_date, total_amount, payment_terms, terms_and_conditions, status, created_at, updated_at)
VALUES
(1, 1, 'Canteen Service Contract 1', 'Annual food supply service.', '2022-01-01', '2024-12-31', 80000.00, 'Monthly', 'Standard conditions', 'active', NOW(), NOW()),
(2, 2, 'Canteen Service Contract 2', 'Yearly food services.', '2021-06-01', '2024-06-01', 95000.00, 'Quarterly', 'Standard conditions', 'active', NOW(), NOW()),
(3, 3, 'Canteen Service Contract 3', 'Complete meal services.', '2022-03-15', '2024-11-30', 90000.00, 'Monthly', 'Standard conditions', 'active', NOW(), NOW()),
(4, 4, 'Canteen Service Contract 4', 'Canteen management.', '2021-09-01', '2024-08-31', 85000.00, 'Monthly', 'Standard conditions', 'active', NOW(), NOW()),
(5, 5, 'Canteen Service Contract 5', 'Meal and snacks service.', '2022-01-10', '2024-12-10', 88000.00, 'Monthly', 'Standard conditions', 'active', NOW(), NOW());

-- Canteen Staff
INSERT INTO canteen_staff (staff_id, contractor_id, name, role, phone, email, hire_date, salary, status, service_type)
VALUES
(1, 1, 'John Doe', 'cook', '9001112233', 'john@canteen.com', '2022-01-15', 18000.00, 'active', 'Canteen'),
(2, 2, 'Jane Roe', 'manager', '9002223344', 'jane@canteen.com', '2021-07-20', 25000.00, 'active', 'Canteen'),
(3, 3, 'Mike Chan', 'cashier', '9003334455', 'mike@canteen.com', '2022-04-05', 17000.00, 'active', 'Canteen'),
(4, 4, 'Sara Lim', 'helper', '9004445566', 'sara@canteen.com', '2021-11-01', 15000.00, 'active', 'Canteen'),
(5, 5, 'Tom Wright', 'cook', '9005556677', 'tom@canteen.com', '2022-02-10', 19000.00, 'active', 'Canteen');

-- Food Categories
INSERT INTO food_categories (canteen_id, name, description)
VALUES
(1, 'Main Course', 'Rice, curries, and breads'),
(2, 'Snacks', 'Light items and finger food'),
(3, 'Beverages', 'Drinks and refreshers'),
(4, 'Desserts', 'Sweets and ice creams'),
(5, 'Breakfast', 'Morning meals');

-- Menu Items (linked to contractor, not food category directly)
INSERT INTO menu_items (item_id, name, canteen_id, description, price, preparation_time, is_available)
VALUES
(1, 'Veg Thali', 1, 'Full meal with veggies', 120.00, 10, TRUE),
(2, 'Samosa', 2, 'Spicy potato snack', 20.00, 5, TRUE),
(3, 'Lassi', 3, 'Chilled yogurt drink', 30.00, 2, TRUE),
(4, 'Gulab Jamun', 4, 'Sweet dessert', 40.00, 3, TRUE),
(5, 'Idli Vada', 5, 'Breakfast combo', 50.00, 7, TRUE);

-- Inventory
INSERT INTO inventory (inventory_id, item_name, category, quantity, unit, threshold_level, last_restocked, supplier_info, storage_location)
VALUES
(1, 'Rice', 'grocery', 100, 'kg', 20, '2024-01-10', 'Agro Supplier', 'Pantry 1'),
(2, 'Milk', 'dairy', 50, 'l', 10, '2024-02-01', 'Dairy Corp', 'Fridge A'),
(3, 'Potatoes', 'vegetable', 75, 'kg', 15, '2024-03-05', 'Fresh Farms', 'Pantry 2'),
(4, 'Coke', 'beverage', 100, 'packet', 30, '2024-03-20', 'Beverage Inc', 'Fridge B'),
(5, 'Sugar', 'grocery', 40, 'kg', 10, '2024-04-01', 'SweetSupplies', 'Pantry 3');

-- Orders
INSERT INTO orders (order_id, customer_name, customer_phone, order_date, status, total_amount, payment_method, payment_status, staff_id, notes, tax_amount, grand_total)
VALUES
(1, 'Student A', '9991110001', NOW(), 'pending', 100.00, 'cash', 'pending', 1, 'Extra spicy', 10.00, 110.00),
(2, 'Student B', '9991110002', NOW(), 'pending', 120.00, 'card', 'pending', 2, '', 12.00, 132.00),
(3, 'Student C', '9991110003', NOW(), 'pending', 90.00, 'upi', 'pending', 3, '', 9.00, 99.00),
(4, 'Student D', '9991110004', NOW(), 'pending', 60.00, 'cash', 'pending', 4, '', 6.00, 66.00),
(5, 'Student E', '9991110005', NOW(), 'pending', 150.00, 'campus_wallet', 'pending', 5, 'No onions', 15.00, 165.00);

-- Order Items
INSERT INTO order_items (order_item_id, order_id, item_id, quantity, special_requests, price_at_order, item_name)
VALUES
(1, 1, 1, 1, 'Less spicy', 120.00, 'Veg Thali'),
(2, 2, 2, 2, 'Extra chutney', 20.00, 'Samosa'),
(3, 3, 3, 1, '', 30.00, 'Lassi'),
(4, 4, 4, 2, '', 40.00, 'Gulab Jamun'),
(5, 5, 5, 1, '', 50.00, 'Idli Vada');

-- Contractor Payments
INSERT INTO contractor_payments (payment_id, contract_id, amount, payment_date, payment_method, reference_number, description, status, created_at)
VALUES
(1, 1, 20000.00, '2024-01-10', 'online', 'REF12345', 'Monthly Jan', 'processed', NOW()),
(2, 2, 22000.00, '2024-01-15', 'cash', 'REF12346', 'Monthly Jan', 'processed', NOW()),
(3, 3, 18000.00, '2024-01-20', 'bank_transfer', 'REF12347', 'Monthly Jan', 'processed', NOW()),
(4, 4, 24000.00, '2024-01-25', 'online', 'REF12348', 'Monthly Jan', 'processed', NOW()),
(5, 5, 25000.00, '2024-01-30', 'cheque', 'REF12349', 'Monthly Jan', 'processed', NOW());

-- Feedback
INSERT INTO feedback (feedback_id, order_id, rating, comments, feedback_date)
VALUES
(1, 1, 5, 'Excellent food!', NOW()),
(2, 2, 4, 'Tasty snacks', NOW()),
(3, 3, 5, 'Loved the drink!', NOW()),
(4, 4, 4, 'Sweet was nice', NOW()),
(5, 5, 5, 'Perfect breakfast!', NOW());

-- Inventory Restocks
INSERT INTO inventory_restocks (restock_id, inventory_id, quantity_added, restock_date, supplier_info)
VALUES
(1, 1, 50, NOW(), 'Agro Supplier'),
(2, 2, 20, NOW(), 'Dairy Corp'),
(3, 3, 30, NOW(), 'Fresh Farms'),
(4, 4, 40, NOW(), 'Beverage Inc'),
(5, 5, 25, NOW(), 'SweetSupplies');

-- Contractor Feedback
INSERT INTO contractor_feedback (feedback_id, contractor_id, order_id, rating, comments, feedback_date)
VALUES
(1, 1, 1, 5, 'Great service!', NOW()),
(2, 2, 2, 4, 'Reliable staff', NOW()),
(3, 3, 3, 5, 'Very good food', NOW()),
(4, 4, 4, 4, 'Responsive team', NOW()),
(5, 5, 5, 5, 'Well managed', NOW());

-- View table structures (sample)
SELECT * FROM contractors;
SELECT * FROM menu_items ;
SELECT * FROM order_items ;
SELECT * FROM orders ;
SELECT * FROM inventory ;
SELECT * FROM canteen_staff ;
SELECT * FROM contracts ;