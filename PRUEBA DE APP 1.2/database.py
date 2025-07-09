# database.py
import sqlite3
import os
from datetime import datetime

DATABASE_FILE = "demoga_emaldo.db"

def connect_db():
    """Crea una conexión a la base de datos SQLite."""
    db_path = os.path.join(os.path.dirname(__file__), DATABASE_FILE)
    conn = sqlite3.connect(db_path)
    return conn

def create_tables():
    """Crea todas las tablas en la base de datos si no existen."""
    conn = connect_db()
    cursor = conn.cursor()
    # ... (El código de create_tables no cambia, se mantiene igual)
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL, role TEXT NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS products (code TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT, supplier TEXT, stock INTEGER NOT NULL, sale_price REAL NOT NULL, cost_price REAL NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_number TEXT NOT NULL, product_code TEXT NOT NULL, quantity_sold INTEGER NOT NULL, total_price REAL NOT NULL, customer_name TEXT, seller_name TEXT, sale_date TEXT NOT NULL, FOREIGN KEY (product_code) REFERENCES products (code));")
    cursor.execute("CREATE TABLE IF NOT EXISTS purchases (id INTEGER PRIMARY KEY AUTOINCREMENT, po_number TEXT NOT NULL, product_code TEXT NOT NULL, quantity_received INTEGER NOT NULL, supplier_name TEXT, purchase_date TEXT NOT NULL, status TEXT NOT NULL, FOREIGN KEY (product_code) REFERENCES products (code));")
    conn.commit()
    conn.close()

# --- Funciones para Usuarios (sin cambios) ---
def get_all_users():
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("SELECT full_name, email, role FROM users")
    users = cursor.fetchall(); conn.close(); return users
def add_user(full_name, email, password, role):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (full_name, email, password, role) VALUES (?, ?, ?, ?)", (full_name, email, password, role))
        conn.commit(); return True
    except sqlite3.IntegrityError: return False
    finally: conn.close()
def check_user_credentials(email, password):
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone(); conn.close(); return user is not None
def delete_user(email):
    conn = connect_db(); cursor = conn.cursor()
    if email == 'admin': conn.close(); return False
    cursor.execute("DELETE FROM users WHERE email = ?", (email,)); conn.commit()
    success = cursor.rowcount > 0; conn.close(); return success
def get_user_by_email(email):
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("SELECT full_name, email, role FROM users WHERE email = ?", (email,))
    user = cursor.fetchone(); conn.close(); return user
def update_user(original_email, full_name, new_email, role):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET full_name = ?, email = ?, role = ? WHERE email = ?", (full_name, new_email, role, original_email))
        conn.commit(); return True
    except sqlite3.IntegrityError: return False
    finally: conn.close()
def update_user_password(email, new_password):
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email)); conn.commit(); conn.close()

# --- Funciones para Productos (ACTUALIZADO) ---
def get_all_products():
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("SELECT code, name, category, supplier, stock, sale_price, cost_price FROM products")
    products = cursor.fetchall(); conn.close(); return products

def update_product(code, name, category, supplier, sale_price, cost_price):
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("UPDATE products SET name = ?, category = ?, supplier = ?, sale_price = ?, cost_price = ? WHERE code = ?", (name, category, supplier, sale_price, cost_price, code))
    conn.commit(); conn.close()

# --- NUEVO: Funciones para Añadir y Eliminar Productos ---
def add_product(code, name, category, supplier, stock, sale_price, cost_price):
    """Añade un nuevo producto a la base de datos."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?)",
                       (code, name, category, supplier, stock, sale_price, cost_price))
        conn.commit()
        return True
    except sqlite3.IntegrityError: # Ocurre si el código (PRIMARY KEY) ya existe
        return False
    finally:
        conn.close()

def delete_product(code):
    """Elimina un producto de la base de datos usando su código."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE code = ?", (code,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# --- Funciones para Ventas, Compras y KPIs (sin cambios) ---
def get_sales_history():
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("SELECT s.sale_date, s.invoice_number, p.name, p.category, s.customer_name, s.total_price, s.seller_name FROM sales s JOIN products p ON s.product_code = p.code ORDER BY s.sale_date DESC")
    sales = cursor.fetchall(); conn.close(); return sales
def register_sale(product_code, quantity, customer_name, seller_name):
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("SELECT stock, sale_price FROM products WHERE code = ?", (product_code,)); product = cursor.fetchone()
    if not product: conn.close(); return "Producto no encontrado."
    current_stock, sale_price = product
    if quantity > current_stock: conn.close(); return f"Stock insuficiente. Solo hay {current_stock}."
    new_stock = current_stock - quantity; total_price = quantity * sale_price
    cursor.execute("UPDATE products SET stock = ? WHERE code = ?", (new_stock, product_code))
    sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S"); invoice_number = f"INV-{int(datetime.now().timestamp())}"
    cursor.execute("INSERT INTO sales (invoice_number, product_code, quantity_sold, total_price, customer_name, seller_name, sale_date) VALUES (?, ?, ?, ?, ?, ?, ?)", (invoice_number, product_code, quantity, total_price, customer_name, seller_name, sale_date))
    conn.commit(); conn.close(); return "Venta registrada con éxito."
def get_purchase_history():
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("SELECT pu.purchase_date, pu.po_number, p.name, pu.supplier_name, pu.quantity_received, pu.status FROM purchases pu JOIN products p ON pu.product_code = p.code ORDER BY pu.purchase_date DESC")
    purchases = cursor.fetchall(); conn.close(); return purchases
def register_purchase(product_code, quantity, supplier_name):
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("SELECT stock FROM products WHERE code = ?", (product_code,)); product = cursor.fetchone()
    if not product: conn.close(); return "Producto no encontrado."
    new_stock = product[0] + quantity
    cursor.execute("UPDATE products SET stock = ? WHERE code = ?", (new_stock, product_code))
    purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S"); po_number = f"PO-{int(datetime.now().timestamp())}"
    cursor.execute("INSERT INTO purchases (po_number, product_code, quantity_received, supplier_name, purchase_date, status) VALUES (?, ?, ?, ?, ?, ?)", (po_number, product_code, quantity, supplier_name, purchase_date, "Recibido"))
    conn.commit(); conn.close(); return "Compra registrada y stock actualizado con éxito."
def get_dashboard_kpis():
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("SELECT SUM(total_price) FROM sales WHERE strftime('%Y-%m', sale_date) = strftime('%Y-%m', 'now')")
    monthly_sales = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT SUM(stock * cost_price) FROM products")
    inventory_value = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT COUNT(*) FROM purchases")
    pending_orders = cursor.fetchone()[0] or 0
    conn.close()
    return {"ventas_mes": monthly_sales, "valor_inventario": inventory_value, "ordenes_pendientes": pending_orders}

# --- Inicializar la base de datos al importar ---
create_tables()
