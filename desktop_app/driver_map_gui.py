import tkinter as tk
from tkinter import ttk, messagebox
import io
import base64
import urllib.request
import api_client

def start_driver_map():
    root = tk.Toplevel()
    root.title("MealPrep – Driver Map")
    root.geometry("600x500")
    root.configure(bg="#f3f5f9")

    tk.Label(root, text="Driver Map (simulated route)",
             bg="#f3f5f9", font=("Segoe UI", 14, "bold")).pack(pady=10)

    frame = tk.Frame(root, bg="#ffffff", bd=1, relief="solid")
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(frame, width=512, height=512, bg="white")
    canvas.pack(padx=10, pady=10)

    marker = None
    path_points = [(50, 450), (150, 350), (250, 250), (350, 150), (450, 80)]
    idx = 0

    def load_tile():
        nonlocal marker
        url = "https://tile.openstreetmap.org/13/4953/3274.png"
        try:
            with urllib.request.urlopen(url) as resp:
                data = resp.read()
            b64 = base64.b64encode(data)
            img = tk.PhotoImage(data=b64)
            canvas.image = img
            canvas.create_image(0, 0, anchor="nw", image=img)
            marker = canvas.create_oval(45, 445, 55, 455, fill="red")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load map tile:\n{e}")

    def animate():
        nonlocal idx
        if marker is None:
            return
        if idx >= len(path_points):
            return
        x, y = path_points[idx]
        canvas.coords(marker, x-5, y-5, x+5, y+5)
        idx += 1
        root.after(1500, animate)

    tk.Button(root, text="Load Map & Start Route",
              command=lambda: (load_tile(), animate()),
              bg="#2e7d32", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=5)

    root.transient()
    root.grab_set()
    root.wait_window()

if __name__ == "__main__":
    start_driver_map()
