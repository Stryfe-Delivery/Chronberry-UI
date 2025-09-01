import tkinter as tk
from tkinter import ttk, messagebox
from crontab import CronTab
import os

class CronGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cron Job Manager for Raspbian")
        self.user_cron = CronTab(user=True)
        try:
            self.system_cron = CronTab(tabfile='/etc/crontab')
        except:
            self.system_cron = None
            messagebox.showerror("Error", "Cannot access system crontab. Run with sudo for system jobs.")
        
        self.setup_gui()
        self.load_jobs()
        
    def setup_gui(self):
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(self.root)
        notebook.pack(padx=10, pady=10, fill='both', expand=True)
        
        # User tab
        user_frame = ttk.Frame(notebook, padding=10)
        notebook.add(user_frame, text='User Jobs')
        self.user_tree = self.setup_job_table(user_frame)
        
        # System tab
        system_frame = ttk.Frame(notebook, padding=10)
        notebook.add(system_frame, text='System Jobs')
        self.system_tree = self.setup_job_table(system_frame)
        
        # Control buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="Add New Job", command=self.add_job).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.load_jobs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_job).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Toggle Enabled", command=self.toggle_job).pack(side=tk.LEFT, padx=5)

    def setup_job_table(self, parent):
        columns = ('schedule', 'command', 'enabled')
        tree = ttk.Treeview(parent, columns=columns, show='headings')
        
        # Define headings
        tree.heading('schedule', text='Schedule')
        tree.heading('command', text='Command')
        tree.heading('enabled', text='Enabled')
        
        # Define column widths
        tree.column('schedule', width=150)
        tree.column('command', width=400)
        tree.column('enabled', width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        return tree

    def load_jobs(self):
        # Clear existing items
        for tree in [self.user_tree, self.system_tree]:
            for item in tree.get_children():
                tree.delete(item)
        
        # Load user jobs
        for job in self.user_cron:
            self.user_tree.insert('', 'end', values=(
                job.schedule_description(), 
                str(job), 
                job.is_enabled()
            ))
        
        # Load system jobs if available
        if self.system_cron:
            for job in self.system_cron:
                self.system_tree.insert('', 'end', values=(
                    job.schedule_description(), 
                    str(job), 
                    job.is_enabled()
                ))

    def add_job(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Cron Job")
        add_window.geometry("500x300")
        add_window.resizable(False, False)
        
        # Schedule selection
        ttk.Label(add_window, text="Minute (0-59):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        minute_entry = ttk.Entry(add_window, width=10)
        minute_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        minute_entry.insert(0, "*")
        
        ttk.Label(add_window, text="Hour (0-23):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        hour_entry = ttk.Entry(add_window, width=10)
        hour_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        hour_entry.insert(0, "*")
        
        ttk.Label(add_window, text="Day of Month (1-31):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        dom_entry = ttk.Entry(add_window, width=10)
        dom_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        dom_entry.insert(0, "*")
        
        ttk.Label(add_window, text="Month (1-12):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        month_entry = ttk.Entry(add_window, width=10)
        month_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        month_entry.insert(0, "*")
        
        ttk.Label(add_window, text="Day of Week (0-6, 0=Sunday):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        dow_entry = ttk.Entry(add_window, width=10)
        dow_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        dow_entry.insert(0, "*")
        
        # Command entry
        ttk.Label(add_window, text="Command:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        command_entry = ttk.Entry(add_window, width=50)
        command_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Job type selection
        ttk.Label(add_window, text="Job Type:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        job_type = tk.StringVar(value="user")
        ttk.Radiobutton(add_window, text="User Job", variable=job_type, value="user").grid(row=6, column=1, sticky=tk.W)
        ttk.Radiobutton(add_window, text="System Job", variable=job_type, value="system").grid(row=7, column=1, sticky=tk.W)
        
        # Environment variables for GUI applications
        env_var = tk.BooleanVar()
        ttk.Checkbutton(add_window, text="Add DISPLAY=:0 for GUI apps", 
                       variable=env_var).grid(row=8, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        # Add button
        ttk.Button(add_window, text="Add Job", 
                  command=lambda: self.save_new_job(
                      minute_entry.get(),
                      hour_entry.get(),
                      dom_entry.get(),
                      month_entry.get(),
                      dow_entry.get(),
                      command_entry.get(),
                      env_var.get(),
                      job_type.get()
                  )).grid(row=9, column=1, pady=10, sticky=tk.E)

    def save_new_job(self, minute, hour, dom, month, dow, command, add_display, job_type):
        if not command:
            messagebox.showerror("Error", "Command cannot be empty!")
            return
            
        try:
            if job_type == "user":
                cron = self.user_cron
            else:
                if not self.system_cron:
                    messagebox.showerror("Error", "System crontab not accessible. Run with sudo.")
                    return
                cron = self.system_cron
                
            job = cron.new(command=command)
            job.setall(minute, hour, dom, month, dow)
            
            if add_display:
                job.env['DISPLAY'] = ':0'
                
            cron.write()
            self.load_jobs()
            messagebox.showinfo("Success", "Cron job added successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add cron job: {str(e)}")

    def delete_job(self):
        # Get currently selected tab
        notebook = self.root.winfo_children()[0]
        current_tab = notebook.index(notebook.select())
        
        if current_tab == 0:  # User tab
            tree = self.user_tree
            cron = self.user_cron
        else:  # System tab
            tree = self.system_tree
            cron = self.system_cron
            
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a job to delete.")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete the selected job?"):
            try:
                for item in selected:
                    values = tree.item(item, 'values')
                    # Find and remove the job
                    for job in cron:
                        if str(job) == values[1]:  # Compare command string
                            cron.remove(job)
                            break
                cron.write()
                self.load_jobs()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete job: {str(e)}")

    def toggle_job(self):
        # Get currently selected tab
        notebook = self.root.winfo_children()[0]
        current_tab = notebook.index(notebook.select())
        
        if current_tab == 0:  # User tab
            tree = self.user_tree
            cron = self.user_cron
        else:  # System tab
            tree = self.system_tree
            cron = self.system_cron
            
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a job to toggle.")
            return
            
        try:
            for item in selected:
                values = tree.item(item, 'values')
                # Find and toggle the job
                for job in cron:
                    if str(job) == values[1]:  # Compare command string
                        job.enable(not job.is_enabled())
                        break
            cron.write()
            self.load_jobs()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle job: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x500")
    app = CronGUI(root)
    root.mainloop()
