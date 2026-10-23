from flask import * 
import sqlite3 as sq
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
load_dotenv()

app=Flask(__name__)

app.secret_key =os.getenv("SECRET_KEY")

#user_Panel
#home page
@app.route("/")
def home():

    con = sq.connect("zambare.db", timeout=10)
    con.row_factory = sq.Row
    cur = con.cursor()

    # Get latest products
    cur.execute("SELECT *FROM products ORDER BY id DESC LIMIT 12")

    products = cur.fetchall()

    con.close()

    # Products for moving banner
    featured_products = products[:5]

    return render_template("home.html",pd=products,featured_products=featured_products)

#about Page

@app.route("/about")
def about():
    return render_template("about.html")


#user-categories Page
@app.route("/ucategories")
def ucategories():

    category_list = ["Hardware","Electrical","Water Motors, Pumps & Accessories","Pipes & Irrigation","Sprayers & Farming Tools"]

    con = sq.connect("zambare.db", timeout=10)
    cur = con.cursor()

    # Count products in each category
    category_counts = {
        category: 0 for category in category_list
    }

    cur.execute("SELECT category, COUNT(*)FROM products GROUP BY category")

    rows = cur.fetchall()

    for category, count in rows:
        if category in category_counts:
            category_counts[category] = count

    con.close()

    return render_template("ucategories.html",categories=category_list,category_counts=category_counts)


@app.route("/products")
def products():

    selected_category = request.args.get("category", "").strip()

    con = sq.connect("zambare.db")
    con.row_factory = sq.Row
    cur = con.cursor()

    # Get categories from database
    cur.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND TRIM(category) != ''ORDER BY category COLLATE NOCASE")

    categories = [row["category"] for row in cur.fetchall()]

    # Get all existing products
    cur.execute("SELECT *FROM products ORDER BY id DESC")

    all_products = cur.fetchall()

    # Get products for selected category
    category_products = []

    if selected_category in categories:

        cur.execute("SELECT *FROM products WHERE category = ? ORDER BY id DESC", (selected_category,))

        category_products = cur.fetchall()

    con.close()

    return render_template("products.html",categories=categories,selected_category=selected_category,category_products=category_products,all_products=all_products)


#cart Page
@app.route("/cart")
def cart():

    if "user_id" not in session or session.get("role") != "customer":
        flash("Please login to view your cart.")
        return redirect(url_for("login"))

    con = sq.connect("zambare.db")
    con.row_factory = sq.Row
    cur = con.cursor()

    # Create cart table if it does not exist
    cur.execute("CREATE TABLE IF NOT EXISTS user_cart (cart_id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,product_id INTEGER NOT NULL,quantity INTEGER NOT NULL DEFAULT 1,UNIQUE(user_id, product_id))")

    # Get logged-in customer's cart products
    cur.execute("SELECT user_cart.cart_id,user_cart.quantity,products.id AS product_id,products.name,products.image,products.price,products.stock,products.category FROM user_cart JOIN products ON user_cart.product_id = products.id WHERE user_cart.user_id = ? ORDER BY user_cart.cart_id DESC", (session["user_id"],))

    cart_items = cur.fetchall()

    # Calculate cart total
    grand_total = sum(
        item["price"] * item["quantity"]
        for item in cart_items
    )

    con.close()

    return render_template("cart.html",cart_items=cart_items,grand_total=grand_total)


# =========================================
# REMOVE ITEM FROM CART
# =========================================

@app.route("/remove_from_cart/<int:cart_id>", methods=["POST"])
def remove_from_cart(cart_id):

    if "user_id" not in session or session.get("role") != "customer":
        flash("Please login first.")
        return redirect(url_for("login"))

    con = sq.connect("zambare.db")
    cur = con.cursor()

    cur.execute(" DELETE FROM user_cart WHERE cart_id = ? AND user_id = ?", (cart_id, session["user_id"]))

    con.commit()
    con.close()

    flash("Product removed from cart.")
    return redirect(url_for("cart"))

