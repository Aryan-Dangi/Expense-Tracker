
import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Define colors for the professional color palette
BACKGROUND_COLOR = "#f4f4f9"
PRIMARY_COLOR = "#007acc"
SECONDARY_COLOR = "#005a8d"
TEXT_COLOR = "#ffffff"
ENTRY_BG_COLOR = "#e0e0eb"
BUTTON_DEFAULT = "#d3d3d3"
BUTTON_HOVER = "#a9a9a9"

# Create the main window
root = tb.Window(themename="flatly")
root.title("Expense Tracker")
root.geometry("800x600")
root.minsize(800, 600)
root.configure(bg=BACKGROUND_COLOR)

# Database initialization
conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        user TEXT,
        category TEXT,
        amount REAL,
        date TEXT,
        description TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY,
        user TEXT,
        goal_amount REAL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
''')
conn.commit()
conn.close()

# Global variable to store the logged-in username
logged_in_user = ""

def show_homepage():
    for widget in root.winfo_children():
        widget.destroy()

    homepage_frame = ttk.Frame(root, padding="20")
    homepage_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    homepage_frame.columnconfigure(0, weight=1)
    homepage_frame.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Add a welcome label
    welcome_label = ttk.Label(homepage_frame, text=f"Welcome to Expense Tracker, {logged_in_user}", font=("Helvetica", 24, "bold"), foreground=PRIMARY_COLOR)
    welcome_label.grid(row=0, column=0, pady=(0, 30), sticky=tk.N)

    # Recent Transactions Section
    recent_label = ttk.Label(homepage_frame, text="Recent Transactions", font=("Helvetica", 16), foreground=PRIMARY_COLOR)
    recent_label.grid(row=7, column=0, pady=(20, 10))
    
    recent_transactions = tk.Listbox(homepage_frame, width=50, height=10, font=("Helvetica", 12))
    recent_transactions.grid(row=8, column=0, pady=(10, 10))

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE user=? ORDER BY date DESC LIMIT 10", (logged_in_user,))
    transactions = cursor.fetchall()
    conn.close()
    
    for transaction in transactions:
        recent_transactions.insert(tk.END, f"{transaction[2]}: {transaction[3]} on {transaction[4]}")

    # Functions to open new windows
    def add_expense():
        new_window = tk.Toplevel(root)
        new_window.title("Add Expense")
        new_window.geometry("400x300")

        def submit_expense():
            category = category_entry.get()
            amount = float(amount_entry.get())
            date = date_entry.get()
            description = description_entry.get()

            conn = sqlite3.connect('expenses.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO expenses (user, category, amount, date, description) VALUES (?, ?, ?, ?, ?)",
                           (logged_in_user, category, amount, date, description))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Expense added successfully")
            new_window.destroy()

        tk.Label(new_window, text="Category:").grid(row=0, column=0)
        category_entry = ttk.Entry(new_window)
        category_entry.grid(row=0, column=1)

        tk.Label(new_window, text="Amount:").grid(row=1, column=0)
        amount_entry = ttk.Entry(new_window)
        amount_entry.grid(row=1, column=1)

        tk.Label(new_window, text="Date:").grid(row=2, column=0)
        date_entry = ttk.Entry(new_window)
        date_entry.grid(row=2, column=1)

        tk.Label(new_window, text="Description:").grid(row=3, column=0)
        description_entry = ttk.Entry(new_window)
        description_entry.grid(row=3, column=1)

        submit_button = ttk.Button(new_window, text="Submit", command=submit_expense)
        submit_button.grid(row=4, column=0, columnspan=2)

    def update_expense():
        new_window = tk.Toplevel(root)
        new_window.title("Update Expense")
        new_window.geometry("400x300")

        def fetch_expense():
            expense_id = int(id_entry.get())

            conn = sqlite3.connect('expenses.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
            expense = cursor.fetchone()
            conn.close()

            if expense:
                category_entry.delete(0, tk.END)
                category_entry.insert(0, expense[2])
                amount_entry.delete(0, tk.END)
                amount_entry.insert(0, expense[3])
                date_entry.delete(0, tk.END)
                date_entry.insert(0, expense[4])
                description_entry.delete(0, tk.END)
                description_entry.insert(0, expense[5])
            else:
                messagebox.showerror("Error", "Expense not found")

        def submit_update():
            expense_id = int(id_entry.get())
            category = category_entry.get()
            amount = float(amount_entry.get())
            date = date_entry.get()
            description = description_entry.get()

            conn = sqlite3.connect('expenses.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE expenses SET category=?, amount=?, date=?, description=? WHERE id=?",
                           (category, amount, date, description, expense_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Expense updated successfully")
            new_window.destroy()

        tk.Label(new_window, text="Expense ID:").grid(row=0, column=0)
        id_entry = ttk.Entry(new_window)
        id_entry.grid(row=0, column=1)

        fetch_button = ttk.Button(new_window, text="Fetch Expense", command=fetch_expense)
        fetch_button.grid(row=1, column=0, columnspan=2)

        tk.Label(new_window, text="Category:").grid(row=2, column=0)
        category_entry = ttk.Entry(new_window)
        category_entry.grid(row=2, column=1)

        tk.Label(new_window, text="Amount:").grid(row=3, column=0)
        amount_entry = ttk.Entry(new_window)
        amount_entry.grid(row=3, column=1)

        tk.Label(new_window, text="Date:").grid(row=4, column=0)
        date_entry = ttk.Entry(new_window)
        date_entry.grid(row=4, column=1)

        tk.Label(new_window, text="Description:").grid(row=5, column=0)
        description_entry = ttk.Entry(new_window)
        description_entry.grid(row=5, column=1)

        submit_button = ttk.Button(new_window, text="Submit", command=submit_update)
        submit_button.grid(row=6, column=0, columnspan=2)

    def delete_expense():
        new_window = tk.Toplevel(root)
        new_window.title("Delete Expense")
        new_window.geometry("400x300")

        def submit_delete():
            expense_id = int(id_entry.get())

            conn = sqlite3.connect('expenses.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Expense deleted successfully")
            new_window.destroy()

        tk.Label(new_window, text="Expense ID:").grid(row=0, column=0)
        id_entry = ttk.Entry(new_window)
        id_entry.grid(row=0, column=1)

        submit_button = ttk.Button(new_window, text="Submit", command=submit_delete)
        submit_button.grid(row=1, column=0, columnspan=2)

    def filter_expense():
        new_window = tk.Toplevel(root)
        new_window.title("Filter Expense")
        new_window.geometry("400x300")

        def submit_filter():
            category = category_entry.get()
            date_from = date_from_entry.get()
            date_to = date_to_entry.get()

            conn = sqlite3.connect('expenses.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses WHERE user=? AND category=? AND date BETWEEN ? AND ?",
                           (logged_in_user, category, date_from, date_to))
            filtered_expenses = cursor.fetchall()
            conn.close()

            filter_result.delete(0, tk.END)
            for expense in filtered_expenses:
                filter_result.insert(tk.END, f"{expense[2]}: {expense[3]} on {expense[4]}")

        tk.Label(new_window, text="Category:").grid(row=0, column=0)
        category_entry = ttk.Entry(new_window)
        
        category_entry = ttk.Entry(new_window)
        category_entry.grid(row=0, column=1)

        tk.Label(new_window, text="From (YYYY-MM-DD):").grid(row=1, column=0)
        date_from_entry = ttk.Entry(new_window)
        date_from_entry.grid(row=1, column=1)

        tk.Label(new_window, text="To (YYYY-MM-DD):").grid(row=2, column=0)
        date_to_entry = ttk.Entry(new_window)
        date_to_entry.grid(row=2, column=1)

        submit_button = ttk.Button(new_window, text="Submit", command=submit_filter)
        submit_button.grid(row=3, column=0, columnspan=2)

        filter_result = tk.Listbox(new_window, width=50, height=10)
        filter_result.grid(row=4, column=0, columnspan=2, pady=(10, 10))

    def view_expense():
        new_window = tk.Toplevel(root)
        new_window.title("View Expense")
        new_window.geometry("800x600")

        # Create a sample pie chart
        fig, ax = plt.subplots()
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE user=? GROUP BY category", (logged_in_user,))
        data = cursor.fetchall()
        conn.close()

        categories = [row[0] for row in data]
        sizes = [row[1] for row in data]
        ax.pie(sizes, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')

        # Embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def set_expenditure_goals():
        new_window = tk.Toplevel(root)
        new_window.title("Set Expenditure Goals")
        new_window.geometry("400x300")

        def submit_goal():
            goal_amount = float(goal_entry.get())

            conn = sqlite3.connect('expenses.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO goals (user, goal_amount) VALUES (?, ?)", (logged_in_user, goal_amount))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Goal set successfully")
            new_window.destroy()

        tk.Label(new_window, text="Goal Amount:").grid(row=0, column=0)
        goal_entry = ttk.Entry(new_window)
        goal_entry.grid(row=0, column=1)

        submit_button = ttk.Button(new_window, text="Submit", command=submit_goal)
        submit_button.grid(row=1, column=0, columnspan=2)

    # Add buttons for functionalities
    buttons = [
        ("Add Expense", add_expense),
        ("Update Expense", update_expense),
        ("Delete Expense", delete_expense),
        ("Filter Expense", filter_expense),
        ("View Expense", view_expense),
        ("Set Expenditure Goals", set_expenditure_goals),
    ]

    for i, (text, command) in enumerate(buttons):
        button = ttk.Button(homepage_frame, text=text, command=command, style='Primary.TButton')
        button.grid(row=i + 1, column=0, pady=(10, 10))

# Function to show admin dashboard
def show_admin_dashboard():
    for widget in root.winfo_children():
        widget.destroy()

    admin_frame = ttk.Frame(root, padding="20")
    admin_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    admin_frame.columnconfigure(0, weight=1)
    admin_frame.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Add a welcome label
    welcome_label = ttk.Label(admin_frame, text="Admin Dashboard", font=("Helvetica", 24, "bold"), foreground=PRIMARY_COLOR)
    welcome_label.grid(row=0, column=0, pady=(0, 30), sticky=tk.N)

    def view_user_expenditures():
        new_window = tk.Toplevel(root)
        new_window.title("User Expenditures")
        new_window.geometry("800x600")

        # Create a sample bar chart
        fig, ax = plt.subplots()
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user, SUM(amount) FROM expenses GROUP BY user")
        data = cursor.fetchall()
        conn.close()

        users = [row[0] for row in data]
        expenditures = [row[1] for row in data]
        ax.bar(users, expenditures, color=[PRIMARY_COLOR, SECONDARY_COLOR, 'green'])
        ax.set_xlabel('Users')
        ax.set_ylabel('Expenditure')
        ax.set_title('Expenditure by User')

        # Embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    admin_buttons = [
        ("View User Expenditures", view_user_expenditures)
    ]

    for i, (text, command) in enumerate(admin_buttons):
        button = ttk.Button(admin_frame, text=text, command=command, style='Primary.TButton')
        button.grid(row=i + 1, column=0, pady=(10, 10))

# Create a frame for the login form
frame = ttk.Frame(root, padding="20")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Style configuration
style = ttk.Style()
style.configure("TFrame", background=BACKGROUND_COLOR)
style.configure("TLabel", background=BACKGROUND_COLOR, font=("Helvetica", 16))
style.configure("TRadiobutton", background=BACKGROUND_COLOR, font=("Helvetica", 16))
style.configure("TEntry", font=("Helvetica", 16))

# Custom button style for default and hover states
style.configure("TButton", font=("Helvetica", 16), background=BUTTON_DEFAULT, foreground=TEXT_COLOR)
style.map("TButton", background=[('!active', BUTTON_DEFAULT), ('active', BUTTON_HOVER)])

# Add a welcome label
welcome_label = ttk.Label(frame, text="Welcome to Expense Tracker", font=("Helvetica", 24, "bold"), foreground=PRIMARY_COLOR)
welcome_label.grid(row=0, column=0, columnspan=2, pady=(0, 30), sticky=tk.N)

# Add radio buttons for Admin and User
user_type = tk.StringVar(value="User")
admin_radio = ttk.Radiobutton(frame, text="Admin", variable=user_type, value="Admin")
user_radio = ttk.Radiobutton(frame, text="User", variable=user_type, value="User")
admin_radio.grid(row=1, column=0, sticky=tk.E, padx=(0, 20))
user_radio.grid(row=1, column=1, sticky=tk.W, padx=(20, 0))

# Add username and password labels and entry fields
username_label = ttk.Label(frame, text="Username:")
username_label.grid(row=2, column=0, pady=(30, 10), sticky=tk.E)
username_entry = ttk.Entry(frame, width=30)
username_entry.grid(row=2, column=1, pady=(30, 10), padx=(10, 0))

password_label = ttk.Label(frame, text="Password:")
password_label.grid(row=3, column=0, pady=(10, 30), sticky=tk.E)
password_entry = ttk.Entry(frame, width=30, show="*")
password_entry.grid(row=3, column=1, pady=(10, 30), padx=(10, 0))

# Function to handle login
def login():
    global logged_in_user
    username = username_entry.get()
    password = password_entry.get()
    role = user_type.get()

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE username=? AND password=? AND role=?"
    cursor.execute(query, (username, password, role))
    result = cursor.fetchone()

    if result:
        logged_in_user = username
        messagebox.showinfo("Success", f"Welcome, {username}!")
        if role == "Admin":
            show_admin_dashboard()
        else:
            show_homepage()
    else:
        messagebox.showerror("Error", "Invalid credentials")

    conn.close()

# Function to handle signup
def signup():
    def register_user():
        new_username = new_username_entry.get()
        new_password = new_password_entry.get()
        new_role = new_user_type.get()

        if len(new_password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
            return

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (new_username,))
        existing_user = cursor.fetchone()

        if existing_user:
            messagebox.showerror("Error", "Username already taken, please choose another")
        else:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                           (new_username, new_password, new_role))
            conn.commit()
            messagebox.showinfo("Success", "User registered successfully")
            signup_window.destroy()

        conn.close()

  
    signup_window = tk.Toplevel(root)
    signup_window.title("Signup")
    signup_window.geometry("400x300")
    signup_window.configure(bg=BACKGROUND_COLOR)

    new_username_label = ttk.Label(signup_window, text="New Username:")
    new_username_label.grid(row=0, column=0, pady=(20, 5), sticky=tk.E)
    new_username_entry = ttk.Entry(signup_window, width=25)
    new_username_entry.grid(row=0, column=1, pady=(20, 5))

    new_password_label = ttk.Label(signup_window, text="New Password:")
    new_password_label.grid(row=1, column=0, pady=(5, 20), sticky=tk.E)
    new_password_entry = ttk.Entry(signup_window, width=25, show="*")
    new_password_entry.grid(row=1, column=1, pady=(5, 20))

    new_user_type = tk.StringVar(value="User")
    new_admin_radio = ttk.Radiobutton(signup_window, text="Admin", variable=new_user_type, value="Admin")
    new_user_radio = ttk.Radiobutton(signup_window, text="User", variable=new_user_type, value="User")
    new_admin_radio.grid(row=2, column=0, sticky=tk.W)
    new_user_radio.grid(row=2, column=1, sticky=tk.W)

    register_button = ttk.Button(signup_window, text="Register", command=register_user)
    register_button.grid(row=3, column=0, columnspan=2, pady=(20, 20))

# Add buttons for login and signup
login_button = ttk.Button(frame, text="Login", command=login, style='TButton')
login_button.grid(row=4, column=0, pady=(0, 20), sticky=tk.E)

signup_button = ttk.Button(frame, text="Signup", command=signup, style='TButton')
signup_button.grid(row=4, column=1, pady=(0, 20), sticky=tk.W)

# Run the application
root.mainloop()