import sqlite3 as sq
con=sq.connect("zambare.db")
cur=con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,category TEXT NOT NULL,description TEXT,price REAL NOT NULL,stock INTEGER NOT NULL DEFAULT 0,image TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'customer')")
cur.execute("CREATE TABLE IF NOT EXISTS cart (id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,product_id INTEGER NOT NULL,quantity INTEGER NOT NULL DEFAULT 1,UNIQUE(user_id, product_id))")
cur.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,total REAL NOT NULL,address TEXT NOT NULL,payment_method TEXT NOT NULL DEFAULT 'COD',status TEXT NOT NULL DEFAULT 'Order Placed',created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
cur.execute("CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY AUTOINCREMENT,order_id INTEGER NOT NULL,product_id INTEGER NOT NULL,quantity INTEGER NOT NULL,price REAL NOT NULL)")
# Check existing users table columns
cur.execute("PRAGMA table_info(users)")
columns = [row[1] for row in cur.fetchall()]

# Add contact column
if "contact" not in columns:
    cur.execute("ALTER TABLE users ADD COLUMN contact TEXT")

# Add city column
if "city" not in columns:
    cur.execute("ALTER TABLE users ADD COLUMN city TEXT")

cur.execute("CREATE TABLE IF NOT EXISTS user_wishlist (wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,product_id INTEGER NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(user_id, product_id))")
# cur.execute("drop table cart")


print("Users table updated successfully!")
con.commit()
con.close()
# print("Zambre Agencies database created successfully!")