@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

    if (
        "user_id" not in session
        or session.get("role") != "customer"
    ):
        flash("Please login as a customer to add products.")
        return redirect(url_for("login"))

    con = sq.connect("zambare.db")
    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS user_cart ( cart_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, product_id INTEGER NOT NULL, quantity INTEGER NOT NULL DEFAULT 1, UNIQUE(user_id, product_id))")

    cur.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
    product = cur.fetchone()

    if product is None:
        con.close()
        flash("Product not found.")
        return redirect(url_for("products"))

    stock = product[0]

    if stock <= 0:
        con.close()
        flash("This product is out of stock.")
        return redirect(url_for("products"))

    user_id = session["user_id"]

    cur.execute(" SELECT quantity FROM user_cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))

    existing = cur.fetchone()

    if existing:
        if existing[0] >= stock:
            con.close()
            flash("You cannot add more than the available stock.")
            return redirect(url_for("products"))

        cur.execute(" UPDATE user_cart SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?", (user_id, product_id))

    else:
        cur.execute("INSERT INTO user_cart (user_id, product_id, quantity) VALUES (?, ?, 1)", (user_id, product_id))

    con.commit()
    con.close()

    flash("Product added to cart successfully!")
    return redirect(url_for("products"))

# =========================================
# CHECKOUT PAGE
# =========================================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    if "user_id" not in session or session.get("role") != "customer":
        flash("Please login to continue.")
        return redirect(url_for("login"))

    con = sq.connect("zambare.db")
    con.row_factory = sq.Row
    cur = con.cursor()

    # Create order tables if they do not exist
    cur.execute(" CREATE TABLE IF NOT EXISTS customer_orders (order_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, fullname TEXT NOT NULL, contact TEXT NOT NULL, address TEXT NOT NULL, city TEXT NOT NULL, pincode TEXT NOT NULL, payment_method TEXT NOT NULL, total_amount REAL NOT NULL,order_status TEXT NOT NULL DEFAULT 'Placed',order_date TEXT DEFAULT CURRENT_TIMESTAMP)")

    cur.execute("CREATE TABLE IF NOT EXISTS customer_order_items (item_id INTEGER PRIMARY KEY AUTOINCREMENT,order_id INTEGER NOT NULL,product_id INTEGER NOT NULL,product_name TEXT NOT NULL,unit_price REAL NOT NULL,quantity INTEGER NOT NULL,line_total REAL NOT NULL,image TEXT)")

    # Get the logged-in customer's cart
    cur.execute("SELECT user_cart.cart_id,user_cart.quantity,products.id AS product_id,products.name,products.image,products.price,products.stock,products.category FROM user_cart JOIN products ON user_cart.product_id = products.id WHERE user_cart.user_id = ? ORDER BY user_cart.cart_id DESC", (session["user_id"],))

    cart_items = cur.fetchall()

    if not cart_items:
        con.close()
        flash("Your cart is empty. Please add products first.")
        return redirect(url_for("products"))

    grand_total = sum(
        item["price"] * item["quantity"]
        for item in cart_items
    )

    # Display checkout form
    if request.method == "GET":
        con.close()

        return render_template("checkout.html",cart_items=cart_items,grand_total=grand_total,user_name=session.get("user_name", ""))

    # Read delivery details
    fullname = request.form.get("fullname", "").strip()
    contact = request.form.get("contact", "").strip()
    address = request.form.get("address", "").strip()
    city = request.form.get("city", "").strip()
    pincode = request.form.get("pincode", "").strip()
    payment_method = request.form.get("payment_method", "COD")

    if not all([fullname, contact, address, city, pincode]):
        con.close()
        flash("Please fill in all delivery details.")
        return redirect(url_for("checkout"))

    # COD is the only payment method enabled in this step
    if payment_method != "COD":
        con.close()
        flash("Please select Cash on Delivery.")
        return redirect(url_for("checkout"))

    try:
        # Create the order
        cur.execute("INSERT INTO customer_orders(user_id, fullname, contact, address,city, pincode, payment_method,total_amount, order_status)VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Placed')", (
            session["user_id"],
            fullname,
            contact,
            address,
            city,
            pincode,
            payment_method,
            grand_total
        ))

        order_id = cur.lastrowid

        # Save each order item and reduce stock safely
        for item in cart_items:

            cur.execute("UPDATE products SET stock = stock - ?WHERE id = ? AND stock >= ?", (
                item["quantity"],
                item["product_id"],
                item["quantity"]
            ))

            if cur.rowcount != 1:
                con.rollback()
                con.close()
                flash(
                    "Stock is no longer sufficient for "
                    + item["name"]
                    + ". Please review your cart."
                )
                return redirect(url_for("cart"))

            cur.execute("INSERT INTO customer_order_items( order_id, product_id, product_name, unit_price, quantity, line_total, image)VALUES (?, ?, ?, ?, ?, ?, ?)", (
                order_id,
                item["product_id"],
                item["name"],
                item["price"],
                item["quantity"],
                item["price"] * item["quantity"],
                item["image"]
            ))

        # Empty this customer's cart only after saving the order
        cur.execute(" DELETE FROM user_cart WHERE user_id = ?", (session["user_id"],))

        con.commit()
        con.close()

        return redirect(
            url_for("order_success", order_id=order_id)
        )

    except sq.Error:
        con.rollback()
        con.close()
        flash("Unable to place your order. Please try again.")
        return redirect(url_for("checkout"))


# =========================================
# ORDER SUCCESS PAGE
# =========================================

@app.route("/order_success/<int:order_id>")
def order_success(order_id):

    if "user_id" not in session or session.get("role") != "customer":
        flash("Please login to view your order.")
        return redirect(url_for("login"))

    con = sq.connect("zambare.db")
    con.row_factory = sq.Row
    cur = con.cursor()

    # Only allow the owner to view this order
    cur.execute("SELECT * FROM customer_orders WHERE order_id = ? AND user_id = ?", (order_id, session["user_id"]))

    order = cur.fetchone()

    if order is None:
        con.close()
        flash("Order not found.")
        return redirect(url_for("products"))

    cur.execute(" SELECT *FROM customer_order_items WHERE order_id = ?ORDER BY item_id", (order_id,))

    order_items = cur.fetchall()
    con.close()

    return render_template("order_success.html",order=order,order_items=order_items)

# =========================================
# MY ORDERS - CUSTOMER
# =========================================

@app.route("/my_orders")
def my_orders():

    # Check customer login
    if "user_id" not in session or session.get("role") != "customer":
        flash("Please login to view your orders.")
        return redirect(url_for("login"))

    con = sq.connect("zambare.db")
    con.row_factory = sq.Row
    cur = con.cursor()

    # Get orders of the logged-in customer
    cur.execute("SELECT *FROM customer_orders WHERE user_id = ? ORDER BY order_id DESC", (session["user_id"],))

    orders = cur.fetchall()

    # Get products belonging to each order
    order_items = {}

    for order in orders:

        cur.execute(" SELECT * FROM customer_order_items WHERE order_id = ? ORDER BY item_id", (order["order_id"],))

        order_items[order["order_id"]] = cur.fetchall()

    con.close()

    return render_template("my_orders.html",orders=orders,order_items=order_items)

# =========================================
# USER REGISTRATION
# =========================================

@app.route("/register")
def register():
    return render_template("register.html")



@app.route("/registersave", methods=["POST"])
def registersave():

    fn = request.form["fullname"].strip()
    em = request.form["email"].strip().lower()
    ps = request.form["password"]
    cn = request.form["contact"].strip()
    ct = request.form["city"].strip()

    if not fn or not em or not ps or not cn or not ct:
        flash("Please fill in all fields.")
        return redirect(url_for("register"))

    con = sq.connect("zambare.db")
    cur = con.cursor()

    try:
        cur.execute("INSERT INTO users(name, email, password, contact, city, role)VALUES (?, ?, ?, ?, ?, 'customer')", (fn, em, ps, cn, ct))

        con.commit()
        con.close()

        flash("Registration successful! Please login.")
        return redirect(url_for("login"))

    except sq.IntegrityError:
        con.close()
        flash("This email is already registered.")
        return redirect(url_for("register"))


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/logincheck", methods=["POST"])
def logincheck():

    em = request.form["email"].strip().lower()
    ps = request.form["password"]

    # Admin Login Check
    if em == "zambare@gmail.com" and ps == "admin@123":

        session.clear()
        session["user_id"] = "admin"
        session["user_name"] = "Zambre Admin"
        session["user_email"] = em
        session["role"] = "admin"

        return redirect(url_for("admin_dashboard"))

    # Customer Login Check
    con = sq.connect("zambare.db")
    cur = con.cursor()

    cur.execute("SELECT id, name, email, password, role FROM users WHERE email = ? AND password = ?AND role = 'customer' ", (em, ps))

    user = cur.fetchone()
    con.close()

    if user:

        session.clear()
        session["user_id"] = user[0]
        session["user_name"] = user[1]
        session["user_email"] = user[2]
        session["role"] = user[4]

        # Customer login झाल्यावर Home Page
        return redirect(url_for("home"))

    else:
        flash("Invalid email or password.")
        return redirect(url_for("login"))

# LOGOUT

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out successfully.")

    return redirect(url_for("login"))

# USER DASHBOARD

@app.route("/user_dashboard")
def user_dashboard():

    if "user_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "customer":
        flash("Access denied.")
        return redirect(url_for("login"))

    return render_template("user_dashboard.html")

#admin_panel
@app.route("/admin_dashboard")
def admin_dashboard():

    con = sq.connect("zambare.db")
    con.row_factory = sq.Row
    cur = con.cursor()

    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()

    con.close()

    return render_template("admin_dashboard.html",products=products)


@app.route("/add_product")
def add_product_page():
    return render_template("add_product.html")


@app.route("/add_products", methods=["GET","POST"])
def add_products():

    name = request.form["name"]
    category = request.form["category"]
    description = request.form["description"]
    price = float(request.form["price"])
    stock = int(request.form["stock"])

    image = request.files["image"]

    if image and image.filename:
        filename = secure_filename(image.filename)

        image.save(
            "static/uploads/" + filename
        )
    else:
        flash("Please select product image.")
        return redirect(url_for("add_product_page"))

    con = sq.connect("zambare.db")
    cur = con.cursor()

    cur.execute("INSERT INTO products(name, category, description, price, stock, image) VALUES (?, ?, ?, ?, ?, ?)", (name, category, description,price, stock, filename))

    con.commit()
    con.close()

    flash("Product added successfully!")
    return redirect(url_for("admin_dashboard"))

@app.route("/view_products")
def view_products():

    con = sq.connect("zambare.db")
    con.row_factory = sq.Row
    cur = con.cursor()

    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()

    con.close()

    return render_template("view_products.html",products=products)


@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):

    con = sq.connect("zambare.db")
    con.row_factory = sq.Row
    cur = con.cursor()

    cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cur.fetchone()

    if product is None:
        con.close()
        flash("Product not found.")
        return redirect(url_for("view_products"))

    if request.method == "POST":
        name = request.form["name"].strip()
        category = request.form["category"]
        description = request.form["description"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])

        # Keep the old image if a new image isn't selected
        filename = product["image"]
        image = request.files.get("image")

        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save("static/uploads/" + filename)

        cur.execute("UPDATE products SET name = ?, category = ?, description = ?,price = ?, stock = ?, image = ? WHERE id = ?", (name, category, description, price, stock, filename, product_id))

        con.commit()
        con.close()

        flash("Product updated successfully!")
        return redirect(url_for("view_products"))

    con.close()
    return render_template("edit_product.html", product=product)


