import tkinter as tk
from tkinter import ttk, messagebox
import api_client

STATUSES = ["Preparing", "Packed", "Out for Delivery", "Delivered"]


def start_admin_gui(email):
    root = tk.Tk()
    root.title(f"MealPrep – Admin Dashboard ({email})")
    root.geometry("900x600")
    root.configure(bg="#f3f5f9")

    top = tk.Frame(root, bg="#263238", height=50)
    top.pack(side="top", fill="x")
    tk.Label(top, text="MealPrep Admin", fg="white", bg="#263238",
             font=("Segoe UI", 14, "bold")).pack(side="left", padx=20)
    tk.Label(top, text=f"Admin: {email}", fg="white", bg="#263238",
             font=("Segoe UI", 10)).pack(side="right", padx=20)

    main = tk.Frame(root, bg="#f3f5f9")
    main.pack(fill="both", expand=True, padx=10, pady=10)

    # left: orders list
    left = tk.Frame(main, bg="#f3f5f9")
    left.pack(side="left", fill="both", expand=True)

    tk.Label(left, text="Orders", bg="#f3f5f9",
             font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=5)

    columns = ("id", "user", "status", "paid")
    tree = ttk.Treeview(left, columns=columns, show="headings", height=20)
    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True)

    # right: details + controls
    right = tk.Frame(main, bg="#ffffff", bd=1, relief="solid")
    right.pack(side="left", fill="y", padx=10)

    tk.Label(right, text="Order details", bg="white",
             font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=10)

    details_text = tk.Text(right, width=40, height=15, bg="#fafafa", font=("Segoe UI", 9))
    details_text.pack(padx=10, pady=5)

    status_var = tk.StringVar(value="Preparing")
    tk.Label(right, text="Update status:", bg="white").pack(anchor="w", padx=10, pady=(10, 0))
    status_combo = ttk.Combobox(right, textvariable=status_var, values=STATUSES, state="readonly")
    status_combo.pack(anchor="w", padx=10, pady=5)

    def load_orders():
        tree.delete(*tree.get_children())
        try:
            orders = api_client.admin_get_orders()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders:\n{e}")
            return
        tree.orders_data = orders
        for o in orders:
            tree.insert("", tk.END, values=(
                o["order_id"],
                o.get("user", ""),
                o["status"],
                "Yes" if o.get("paid") else "No"
            ))
        load_stats()

    def on_select(event):
        sel = tree.selection()
        if not sel:
            return
        item_id = sel[0]
        vals = tree.item(item_id, "values")
        order_id = vals[0]
        order = next((o for o in tree.orders_data if o["order_id"] == order_id), None)
        if not order:
            return
        details_text.delete("1.0", tk.END)
        details_text.insert(tk.END, f"Order ID: {order['order_id']}\n")
        details_text.insert(tk.END, f"User: {order.get('user', '')}\n")
        details_text.insert(tk.END, f"Status: {order['status']}\n")
        details_text.insert(tk.END, f"Paid: {'Yes' if order.get('paid') else 'No'}\n")
        details_text.insert(tk.END, f"ETA: {order['eta']}\n")
        details_text.insert(tk.END, f"Driver: {order['driver']}\n\n")
        details_text.insert(tk.END, "Meals:\n")
        for m in order.get("meals", []):
            details_text.insert(
                tk.END,
                f" - {m['name']} (${m['price']:.2f}) removed: {', '.join(m['removed_ingredients']) or 'none'}\n"
            )
        status_var.set(order["status"])

    tree.bind("<<TreeviewSelect>>", on_select)

    def update_status():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Select order", "Select an order first.")
            return
        item_id = sel[0]
        vals = tree.item(item_id, "values")
        order_id = vals[0]
        new_status = status_var.get()
        try:
            api_client.admin_update_status(order_id, new_status)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status:\n{e}")
            return
        load_orders()
        messagebox.showinfo("Updated", f"Order {order_id} status set to {new_status}")

    tk.Button(right, text="Save Status",
              command=update_status, bg="#2e7d32", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=10, padx=10, anchor="e")

    # stats
    stats_frame = tk.Frame(right, bg="white")
    stats_frame.pack(fill="x", padx=10, pady=10)

    stats_label = tk.Label(stats_frame, text="Stats: -", bg="white", justify="left",
                           font=("Segoe UI", 9))
    stats_label.pack(anchor="w")

    def load_stats():
        try:
            s = api_client.admin_stats()
        except Exception:
            stats_label.config(text="Stats: unavailable")
            return
        text = (
            f"Total orders: {s.get('total', 0)}\n"
            f"Delivered: {s.get('delivered', 0)}\n"
            f"Unpaid: {s.get('unpaid', 0)}\n"
        )
        stats_label.config(text=text)

    # menu
    menubar = tk.Menu(root)
    account_menu = tk.Menu(menubar, tearoff=0)

    def do_logout():
        api_client.logout()
        messagebox.showinfo("Logout", "Admin logged out.")
        root.destroy()

    account_menu.add_command(label="Logout", command=do_logout)
    menubar.add_cascade(label="Account", menu=account_menu)
    root.config(menu=menubar)

    load_orders()
    root.mainloop()


if __name__ == "__main__":
    start_admin_gui("admin@mealprep.com")
