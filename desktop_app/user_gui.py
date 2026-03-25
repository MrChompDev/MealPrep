import tkinter as tk
from tkinter import ttk, messagebox
import io
import base64
import urllib.request

import api_client

cart = []

INGREDIENT_IMPACT = {
    "Cheese": {"cal": -80, "price": -0.50},
    "Sauce": {"cal": -40, "price": -0.20},
    "Tomato": {"cal": -10, "price": 0},
    "Onion": {"cal": -5, "price": 0},
    "Avocado": {"cal": -60, "price": -0.40},
    "Sesame Seeds": {"cal": -20, "price": -0.10},
    "Croutons": {"cal": -50, "price": -0.30},
    "Parmesan": {"cal": -70, "price": -0.40},
    "Garlic": {"cal": -5, "price": 0},
    "Chili Flakes": {"cal": -2, "price": 0}
}

CATEGORIES = ["All", "Seafood", "Burgers", "Vegetarian", "Low-Carb"]
ALLERGENS = ["Gluten", "Dairy", "Nuts", "Shellfish", "Eggs", "Soy", "Fish", "Sesame"]


def start_user_gui(email):
    root = tk.Tk()
    root.title(f"MealPrep – Desktop ({email})")
    root.geometry("950x650")
    root.configure(bg="#f3f5f9")

    top = tk.Frame(root, bg="#2e7d32", height=50)
    top.pack(side="top", fill="x")
    tk.Label(top, text="MealPrep Desktop", fg="white", bg="#2e7d32",
             font=("Segoe UI", 14, "bold")).pack(side="left", padx=20)
    tk.Label(top, text=f"Logged in as {email}", fg="white", bg="#2e7d32",
             font=("Segoe UI", 10)).pack(side="right", padx=20)

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both", padx=10, pady=10)

    meals_tab = tk.Frame(notebook, bg="#f3f5f9")
    checkout_tab = tk.Frame(notebook, bg="#f3f5f9")
    tracking_tab = tk.Frame(notebook, bg="#f3f5f9")
    map_tab = tk.Frame(notebook, bg="#f3f5f9")

    notebook.add(meals_tab, text="Meals")
    notebook.add(checkout_tab, text="Checkout")
    notebook.add(tracking_tab, text="Tracking")
    notebook.add(map_tab, text="Map")

    # ---------- MEALS TAB ----------
    tk.Label(meals_tab, text="Browse Meals",
             font=("Segoe UI", 14, "bold"), bg="#f3f5f9").pack(anchor="w", padx=10, pady=10)

    filter_frame = tk.Frame(meals_tab, bg="#f3f5f9")
    filter_frame.pack(fill="x", padx=10)

    # category buttons
    tk.Label(filter_frame, text="Category:", bg="#f3f5f9",
             font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
    cat_var = tk.StringVar(value="All")
    cat_buttons = []
    for i, cat in enumerate(CATEGORIES):
        b = tk.Radiobutton(filter_frame, text=cat, value=cat, variable=cat_var,
                           bg="#f3f5f9", indicatoron=False, width=10,
                           selectcolor="#2e7d32", fg="white" if cat == "All" else "black")
        b.grid(row=0, column=i+1, padx=2, pady=5)
        cat_buttons.append(b)

    # allergy checkboxes
    tk.Label(filter_frame, text="Exclude allergens:",
             bg="#f3f5f9", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(5, 0))
    allergy_vars = {}
    for i, a in enumerate(ALLERGENS):
        var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(filter_frame, text=a, variable=var, bg="#f3f5f9")
        cb.grid(row=1 + i // 4, column=1 + (i % 4), sticky="w")
        allergy_vars[a] = var

    meals_frame = tk.Frame(meals_tab, bg="#f3f5f9")
    meals_frame.pack(fill="both", expand=True, padx=10, pady=5)

    meals_list = tk.Listbox(meals_frame, width=40, height=20, font=("Segoe UI", 10))
    meals_list.pack(side="left", fill="y")

    detail_frame = tk.Frame(meals_frame, bg="#ffffff", bd=1, relief="solid")
    detail_frame.pack(side="left", fill="both", expand=True, padx=10)

    detail_name = tk.Label(detail_frame, text="Select a meal", font=("Segoe UI", 12, "bold"), bg="white")
    detail_name.pack(anchor="w", padx=10, pady=(10, 0))

    detail_info = tk.Label(detail_frame, text="", font=("Segoe UI", 10), bg="white", justify="left")
    detail_info.pack(anchor="w", padx=10, pady=5)

    meals_list.meals_data = []

    def apply_filters():
        meals_list.delete(0, tk.END)
        filtered = []
        for m in meals_list.all_meals:
            if cat_var.get() != "All" and m["category"] != cat_var.get():
                continue
            excluded = [a for a, v in allergy_vars.items() if v.get()]
            if excluded and any(a in excluded for a in m.get("allergens", [])):
                continue
            filtered.append(m)
        meals_list.meals_data = filtered
        for m in filtered:
            meals_list.insert(tk.END, f"{m['id']}: {m['name']} ({m['category']})")

    def load_meals():
        try:
            meals = api_client.get_meals()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load meals:\n{e}")
            return
        meals_list.all_meals = meals
        apply_filters()

    def on_meal_select(event):
        sel = meals_list.curselection()
        if not sel:
            return
        idx = sel[0]
        meal = meals_list.meals_data[idx]
        text = (
            f"Category: {meal['category']}\n"
            f"Calories: {meal['calories']} kcal\n"
            f"Price: ${meal['price']:.2f}\n"
            f"Allergens: {', '.join(meal.get('allergens', [])) or 'None'}"
        )
        detail_name.config(text=meal["name"])
        detail_info.config(text=text)

    meals_list.bind("<<ListboxSelect>>", on_meal_select)

    def open_customise():
        sel = meals_list.curselection()
        if not sel:
            messagebox.showinfo("Select meal", "Please select a meal first.")
            return
        idx = sel[0]
        meal = meals_list.meals_data[idx]
        open_customisation_window(root, meal, refresh_cart)

    tk.Button(meals_tab, text="Customise & Add to Cart",
              command=open_customise, bg="#2e7d32", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=10)

    # re-filter when category/allergy changes
    def on_filter_change(*_):
        apply_filters()

    cat_var.trace_add("write", on_filter_change)
    for v in allergy_vars.values():
        v.trace_add("write", on_filter_change)

    load_meals()

    # ---------- CHECKOUT TAB ----------
    tk.Label(checkout_tab, text="Checkout",
             font=("Segoe UI", 14, "bold"), bg="#f3f5f9").pack(anchor="w", padx=10, pady=10)

    checkout_frame = tk.Frame(checkout_tab, bg="#f3f5f9")
    checkout_frame.pack(fill="both", expand=True, padx=10, pady=5)

    cart_box = tk.Listbox(checkout_frame, width=50, height=15, font=("Segoe UI", 10))
    cart_box.pack(side="left", fill="y")

    form_frame = tk.Frame(checkout_frame, bg="#ffffff", bd=1, relief="solid")
    form_frame.pack(side="left", fill="both", expand=True, padx=10)

    tk.Label(form_frame, text="Customer details", font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=10)

    def labeled_entry(parent, label):
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill="x", padx=10, pady=3)
        tk.Label(frame, text=label, bg="white", font=("Segoe UI", 9)).pack(anchor="w")
        entry = tk.Entry(frame, width=40)
        entry.pack(anchor="w")
        return entry

    name_entry = labeled_entry(form_frame, "Name")
    email_entry = labeled_entry(form_frame, "Email")
    phone_entry = labeled_entry(form_frame, "Phone")
    addr_entry = labeled_entry(form_frame, "Address")

    total_label = tk.Label(form_frame, text="Total: $0.00", bg="white", font=("Segoe UI", 11, "bold"))
    total_label.pack(anchor="w", padx=10, pady=10)

    def refresh_cart():
        cart_box.delete(0, tk.END)
        total = 0.0
        for item in cart:
            cart_box.insert(
                tk.END,
                f"{item['name']} – ${item['price']:.2f} (removed: {', '.join(item['removed_ingredients']) or 'none'})"
            )
            total += item["price"]
        total_label.config(text=f"Total: ${total:.2f}")

    def place_order():
        if not cart:
            messagebox.showinfo("Cart empty", "Add some meals first.")
            return
        customer = {
            "name": name_entry.get(),
            "email": email_entry.get(),
            "phone": phone_entry.get(),
            "address": addr_entry.get()
        }
        if not customer["name"] or not customer["email"]:
            messagebox.showinfo("Missing info", "Name and email are required.")
            return
        try:
            order = api_client.create_order(cart, customer)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to place order:\n{e}")
            return
        cart.clear()
        refresh_cart()
        messagebox.showinfo(
            "Order placed",
            f"Order ID: {order['order_id']}\nStatus: {order['status']}\nETA: {order['eta']}\nDriver: {order['driver']}"
        )

    tk.Button(form_frame, text="Place Order",
              command=place_order, bg="#2e7d32", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=10, padx=10, anchor="e")

    refresh_cart()

    # ---------- TRACKING TAB ----------
    tk.Label(tracking_tab, text="Live Tracking",
             font=("Segoe UI", 14, "bold"), bg="#f3f5f9").pack(anchor="w", padx=10, pady=10)

    track_frame = tk.Frame(tracking_tab, bg="#ffffff", bd=1, relief="solid")
    track_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(track_frame, text="Order ID:", bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    order_id_entry = tk.Entry(track_frame, width=20)
    order_id_entry.grid(row=0, column=1, padx=5, pady=10, sticky="w")

    status_label = tk.Label(track_frame, text="Status: -", bg="white", font=("Segoe UI", 10))
    status_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    eta_label = tk.Label(track_frame, text="ETA: -", bg="white", font=("Segoe UI", 10))
    eta_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    driver_label = tk.Label(track_frame, text="Driver: -", bg="white", font=("Segoe UI", 10))
    driver_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    progress = ttk.Progressbar(track_frame, orient="horizontal", length=300, mode="determinate")
    progress.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="w")

    statuses = ["Preparing", "Packed", "Out for Delivery", "Delivered"]

    def update_tracking():
        order_id = order_id_entry.get().strip()
        if not order_id:
            return
        try:
            data = api_client.track_order(order_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to track order:\n{e}")
            return
        status_label.config(text=f"Status: {data['status']}")
        eta_label.config(text=f"ETA: {data['eta']}")
        driver_label.config(text=f"Driver: {data['driver']}")
        if data["status"] in statuses:
            idx = statuses.index(data["status"])
            progress["value"] = (idx / 3) * 100
        else:
            progress["value"] = 0
        if data["status"] != "Delivered":
            track_frame.after(5000, update_tracking)

    tk.Button(track_frame, text="Start Tracking",
              command=update_tracking, bg="#2e7d32", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").grid(row=0, column=2, padx=10, pady=10)

    # ---------- MAP TAB ----------
    tk.Label(map_tab, text="Map Viewer (OpenStreetMap tile)",
             font=("Segoe UI", 14, "bold"), bg="#f3f5f9").pack(anchor="w", padx=10, pady=10)

    map_frame = tk.Frame(map_tab, bg="#ffffff", bd=1, relief="solid")
    map_frame.pack(padx=10, pady=10)

    map_label = tk.Label(map_frame, bg="white")
    map_label.pack(padx=10, pady=10)

    def load_tile():
        url = "https://tile.openstreetmap.org/13/4953/3274.png"
        try:
            with urllib.request.urlopen(url) as resp:
                data = resp.read()
            b64 = base64.b64encode(data)
            img = tk.PhotoImage(data=b64)
            map_label.image = img
            map_label.config(image=img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load map tile:\n{e}")

    tk.Button(map_tab, text="Load Map Tile",
              command=load_tile, bg="#2e7d32", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=5, padx=10, anchor="w")

    # ---------- MENU ----------
    menubar = tk.Menu(root)
    account_menu = tk.Menu(menubar, tearoff=0)

    def do_logout():
        api_client.logout()
        messagebox.showinfo("Logout", "You have been logged out.")
        root.destroy()

    account_menu.add_command(label="Logout", command=do_logout)
    menubar.add_cascade(label="Account", menu=account_menu)
    root.config(menu=menubar)

    root.mainloop()


def open_customisation_window(parent, meal, refresh_cart_callback):
    win = tk.Toplevel(parent)
    win.title(f"Customise – {meal['name']}")
    win.geometry("400x450")
    win.configure(bg="white")

    tk.Label(win, text=meal["name"], font=("Segoe UI", 13, "bold"), bg="white").pack(pady=10)

    current_cal = tk.IntVar(value=meal["calories"])
    current_price = tk.DoubleVar(value=meal["price"])

    cal_label = tk.Label(win, text=f"Calories: {current_cal.get()} kcal", bg="white", font=("Segoe UI", 10))
    cal_label.pack()
    price_label = tk.Label(win, text=f"Price: ${current_price.get():.2f}", bg="white", font=("Segoe UI", 10, "bold"))
    price_label.pack(pady=5)

    tk.Label(win, text="Remove ingredients:", bg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)

    checks = []
    for ing in meal.get("removable_ingredients", []):
        var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(win, text=ing, variable=var, bg="white")
        cb.pack(anchor="w", padx=40)
        checks.append((ing, var))

    def recalc():
        cal = meal["calories"]
        price = meal["price"]
        removed = []
        for ing, var in checks:
            if var.get() and ing in INGREDIENT_IMPACT:
                cal += INGREDIENT_IMPACT[ing]["cal"]
                price += INGREDIENT_IMPACT[ing]["price"]
                removed.append(ing)
        current_cal.set(cal)
        current_price.set(price)
        cal_label.config(text=f"Calories: {cal} kcal")
        price_label.config(text=f"Price: ${price:.2f}")
        return removed, price

    def on_toggle(*_):
        recalc()

    for _, var in checks:
        var.trace_add("write", on_toggle)

    def add_to_cart():
        removed, price = recalc()
        cart.append({
            "id": meal["id"],
            "name": meal["name"],
            "removed_ingredients": removed,
            "price": price
        })
        messagebox.showinfo("Added", f"{meal['name']} added to cart.")
        refresh_cart_callback()
        win.destroy()

    tk.Button(win, text="Add to Cart",
              command=add_to_cart, bg="#2e7d32", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=20)

    win.transient(parent)
    win.grab_set()
    parent.wait_window(win)


if __name__ == "__main__":
    start_user_gui("test@user.com")