@app.route("/delete_product/<int:product_id>", methods=["POST"])
def delete_product(product_id):

    con = sq.connect("zambare.db")
    cur = con.cursor()

    cur.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,)
    )

    con.commit()
    con.close()

    flash("Product deleted successfully!")
    return redirect(url_for("view_products"))


@app.route("/categories")
def categories():

    con = sq.connect("zambare.db")
    cur = con.cursor()

    category_list = [
        "Hardware",
        "Electrical",
        "Water Motors, Pumps & Accessories",
        "Pipes & Irrigation",
        "Sprayers & Farming Tools"
    ]

    category_counts = {category: 0 for category in category_list}

    cur.execute(" SELECT category, COUNT(*) FROM products GROUP BY category")

    rows = cur.fetchall()

    for category, count in rows:
        if category in category_counts:
            category_counts[category] = count

    con.close()

    return render_template("categories.html",categories=category_list,category_counts=category_counts)


@app.route("/category_products")
def category_products():

    category = request.args.get("category", "").strip()

    allowed_categories = [
        "Hardware",
        "Electrical",
        "Water Motors, Pumps & Accessories",
        "Pipes & Irrigation",
        "Sprayers & Farming Tools"
    ]

    if category not in allowed_categories:
        return redirect(url_for("categories"))

    con = sq.connect("zambare.db")
    con.row_factory = sq.Row
    cur = con.cursor()

    cur.execute(" SELECT * FROM products WHERE category = ? ORDER BY id DESC", (category,))

    products = cur.fetchall()
    con.close()

    return render_template(
        "category_products.html",
        products=products,
        category=category
    )



