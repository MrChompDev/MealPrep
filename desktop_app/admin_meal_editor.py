import tkinter as tk
from tkinter import ttk, messagebox
import api_client

def start_meal_editor():
    root = tk.Toplevel()
    root.title("MealPrep – Admin Meal Editor")
    root.geometry("800x500")
    root.configure(bg="#f3f5f9")

    tk.Label(root, text="Meal Editor", bg="#f3f5f9",
             font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=10, pady=10)

    main = tk.Frame(root, bg="#f3f5f9")
    main.pack(fill="both", expand=True, padx=10, pady=5)

    left = tk.Frame(main, bg="#f3f5f9")
    left.pack(side="left", fill="both", expand=True)

    columns = ("id", "name", "category", "price")
    tree = ttk.Treeview(left, columns=columns, show="headings", height=18)
    for c in columns:
        tree.heading(c, text=c.capitalize())
        tree.column(c, width=150)
    tree.pack(fill="both", expand=True)

    right = tk.Frame(main, bg="#ffffff", bd=1, relief="solid")
    right.pack(side="left", fill="y", padx=10)

    tk.Label(right, text="Meal details", bg="white",
             font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=10)

    def labeled_entry(parent, label):
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill="x", padx=10, pady=3)
        tk.Label(frame, text=label, bg="white").pack(anchor="w")
        entry = tk.Entry(frame, width=30)
        entry.pack(anchor="w")
        return entry

    id_entry = labeled_entry(right, "ID (leave blank for new)")
    name_entry = labeled_entry(right, "Name")
    cat_entry = labeled_entry(right, "Category")
    cal_entry = labeled_entry(right, "Calories")
    price_entry = labeled_entry(right, "Price")
    week_entry = labeled_entry(right, "Week index (0/1)")

    allergens_entry = labeled_entry(right, "Allergens (comma separated)")
    removable_entry = labeled_entry(right, "Removable ingredients (comma separated)")

    def load_meals():
        tree.delete(*tree.get_children())
        try:
            meals = api_client.admin_get_meals()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load meals:\n{e}")
            return
        tree.meals_data = meals
        for m in meals:
            tree.insert("", tk.END, values=(
                m["id"], m["name"], m["category"], f"${m['price']:.2f}"
            ))

    def on_select(event):
        sel = tree.selection()
        if not sel:
            return
        item_id = sel[0]
        vals = tree.item(item_id, "values")
        mid = int(vals[0])
        meal = next((m for m in tree.meals_data if m["id"] == mid), None)
        if not meal:
            return
        id_entry.delete(0, tk.END)
        id_entry.insert(0, str(meal["id"]))
        name_entry.delete(0, tk.END)
        name_entry.insert(0, meal["name"])
        cat_entry.delete(0, tk.END)
        cat_entry.insert(0, meal["category"])
        cal_entry.delete(0, tk.END)
        cal_entry.insert(0, str(meal["calories"]))
        price_entry.delete(0, tk.END)
        price_entry.insert(0, str(meal["price"]))
        week_entry.delete(0, tk.END)
        week_entry.insert(0, str(meal.get("week", 0)))
        allergens_entry.delete(0, tk.END)
        allergens_entry.insert(0, ", ".join(meal.get("allergens", [])))
        removable_entry.delete(0, tk.END)
        removable_entry.insert(0, ", ".join(meal.get("removable_ingredients", [])))

    tree.bind("<<TreeviewSelect>>", on_select)

    def collect_meal():
        name = name_entry.get().strip()
        category = cat_entry.get().strip()
        if not name or not category:
            messagebox.showinfo("Missing", "Name and category are required.")
            return None
        try:
            calories = int(cal_entry.get().strip() or "0")
            price = float(price_entry.get().strip() or "0")
            week = int(week_entry.get().strip() or "0")
        except ValueError:
            messagebox.showinfo("Invalid", "Calories, price, week must be numbers.")
            return None
        allergens = [a.strip() for a in allergens_entry.get().split(",") if a.strip()]
        removable = [r.strip() for r in removable_entry.get().split(",") if r.strip()]
        meal = {
            "name": name,
            "category": category,
            "calories": calories,
            "price": price,
            "week": week,
            "allergens": allergens,
            "removable_ingredients": removable
        }
        if id_entry.get().strip():
            meal["id"] = int(id_entry.get().strip())
        return meal

    def save_meal():
        meal = collect_meal()
        if not meal:
            return
        try:
            if "id" in meal:
                api_client.admin_update_meal(meal)
            else:
                res = api_client.admin_add_meal(meal)
                meal["id"] = res["meal"]["id"]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save meal:\n{e}")
            return
        load_meals()
        messagebox.showinfo("Saved", "Meal saved.")

    def delete_meal():
        mid = id_entry.get().strip()
        if not mid:
            messagebox.showinfo("Select", "Select a meal first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this meal?"):
            return
        try:
            api_client.admin_delete_meal(int(mid))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete meal:\n{e}")
            return
        load_meals()
        id_entry.delete(0, tk.END)
        name_entry.delete(0, tk.END)
        cat_entry.delete(0, tk.END)
        cal_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        week_entry.delete(0, tk.END)
        allergens_entry.delete(0, tk.END)
        removable_entry.delete(0, tk.END)

    btn_frame = tk.Frame(right, bg="white")
    btn_frame.pack(fill="x", padx=10, pady=10)
    tk.Button(btn_frame, text="Save",
              command=save_meal, bg="#2e7d32", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(side="left", padx=5)
    tk.Button(btn_frame, text="Delete",
              command=delete_meal, bg="#c62828", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(side="left", padx=5)

    load_meals()
    root.transient()
    root.grab_set()
    root.wait_window()

if __name__ == "__main__":
    start_meal_editor()
