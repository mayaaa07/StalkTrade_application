import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import random
import threading
import time
import requests
from bs4 import BeautifulSoup
import logging
from bs4 import BeautifulSoup
import json
import os
import hashlib


class LoginSystem:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.users_file = "users.json"
        self.current_user = None
        self.setup_users_file()
    
    def setup_users_file(self):
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
    
    def show_login(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("StalkTrade Pro - Login")
        self.login_window.geometry("400x300")
        self.login_window.configure(bg="#0a0e17")
        self.login_window.resizable(False, False)
        
        # Make sure main window is hidden during login
        self.root.withdraw()
        
        # Center the window
        self.center_window(self.login_window)
        
        # Make the login window modal
        self.login_window.grab_set()
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_login_close)
        
        # Title
        title_label = ttk.Label(self.login_window, text="STALKTRADE PRO", 
                              font=("Arial", 18, "bold"), foreground="#1e88e5")
        title_label.pack(pady=20)
        
        # Login Frame
        login_frame = ttk.Frame(self.login_window)
        login_frame.pack(pady=20)
        
        # Username
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Password
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.login_window)
        button_frame.pack(pady=20)
        
        login_btn = ttk.Button(button_frame, text="Login", command=self.attempt_login)
        login_btn.pack(side=tk.LEFT, padx=10)
        
        register_btn = ttk.Button(button_frame, text="Register", command=self.show_register)
        register_btn.pack(side=tk.LEFT, padx=10)
        
        # Focus on username field
        self.username_entry.focus_set()
        
        # Bind Enter key to login
        self.login_window.bind('<Return>', lambda event: self.attempt_login())
    
    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'+{x}+{y}')
    
    def on_login_close(self):
        self.root.destroy()
    
    def show_register(self):
        self.register_window = tk.Toplevel(self.login_window)
        self.register_window.title("Register New Account")
        self.register_window.geometry("400x350")
        self.register_window.configure(bg="#0a0e17")
        self.register_window.resizable(False, False)
        
        self.center_window(self.register_window)
        
        # Make the register window modal
        self.register_window.grab_set()
        
        # Title
        title_label = ttk.Label(self.register_window, text="REGISTER NEW ACCOUNT", 
                              font=("Arial", 14, "bold"), foreground="#1e88e5")
        title_label.pack(pady=15)
        
        # Register Frame
        register_frame = ttk.Frame(self.register_window)
        register_frame.pack(pady=10)
        
        # Username
        ttk.Label(register_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.reg_username_entry = ttk.Entry(register_frame)
        self.reg_username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Password
        ttk.Label(register_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.reg_password_entry = ttk.Entry(register_frame, show="*")
        self.reg_password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Confirm Password
        ttk.Label(register_frame, text="Confirm Password:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.reg_confirm_entry = ttk.Entry(register_frame, show="*")
        self.reg_confirm_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Email (optional)
        ttk.Label(register_frame, text="Email (optional):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.reg_email_entry = ttk.Entry(register_frame)
        self.reg_email_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.register_window)
        button_frame.pack(pady=15)
        
        register_btn = ttk.Button(button_frame, text="Register", command=self.register_user)
        register_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.register_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Focus on username field
        self.reg_username_entry.focus_set()
        
        # Bind Enter key to register
        self.register_window.bind('<Return>', lambda event: self.register_user())
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self):
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm = self.reg_confirm_entry.get()
        email = self.reg_email_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
            
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
            
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
        except:
            users = {}
            
        if username in users:
            messagebox.showerror("Error", "Username already exists")
            return
            
        hashed_password = self.hash_password(password)
        
        users[username] = {
        'password': hashed_password,
        'email': email,
        'portfolio': {
            # Existing stocks
            "AAPL": {"shares": 10, "avg_price": 150.25},
            "MSFT": {"shares": 5, "avg_price": 300.50},
            "TSLA": {"shares": 3, "avg_price": 220.75},
            # New portfolio additions (5 stocks)
            "V": {"shares": 1.0, "avg_price": 250.00},     # Visa
            "NVDA": {"shares": 2, "avg_price": 400.00},     # NVIDIA
            "JPM": {"shares": 4, "avg_price": 180.00},      # JPMorgan
            "HD": {"shares": 2, "avg_price": 350.00},       # Home Depot
            "BAC": {"shares": 10, "avg_price": 45.00}       # Bank of America
        },
        'watchlist': [
            # Existing
            "AAPL", "MSFT", "TSLA", 
            # New watchlist additions (5 stocks)
            "AMZN", "GOOG", "META", "PYPL", "DIS"
        ]
    }
        
        try:
            with open(self.users_file, 'w') as f:
                json.dump(users, f)
            messagebox.showinfo("Success", "Account created successfully")
            self.register_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save user data: {str(e)}")
    
    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
            
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load user data: {str(e)}")
            return
            
        if username not in users:
            messagebox.showerror("Error", "Invalid username or password")
            return
            
        hashed_password = self.hash_password(password)
        if users[username]['password'] != hashed_password:
            messagebox.showerror("Error", "Invalid username or password")
            return
            
        self.current_user = username
        self.user_data = users[username]
        self.login_window.destroy()
        self.root.deiconify()  # Show the main window
        self.on_login_success(self.user_data)


class AdvancedTradingPlatform:
    def __init__(self, root):
        self.root = root
        self.root.title("StalkTrade Pro")
        self.root.geometry("1400x900")
        self.root.configure(bg="#0a0e17")
        
        # Set custom font
        self.title_font = ("Arial", 18, "bold")
        self.header_font = ("Arial", 12, "bold")
        self.base_font = ("Arial", 10)
        
        # Create style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.configure_styles()
        
        # Current stock
        self.current_symbol = "AAPL"  # Default selected stock

        # Expanded watchlist (10 existing + 10 new = 20 total)
        self.watchlist = [
            # Original 10
            "AAPL", "MSFT", "TSLA", "AMZN", "GOOG", 
            "META", "NVDA", "JPM", "V", "DIS",
            # New additions (10 more)
            "HD", "BAC", "PYPL", "INTC", "CSCO",
            "GS", "WMT", "NFLX", "ADBE", "CRM"
        ]

        # Expanded portfolio (3 existing + 5 new = 8 total)
        self.portfolio = {
            # Original holdings
            "AAPL": {"shares": 10, "avg_price": 150.25},
            "MSFT": {"shares": 5, "avg_price": 300.50},
            "TSLA": {"shares": 3, "avg_price": 220.75},
            # New portfolio additions (5 stocks)
            "V": {"shares": 1.0, "avg_price": 250.00},     # Visa
            "NVDA": {"shares": 2, "avg_price": 400.00},    # NVIDIA
            "JPM": {"shares": 4, "avg_price": 180.00},     # JPMorgan
            "HD": {"shares": 2, "avg_price": 350.00},      # Home Depot
            "BAC": {"shares": 10, "avg_price": 45.00}      # Bank of America
        }
        
        # Price simulation
        self.simulate_prices = True
        self.simulation_thread = None
        
        # Create main frames
        self.create_main_frames()
        
        # Create widgets
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        self.create_portfolio_section()
        self.create_news_section()
        self.create_status_bar()
        
        # Start price simulation
        self.start_price_simulation()
        
        # Load initial data
        self.fetch_stock_data(self.current_symbol)
        self.update_watchlist()
        self.update_portfolio()
        self.fetch_market_news()

        style = ttk.Style()
        style.configure("Header.TFrame", background="#1e2a3a")
        style.configure("Header.TLabel", background="#1e2a3a", foreground="white")
        style.configure("Accent.TButton", foreground="white", background="#4CAF50")
        style.configure("Secondary.TButton", foreground="white", background="#607D8B")

        style.configure("Danger.TButton", foreground="white", background="#e74c3c",  font=('Helvetica', 10, 'bold'),padding=6)
        style.map("Danger.TButton",background=[('active', '#c0392b'), ('disabled', '#cccccc')])

        style.configure("SmallHeader.TLabel", font=('Helvetica', 9, 'bold'))
        style.configure("NormalText.TLabel",font=('Helvetica', 10))
        style.configure("LargeText.TLabel", font=('Helvetica', 16, 'bold'))

    def configure_styles(self):
        # Configure colors
        bg_color = "#0a0e17"
        card_bg = "#131a29"
        text_color = "#e0e6f0"
        accent_color = "#1e88e5"
        positive_color = "#4caf50"
        negative_color = "#f44336"
        border_color = "#1c2a44"
        button_bg = "#1a3d6c"
        
        # General styles
        self.style.configure('.', background=bg_color, foreground=text_color, font=self.base_font)
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=text_color)
        self.style.configure('TButton', background=button_bg, foreground=text_color, borderwidth=1, focusthickness=3, focuscolor='none')
        self.style.map('TButton', background=[('active', '#255a9e')])
        self.style.configure('TNotebook', background=bg_color, borderwidth=0)
        self.style.configure('TNotebook.Tab', background=card_bg, foreground=text_color,padding=[10, 5], font=self.header_font)
        self.style.map('TNotebook.Tab', background=[('selected', '#1a3d6c')])
        self.style.configure('TLabelframe', background=card_bg, foreground=accent_color,bordercolor=border_color, borderwidth=2, relief='solid')
        self.style.configure('TLabelframe.Label', background=card_bg, foreground=accent_color)
        self.style.configure('TEntry', fieldbackground=card_bg, foreground=text_color, bordercolor=border_color, lightcolor=border_color)
        self.style.configure('TCombobox', fieldbackground=card_bg, foreground=text_color, background=card_bg, bordercolor=border_color)
        self.style.configure('Treeview', background=card_bg, fieldbackground=card_bg, foreground=text_color, borderwidth=0)
        self.style.configure('Treeview.Heading', background='#1a3d6c', foreground=text_color,font=self.header_font)
        self.style.map('Treeview', background=[('selected', '#1a3d6c')])
        self.style.configure('Vertical.TScrollbar', background=card_bg, bordercolor=border_color,arrowcolor=text_color)
        self.style.configure('Horizontal.TScrollbar', background=card_bg, bordercolor=border_color,arrowcolor=text_color)
        self.style.configure('Status.TLabel', background='#091020', foreground='#94a3b8', font=("Arial", 9))

    def create_main_frames(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.header_frame = ttk.Frame(main_container)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Content area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar_frame = ttk.LabelFrame(content_frame, text="Portfolio", width=300)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Main content
        self.main_content_frame = ttk.Frame(content_frame)
        self.main_content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_frame = ttk.Frame(main_container)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))

    def create_header(self):
        # Title
        title_label = ttk.Label(self.header_frame, text="StalkTrade Pro", font=self.title_font, foreground="#1e88e5")
        title_label.pack(side=tk.LEFT)
        
        # Search and actions
        action_frame = ttk.Frame(self.header_frame)
        action_frame.pack(side=tk.RIGHT)
        
        # Search box
        search_frame = ttk.Frame(action_frame)
        search_frame.pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT)
        search_entry.bind("<Return>", lambda e: self.search_stock())
        
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_stock)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        buy_btn = ttk.Button(action_frame, text="Buy", command=self.show_buy_dialog)
        buy_btn.pack(side=tk.LEFT, padx=5)
        
        sell_btn = ttk.Button(action_frame, text="Sell", command=self.show_sell_dialog)
        sell_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(action_frame, text="Refresh", command=self.refresh_data)
        refresh_btn.pack(side=tk.LEFT, padx=5)

    def create_sidebar(self):
        # Portfolio summary
        portfolio_summary_frame = ttk.Frame(self.sidebar_frame)
        portfolio_summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(portfolio_summary_frame, text="PORTFOLIO VALUE", font=self.header_font).pack(anchor="w")
        self.portfolio_value_var = tk.StringVar()
        self.portfolio_value_var.set("$12,450.75")
        ttk.Label(portfolio_summary_frame, textvariable=self.portfolio_value_var, font=("Arial", 16, "bold"), foreground="#4caf50").pack(anchor="w", pady=(5, 0))
        
        ttk.Label(portfolio_summary_frame, text="Daily Change", font=self.base_font).pack(anchor="w")
        self.daily_change_var = tk.StringVar()
        self.daily_change_var.set("+$245.50 (1.92%)")
        ttk.Label(portfolio_summary_frame, textvariable=self.daily_change_var, 
                 font=self.base_font, foreground="#4caf50").pack(anchor="w")
        
        # Portfolio table
        portfolio_table_frame = ttk.Frame(self.sidebar_frame)
        portfolio_table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("symbol", "shares", "price", "value", "change")
        self.portfolio_table = ttk.Treeview(
            portfolio_table_frame, 
            columns=columns, 
            show="headings",
            height=8,
            selectmode="browse"
        )
        
        # Configure columns
        self.portfolio_table.heading("symbol", text="Symbol")
        self.portfolio_table.heading("shares", text="Shares")
        self.portfolio_table.heading("price", text="Price")
        self.portfolio_table.heading("value", text="Value")
        self.portfolio_table.heading("change", text="Change")
        
        self.portfolio_table.column("symbol", width=60, anchor="center")
        self.portfolio_table.column("shares", width=60, anchor="center")
        self.portfolio_table.column("price", width=70, anchor="center")
        self.portfolio_table.column("value", width=80, anchor="center")
        self.portfolio_table.column("change", width=80, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(portfolio_table_frame, orient="vertical", 
                                command=self.portfolio_table.yview)
        self.portfolio_table.configure(yscrollcommand=scrollbar.set)
        
        self.portfolio_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Watchlist
        watchlist_frame = ttk.LabelFrame(self.sidebar_frame, text="Watchlist")
        watchlist_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.watchlist_table = ttk.Treeview(
            watchlist_frame, 
            columns=("symbol", "price", "change"), 
            show="headings",
            height=5
        )
        
        self.watchlist_table.heading("symbol", text="Symbol")
        self.watchlist_table.heading("price", text="Price")
        self.watchlist_table.heading("change", text="Change")
        
        self.watchlist_table.column("symbol", width=60, anchor="center")
        self.watchlist_table.column("price", width=80, anchor="center")
        self.watchlist_table.column("change", width=80, anchor="center")
        
        self.watchlist_table.pack(fill=tk.BOTH, padx=5, pady=5)
        
        # Bind selection events
        self.portfolio_table.bind("<<TreeviewSelect>>", self.on_portfolio_select)
        self.watchlist_table.bind("<<TreeviewSelect>>", self.on_watchlist_select)

    def create_main_content(self):
        # Create tabs
        self.tab_control = ttk.Notebook(self.main_content_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Overview tab
        self.overview_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.overview_tab, text="Overview")
        
        # Chart tab
        self.chart_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.chart_tab, text="Chart")
        
        # Financials tab
        self.financials_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.financials_tab, text="Financials")
        
        # Create content for each tab
        self.create_overview_tab()
        self.create_chart_tab()
        self.create_financials_tab()

    def create_overview_tab(self):
        # Stock header
        header_frame = ttk.Frame(self.overview_tab)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.stock_name_var = tk.StringVar()
        self.stock_name_var.set("Apple Inc. (AAPL)")
        ttk.Label(header_frame, textvariable=self.stock_name_var, font=self.title_font).pack(side=tk.LEFT)
        
        price_frame = ttk.Frame(header_frame)
        price_frame.pack(side=tk.RIGHT)
        
        self.stock_price_var = tk.StringVar()
        self.stock_price_var.set("$172.35")
        ttk.Label(price_frame, textvariable=self.stock_price_var,font=("Arial", 20, "bold"), foreground="#4caf50").pack(anchor="e")
        
        self.stock_change_var = tk.StringVar()
        self.stock_change_var.set("+2.35 (1.38%)")
        ttk.Label(price_frame, textvariable=self.stock_change_var,font=self.header_font, foreground="#4caf50").pack(anchor="e")
        
        # Key statistics
        stats_frame = ttk.LabelFrame(self.overview_tab, text="Key Statistics")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        stats = [
            ("Open", "open_var"),
            ("Previous Close", "prev_close_var"),
            ("Day Range", "day_range_var"),
            ("52 Week Range", "year_range_var"),
            ("Volume", "volume_var"),
            ("Avg. Volume", "avg_volume_var"),
            ("Market Cap", "market_cap_var"),
            ("P/E Ratio", "pe_ratio_var"),
            ("Dividend Yield", "dividend_var"),
            ("Beta", "beta_var"),
            ("EPS", "eps_var"),
            ("Shares Out", "shares_out_var")
        ]
        
        self.stats_vars = {}
        
        for i, (label, var_name) in enumerate(stats):
            row = i // 4
            col = i % 4
            
            if col == 0:
                frame = ttk.Frame(stats_grid)
                frame.pack(fill=tk.X, pady=5)
            
            stat_frame = ttk.Frame(frame)
            stat_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
            
            ttk.Label(stat_frame, text=label, width=15, anchor="w").pack(anchor="w")
            var = tk.StringVar()
            var.set("N/A")
            ttk.Label(stat_frame, textvariable=var, font=self.base_font).pack(anchor="w")
            
            self.stats_vars[var_name] = var
        
        # About section
        about_frame = ttk.LabelFrame(self.overview_tab, text="About")
        about_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.about_text = scrolledtext.ScrolledText(
            about_frame, 
            wrap=tk.WORD, 
            bg="#131a29", 
            fg="#e0e6f0",
            insertbackground="#e0e6f0",
            relief="flat",
            font=self.base_font,
            padx=10,
            pady=10
        )
        self.about_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.about_text.insert(tk.END, "Loading company information...")
        self.about_text.config(state=tk.DISABLED)

    def create_chart_tab(self):
        # Chart controls
        controls_frame = ttk.Frame(self.chart_tab)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(controls_frame, text="Time Frame:").pack(side=tk.LEFT)
        
        time_frames = ["1D", "1W", "1M", "3M", "6M", "YTD", "1Y", "5Y"]
        self.time_frame_var = tk.StringVar()
        self.time_frame_var.set("1M")
        
        for tf in time_frames:
            rb = ttk.Radiobutton(controls_frame, text=tf, variable=self.time_frame_var, value=tf, command=self.update_chart)
            rb.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(controls_frame, text="Chart Type:").pack(side=tk.LEFT, padx=(20, 5))
        
        chart_types = ["Line", "Candlestick"]
        self.chart_type_var = tk.StringVar()
        self.chart_type_var.set("Candlestick")
        
        for ct in chart_types:
            rb = ttk.Radiobutton(controls_frame, text=ct, variable=self.chart_type_var,value=ct, command=self.update_chart)
            rb.pack(side=tk.LEFT, padx=5)
        
        # Chart canvas
        chart_container = ttk.Frame(self.chart_tab)
        chart_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.fig = Figure(figsize=(8, 4), dpi=100, facecolor="#131a29")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#131a29")
        
        # Set colors for axes
        self.ax.spines['bottom'].set_color('#2a3a5e')
        self.ax.spines['top'].set_color('#2a3a5e') 
        self.ax.spines['right'].set_color('#2a3a5e')
        self.ax.spines['left'].set_color('#2a3a5e')
        self.ax.tick_params(axis='x', colors='#94a3b8')
        self.ax.tick_params(axis='y', colors='#94a3b8')
        self.ax.yaxis.label.set_color('#94a3b8')
        self.ax.xaxis.label.set_color('#94a3b8')
        self.ax.title.set_color('#e0e6f0')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_container)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_financials_tab(self):
        # Placeholder for financials
        placeholder_frame = ttk.Frame(self.financials_tab)
        placeholder_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(placeholder_frame, text="Financial Statements", font=self.header_font).pack(pady=20)
        
        ttk.Label(placeholder_frame, text="Income Statement, Balance Sheet, and Cash Flow data will be displayed here.").pack()
        
        # Add tabs for financial statements
        fin_tabs = ttk.Notebook(placeholder_frame)
        fin_tabs.pack(fill=tk.BOTH, expand=True, pady=10)
        
        income_frame = ttk.Frame(fin_tabs)
        balance_frame = ttk.Frame(fin_tabs)
        cashflow_frame = ttk.Frame(fin_tabs)
        
        fin_tabs.add(income_frame, text="Income Statement")
        fin_tabs.add(balance_frame, text="Balance Sheet")
        fin_tabs.add(cashflow_frame, text="Cash Flow")
        
        # Placeholder content
        for frame in [income_frame, balance_frame, cashflow_frame]:
            placeholder = ttk.Label(frame, text="Financial data will be displayed here")
            placeholder.pack(pady=50)

    def create_portfolio_section(self):
        # This is already created in the sidebar
        pass

    def create_news_section(self):
        # News section
        news_frame = ttk.LabelFrame(self.main_content_frame, text="Market News")
        news_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        self.news_text = scrolledtext.ScrolledText(
            news_frame, 
            wrap=tk.WORD, 
            bg="#131a29", 
            fg="#e0e6f0",
            insertbackground="#e0e6f0",
            relief="flat",
            font=self.base_font,
            padx=10,
            pady=10,
            height=8
        )
        self.news_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.news_text.insert(tk.END, "Loading market news...")
        self.news_text.config(state=tk.DISABLED)

    def create_status_bar(self):
        # Status bar
        status_bar = ttk.Label(self.status_frame, style="Status.TLabel", 
                              anchor="w", padding=(10, 5))
        status_bar.pack(fill=tk.X)
        
        # Status elements
        market_status_frame = ttk.Frame(status_bar)
        market_status_frame.pack(side=tk.LEFT)
        
        ttk.Label(market_status_frame, text="US Market: OPEN", style="Status.TLabel", foreground="#4caf50").pack(side=tk.LEFT, padx=10)
        
        self.last_update_var = tk.StringVar()
        self.last_update_var.set("Last Update: " + datetime.now().strftime("%H:%M:%S"))
        ttk.Label(market_status_frame, textvariable=self.last_update_var,  style="Status.TLabel").pack(side=tk.LEFT, padx=10)
        
        # Connection status
        connection_frame = ttk.Frame(status_bar)
        connection_frame.pack(side=tk.RIGHT)
        
        ttk.Label(connection_frame, text="Real-time Data: ACTIVE", 
                 style="Status.TLabel", foreground="#4caf50").pack(side=tk.RIGHT, padx=10)

    def fetch_stock_data(self, symbol):
        try:
            self.current_symbol = symbol
            stock = yf.Ticker(symbol)
            
            # Get basic info
            info = stock.info
            name = info.get('longName', symbol)
            self.stock_name_var.set(f"{name} ({symbol})")
            
            # Get price data
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            prev_close = info.get('previousClose', 0)
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close else 0
            
            # Format price and change
            price_str = f"${current_price:,.2f}" if current_price else "N/A"
            change_str = f"{change:+.2f} ({change_percent:+.2f}%)" if prev_close else "N/A"
            
            # Set color based on change
            change_color = "#4caf50" if change >= 0 else "#f44336"
            
            self.stock_price_var.set(price_str)
            self.stock_change_var.set(change_str)
            self.stock_price_label = ttk.Label(self.overview_tab, textvariable=self.stock_price_var, font=("Arial", 20, "bold"), foreground=change_color)
            self.stock_change_label = ttk.Label(self.overview_tab, textvariable=self.stock_change_var, font=self.header_font, foreground=change_color)
            
            # Update statistics
            self.stats_vars['open_var'].set(f"${info.get('open', 'N/A')}")
            self.stats_vars['prev_close_var'].set(f"${prev_close:,.2f}" if prev_close else "N/A")
            
            day_high = info.get('dayHigh', 'N/A')
            day_low = info.get('dayLow', 'N/A')
            self.stats_vars['day_range_var'].set(f"${day_low:,.2f} - ${day_high:,.2f}"  if isinstance(day_low, float) else "N/A")
            
            year_high = info.get('fiftyTwoWeekHigh', 'N/A')
            year_low = info.get('fiftyTwoWeekLow', 'N/A')
            self.stats_vars['year_range_var'].set(f"${year_low:,.2f} - ${year_high:,.2f}" if isinstance(year_low, float) else "N/A")
            
            volume = info.get('volume', 0)
            avg_volume = info.get('averageVolume', 0)
            self.stats_vars['volume_var'].set(f"{volume:,}" if volume else "N/A")
            self.stats_vars['avg_volume_var'].set(f"{avg_volume:,}" if avg_volume else "N/A")
            
            market_cap = info.get('marketCap', 0)
            if market_cap >= 1e12:
                market_cap_str = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                market_cap_str = f"${market_cap/1e9:.2f}B"
            else:
                market_cap_str = f"${market_cap:,.0f}"
            self.stats_vars['market_cap_var'].set(market_cap_str)
            
            self.stats_vars['pe_ratio_var'].set(str(info.get('trailingPE', 'N/A')))
            
            dividend = info.get('dividendYield', 0)
            self.stats_vars['dividend_var'].set(f"{dividend*100:.2f}%" if dividend else "N/A")
            
            self.stats_vars['beta_var'].set(str(info.get('beta', 'N/A')))
            self.stats_vars['eps_var'].set(str(info.get('trailingEps', 'N/A')))
            
            shares_out = info.get('sharesOutstanding', 0)
            self.stats_vars['shares_out_var'].set(f"{shares_out/1e6:.2f}M" if shares_out else "N/A")
            
            # Update about section
            about_text = info.get('longBusinessSummary', 'No description available.')
            self.about_text.config(state=tk.NORMAL)
            self.about_text.delete(1.0, tk.END)
            self.about_text.insert(tk.END, about_text)
            self.about_text.config(state=tk.DISABLED)
            
            # Update chart
            self.update_chart()
            
            # Update status
            self.last_update_var.set("Last Update: " + datetime.now().strftime("%H:%M:%S"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data for {symbol}: {str(e)}")

    def update_chart(self):
        try:
            time_frame = self.time_frame_var.get()
            chart_type = self.chart_type_var.get()
            
            # Calculate start date based on time frame
            end_date = datetime.now()
            
            if time_frame == "1D":
                start_date = end_date - timedelta(days=1)
                interval = "15m"
            elif time_frame == "1W":
                start_date = end_date - timedelta(weeks=1)
                interval = "60m"
            elif time_frame == "1M":
                start_date = end_date - timedelta(days=30)
                interval = "1d"
            elif time_frame == "3M":
                start_date = end_date - timedelta(days=90)
                interval = "1d"
            elif time_frame == "6M":
                start_date = end_date - timedelta(days=180)
                interval = "1d"
            elif time_frame == "YTD":
                start_date = datetime(end_date.year, 1, 1)
                interval = "1d"
            elif time_frame == "1Y":
                start_date = end_date - timedelta(days=365)
                interval = "1wk"
            else:  # 5Y
                start_date = end_date - timedelta(days=5*365)
                interval = "1mo"
            
            # Get historical data
            stock = yf.Ticker(self.current_symbol)
            hist = stock.history(start=start_date, end=end_date, interval=interval)
            
            if hist.empty:
                return
            
            # Clear previous chart
            self.ax.clear()
            
            # Plot based on chart type
            if chart_type == "Candlestick" and time_frame != "1D":
                # Plot candlestick chart
                for i, (index, row) in enumerate(hist.iterrows()):
                    color = '#4caf50' if row['Close'] >= row['Open'] else '#f44336'
                    
                    # Plot candle body
                    self.ax.plot([i, i], [row['Low'], row['High']], color=color, linewidth=1)
                    self.ax.plot([i-0.2, i+0.2], [row['Open'], row['Open']], color=color, linewidth=1)
                    self.ax.plot([i-0.2, i+0.2], [row['Close'], row['Close']], color=color, linewidth=1)
                    self.ax.fill_between([i-0.2, i+0.2], row['Open'], row['Close'], 
                                       color=color, alpha=0.5)
            else:
                # Plot line chart
                self.ax.plot(hist.index, hist['Close'], color='#1e88e5', linewidth=2)
            
            # Format x-axis dates
            if time_frame == "1D":
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            elif time_frame in ["1W", "1M"]:
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            else:
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            
            # Set title and labels
            self.ax.set_title(f"{self.current_symbol} Price Chart", fontsize=12)
            self.ax.set_ylabel("Price (USD)", fontsize=10)
            
            # Set grid
            self.ax.grid(True, linestyle='--', alpha=0.3, color='#2a3a5e')
            
            # Redraw canvas
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating chart: {str(e)}")

    def update_watchlist(self):
        # Clear existing data
        for item in self.watchlist_table.get_children():
            self.watchlist_table.delete(item)
        
        # Add stocks to watchlist
        for symbol in self.watchlist:
            # Simulate price changes
            price = random.uniform(100, 500)
            change = random.uniform(-5, 5)
            change_percent = (change / price) * 100
            
            # Format values
            price_str = f"${price:,.2f}"
            change_str = f"{change:+.2f} ({change_percent:+.2f}%)"
            
            # Add to table
            self.watchlist_table.insert("", "end", values=(symbol, price_str, change_str), tags=('positive' if change >= 0 else 'negative'))
        
        # Configure tag colors
        self.watchlist_table.tag_configure('positive', foreground='#4caf50')
        self.watchlist_table.tag_configure('negative', foreground='#f44336')

    def update_portfolio(self):
        # Clear existing data
        for item in self.portfolio_table.get_children():
            self.portfolio_table.delete(item)
        
        total_value = 0
        total_change = 0
        
        # Add portfolio items
        for symbol, data in self.portfolio.items():
            # Simulate current price
            current_price = random.uniform(data['avg_price'] * 0.8, data['avg_price'] * 1.2)
            value = data['shares'] * current_price
            change = (current_price - data['avg_price']) * data['shares']
            change_percent = (current_price - data['avg_price']) / data['avg_price'] * 100
            
            # Format values
            price_str = f"${current_price:,.2f}"
            value_str = f"${value:,.2f}"
            change_str = f"{change:+.2f} ({change_percent:+.2f}%)"
            
            # Add to table
            self.portfolio_table.insert("", "end", values=(
                symbol, 
                data['shares'], 
                price_str, 
                value_str, 
                change_str
            ), tags=('positive' if change >= 0 else 'negative'))
            
            total_value += value
            total_change += change
        
        # Configure tag colors
        self.portfolio_table.tag_configure('positive', foreground='#4caf50')
        self.portfolio_table.tag_configure('negative', foreground='#f44336')
        
        # Update portfolio summary
        self.portfolio_value_var.set(f"${total_value:,.2f}")
        
        if total_change >= 0:
            self.daily_change_var.set(f"+${total_change:,.2f} ({(total_change/total_value)*100:.2f}%)")
        else:
            self.daily_change_var.set(f"-${abs(total_change):,.2f} ({(total_change/total_value)*100:.2f}%)")

    def fetch_market_news(self):
        try:
            # In a real application, you would fetch real financial news
            # Here we'll simulate with placeholder news
            
            news_items = [
                "Market rallies as Fed signals potential rate cuts in 2024",
                "Tech stocks lead gains as AI investments surge",
                "Apple announces record quarterly profits, shares up 5%",
                "New regulations proposed for cryptocurrency markets",
                "Global markets react positively to trade agreement",
                "Energy sector faces headwinds amid falling oil prices",
                "Tesla unveils new model with extended battery range",
                "Microsoft acquires AI startup for $1.2 billion",
                "Retail investors flock to blue-chip stocks",
                "Economic indicators show strong consumer spending"
            ]
            
            # Format news text
            news_text = ""
            for i, news in enumerate(news_items, 1):
                news_text += f"• {news}\n\n"
            
            # Update news text widget
            self.news_text.config(state=tk.NORMAL)
            self.news_text.delete(1.0, tk.END)
            self.news_text.insert(tk.END, news_text)
            self.news_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error fetching news: {str(e)}")

    def on_portfolio_select(self, event):
        selected = self.portfolio_table.selection()
        if selected:
            item = self.portfolio_table.item(selected)
            symbol = item['values'][0]
            self.current_symbol = symbol
            self.fetch_stock_data(symbol)

    def on_watchlist_select(self, event):
        selected = self.watchlist_table.selection()
        if selected:
            item = self.watchlist_table.item(selected)
            symbol = item['values'][0]
            self.current_symbol = symbol
            self.fetch_stock_data(symbol)

    def search_stock(self):
        symbol = self.search_var.get().strip().upper()
        if symbol:
            self.current_symbol = symbol
            self.fetch_stock_data(symbol)
            # Add to watchlist if not already there
            if symbol not in self.watchlist:
                self.watchlist.append(symbol)
                self.update_watchlist()

    def refresh_data(self):
        self.fetch_stock_data(self.current_symbol)
        self.update_watchlist()
        self.update_portfolio()
        self.fetch_market_news()

    def start_price_simulation(self):
        if self.simulate_prices:
            self.simulation_thread = threading.Thread(target=self.simulate_price_changes, daemon=True)
            self.simulation_thread.start()

    def simulate_price_changes(self):
        while self.simulate_prices:
            # Update watchlist prices every 5 seconds
            self.update_watchlist()
            self.update_portfolio()
            time.sleep(5)

    def show_buy_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Buy Stock")
        dialog.geometry("350x350")  # Increased size for better layout
        dialog.configure(bg="#131a29")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Header with icon
        header_frame = ttk.Frame(dialog, style="Header.TFrame")
        header_frame.pack(fill=tk.X, pady=(10, 15))
        ttk.Label(header_frame, text="BUY STOCK", font=('Helvetica', 12, 'bold'), 
                  foreground="#4CAF50", style="Header.TLabel").pack()
        
        # Symbol input with autocomplete
        symbol_frame = ttk.Frame(dialog)
        symbol_frame.pack(fill=tk.X, padx=20, pady=8)
        ttk.Label(symbol_frame, text="Symbol:").pack(side=tk.LEFT)
        symbol_var = tk.StringVar(value=self.current_symbol)
        
        # Combobox with popular symbols
        symbol_cb = ttk.Combobox(symbol_frame, textvariable=symbol_var, width=15)
        symbol_cb['values'] = self.get_popular_symbols()  # Implement this method
        symbol_cb.pack(side=tk.RIGHT)
        
        # Shares input with validation
        shares_frame = ttk.Frame(dialog)
        shares_frame.pack(fill=tk.X, padx=20, pady=8)
        ttk.Label(shares_frame, text="Shares:").pack(side=tk.LEFT)
        shares_var = tk.StringVar(value="1")
        
        # Share validation
        def validate_shares(P):
            if P == "": return True
            try:
                return float(P) > 0
            except:
                return False
        
        shares_entry = ttk.Entry(
            shares_frame, 
            textvariable=shares_var, 
            width=15,
            validate="key",
            validatecommand=(dialog.register(validate_shares), '%P')
        )
        shares_entry.pack(side=tk.RIGHT)
        
        # Price with real-time fetching
        price_frame = ttk.Frame(dialog)
        price_frame.pack(fill=tk.X, padx=20, pady=8)
        ttk.Label(price_frame, text="Price:").pack(side=tk.LEFT)
        price_var = tk.StringVar(value="Fetching...")
        
        def fetch_price():
            try:
                stock = yf.Ticker(symbol_var.get())
                price = stock.history(period="1d")["Close"].iloc[-1]
                price_var.set(f"${price:.2f}")
                calculate_total()
            except Exception as e:
                price_var.set("Error")
        
        ttk.Label(price_frame, textvariable=price_var).pack(side=tk.RIGHT)
        
        # Total calculation
        total_frame = ttk.Frame(dialog)
        total_frame.pack(fill=tk.X, padx=20, pady=8)
        ttk.Label(total_frame, text="Total:").pack(side=tk.LEFT)
        total_var = tk.StringVar(value="$0.00")
        ttk.Label(total_frame, textvariable=total_var, font=('Helvetica', 10, 'bold')).pack(side=tk.RIGHT)
        
        def calculate_total():
            try:
                shares = float(shares_var.get())
                price = float(price_var.get().replace('$', ''))
                total = shares * price
                total_var.set(f"${total:,.2f}")
            except:
                total_var.set("Error")
        
        # Order type selection
        order_frame = ttk.Frame(dialog)
        order_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(order_frame, text="Order Type:").pack(side=tk.LEFT)
        
        order_type = tk.StringVar(value="MARKET")
        ttk.Radiobutton(order_frame, text="Market", variable=order_type, value="MARKET").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(order_frame, text="Limit", variable=order_type, value="LIMIT").pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=dialog.destroy,
            style="Secondary.TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Buy", 
            style="Accent.TButton",
            command=lambda: self.execute_trade(
                symbol_var.get(), 
                float(shares_var.get()), 
                float(price_var.get().replace('$', '')), 
                order_type.get(),
                dialog
            )
        ).pack(side=tk.RIGHT)
        
        # Set up trace callbacks
        symbol_var.trace_add("write", lambda *args: fetch_price())
        shares_var.trace_add("write", lambda *args: calculate_total())
        
        # Initial fetch
        fetch_price()
        calculate_total()
        
    def show_sell_dialog(self):
        # Check if stock is in portfolio
        if self.current_symbol not in self.portfolio:
            messagebox.showinfo("Error", "You don't own this stock")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Sell {self.current_symbol}")
        dialog.geometry("350x400")
        dialog.configure(bg="#131a29")
        
        # Variables
        shares_var = tk.StringVar(value="1")
        price_var = tk.StringVar(value="Fetching...")
        total_var = tk.StringVar(value="$0.00")
        order_type = tk.StringVar(value="MARKET")
        available_shares = self.portfolio[self.current_symbol]['shares']

        # Header
        header_frame = ttk.Frame(dialog, style="Header.TFrame")
        header_frame.pack(fill=tk.X, pady=(10, 15))
        ttk.Label(header_frame, 
                 text=f"SELL {self.current_symbol}", 
                 style="Header.TLabel").pack()

        # Position info
        position_frame = ttk.Frame(dialog, style="Card.TFrame")
        position_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(position_frame, text="AVAILABLE SHARES").grid(row=0, column=0, sticky="w")
        ttk.Label(position_frame, text=f"{available_shares} shares").grid(row=1, column=0, sticky="w")

        # Order type
        type_frame = ttk.Frame(dialog)
        type_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(type_frame, text="Order Type:").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Market", variable=order_type, value="MARKET").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Limit", variable=order_type, value="LIMIT").pack(side=tk.LEFT, padx=5)

        # Input fields
        input_frame = ttk.Frame(dialog)
        input_frame.pack(fill=tk.X, padx=20, pady=10)

        # Shares
        ttk.Label(input_frame, text="Shares:").grid(row=0, column=0, sticky="w", pady=2)
        shares_entry = ttk.Entry(input_frame, textvariable=shares_var, width=15)
        shares_entry.grid(row=1, column=0, sticky="w", pady=5)

        # Price
        ttk.Label(input_frame, text="Price:").grid(row=0, column=1, sticky="w", padx=(20,0), pady=2)
        price_entry = ttk.Entry(input_frame, textvariable=price_var, width=15, state='readonly')
        price_entry.grid(row=1, column=1, sticky="w", pady=5)

        # Total
        total_frame = ttk.Frame(dialog, style="Card.TFrame")
        total_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(total_frame, text="ESTIMATED PROCEEDS").grid(row=0, column=0, sticky="w")
        ttk.Label(total_frame, textvariable=total_var, font=('Helvetica', 14, 'bold')).grid(row=1, column=0, sticky="w")

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=(10, 0))

        ttk.Button(
            button_frame,
            text="Cancel",
            style="Secondary.TButton",
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)

        sell_btn = ttk.Button(
            button_frame,
            text="Sell Order",
            style="Danger.TButton",
            command=lambda: self._execute_sell(
                dialog,
                self.current_symbol,
                shares_var.get(),
                price_var.get(),
                order_type.get()
            )
        )
        sell_btn.pack(side=tk.RIGHT)

        # Price fetching and validation
        def fetch_price():
            try:
                stock = yf.Ticker(self.current_symbol)
                price = stock.history(period="1d")["Close"].iloc[-1]
                price_var.set(f"${price:.2f}")
                sell_btn['state'] = 'normal'  # Enable button after price loads
            except Exception as e:
                messagebox.showerror("Error", f"Couldn't fetch price: {str(e)}")
                dialog.destroy()

        def toggle_price_entry():
            if order_type.get() == "LIMIT":
                price_entry.config(state='normal')
            else:
                price_entry.config(state='readonly')
                fetch_price()  # Refresh market price

        # Initialize
        fetch_price()
        order_type.trace_add('write', lambda *_: toggle_price_entry())
        shares_var.trace_add('write', lambda *_: self._calculate_total(shares_var, price_var, total_var))

    def execute_trade(self, symbol, shares, dialog):
        if shares > 0:  # Buy order
            if symbol in self.portfolio:
                # Update existing position
                self.portfolio[symbol]['shares'] += shares
                # For simplicity, keep average price the same (in real app you'd calculate new avg)
            else:
                # Create new position
                # Simulate price - in real app you'd get current market price
                price = random.uniform(100, 500)
                self.portfolio[symbol] = {"shares": shares, "avg_price": price}
            
            messagebox.showinfo("Trade Executed", f"Bought {shares} shares of {symbol}")
        else:  # Sell order
            shares = abs(shares)
            if symbol in self.portfolio:
                if self.portfolio[symbol]['shares'] >= shares:
                    self.portfolio[symbol]['shares'] -= shares
                    if self.portfolio[symbol]['shares'] == 0:
                        del self.portfolio[symbol]
                    messagebox.showinfo("Trade Executed", f"Sold {shares} shares of {symbol}")
                else:
                    messagebox.showerror("Error", "Not enough shares to sell")
            else:
                messagebox.showerror("Error", "You don't own this stock")
        
        dialog.destroy()
        self.update_portfolio()
        if symbol == self.current_symbol:
            self.fetch_stock_data(symbol)

    def on_closing(self):
        self.simulate_prices = False
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=1.0)
        self.root.destroy()
    def get_popular_symbols(self):
        """Return list of popular stock symbols"""
        return ["AAPL", "TSLA", "MSFT", "AMZN", "GOOG", "META", "NVDA", "AMD","V"]

    def execute_trade(self, symbol, shares, price, order_type, dialog):
        """Execute the trade with validation"""
        try:
            # Validate inputs
            if shares <= 0:
                messagebox.showerror("Error", "Shares must be positive")
                return
                
            if price <= 0:
                messagebox.showerror("Error", "Price must be positive")
                return
                
            # Confirm with user
            if not messagebox.askyesno("Confirm", f"Buy {shares} shares of {symbol} at ${price:.2f}?"):
                return
                
            # Execute trade (implement your actual trading logic here)
            print(f"Executing {order_type} order: {shares} shares of {symbol} at ${price:.2f}")
            
            # Update portfolio
            if symbol in self.portfolio:
                self.portfolio[symbol]['shares'] += shares
            else:
                self.portfolio[symbol] = {'shares': shares, 'avg_price': price}
                
            # Close dialog and refresh
            dialog.destroy()
            self.update_portfolio_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Trade failed: {str(e)}")

    def _calculate_total(self, shares_var, price_var, total_var):
        """Calculate order total"""
        try:
            shares = float(shares_var.get())
            price = float(price_var.get().replace('$', ''))
            total_var.set(f"${shares * price:.2f}")
        except:
            total_var.set("$0.00")

    def _execute_sell(self, dialog, symbol, shares_str, price_str, order_type):
        """Validate and execute sell order"""
        try:
            # Convert inputs
            shares = float(shares_str)
            price = float(price_str.replace('$', ''))
            
            # Validate
            if shares <= 0:
                messagebox.showerror("Error", "Shares must be positive")
                return
                
            if price <= 0:
                messagebox.showerror("Error", "Invalid price")
                return
                
            available = self.portfolio[symbol]['shares']
            if shares > available:
                messagebox.showerror("Error", f"Max {available} shares available")
                return
                
            # Confirm
            if not messagebox.askyesno("Confirm", f"Sell {shares} shares at ${price:.2f}?"):
                return
                
            # Execute (replace with your actual sell logic)
            print(f"Selling {shares} shares of {symbol} at ${price} ({order_type})")
            
            # Update portfolio
            self.portfolio[symbol]['shares'] -= shares
            if self.portfolio[symbol]['shares'] <= 0:
                del self.portfolio[symbol]
                
            messagebox.showinfo("Success", "Order executed!")
            dialog.destroy()
            self.update_portfolio_display()  # Refresh your UI
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to sell: {str(e)}")
if __name__ == "__main__":
    root = tk.Tk()
    
    def on_login_success(user_data):
        # This callback runs after successful login
        platform = AdvancedTradingPlatform(root)
        # Pass the user data to your platform if needed
        platform.user_data = user_data
        root.protocol("WM_DELETE_WINDOW", platform.on_closing)
    
    # Create and show login system
    login_system = LoginSystem(root, on_login_success)
    login_system.show_login()
    
    root.mainloop()
