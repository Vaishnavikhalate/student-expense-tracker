import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

DB_NAME = "expenses.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

def clear_fields():
    date_entry.delete(0, tk.END)
    date_entry.insert(0, date.today().isoformat())
    category_var.set("Food")
    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)

def add_expense():
    expense_date = date_entry.get().strip()
    category = category_var.get().strip()
    amount_text = amount_entry.get().strip()
    description = description_entry.get().strip()

    if not expense_date or not amount_text:
        messagebox.showwarning("Missing Data", "Please enter date and amount.")
        return

    try:
        amount = float(amount_text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Amount", "Enter a valid positive amount.")
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (expense_date, category, amount, description) VALUES (?, ?, ?, ?)",
        (expense_date, category, amount, description)
    )
    conn.commit()
    conn.close()

    clear_fields()
    load_expenses()
    messagebox.showinfo("Success", "Expense added successfully.")

def load_expenses():
    for item in tree.get_children():
        tree.delete(item)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, expense_date, category, amount, description "
        "FROM expenses ORDER BY id DESC"
    )
    rows = cursor.fetchall()
    conn.close()

    total = 0
    for row in rows:
        tree.insert("", tk.END, values=(
            row[0], row[1], row[2], f"₹{row[3]:.2f}", row[4]
        ))
        total += row[3]

    total_label.config(text=f"Total Expense: ₹{total:.2f}")

def delete_expense():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select Expense", "Please select an expense to delete.")
        return

    item = tree.item(selected[0])
    expense_id = item["values"][0]

    if not messagebox.askyesno("Confirm Delete", "Delete the selected expense?"):
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

    load_expenses()

def on_tree_select(event):
    selected = tree.selection()
    if not selected:
        return

    item = tree.item(selected[0])
    values = item["values"]

    date_entry.delete(0, tk.END)
    date_entry.insert(0, values[1])

    category_var.set(values[2])

    amount_entry.delete(0, tk.END)
    amount_entry.insert(0, str(values[3]).replace("₹", ""))

    description_entry.delete(0, tk.END)
    description_entry.insert(0, values[4])

def update_expense():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select Expense", "Select an expense to update.")
        return

    try:
        amount = float(amount_entry.get().strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Amount", "Enter a valid positive amount.")
        return

    expense_id = tree.item(selected[0])["values"][0]
    expense_date = date_entry.get().strip()
    category = category_var.get().strip()
    description = description_entry.get().strip()

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE expenses
        SET expense_date = ?, category = ?, amount = ?, description = ?
        WHERE id = ?
    """, (expense_date, category, amount, description, expense_id))
    conn.commit()
    conn.close()

    clear_fields()
    load_expenses()
    messagebox.showinfo("Success", "Expense updated successfully.")

create_table()

root = tk.Tk()
root.title("Student Expense Tracker")
root.geometry("850x600")
root.minsize(800, 550)

title = tk.Label(
    root,
    text="Student Expense Tracker",
    font=("Arial", 22, "bold")
)
title.pack(pady=15)

form = tk.Frame(root)
form.pack(pady=5)

tk.Label(form, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=8, pady=8, sticky="w")
date_entry = tk.Entry(form, width=22)
date_entry.grid(row=0, column=1, padx=8, pady=8)
date_entry.insert(0, date.today().isoformat())

tk.Label(form, text="Category:").grid(row=0, column=2, padx=8, pady=8, sticky="w")
category_var = tk.StringVar(value="Food")
category_box = ttk.Combobox(
    form,
    textvariable=category_var,
    values=["Food", "Travel", "Education", "Shopping", "Bills", "Other"],
    state="readonly",
    width=18
)
category_box.grid(row=0, column=3, padx=8, pady=8)

tk.Label(form, text="Amount (₹):").grid(row=1, column=0, padx=8, pady=8, sticky="w")
amount_entry = tk.Entry(form, width=22)
amount_entry.grid(row=1, column=1, padx=8, pady=8)

tk.Label(form, text="Description:").grid(row=1, column=2, padx=8, pady=8, sticky="w")
description_entry = tk.Entry(form, width=21)
description_entry.grid(row=1, column=3, padx=8, pady=8)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Add Expense", width=15, command=add_expense).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Update", width=15, command=update_expense).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Delete", width=15, command=delete_expense).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Clear", width=15, command=clear_fields).grid(row=0, column=3, padx=5)

columns = ("ID", "Date", "Category", "Amount", "Description")
tree = ttk.Treeview(root, columns=columns, show="headings", height=13)

for column in columns:
    tree.heading(column, text=column)

tree.column("ID", width=50, anchor="center")
tree.column("Date", width=120, anchor="center")
tree.column("Category", width=120, anchor="center")
tree.column("Amount", width=110, anchor="center")
tree.column("Description", width=300)

tree.pack(fill="both", expand=True, padx=20, pady=10)
tree.bind("<<TreeviewSelect>>", on_tree_select)

total_label = tk.Label(root, text="Total Expense: ₹0.00", font=("Arial", 14, "bold"))
total_label.pack(pady=8)

load_expenses()
root.mainloop()
