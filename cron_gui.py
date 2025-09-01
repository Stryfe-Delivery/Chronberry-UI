import tkinter as tk
from tkinter import ttk, messagebox
from crontab import CronTab

class CronGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cron Job Manager for Raspbian")
        self.user_cron = CronTab(user=True)
        self.system_cron = None
        self.setup_gui()
        
    def setup_gui(self):
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(self.root)
        notebook.pack(padx=10, pady=10, fill='both', expand=True)
        
        # User tab
        user_frame = ttk.Frame(notebook, padding=10)
        notebook.add(user_frame, text='User Jobs')
        self.setup_job_table(user_frame)
        
        # System tab
        system_frame = ttk.Frame(notebook, padding=10)
        notebook.add(system_frame, text='System Jobs')
        self.setup_job_table(system_frame)
        
        # Add job button
        add_button = ttk.Button(self.root, text="Add New Job", command=self.add_job)
        add_button.pack(pady=5)

    def add_job(self):
      add_window = tk.Toplevel(self.root)
      add_window.title("Add New Cron Job")
      
      # Schedule selection
      ttk.Label(add_window, text="Minute:").grid(row=0, column=0, padx=5, pady=5)
      minute_entry = ttk.Entry(add_window, width=10)
      minute_entry.grid(row=0, column=1, padx=5, pady=5)
      minute_entry.insert(0, "*")
      
      # Repeat for other time fields...
      
      # Command entry
      ttk.Label(add_window, text="Command:").grid(row=5, column=0, padx=5, pady=5)
      command_entry = ttk.Entry(add_window, width=40)
      command_entry.grid(row=5, column=1, columnspan=2, padx=5, pady=5)
      
      # Environment variables for GUI applications
      env_var = tk.BooleanVar()
      ttk.Checkbutton(add_window, text="Add DISPLAY=:0 for GUI apps", 
                     variable=env_var).grid(row=6, column=0, columnspan=2, pady=5)
      
      # Add button
      ttk.Button(add_window, text="Add Job", 
                command=lambda: self.save_new_job(minute_entry.get(), 
                                                 command_entry.get(), 
                                                 env_var.get())).grid(row=7, column=1, pady=10)