# =========================================
# ADMIN - VIEW CUSTOMER ORDERS
# =========================================

@app.route("/orders")
def orders():

    # Check admin login
    if session.get("role") != "admin":
        flash("Please login as admin to view orders.")
        return redirect(url_for("login"))

    con = sq.connect("zambare.db")
    con.row_factory = sq.Row
    cur = con.cursor()

    # Get orders placed by customers
    cur.execute("SELECT * FROM customer_orders ORDER BY order_id DESC")

    rows = cur.fetchall()

    orders_data = []

    for row in rows:

        orders_data.append({
            "id": row["order_id"],
            "customer": row["fullname"],
            "date": row["order_date"] or "—",
            "amount": row["total_amount"],
            "payment": row["payment_method"],
            "status": row["order_status"]
        })

    con.close()

    return render_template("orders.html",orders=orders_data)

# =========================================
# ADMIN - UPDATE CUSTOMER ORDER STATUS
# =========================================

@app.route("/update_order_status/<int:order_id>", methods=["POST"])
def update_order_status(order_id):

    # Check admin login
    if session.get("role") != "admin":
        flash("Please login as admin to update order status.")
        return redirect(url_for("login"))

    # Read status from the form
    new_status = (
        request.form.get("status")
        or request.form.get("order_status")
        or ""
    ).strip()

    # Allowed delivery statuses
    allowed_statuses = {
        "Placed",
        "Confirmed",
        "Processing",
        "Shipped",
        "Out for Delivery",
        "Delivered",
        "Cancelled"
    }

    # Validate selected status
    status_lookup = {
        status.lower(): status
        for status in allowed_statuses
    }

    normalized_status = (
        new_status.replace("_", " ").replace("-", " ").lower()
    )

    if normalized_status not in status_lookup:
        flash("Please select a valid order status.")
        return redirect(url_for("orders"))

    new_status = status_lookup[normalized_status]

    con = sq.connect("zambare.db")
    cur = con.cursor()

    # Update the customer order
    cur.execute("""
        UPDATE customer_orders
        SET order_status = ?
        WHERE order_id = ?
    """, (new_status, order_id))

    updated = cur.rowcount

    con.commit()
    con.close()

    if updated:
        flash("Order delivery status updated successfully!")
    else:
        flash("Order not found.")

    return redirect(url_for("orders"))

