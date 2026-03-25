import tkinter as tk
from tkinter import messagebox
import api_client
import user_gui
import admin_gui

def start_login_gui():
    root = tk.Tk()
    root.title("MealPrep Login")
    root.geometry("360x260")
    root.configure(bg="#f3f5f9")

    tk.Label(root, text="MealPrep Desktop Login",
             font=("Segoe UI", 14, "bold"), bg="#f3f5f9").pack(pady=15)

    frame = tk.Frame(root, bg="#f3f5f9")
    frame.pack(pady=5)

    tk.Label(frame, text="Email", bg="#f3f5f9").grid(row=0, column=0, sticky="w", pady=5)
    email_entry = tk.Entry(frame, width=30)
    email_entry.grid(row=0, column=1, pady=5)

    tk.Label(frame, text="Password", bg="#f3f5f9").grid(row=1, column=0, sticky="w", pady=5)
    password_entry = tk.Entry(frame, width=30, show="*")
    password_entry.grid(row=1, column=1, pady=5)

    def do_login():
        email = email_entry.get().strip()
        password = password_entry.get().strip()
        if not email or not password:
            messagebox.showinfo("Missing", "Enter email and password.")
            return
        try:
            result = api_client.login(email, password)
        except Exception as e:
            messagebox.showerror("Error", f"Login failed:\n{e}")
            return
        if not result.get("success"):
            messagebox.showerror("Error", "Invalid login")
            return
        is_admin = result.get("admin", False)
        root.destroy()
        if is_admin:
            admin_gui.start_admin_gui(email)
        else:
            user_gui.start_user_gui(email)

    tk.Button(root, text="Login", command=do_login,
              bg="#2e7d32", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=15)

    root.mainloop()

if __name__ == "__main__":
    start_login_gui()
