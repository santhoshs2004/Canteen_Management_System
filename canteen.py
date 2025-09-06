# Modern UI/UX Redesign using ttkbootstrap (easy install, native ttk compatibility)
# To use: pip install ttkbootstrap

import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import json
import os
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import time

INVENTORY_FIELDS = [
    "id", "name", "category", "unit", "quantity", "threshold", "last_restock",
    "expiry_date", "supplier_name", "supplier_contact", "supplier_price",
    "unit_price", "total_value", "status", "remarks"
]

DEFAULT_INVENTORY = [
    {
        "id": 1,
        "name": "Buns",
        "category": "Bakery",
        "unit": "pcs",
        "quantity": 100,
        "threshold": 20,
        "last_restock": "2025-09-01",
        "expiry_date": "2025-09-30",
        "supplier_name": "ABC Bakery",
        "supplier_contact": "9876543210",
        "supplier_price": 2.0,
        "unit_price": 5.0,
        "total_value": 500.0,
        "status": "Available",
        "remarks": ""
    },
    {
        "id": 2,
        "name": "Potatoes",
        "category": "Vegetables",
        "unit": "kg",
        "quantity": 50,
        "threshold": 10,
        "last_restock": "2025-09-01",
        "expiry_date": "2025-09-15",
        "supplier_name": "Fresh Farms",
        "supplier_contact": "9123456780",
        "supplier_price": 20.0,
        "unit_price": 30.0,
        "total_value": 1500.0,
        "status": "Available",
        "remarks": ""
    },
    {
        "id": 3,
        "name": "Soda Syrup",
        "category": "Beverages",
        "unit": "liters",
        "quantity": 30,
        "threshold": 5,
        "last_restock": "2025-09-01",
        "expiry_date": "2025-12-01",
        "supplier_name": "Cool Drinks Co.",
        "supplier_contact": "9988776655",
        "supplier_price": 50.0,
        "unit_price": 80.0,
        "total_value": 2400.0,
        "status": "Available",
        "remarks": ""
    },
    {
        "id": 4,
        "name": "Cheese",
        "category": "Dairy",
        "unit": "kg",
        "quantity": 20,
        "threshold": 5,
        "last_restock": "2025-09-01",
        "expiry_date": "2025-09-20",
        "supplier_name": "Dairy Best",
        "supplier_contact": "9001122334",
        "supplier_price": 100.0,
        "unit_price": 150.0,
        "total_value": 3000.0,
        "status": "Available",
        "remarks": ""
    },
    {
        "id": 5,
        "name": "Lettuce",
        "category": "Vegetables",
        "unit": "kg",
        "quantity": 15,
        "threshold": 3,
        "last_restock": "2025-09-01",
        "expiry_date": "2025-09-10",
        "supplier_name": "Green Leaf",
        "supplier_contact": "9112233445",
        "supplier_price": 15.0,
        "unit_price": 25.0,
        "total_value": 375.0,
        "status": "Available",
        "remarks": ""
    }
]

RECIPE_MAP = {
    1: {"Buns": 1, "Cheese": 0.2},      # Cheeseburger
    2: {"Potatoes": 0.3},                # French Fries
    3: {"Soda Syrup": 0.2},              # Soda
    4: {"Buns": 1, "Cheese": 0.2},       # Pizza Slice
    5: {"Lettuce": 0.1}                  # Salad
}

class AnimatedButton(tb.Button):
    """Button with hover animation"""
    def __init__(self, *args, **kwargs):
        self.default_bg = kwargs.get("bootstyle", "primary")
        super().__init__(*args, **kwargs)
        self.default_fg = "white" if self.default_bg in ["primary", "secondary", "success", "info", "warning", "danger"] else "black"
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def on_enter(self, e):
        self.configure(bootstyle=f"{self.default_bg}-outline")
        
    def on_leave(self, e):
        self.configure(bootstyle=self.default_bg)

class CanteenManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Canteen Management System")
        self.style = tb.Style("minty")  # Modern theme with pleasant colors
        self.theme_mode = "light"
        self.root.geometry("1400x900")
        self.root.minsize(1100, 700)
        
        # Configure custom colors
        self.style.configure("primary.TFrame", background=self.style.colors.primary)
        self.style.configure("light.TFrame", background=self.style.colors.light)
        
        # Load data
        self.menu_items = self.load_data("menu.json", self.default_menu())
        self.orders = self.load_data("orders.json", [])
        self.inventory = self.load_data("inventory.json", DEFAULT_INVENTORY)
        self.ensure_inventory_fields()

        # Setup UI
        self.setup_ui()
        self.show_frame(0)

    def load_data(self, filename, default_data):
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as file:
                    data = json.load(file)
                    return data
            except Exception:
                return default_data
        return default_data

    def save_data(self, filename, data):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

    def default_menu(self):
        return [
            {"id": 1, "name": "Cheeseburger", "price": 5.99, "category": "Main Course", "available": True},
            {"id": 2, "name": "French Fries", "price": 2.99, "category": "Side Dish", "available": True},
            {"id": 3, "name": "Soda", "price": 1.99, "category": "Beverage", "available": True},
            {"id": 4, "name": "Pizza Slice", "price": 3.99, "category": "Main Course", "available": True},
            {"id": 5, "name": "Salad", "price": 4.99, "category": "Side Dish", "available": True}
        ]
    
    def setup_ui(self):
        # Configure grid for responsive layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # --- Sidebar Navigation ---
        self.sidebar = tb.Frame(self.root, width=220, bootstyle="primary")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        
        # App logo/title in sidebar
        logo_frame = tb.Frame(self.sidebar, bootstyle="primary")
        logo_frame.pack(fill="x", pady=(20, 30))
        
        tb.Label(logo_frame, text="🍔", font=("Arial", 28), bootstyle="inverse-primary").pack(pady=(0, 10))
        tb.Label(logo_frame, text="Canteen Manager", font=("Segoe UI", 16, "bold"), 
                bootstyle="inverse-primary").pack()
        
        # Navigation buttons
        self.sidebar_buttons = []
        nav_options = [
            ("🏠 Dashboard", "primary"),
            ("🍽️ Menu", "success"),
            ("📦 Inventory", "info"),
            ("🛒 Orders", "warning"),
            ("📊 Reports", "secondary"),
            ("⚙️ Settings", "light")
        ]
        
        for text, style in nav_options:
            btn = AnimatedButton(
                self.sidebar, text=text, width=20, bootstyle=style,
                command=lambda t=text: self.navigate_to(t),
                cursor="hand2"
            )
            btn.pack(pady=8, padx=20, fill="x")
            self.sidebar_buttons.append(btn)
        
        # Theme toggle at bottom of sidebar
        theme_frame = tb.Frame(self.sidebar, bootstyle="primary")
        theme_frame.pack(side="bottom", fill="x", pady=20)
        
        self.mode_btn = AnimatedButton(
            theme_frame, text="🌙 Dark Mode", bootstyle="secondary",
            command=self.toggle_mode, cursor="hand2"
        )
        self.mode_btn.pack(pady=10, padx=20, fill="x")
        
        # --- Main Content Area ---
        self.main_frame = tb.Frame(self.root, bootstyle="light")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_rowconfigure(0, weight=0)  # Header row, fixed height
        self.main_frame.grid_rowconfigure(1, weight=1)  # Content row, expands
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Header bar
        self.header = tb.Frame(self.main_frame, height=70, bootstyle="light")
        self.header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(0, weight=1)
        
        self.title_label = tb.Label(
            self.header, text="Dashboard", 
            font=("Segoe UI", 20, "bold"), 
            bootstyle="primary"
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=30, pady=20)
        
        # Add refresh button
        refresh_btn = AnimatedButton(self.header, text="🔄 Refresh", bootstyle="info", command=self.setup_dashboard_tab, cursor="hand2")
        refresh_btn.grid(row=0, column=1, sticky="e", padx=30, pady=20)
        
        # Content area
        self.content = tb.Frame(self.main_frame, bootstyle="light")
        self.content.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)  # Remove extra padding here
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        
        # Create frames for each section
        self.frames = {}
        for section in ["Dashboard", "Menu", "Inventory", "Orders", "Reports", "Settings"]:
            frame = tb.Frame(self.content, bootstyle="light")
            frame.grid(row=0, column=0, sticky="nsew")  # This is correct
            self.frames[section] = frame
        
        # Setup each tab
        self.setup_dashboard_tab()
        self.setup_menu_tab()
        self.setup_inventory_tab()
        self.setup_order_tab()
        self.setup_reports_tab()
        self.setup_settings_tab()

    def navigate_to(self, text):
        section = text.split(" ")[1]  # Extract section name from button text
        self.title_label.configure(text=section)
        
        # Hide all frames
        for frame in self.frames.values():
            frame.grid_remove()
        
        # Show selected frame with a fade-in effect
        self.frames[section].grid()
        self.animate_frame(self.frames[section])
        
        # Update active button styling
        for btn in self.sidebar_buttons:
            btn.configure(bootstyle=btn.default_bg)
        
        active_btn = next(btn for btn in self.sidebar_buttons if section in btn.cget("text"))
        active_btn.configure(bootstyle=f"{active_btn.default_bg}-outline")

    def animate_frame(self, widget, alpha=0.0):
        """Simple fade-in animation for frames"""
        if alpha < 1.0:
            alpha += 0.05
            widget.configure(style="TFrame")  # Reset style
            self.root.after(10, lambda: self.animate_frame(widget, alpha))

    def show_frame(self, idx):
        sections = ["Dashboard", "Menu", "Inventory", "Orders", "Reports", "Settings"]
        self.navigate_to(f"icon {sections[idx]}")

    def toggle_mode(self):
        if self.theme_mode == "light":
            self.style.theme_use("darkly")
            self.theme_mode = "dark"
            self.mode_btn.configure(text="☀️ Light Mode")
        else:
            self.style.theme_use("minty")
            self.theme_mode = "light"
            self.mode_btn.configure(text="🌙 Dark Mode")

    # --- Dashboard/Home ---
    def setup_dashboard_tab(self):
        frame = self.frames["Dashboard"]
        for widget in frame.winfo_children():
            widget.destroy()
            
        # Create a canvas for scrolling
        canvas = tk.Canvas(frame, bg=self.style.colors.light)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas, bootstyle="light")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Dashboard content
        tb.Label(scrollable_frame, text="Dashboard Overview", font=("Segoe UI", 18, "bold"), 
                bootstyle="primary").pack(pady=(20, 10))
        
        # Stats cards
        cards_frame = tb.Frame(scrollable_frame, bootstyle="light")
        cards_frame.pack(fill="x", padx=20, pady=10)
        
        # Calculate stats
        today = datetime.now().strftime("%Y-%m-%d")
        today_sales = sum(order.get("total", 0) for order in self.orders 
                         if order.get("datetime", "").startswith(today))
        available_stock = sum(float(item.get("quantity", 0)) for item in self.inventory)
        low_stock_count = sum(1 for item in self.inventory 
                             if item.get("status", "") == "Low Stock" or 
                             float(item.get("quantity", 0)) < float(item.get("threshold", 0)))
        total_orders = len(self.orders)
        
        stats = [
            ("Today's Sales", f"₹{today_sales:.2f}", "success", "💰"),
            ("Total Stock", f"{available_stock:.0f} units", "info", "📦"),
            ("Low Stock Items", f"{low_stock_count}", "danger", "⚠️"),
            ("Total Orders", f"{total_orders}", "warning", "🛒"),
        ]
        
        for i, (title, value, style, icon) in enumerate(stats):
            card = tb.Frame(cards_frame, bootstyle=style, width=240, height=120)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            card.grid_propagate(False)
            
            # Card content
            icon_label = tb.Label(card, text=icon, font=("Arial", 24), bootstyle=f"inverse-{style}")
            icon_label.pack(pady=(15, 5))
            
            value_label = tb.Label(card, text=value, font=("Segoe UI", 18, "bold"), bootstyle=f"inverse-{style}")
            value_label.pack(pady=5)
            
            title_label = tb.Label(card, text=title, font=("Segoe UI", 10), bootstyle=f"inverse-{style}")
            title_label.pack(pady=(0, 10))
            
            cards_frame.grid_columnconfigure(i, weight=1)
        
        # Recent orders table
        tb.Label(scrollable_frame, text="Recent Orders", font=("Segoe UI", 16, "bold"), 
                bootstyle="primary").pack(pady=(30, 10))
        
        table_container = tb.Frame(scrollable_frame, bootstyle="light")
        table_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("ID", "Date/Time", "Items", "Total", "Status")
        tree = tb.Treeview(table_container, columns=columns, show="headings", height=8, bootstyle="info")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        
        # Add scrollbar to table
        tree_scroll = tb.Scrollbar(table_container, orient="vertical", command=tree.yview, bootstyle="primary-round")
        tree.configure(yscrollcommand=tree_scroll.set)
        
        tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        # Populate with recent orders
        for order in sorted(self.orders, key=lambda x: x.get("datetime", ""), reverse=True)[:10]:
            items_text = ", ".join([f"{item['name']} (x{item['quantity']})" for item in order.get("items", [])])
            tree.insert("", "end", values=(
                order.get("id", ""), 
                order.get("datetime", ""), 
                items_text[:30] + "..." if len(items_text) > 30 else items_text,
                f"₹{order.get('total', 0):.2f}", 
                order.get("status", "")
            ))
        
        # Quick actions
        tb.Label(scrollable_frame, text="Quick Actions", font=("Segoe UI", 16, "bold"), 
                bootstyle="primary").pack(pady=(30, 10))
        
        actions_frame = tb.Frame(scrollable_frame, bootstyle="light")
        actions_frame.pack(fill="x", padx=20, pady=10)
        
        actions = [
            ("➕ New Order", self.setup_order_tab, "success"),
            ("📊 View Reports", lambda: self.navigate_to("icon Reports"), "info"),
            ("📦 Manage Inventory", lambda: self.navigate_to("icon Inventory"), "warning"),
            ("⬇️ Download Reports", self.download_reports, "secondary")  # <-- Add this line
        ]
        
        for i, (text, command, style) in enumerate(actions):
            btn = AnimatedButton(actions_frame, text=text, command=command, bootstyle=style, cursor="hand2")
            btn.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            actions_frame.grid_columnconfigure(i, weight=1)

    # --- MENU TAB ---
    def setup_menu_tab(self):
        frame = self.frames["Menu"]
        for widget in frame.winfo_children():
            widget.destroy()
            
        tb.Label(frame, text="Menu Management", font=("Segoe UI", 18, "bold"), 
                bootstyle="primary").pack(pady=(20, 10))
        
        # Action buttons
        btn_frame = tb.Frame(frame, bootstyle="light")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        actions = [
            ("Add Item", self.add_menu_item, "success"),
            ("Edit Item", self.edit_menu_item, "warning"),
            ("Delete Item", self.delete_menu_item, "danger"),
            ("Refresh", self.refresh_menu, "secondary")
        ]
        
        for i, (text, command, style) in enumerate(actions):
            btn = AnimatedButton(btn_frame, text=text, command=command, bootstyle=style, cursor="hand2")
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            btn_frame.grid_columnconfigure(i, weight=1)
        
        # Menu table
        table_frame = tb.Frame(frame, bootstyle="light")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("ID", "Name", "Price", "Category", "Available")
        self.menu_tree = tb.Treeview(table_frame, columns=columns, show="headings", height=15, bootstyle="info")
        
        for col in columns:
            self.menu_tree.heading(col, text=col)
            self.menu_tree.column(col, width=120, anchor="center")
        
        # Add scrollbars
        tree_vscroll = tb.Scrollbar(table_frame, orient="vertical", command=self.menu_tree.yview, bootstyle="primary-round")
        tree_hscroll = tb.Scrollbar(table_frame, orient="horizontal", command=self.menu_tree.xview, bootstyle="primary-round")
        self.menu_tree.configure(yscrollcommand=tree_vscroll.set, xscrollcommand=tree_hscroll.set)
        
        self.menu_tree.grid(row=0, column=0, sticky="nsew")
        tree_vscroll.grid(row=0, column=1, sticky="ns")
        tree_hscroll.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.refresh_menu()

    def refresh_menu(self):
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)
        
        for item in self.menu_items:
            self.menu_tree.insert("", "end", values=(
                item.get("id", ""), 
                item.get("name", ""), 
                f"₹{item.get('price', 0):.2f}", 
                item.get("category", ""), 
                "Yes" if item.get("available", False) else "No"
            ))

    def add_menu_item(self):
        add_window = tb.Toplevel(self.root)
        add_window.title("Add Menu Item")
        add_window.geometry("400x450")
        add_window.resizable(False, False)
        add_window.transient(self.root)
        add_window.grab_set()
        
        # Center the window
        add_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - add_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - add_window.winfo_height()) // 2
        add_window.geometry(f"+{x}+{y}")
        
        tb.Label(add_window, text="Add New Menu Item", font=("Segoe UI", 14, "bold"), 
                bootstyle="primary").pack(pady=10)
        
        form_frame = tb.Frame(add_window, bootstyle="light")
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        fields = [
            ("ID:", "entry", str(max([item.get("id", 0) for item in self.menu_items], default=0) + 1)),
            ("Name:", "entry", ""),
            ("Price:", "entry", ""),
            ("Category:", "combo", ["Main Course", "Side Dish", "Beverage", "Dessert"]),
            ("Available:", "check", True)
        ]
        
        entries = {}
        for i, (label, field_type, default) in enumerate(fields):
            lbl = tb.Label(form_frame, text=label, bootstyle="primary")
            lbl.grid(row=i, column=0, sticky="w", pady=5)
            
            if field_type == "entry":
                ent = tb.Entry(form_frame, bootstyle="primary")
                ent.insert(0, default)
                ent.grid(row=i, column=1, sticky="ew", pady=5, padx=(10, 0))
                entries[label.lower().replace(":", "")] = ent
            elif field_type == "combo":
                var = tk.StringVar(value=default[0] if default else "")
                combo = tb.Combobox(form_frame, textvariable=var, values=default, bootstyle="primary")
                combo.grid(row=i, column=1, sticky="ew", pady=5, padx=(10, 0))
                entries[label.lower().replace(":", "")] = var
            elif field_type == "check":
                var = tk.BooleanVar(value=default)
                check = tb.Checkbutton(form_frame, text="", variable=var, bootstyle="primary-round-toggle")
                check.grid(row=i, column=1, sticky="w", pady=5, padx=(10, 0))
                entries[label.lower().replace(":", "")] = var
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        def save_item():
            try:
                new_id = int(entries["id"].get())
                new_item = {
                    "id": new_id,
                    "name": entries["name"].get(),
                    "price": float(entries["price"].get()),
                    "category": entries["category"].get(),
                    "available": entries["available"].get()
                }
                self.menu_items.append(new_item)
                self.save_data("menu.json", self.menu_items)
                self.refresh_menu()
                self.refresh_available_menu()
                add_window.destroy()
                messagebox.showinfo("Success", "Menu item added successfully!")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid data")
        
        btn_frame = tb.Frame(add_window, bootstyle="light")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        tb.Button(btn_frame, text="Cancel", bootstyle="secondary", 
                 command=add_window.destroy, cursor="hand2").pack(side="right", padx=5)
        tb.Button(btn_frame, text="Save", bootstyle="success", 
                 command=save_item, cursor="hand2").pack(side="right", padx=5)

    def edit_menu_item(self):
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item_id = int(self.menu_tree.item(selected[0])["values"][0])
        item = next((x for x in self.menu_items if x.get("id", 0) == item_id), None)
        
        if not item:
            messagebox.showerror("Error", "Item not found")
            return
        
        edit_window = tb.Toplevel(self.root)
        edit_window.title("Edit Menu Item")
        edit_window.geometry("400x450")
        edit_window.resizable(False, False)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Center the window
        edit_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - edit_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - edit_window.winfo_height()) // 2
        edit_window.geometry(f"+{x}+{y}")
        
        tb.Label(edit_window, text="Edit Menu Item", font=("Segoe UI", 14, "bold"), 
                bootstyle="primary").pack(pady=10)
        
        form_frame = tb.Frame(edit_window, bootstyle="light")
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        fields = [
            ("ID:", "entry", str(item.get("id", ""))),
            ("Name:", "entry", item.get("name", "")),
            ("Price:", "entry", str(item.get("price", ""))),
            ("Category:", "combo", ["Main Course", "Side Dish", "Beverage", "Dessert"]),
            ("Available:", "check", item.get("available", True))
        ]
        
        entries = {}
        for i, (label, field_type, default) in enumerate(fields):
            lbl = tb.Label(form_frame, text=label, bootstyle="primary")
            lbl.grid(row=i, column=0, sticky="w", pady=5)
            
            if field_type == "entry":
                ent = tb.Entry(form_frame, bootstyle="primary")
                ent.insert(0, default)
                ent.grid(row=i, column=1, sticky="ew", pady=5, padx=(10, 0))
                entries[label.lower().replace(":", "")] = ent
            elif field_type == "combo":
                var = tk.StringVar(value=item.get("category", ""))
                combo = tb.Combobox(form_frame, textvariable=var, values=default, bootstyle="primary")
                combo.grid(row=i, column=1, sticky="ew", pady=5, padx=(10, 0))
                entries[label.lower().replace(":", "")] = var
            elif field_type == "check":
                var = tk.BooleanVar(value=item.get("available", True))
                check = tb.Checkbutton(form_frame, text="", variable=var, bootstyle="primary-round-toggle")
                check.grid(row=i, column=1, sticky="w", pady=5, padx=(10, 0))
                entries[label.lower().replace(":", "")] = var
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        def update_item():
            try:
                item["id"] = int(entries["id"].get())
                item["name"] = entries["name"].get()
                item["price"] = float(entries["price"].get())
                item["category"] = entries["category"].get()
                item["available"] = entries["available"].get()
                self.save_data("menu.json", self.menu_items)
                self.refresh_menu()
                self.refresh_available_menu()
                edit_window.destroy()
                messagebox.showinfo("Success", "Menu item updated successfully!")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid data")
        
        btn_frame = tb.Frame(edit_window, bootstyle="light")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        tb.Button(btn_frame, text="Cancel", bootstyle="secondary", 
                 command=edit_window.destroy, cursor="hand2").pack(side="right", padx=5)
        tb.Button(btn_frame, text="Update", bootstyle="success", 
                 command=update_item, cursor="hand2").pack(side="right", padx=5)

    def delete_menu_item(self):
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        item_id = int(self.menu_tree.item(selected[0])["values"][0])
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            self.menu_items = [item for item in self.menu_items if item.get("id", 0) != item_id]
            self.save_data("menu.json", self.menu_items)
            self.refresh_menu()
            self.refresh_available_menu()
            messagebox.showinfo("Success", "Menu item deleted successfully!")

    # --- ORDER TAB ---
    def setup_order_tab(self):
        frame = self.frames["Orders"]
        for widget in frame.winfo_children():
            widget.destroy()
            
        tb.Label(frame, text="Order Processing", font=("Segoe UI", 18, "bold"), 
                bootstyle="primary").pack(pady=(20, 10))
        
        # Two-panel layout
        paned_window = tb.PanedWindow(frame, orient=tk.HORIZONTAL, bootstyle="primary")
        paned_window.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left panel - Available menu items
        left_frame = tb.Frame(paned_window, bootstyle="light")
        paned_window.add(left_frame, weight=1)
        
        tb.Label(left_frame, text="Available Menu Items", font=("Segoe UI", 12, "bold"), 
                bootstyle="primary").pack(pady=(0, 10))
        
        # Menu items table
        menu_tree_frame = tb.Frame(left_frame, bootstyle="light")
        menu_tree_frame.pack(fill="both", expand=True)
        
        columns = ("ID", "Name", "Price", "Category")
        self.available_menu_tree = tb.Treeview(menu_tree_frame, columns=columns, show="headings", height=15, bootstyle="info")
        
        for col in columns:
            self.available_menu_tree.heading(col, text=col)
            self.available_menu_tree.column(col, width=100, anchor="center")
        
        # Add scrollbars
        menu_vscroll = tb.Scrollbar(menu_tree_frame, orient="vertical", command=self.available_menu_tree.yview, bootstyle="primary-round")
        menu_hscroll = tb.Scrollbar(menu_tree_frame, orient="horizontal", command=self.available_menu_tree.xview, bootstyle="primary-round")
        self.available_menu_tree.configure(yscrollcommand=menu_vscroll.set, xscrollcommand=menu_hscroll.set)
        
        self.available_menu_tree.grid(row=0, column=0, sticky="nsew")
        menu_vscroll.grid(row=0, column=1, sticky="ns")
        menu_hscroll.grid(row=1, column=0, sticky="ew")
        
        menu_tree_frame.grid_rowconfigure(0, weight=1)
        menu_tree_frame.grid_columnconfigure(0, weight=1)
        
        # Right panel - Current order
        right_frame = tb.Frame(paned_window, bootstyle="light")
        paned_window.add(right_frame, weight=1)
        
        tb.Label(right_frame, text="Current Order", font=("Segoe UI", 12, "bold"), 
                bootstyle="primary").pack(pady=(0, 10))
        
        # Order items table
        order_tree_frame = tb.Frame(right_frame, bootstyle="light")
        order_tree_frame.pack(fill="both", expand=True)
        
        columns = ("ID", "Name", "Price", "Qty", "Total")
        self.order_tree = tb.Treeview(order_tree_frame, columns=columns, show="headings", height=10, bootstyle="info")
        
        for col in columns:
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, width=80, anchor="center")
        
        # Add scrollbars
        order_vscroll = tb.Scrollbar(order_tree_frame, orient="vertical", command=self.order_tree.yview, bootstyle="primary-round")
        order_hscroll = tb.Scrollbar(order_tree_frame, orient="horizontal", command=self.order_tree.xview, bootstyle="primary-round")
        self.order_tree.configure(yscrollcommand=order_vscroll.set, xscrollcommand=order_hscroll.set)
        
        self.order_tree.grid(row=0, column=0, sticky="nsew")
        order_vscroll.grid(row=0, column=1, sticky="ns")
        order_hscroll.grid(row=1, column=0, sticky="ew")
        
        order_tree_frame.grid_rowconfigure(0, weight=1)
        order_tree_frame.grid_columnconfigure(0, weight=1)
        
        # Order summary and buttons
        summary_frame = tb.Frame(right_frame, bootstyle="light")
        summary_frame.pack(fill="x", pady=10)
        
        self.total_var = tk.StringVar(value="Total: ₹0.00")
        total_label = tb.Label(summary_frame, textvariable=self.total_var, font=("Segoe UI", 14, "bold"), 
                              bootstyle="primary")
        total_label.pack(side="left", padx=10)
        
        button_frame = tb.Frame(right_frame, bootstyle="light")
        button_frame.pack(fill="x", pady=10)
        
        actions = [
            ("Add to Order", self.add_to_order, "success"),
            ("Remove from Order", self.remove_from_order, "warning"),
            ("Clear Order", self.clear_order, "secondary"),
            ("Checkout", self.checkout_order, "danger")
        ]
        
        for i, (text, command, style) in enumerate(actions):
            btn = AnimatedButton(button_frame, text=text, command=command, bootstyle=style, cursor="hand2")
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            button_frame.grid_columnconfigure(i, weight=1)
        
        self.current_order = []
        self.refresh_available_menu()

    def refresh_order_tree(self):
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        total = 0
        for item in self.current_order:
            self.order_tree.insert("", "end", values=(
                item["id"], item["name"], f"₹{item['price']:.2f}", item["quantity"], f"₹{item['total']:.2f}"
            ))
            total += item["total"]
        self.total_var.set(f"Total: ₹{total:.2f}")

    def add_to_order(self):
        selected = self.available_menu_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a menu item to add")
            return
        item_id = int(self.available_menu_tree.item(selected[0])["values"][0])
        menu_item = next((x for x in self.menu_items if x.get("id", 0) == item_id), None)
        if not menu_item:
            messagebox.showerror("Error", "Menu item not found")
            return
        # Ask for quantity
        qty_win = tb.Toplevel(self.root)
        qty_win.title("Select Quantity")
        qty_win.geometry("300x150")
        tb.Label(qty_win, text=f"Add '{menu_item['name']}' to order", font=("Segoe UI", 12, "bold")).pack(pady=10)
        qty_var = tk.IntVar(value=1)
        tb.Entry(qty_win, textvariable=qty_var, font=("Segoe UI", 12)).pack(pady=10)
        def confirm_qty():
            qty = qty_var.get()
            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be positive")
                return
            # Add to current order
            for item in self.current_order:
                if item["id"] == menu_item["id"]:
                    item["quantity"] += qty
                    item["total"] = item["quantity"] * menu_item["price"]
                    break
            else:
                self.current_order.append({
                    "id": menu_item["id"],
                    "name": menu_item["name"],
                    "price": menu_item["price"],
                    "quantity": qty,
                    "total": qty * menu_item["price"]
                })
            self.refresh_order_tree()
            qty_win.destroy()
        tb.Button(qty_win, text="Add", bootstyle="success", command=confirm_qty).pack(pady=5)
        tb.Button(qty_win, text="Cancel", bootstyle="secondary", command=qty_win.destroy).pack()

    def remove_from_order(self):
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        item_id = int(self.order_tree.item(selected[0])["values"][0])
        self.current_order = [item for item in self.current_order if item["id"] != item_id]
        self.refresh_order_tree()

    def clear_order(self):
        self.current_order = []
        self.refresh_order_tree()

    def checkout_order(self):
        if not self.current_order:
            messagebox.showwarning("Warning", "No items in order")
            return
        # Create order record
        order_id = max([o.get("id", 0) for o in self.orders], default=0) + 1
        total = sum(item["total"] for item in self.current_order)
        order = {
            "id": order_id,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": self.current_order.copy(),
            "total": total,
            "status": "Completed"
        }
        self.orders.append(order)
        self.save_data("orders.json", self.orders)
        self.clear_order()
        messagebox.showinfo("Success", f"Order #{order_id} placed successfully!")

    # --- REPORTS TAB ---
    def setup_reports_tab(self):
        frame = self.frames["Reports"]
        for widget in frame.winfo_children():
            widget.destroy()

        # Refresh button
        refresh_btn = AnimatedButton(frame, text="🔄 Refresh", bootstyle="info", command=self.setup_reports_tab, cursor="hand2")
        refresh_btn.place(relx=0.98, rely=0.02, anchor="ne")

        # Tabbed notebook for reports
        notebook = tb.Notebook(frame, bootstyle="primary")
        notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Sales Report Tab ---
        sales_tab = tb.Frame(notebook, bootstyle="light")
        notebook.add(sales_tab, text="Sales Report")
        self._build_sales_report(sales_tab)

        # --- Top-Selling Items Tab ---
        top_tab = tb.Frame(notebook, bootstyle="light")
        notebook.add(top_tab, text="Top-Selling Items")
        self._build_top_selling_report(top_tab)

        # --- Inventory Usage Tab ---
        usage_tab = tb.Frame(notebook, bootstyle="light")
        notebook.add(usage_tab, text="Inventory Usage")
        self._build_inventory_usage_report(usage_tab)

        # --- Low Stock Tab ---
        low_tab = tb.Frame(notebook, bootstyle="light")
        notebook.add(low_tab, text="Low Stock")
        self._build_low_stock_report(low_tab)

        # --- Wastage & Expiry Tab ---
        wastage_tab = tb.Frame(notebook, bootstyle="light")
        notebook.add(wastage_tab, text="Wastage & Expiry")
        self._build_wastage_expiry_report(wastage_tab)

        # --- Profit/Loss Tab ---
        profit_tab = tb.Frame(notebook, bootstyle="light")
        notebook.add(profit_tab, text="Profit/Loss")
        self._build_profit_loss_report(profit_tab)

        # --- Peak Hour Tab ---
        peak_tab = tb.Frame(notebook, bootstyle="light")
        notebook.add(peak_tab, text="Peak Hour")
        self._build_peak_hour_report(peak_tab)

    # --- Helper methods for each report tab ---
    def _build_sales_report(self, tab):
        tb.Label(tab, text="Sales Report", font=("Segoe UI", 16, "bold"), bootstyle="primary").pack(pady=(20, 10))
        sales_by_day = {}
        for order in self.orders:
            dt = order.get("datetime", "")[:10]
            sales_by_day.setdefault(dt, 0)
            sales_by_day[dt] += order.get("total", 0)
        days = sorted(sales_by_day.keys())
        sales = [sales_by_day[d] for d in days]
        fig, ax = plt.subplots(figsize=(5, 2.5))
        ax.bar(days, sales, color="#4caf50")
        ax.set_title("Daily Sales")
        ax.set_ylabel("Revenue (₹)")
        ax.set_xlabel("Date")
        fig.tight_layout()
        sales_canvas = FigureCanvasTkAgg(fig, master=tab)
        sales_canvas.draw()
        sales_canvas.get_tk_widget().pack(fill="both", expand=True)
        # Zoom buttons
        zoom_frame = tb.Frame(tab, bootstyle="light")
        zoom_frame.pack(anchor="ne", padx=10)
        tb.Button(zoom_frame, text="➕", bootstyle="success", command=lambda: self.zoom_figure(fig, sales_canvas, 1.2)).pack(side="left", padx=2)
        tb.Button(zoom_frame, text="➖", bootstyle="danger", command=lambda: self.zoom_figure(fig, sales_canvas, 0.8)).pack(side="left", padx=2)
        # Sales summary
        total_sales = sum(sales)
        tb.Label(tab, text=f"Total Sales: ₹{total_sales:.2f}", font=("Segoe UI", 12), bootstyle="success").pack(anchor="w", padx=20, pady=10)

    def _build_top_selling_report(self, tab):
        tb.Label(tab, text="Top-Selling Items", font=("Segoe UI", 16, "bold"), bootstyle="primary").pack(pady=(20, 10))
        item_sales = {}
        for order in self.orders:
            for item in order.get("items", []):
                name = item["name"]
                item_sales.setdefault(name, 0)
                item_sales[name] += item["quantity"]
        top_names = list(item_sales.keys())
        top_quantities = [item_sales[n] for n in top_names]
        fig2, ax2 = plt.subplots(figsize=(4, 2.5))
        ax2.pie(top_quantities, labels=top_names, autopct='%1.1f%%', startangle=140)
        ax2.set_title("Top-Selling Items")
        fig2.tight_layout()
        pie_canvas = FigureCanvasTkAgg(fig2, master=tab)
        pie_canvas.draw()
        pie_canvas.get_tk_widget().pack(fill="both", expand=True)
        zoom_frame = tb.Frame(tab, bootstyle="light")
        zoom_frame.pack(anchor="ne", padx=10)
        tb.Button(zoom_frame, text="➕", bootstyle="success", command=lambda: self.zoom_figure(fig2, pie_canvas, 1.2)).pack(side="left", padx=2)
        tb.Button(zoom_frame, text="➖", bootstyle="danger", command=lambda: self.zoom_figure(fig2, pie_canvas, 0.8)).pack(side="left", padx=2)

    def _build_inventory_usage_report(self, tab):
        tb.Label(tab, text="Inventory Usage Report", font=("Segoe UI", 16, "bold"), bootstyle="primary").pack(pady=(20, 10))
        used = {}
        for order in self.orders:
            for item in order.get("items", []):
                recipe = RECIPE_MAP.get(item["id"], {})
                for inv_name, qty_per in recipe.items():
                    used.setdefault(inv_name, 0)
                    used[inv_name] += qty_per * item["quantity"]
        available = {item["name"]: item["quantity"] for item in self.inventory}
        inv_names = list(available.keys())
        used_qty = [used.get(n, 0) for n in inv_names]
        avail_qty = [available[n] for n in inv_names]
        fig3, ax3 = plt.subplots(figsize=(5, 2.5))
        ax3.plot(inv_names, avail_qty, label="Available", marker='o')
        ax3.plot(inv_names, used_qty, label="Used", marker='o')
        ax3.set_title("Inventory Usage")
        ax3.set_ylabel("Quantity")
        ax3.set_xlabel("Item")
        ax3.legend()
        fig3.tight_layout()
        usage_canvas = FigureCanvasTkAgg(fig3, master=tab)
        usage_canvas.draw()
        usage_canvas.get_tk_widget().pack(fill="both", expand=True)
        zoom_frame = tb.Frame(tab, bootstyle="light")
        zoom_frame.pack(anchor="ne", padx=10)
        tb.Button(zoom_frame, text="➕", bootstyle="success", command=lambda: self.zoom_figure(fig3, usage_canvas, 1.2)).pack(side="left", padx=2)
        tb.Button(zoom_frame, text="➖", bootstyle="danger", command=lambda: self.zoom_figure(fig3, usage_canvas, 0.8)).pack(side="left", padx=2)

    def _build_low_stock_report(self, tab):
        tb.Label(tab, text="Low Stock Report", font=("Segoe UI", 16, "bold"), bootstyle="primary").pack(pady=(20, 10))
        columns = ("ID", "Name", "Category", "Quantity", "Threshold")
        tree = tb.Treeview(tab, columns=columns, show="headings", height=12, bootstyle="danger")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        scroll = tb.Scrollbar(tab, orient="vertical", command=tree.yview, bootstyle="danger-round")
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        for item in self.inventory:
            if float(item.get("quantity", 0)) < float(item.get("threshold", 0)):
                tree.insert("", "end", values=(
                    item.get("id", ""), item.get("name", ""), item.get("category", ""),
                    item.get("quantity", ""), item.get("threshold", "")
                ), tags=("low",))
        tree.tag_configure("low", foreground="red")

    def _build_wastage_expiry_report(self, tab):
        tb.Label(tab, text="Wastage & Expiry Report", font=("Segoe UI", 16, "bold"), bootstyle="primary").pack(pady=(20, 10))
        expired_items = []
        today = datetime.now().date()
        for item in self.inventory:
            try:
                expiry = datetime.strptime(item.get("expiry_date", ""), "%Y-%m-%d").date()
                if expiry < today:
                    expired_items.append(item)
            except Exception:
                continue
        expiry_trend = {}
        for item in expired_items:
            try:
                expiry = datetime.strptime(item.get("expiry_date", ""), "%Y-%m-%d").date()
                key = expiry.strftime("%Y-%m")
                expiry_trend.setdefault(key, 0)
                expiry_trend[key] += 1
            except Exception:
                continue
        months = sorted(expiry_trend.keys())
        counts = [expiry_trend[m] for m in months]
        fig4, ax4 = plt.subplots(figsize=(4, 2.5))
        ax4.plot(months, counts, marker='o', color="red")
        ax4.set_title("Wastage Trend (Expired Items)")
        ax4.set_ylabel("Count")
        ax4.set_xlabel("Month")
        fig4.tight_layout()
        wastage_canvas = FigureCanvasTkAgg(fig4, master=tab)
        wastage_canvas.draw()
        wastage_canvas.get_tk_widget().pack(fill="both", expand=True)
        zoom_frame = tb.Frame(tab, bootstyle="light")
        zoom_frame.pack(anchor="ne", padx=10)
        tb.Button(zoom_frame, text="➕", bootstyle="success", command=lambda: self.zoom_figure(fig4, wastage_canvas, 1.2)).pack(side="left", padx=2)
        tb.Button(zoom_frame, text="➖", bootstyle="danger", command=lambda: self.zoom_figure(fig4, wastage_canvas, 0.8)).pack(side="left", padx=2)
        # Table of expired items
        tb.Label(tab, text="Expired Items", font=("Segoe UI", 12, "bold"), bootstyle="danger").pack(pady=(20, 5))
        expired_tree = tb.Treeview(tab, columns=("ID", "Name", "Expiry Date"), show="headings", height=8, bootstyle="danger")
        for col in ("ID", "Name", "Expiry Date"):
            expired_tree.heading(col, text=col)
            expired_tree.column(col, width=100, anchor="center")
        expired_tree.pack(fill="both", expand=True, padx=20, pady=10)
        expired_scroll = tb.Scrollbar(tab, orient="vertical", command=expired_tree.yview, bootstyle="danger-round")
        expired_tree.configure(yscrollcommand=expired_scroll.set)
        expired_scroll.pack(side="right", fill="y")
        for item in expired_items:
            expired_tree.insert("", "end", values=(item.get("id", ""), item.get("name", ""), item.get("expiry_date", "")), tags=("expired",))
        expired_tree.tag_configure("expired", foreground="red")

    def _build_profit_loss_report(self, tab):
        tb.Label(tab, text="Profit/Loss Report", font=("Segoe UI", 16, "bold"), bootstyle="primary").pack(pady=(20, 10))
        total_revenue = sum(order.get("total", 0) for order in self.orders)
        total_cost = 0
        for order in self.orders:
            for item in order.get("items", []):
                recipe = RECIPE_MAP.get(item["id"], {})
                for inv_name, qty_per in recipe.items():
                    inv_item = next((x for x in self.inventory if x["name"] == inv_name), None)
                    if inv_item:
                        total_cost += qty_per * item["quantity"] * inv_item.get("supplier_price", 0)
        net_profit = total_revenue - total_cost
        fig5, ax5 = plt.subplots(figsize=(4, 2.5))
        ax5.bar(["Revenue", "Cost", "Profit"], [total_revenue, total_cost, net_profit], color=["#4caf50", "#f44336", "#2196f3"])
        ax5.set_title("Profit/Loss")
        ax5.set_ylabel("Amount (₹)")
        fig5.tight_layout()
        profit_canvas = FigureCanvasTkAgg(fig5, master=tab)
        profit_canvas.draw()
        profit_canvas.get_tk_widget().pack(fill="both", expand=True)
        zoom_frame = tb.Frame(tab, bootstyle="light")
        zoom_frame.pack(anchor="ne", padx=10)
        tb.Button(zoom_frame, text="➕", bootstyle="success", command=lambda: self.zoom_figure(fig5, profit_canvas, 1.2)).pack(side="left", padx=2)
        tb.Button(zoom_frame, text="➖", bootstyle="danger", command=lambda: self.zoom_figure(fig5, profit_canvas, 0.8)).pack(side="left", padx=2)
        tb.Label(tab, text=f"Total Revenue: ₹{total_revenue:.2f}", font=("Segoe UI", 12), bootstyle="success").pack(anchor="w", padx=20, pady=5)
        tb.Label(tab, text=f"Total Cost: ₹{total_cost:.2f}", font=("Segoe UI", 12), bootstyle="danger").pack(anchor="w", padx=20, pady=5)
        tb.Label(tab, text=f"Net Profit: ₹{net_profit:.2f}", font=("Segoe UI", 12), bootstyle="info").pack(anchor="w", padx=20, pady=5)

    def _build_peak_hour_report(self, tab):
        tb.Label(tab, text="Peak Hour Report", font=("Segoe UI", 16, "bold"), bootstyle="primary").pack(pady=(20, 10))
        hour_counts = {}
        for order in self.orders:
            try:
                dt = datetime.strptime(order.get("datetime", ""), "%Y-%m-%d %H:%M:%S")
                hour = dt.strftime("%H")
                hour_counts.setdefault(hour, 0)
                hour_counts[hour] += 1
            except Exception:
                continue
        hours = sorted(hour_counts.keys())
        counts = [hour_counts[h] for h in hours]
        fig6, ax6 = plt.subplots(figsize=(5, 2.5))
        ax6.plot(hours, counts, marker='o', color="#ff9800")
        ax6.set_title("Peak Hours (Orders per Hour)")
        ax6.set_ylabel("Orders")
        ax6.set_xlabel("Hour")
        fig6.tight_layout()
        peak_canvas = FigureCanvasTkAgg(fig6, master=tab)
        peak_canvas.draw()
        peak_canvas.get_tk_widget().pack(fill="both", expand=True)
        zoom_frame = tb.Frame(tab, bootstyle="light")
        zoom_frame.pack(anchor="ne", padx=10)
        tb.Button(zoom_frame, text="➕", bootstyle="success", command=lambda: self.zoom_figure(fig6, peak_canvas, 1.2)).pack(side="left", padx=2)
        tb.Button(zoom_frame, text="➖", bootstyle="danger", command=lambda: self.zoom_figure(fig6, peak_canvas, 0.8)).pack(side="left", padx=2)

    def download_reports(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Canteen_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            title="Save Report As"
        )
        if not filename:
            return  # User cancelled
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # --- Sales Report ---
        elements.append(Paragraph("Sales Report", styles['Heading2']))
        sales_by_day = {}
        for order in self.orders:
            dt = order.get("datetime", "")[:10]
            sales_by_day.setdefault(dt, 0)
            sales_by_day[dt] += order.get("total", 0)
        days = sorted(sales_by_day.keys())
        sales = [sales_by_day[d] for d in days]
        sales_table = [["Date", "Sales (₹)"]]
        for d in days:
            sales_table.append([d, f"{sales_by_day[d]:.2f}"])
        elements.append(Table(sales_table, hAlign='LEFT'))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Total Sales: ₹{sum(sales):.2f}", styles['Normal']))
        elements.append(PageBreak())

        # --- Top-Selling Items ---
        elements.append(Paragraph("Top-Selling Items", styles['Heading2']))
        item_sales = {}
        for order in self.orders:
            for item in order.get("items", []):
                name = item["name"]
                item_sales.setdefault(name, 0)
                item_sales[name] += item["quantity"]
        top_table = [["Item", "Quantity Sold"]]
        for name, qty in item_sales.items():
            top_table.append([name, qty])
        elements.append(Table(top_table, hAlign='LEFT'))
        elements.append(PageBreak())

        # --- Inventory Usage ---
        elements.append(Paragraph("Inventory Usage Report", styles['Heading2']))
        used = {}
        for order in self.orders:
            for item in order.get("items", []):
                recipe = RECIPE_MAP.get(item["id"], {})
                for inv_name, qty_per in recipe.items():
                    used.setdefault(inv_name, 0)
                    used[inv_name] += qty_per * item["quantity"]
        available = {item["name"]: item["quantity"] for item in self.inventory}
        usage_table = [["Item", "Available", "Used"]]
        for name in available:
            usage_table.append([name, available[name], used.get(name, 0)])
        elements.append(Table(usage_table, hAlign='LEFT'))
        elements.append(PageBreak())

        # --- Low Stock Report ---
        elements.append(Paragraph("Low Stock Report", styles['Heading2']))
        low_table = [["ID", "Name", "Category", "Quantity", "Threshold"]]
        for item in self.inventory:
            if float(item.get("quantity", 0)) < float(item.get("threshold", 0)):
                low_table.append([
                    item.get("id", ""), item.get("name", ""), item.get("category", ""),
                    item.get("quantity", ""), item.get("threshold", "")
                ])
        elements.append(Table(low_table, hAlign='LEFT'))
        elements.append(PageBreak())

        # --- Wastage & Expiry Report ---
        elements.append(Paragraph("Wastage & Expiry Report", styles['Heading2']))
        expired_items = []
        today = datetime.now().date()
        for item in self.inventory:
            try:
                expiry = datetime.strptime(item.get("expiry_date", ""), "%Y-%m-%d").date()
                if expiry < today:
                    expired_items.append(item)
            except Exception:
                continue
        expired_table = [["ID", "Name", "Expiry Date"]]
        for item in expired_items:
            expired_table.append([item.get("id", ""), item.get("name", ""), item.get("expiry_date", "")])
        elements.append(Table(expired_table, hAlign='LEFT'))
        elements.append(PageBreak())

        # --- Profit/Loss Report ---
        elements.append(Paragraph("Profit/Loss Report", styles['Heading2']))
        total_revenue = sum(order.get("total", 0) for order in self.orders)
        total_cost = 0
        for order in self.orders:
            for item in order.get("items", []):
                recipe = RECIPE_MAP.get(item["id"], {})
                for inv_name, qty_per in recipe.items():
                    inv_item = next((x for x in self.inventory if x["name"] == inv_name), None)
                    if inv_item:
                        total_cost += qty_per * item["quantity"] * inv_item.get("supplier_price", 0)
        net_profit = total_revenue - total_cost
        profit_table = [
            ["Total Revenue (₹)", f"{total_revenue:.2f}"],
            ["Total Cost (₹)", f"{total_cost:.2f}"],
            ["Net Profit (₹)", f"{net_profit:.2f}"]
        ]
        elements.append(Table(profit_table, hAlign='LEFT'))
        elements.append(PageBreak())

        # --- Peak Hour Report ---
        elements.append(Paragraph("Peak Hour Report", styles['Heading2']))
        hour_counts = {}
        for order in self.orders:
            try:
                dt = datetime.strptime(order.get("datetime", ""), "%Y-%m-%d %H:%M:%S")
                hour = dt.strftime("%H")
                hour_counts.setdefault(hour, 0)
                hour_counts[hour] += 1
            except Exception:
                continue
        peak_table = [["Hour", "Orders"]]
        for hour in sorted(hour_counts.keys()):
            peak_table.append([hour, hour_counts[hour]])
        elements.append(Table(peak_table, hAlign='LEFT'))

        # Build PDF
        try:
            doc.build(elements)
            messagebox.showinfo("Report Downloaded", f"Report saved as {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")

    # --- Settings Tab ---
    def setup_settings_tab(self):
        frame = self.frames["Settings"]
        for widget in frame.winfo_children():
            widget.destroy()
        tb.Label(frame, text="Settings", font=("Segoe UI", 18, "bold"), bootstyle="primary").pack(pady=20)
        # Add settings options here

    def ensure_inventory_fields(self):
        for item in self.inventory:
            for field in INVENTORY_FIELDS:
                if field not in item:
                    if field == "id":
                        item[field] = max([x.get("id", 0) for x in self.inventory], default=0) + 1
                    elif field in ["quantity", "threshold", "supplier_price", "unit_price", "total_value"]:
                        item[field] = 0.0
                    elif field == "last_restock":
                        item[field] = datetime.now().strftime("%Y-%m-%d")
                    elif field == "status":
                        item[field] = "Available"
                    else:
                        item[field] = ""
            item["total_value"] = float(item.get("quantity", 0)) * float(item.get("unit_price", 0))

    # --- INVENTORY TAB ---
    def setup_inventory_tab(self):
        frame = self.frames["Inventory"]
        for widget in frame.winfo_children():
            widget.destroy()
        tb.Label(frame, text="Inventory Management", font=("Segoe UI", 18, "bold"), bootstyle="primary").pack(pady=20)

        # Action buttons
        btn_frame = tb.Frame(frame, bootstyle="light")
        btn_frame.pack(fill="x", padx=20, pady=10)
        actions = [
            ("Add Item", self.add_inventory_item, "success"),
            ("Edit Item", self.edit_inventory_item, "warning"),
            ("Delete Item", self.delete_inventory_item, "danger"),
            ("Refresh", self.refresh_inventory, "secondary")
        ]
        for i, (text, command, style) in enumerate(actions):
            btn = AnimatedButton(btn_frame, text=text, command=command, bootstyle=style, cursor="hand2")
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            btn_frame.grid_columnconfigure(i, weight=1)

        # Inventory table
        table_frame = tb.Frame(frame, bootstyle="light")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = INVENTORY_FIELDS
        self.inventory_tree = tb.Treeview(table_frame, columns=columns, show="headings", height=15, bootstyle="info")
        for col in columns:
            self.inventory_tree.heading(col, text=col.replace("_", " ").title())
            self.inventory_tree.column(col, width=110, anchor="center")
        tree_vscroll = tb.Scrollbar(table_frame, orient="vertical", command=self.inventory_tree.yview, bootstyle="primary-round")
        tree_hscroll = tb.Scrollbar(table_frame, orient="horizontal", command=self.inventory_tree.xview, bootstyle="primary-round")
        self.inventory_tree.configure(yscrollcommand=tree_vscroll.set, xscrollcommand=tree_hscroll.set)
        self.inventory_tree.grid(row=0, column=0, sticky="nsew")
        tree_vscroll.grid(row=0, column=1, sticky="ns")
        tree_hscroll.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        self.refresh_inventory()

    def refresh_inventory(self):
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        for idx, item in enumerate(self.inventory):
            values = [item.get(col, "") for col in INVENTORY_FIELDS]
            tag = "even" if idx % 2 == 0 else "odd"
            color_tag = ""
            if item.get("status", "") == "Low Stock" or float(item.get("quantity", 0)) < float(item.get("threshold", 0)):
                color_tag = "lowstock"
            self.inventory_tree.insert("", "end", values=values, tags=(tag, color_tag))
        self.inventory_tree.tag_configure("even", background="#f7f7f7")
        self.inventory_tree.tag_configure("odd", background="#e3eafc")
        self.inventory_tree.tag_configure("lowstock", foreground="red", background="#ffeaea")

    def add_inventory_item(self):
        add_window = tb.Toplevel(self.root)
        add_window.title("Add Inventory Item")
        add_window.geometry("420x540")
        add_window.resizable(False, False)
        add_window.transient(self.root)
        add_window.grab_set()

        # --- Scrollable form ---
        container = tb.Frame(add_window)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, bg=self.style.colors.light, highlightthickness=0, height=500)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        form_frame = tb.Frame(canvas, bootstyle="light")
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _resize_form(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        form_frame.bind("<Configure>", _resize_form)

        tb.Label(form_frame, text="Add New Inventory Item", font=("Segoe UI", 14, "bold"), bootstyle="primary").grid(row=0, column=0, columnspan=2, pady=10)
        new_id = max([item.get("id", 0) for item in self.inventory], default=0) + 1
        fields = [
            ("Item ID", "readonly", str(new_id)),
            ("Item Name", "entry", ""),
            ("Category", "entry", ""),
            ("Quantity", "entry", ""),
            ("Unit", "entry", ""),
            ("Unit Price (Selling)", "entry", ""),
            ("Cost Price", "entry", ""),
            ("Expiry Date", "entry", ""),
            ("Supplier Name", "entry", ""),
            ("Supplier Contact", "entry", ""),
            ("Threshold", "entry", ""),
            ("Remarks", "entry", "")
        ]
        entries = {}
        for i, (label, field_type, default) in enumerate(fields, start=1):
            lbl = tb.Label(form_frame, text=label + ":", bootstyle="primary")
            lbl.grid(row=i, column=0, sticky="w", pady=5, padx=(10, 0))
            if field_type == "readonly":
                ent = tb.Entry(form_frame, bootstyle="secondary")
                ent.insert(0, default)
                ent.configure(state="readonly")
            else:
                ent = tb.Entry(form_frame, bootstyle="primary")
                ent.insert(0, default)
            ent.grid(row=i, column=1, sticky="ew", pady=5, padx=(0, 10))
            entries[label.lower().replace(" ", "_")] = ent
        form_frame.grid_columnconfigure(1, weight=1)

        def save_item():
            try:
                item = {
                    "id": int(entries["item_id"].get()),
                    "name": entries["item_name"].get(),
                    "category": entries["category"].get(),
                    "unit": entries["unit"].get(),
                    "quantity": float(entries["quantity"].get()),
                    "threshold": float(entries["threshold"].get()),
                    "last_restock": datetime.now().strftime("%Y-%m-%d"),
                    "expiry_date": entries["expiry_date"].get(),
                    "supplier_name": entries["supplier_name"].get(),
                    "supplier_contact": entries["supplier_contact"].get(),
                    "supplier_price": float(entries["cost_price"].get()),
                    "unit_price": float(entries["unit_price_(selling)"].get()),
                    "total_value": float(entries["quantity"].get()) * float(entries["unit_price_(selling)"].get()),
                    "status": "Available",
                    "remarks": entries["remarks"].get()
                }
                self.inventory.append(item)
                self.save_data("inventory.json", self.inventory)
                self.refresh_inventory()
                add_window.destroy()
                messagebox.showinfo("Success", "Inventory item added successfully!")
            except Exception:
                messagebox.showerror("Error", "Please enter valid data")

        btn_frame = tb.Frame(form_frame, bootstyle="light")
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        tb.Button(btn_frame, text="Cancel", bootstyle="secondary", command=add_window.destroy, cursor="hand2").pack(side="right", padx=5)
        tb.Button(btn_frame, text="Save", bootstyle="success", command=save_item, cursor="hand2").pack(side="right", padx=5)

    def edit_inventory_item(self):
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        item_id = int(self.inventory_tree.item(selected[0])["values"][0])
        item = next((x for x in self.inventory if x.get("id", 0) == item_id), None)
        if not item:
            messagebox.showerror("Error", "Item not found")
            return

        edit_window = tb.Toplevel(self.root)
        edit_window.title("Edit Inventory Item")
        edit_window.geometry("420x540")
        edit_window.resizable(False, False)
        edit_window.transient(self.root)
        edit_window.grab_set()

        container = tb.Frame(edit_window)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, bg=self.style.colors.light, highlightthickness=0, height=500)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        form_frame = tb.Frame(canvas, bootstyle="light")
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _resize_form(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        form_frame.bind("<Configure>", _resize_form)

        tb.Label(form_frame, text="Edit Inventory Item", font=("Segoe UI", 14, "bold"), bootstyle="primary").grid(row=0, column=0, columnspan=2, pady=10)
        fields = [
            ("Item ID", "readonly", str(item.get("id", ""))),
            ("Item Name", "entry", item.get("name", "")),
            ("Category", "entry", item.get("category", "")),
            ("Quantity", "entry", str(item.get("quantity", ""))),
            ("Unit", "entry", item.get("unit", "")),
            ("Unit Price (Selling)", "entry", str(item.get("unit_price", ""))),
            ("Cost Price", "entry", str(item.get("supplier_price", ""))),
            ("Expiry Date", "entry", item.get("expiry_date", "")),
            ("Supplier Name", "entry", item.get("supplier_name", "")),
            ("Supplier Contact", "entry", item.get("supplier_contact", "")),
            ("Threshold", "entry", str(item.get("threshold", ""))),
            ("Remarks", "entry", item.get("remarks", ""))
        ]
        entries = {}
        for i, (label, field_type, default) in enumerate(fields, start=1):
            lbl = tb.Label(form_frame, text=label + ":", bootstyle="primary")
            lbl.grid(row=i, column=0, sticky="w", pady=5, padx=(10, 0))
            if field_type == "readonly":
                ent = tb.Entry(form_frame, bootstyle="secondary")
                ent.insert(0, default)
                ent.configure(state="readonly")
            else:
                ent = tb.Entry(form_frame, bootstyle="primary")
                ent.insert(0, default)
            ent.grid(row=i, column=1, sticky="ew", pady=5, padx=(0, 10))
            entries[label.lower().replace(" ", "_")] = ent
        form_frame.grid_columnconfigure(1, weight=1)

        def update_item():
            try:
                item["name"] = entries["item_name"].get()
                item["category"] = entries["category"].get()
                item["unit"] = entries["unit"].get()
                item["quantity"] = float(entries["quantity"].get())
                item["threshold"] = float(entries["threshold"].get())
                item["expiry_date"] = entries["expiry_date"].get()
                item["supplier_name"] = entries["supplier_name"].get()
                item["supplier_contact"] = entries["supplier_contact"].get()
                item["supplier_price"] = float(entries["cost_price"].get())
                item["unit_price"] = float(entries["unit_price_(selling)"].get())
                item["total_value"] = float(entries["quantity"].get()) * float(entries["unit_price_(selling)"].get())
                item["remarks"] = entries["remarks"].get()
                item["last_restock"] = datetime.now().strftime("%Y-%m-%d")
                item["status"] = "Available" if item["quantity"] >= item["threshold"] else "Low Stock"
                self.save_data("inventory.json", self.inventory)
                self.refresh_inventory()
                edit_window.destroy()
                messagebox.showinfo("Success", "Inventory item updated successfully!")
            except Exception:
                messagebox.showerror("Error", "Please enter valid data")

        btn_frame = tb.Frame(form_frame, bootstyle="light")
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        tb.Button(btn_frame, text="Cancel", bootstyle="secondary", command=edit_window.destroy, cursor="hand2").pack(side="right", padx=5)
        tb.Button(btn_frame, text="Update", bootstyle="success", command=update_item, cursor="hand2").pack(side="right", padx=5)

    def delete_inventory_item(self):
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        item_id = int(self.inventory_tree.item(selected[0])["values"][0])
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            self.inventory = [item for item in self.inventory if item.get("id", 0) != item_id]
            self.save_data("inventory.json", self.inventory)
            self.refresh_inventory()
            messagebox.showinfo("Success", "Inventory item deleted successfully!")

    def refresh_inventory(self):
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        for idx, item in enumerate(self.inventory):
            values = [item.get(col, "") for col in INVENTORY_FIELDS]
            tag = "even" if idx % 2 == 0 else "odd"
            color_tag = ""
            if item.get("status", "") == "Low Stock" or float(item.get("quantity", 0)) < float(item.get("threshold", 0)):
                color_tag = "lowstock"
            self.inventory_tree.insert("", "end", values=values, tags=(tag, color_tag))
        self.inventory_tree.tag_configure("even", background="#f7f7f7")
        self.inventory_tree.tag_configure("odd", background="#e3eafc")
        self.inventory_tree.tag_configure("lowstock", foreground="red", background="#ffeaea")

    def refresh_available_menu(self):
        for item in self.available_menu_tree.get_children():
            self.available_menu_tree.delete(item)
        for item in self.menu_items:
            if item.get("available", False):
                self.available_menu_tree.insert("", "end", values=(
                    item.get("id", ""), item.get("name", ""), f"₹{item.get('price', 0):.2f}", item.get("category", "")
                ))

    def zoom_figure(self, fig, canvas, factor):
        w, h = fig.get_size_inches()
        fig.set_size_inches(w * factor, h * factor)
        canvas.draw()


if __name__ == "__main__":
    root = tb.Window(themename="minty")
    app = CanteenManagementSystem(root)
    root.mainloop()