@app.route("/stock")
def stock():

    con = sq.connect("zambare.db")
    con.row_factory = sq.Row
    cur = con.cursor()

    cur.execute("SELECT id, name, category, price, stock, image FROM products ORDER BY stock ASC, name ASC")

    products = cur.fetchall()
    con.close()

    return render_template("stock.html",products=products)


@app.route("/update_stock/<int:product_id>", methods=["POST"])
def update_stock(product_id):

    stock_value = request.form.get("stock", "").strip()

    try:
        quantity = int(stock_value)

        if quantity < 0:
            flash("Stock quantity cannot be negative.")
            return redirect(url_for("stock"))

    except ValueError:
        flash("Please enter a valid whole-number quantity.")
        return redirect(url_for("stock"))

    con = sq.connect("zambare.db")
    cur = con.cursor()

    cur.execute(
        "UPDATE products SET stock = ? WHERE id = ?",
        (quantity, product_id)
    )

    updated = cur.rowcount

    con.commit()
    con.close()

    if updated:
        flash("Stock updated successfully!")
    else:
        flash("Product not found.")

    return redirect(url_for("stock"))

@app.route("/admin_profile")
def admin_profile():
    return render_template("admin_profile.html")

# =========================================
# VIEW MY WISHLIST
# =========================================

