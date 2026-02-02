import tkinter as tk
from tkinter import messagebox
import api_client

def start_subscription_manager():
    root = tk.Toplevel()
    root.title("MealPrep – Subscription Manager")
    root.geometry("400x350")
    root.configure(bg="#f3f5f9")

    tk.Label(root, text="Subscription Plans",
             bg="#f3f5f9", font=("Segoe UI", 14, "bold")).pack(pady=10)

    listbox = tk.Listbox(root, width=40, height=10, font=("Segoe UI", 10))
    listbox.pack(padx=10, pady=10)

    def load_subs():
        listbox.delete(0, tk.END)
        try:
            subs = api_client.get_subscriptions()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load subscriptions:\n{e}")
            return
        listbox.subs_data = subs
        for s in subs:
            listbox.insert(tk.END, f"{s['id']}: {s['name']} – ${s['price']:.2f}/week")

    def choose():
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("Select", "Select a plan first.")
            return
        idx = sel[0]
        plan = listbox.subs_data[idx]
        try:
            api_client.subscribe(plan["id"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update subscription:\n{e}")
            return
        messagebox.showinfo("Updated", f"Subscription set to: {plan['name']}")

    tk.Button(root, text="Choose Plan",
              command=choose, bg="#2e7d32", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=5)

    load_subs()
    root.transient()
    root.grab_set()
    root.wait_window()

if __name__ == "__main__":
    start_subscription_manager()