@app.route("/wishlist")
def wishlist():

    if (
        "user_id" not in session
        or session.get("role") != "customer"
    ):
        flash("Please login to view your wishlist.")
        return redirect(url_for("login"))
    

    con = sq.connect("zambare.db", timeout=10)
    con.row_factory = sq.Row
    cur = con.cursor()

    cur.execute("SELECT user_wishlist.wishlist_id, products.id AS product_id, products.name, products.category, products.description, products.price, products.stock, products.image FROM user_wishlist JOIN products ON user_wishlist.product_id = products.id WHERE user_wishlist.user_id = ? ORDER BY user_wishlist.wishlist_id DESC", (session["user_id"],))

    wishlist_items = cur.fetchall()

    con.close()

    return render_template("wishlist.html", wishlist_items=wishlist_items)


# =========================================
# ADD PRODUCT TO WISHLIST
# =========================================

@app.route("/add_to_wishlist/<int:product_id>",methods=["POST"])
def add_to_wishlist(product_id):

    if (
        "user_id" not in session
        or session.get("role") != "customer"
    ):
        flash("Please login to add products to your wishlist.")
        return redirect(url_for("login"))

    con = sq.connect("zambare.db", timeout=10)
    cur = con.cursor()

    cur.execute("INSERT OR IGNORE INTO user_wishlist (user_id, product_id) SELECT ?, id FROM products WHERE id = ?", (session["user_id"], product_id))

    added = cur.rowcount

    con.commit()
    con.close()

    if added:
        flash("Product added to your wishlist!")
    else:
        flash("Product is already in your wishlist or was not found.")

    return redirect(url_for("products"))


# =========================================
# REMOVE PRODUCT FROM WISHLIST
# =========================================

@app.route("/remove_from_wishlist/<int:wishlist_id>",methods=["POST"])
def remove_from_wishlist(wishlist_id):

    if (
        "user_id" not in session
        or session.get("role") != "customer"
    ):
        flash("Please login to manage your wishlist.")
        return redirect(url_for("login"))

    con = sq.connect("zambare.db", timeout=10)
    cur = con.cursor()

    cur.execute(" DELETE FROM user_wishlist WHERE wishlist_id = ? AND user_id = ?", (wishlist_id, session["user_id"]))

    removed = cur.rowcount

    con.commit()
    con.close()

    if removed:
        flash("Product removed from your wishlist.")
    else:
        flash("Wishlist item not found.")

    return redirect(url_for("wishlist"))


# =========================================
# USER - MY PROFILE
# =========================================

@app.route("/my_profile", methods=["GET", "POST"])
def my_profile():

    # Check customer login
    if (
        "user_id" not in session
        or session.get("role") != "customer"
    ):
        flash("Please login to view your profile.")
        return redirect(url_for("login"))

    con = sq.connect("zambare.db", timeout=10)
    con.row_factory = sq.Row
    cur = con.cursor()

    # Update profile when form is submitted
    if request.method == "POST":

        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        contact = request.form.get("contact", "").strip()
        city = request.form.get("city", "").strip()

        if not all([fullname, email, contact, city]):
            con.close()
            flash("Please fill in all profile fields.")
            return redirect(url_for("my_profile"))

        try:
            cur.execute("UPDATE users SET name = ?, email = ?, contact = ?, city = ? WHERE id = ? AND role = 'customer'", (
                fullname,
                email,
                contact,
                city,
                session["user_id"]
            ))

            con.commit()

            # Update session details
            session["user_name"] = fullname
            session["user_email"] = email

            con.close()

            flash("Your profile has been updated successfully!")
            return redirect(url_for("my_profile"))

        except sq.IntegrityError:
            con.rollback()
            con.close()

            flash("This email is already registered with another account.")
            return redirect(url_for("my_profile"))

    # Fetch the logged-in customer's profile
    cur.execute(" SELECT id, name, email, contact, city FROM users WHERE id = ? AND role = 'customer'", (session["user_id"],))

    user = cur.fetchone()
    con.close()

    if user is None:
        session.clear()
        flash("User account not found. Please login again.")
        return redirect(url_for("login"))

    return render_template("uprofile.html",user=user)


if __name__=="__main__" :
    app.run(debug=True,port=2004)