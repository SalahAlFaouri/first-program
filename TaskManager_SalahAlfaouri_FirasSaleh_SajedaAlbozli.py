import os
import random
import datetime

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError as e:
    print("Error:", e)
    print("This application requires the tkinter module. Please install it or run in an environment that includes tkinter.")
    exit(1)

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# constants

TASK_FILE = 'tasks.txt'
DIFFICULTIES = ['Easy', 'Medium', 'Hard']
DIFF_COLORS = {'Easy': 'success', 'Medium': 'warning', 'Hard': 'danger'}
QUOTES = [
    "The more you do, the more you can do.",
    "It always seems impossible until it’s done.",
    "Don't watch the clock; do what it does. Keep going.",
    "Keep your eyes on the stars, and your feet on the ground.",
    "Done is better than perfect.",
]

def load_tasks():
    tasks = []
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, 'r') as f:
            for line in f:
                desc, diff = line.rstrip().split('|||')
                tasks.append({'desc': desc, 'diff': diff})
    return tasks

def save_tasks(tasks):
    with open(TASK_FILE, 'w') as f:
        for t in tasks:
            f.write(f"{t['desc']}|||{t['diff']}\n")

class TaskManagerApp:
    def __init__(self, theme=None):
        self.light_theme = 'litera'
        self.dark_theme = 'darkly'
        self.current_theme = theme or self.light_theme

        # create root window with fixed geometry propagation disabled

        self.root = ttk.Window(themename=self.current_theme)
        self.root.title('Daily Task Manager')
        self.root.geometry('600x450')                     # set initial window size
        self.root.grid_propagate(False)                   # disable resizing to fit children (stop propagation) ([reddit.com](https://www.reddit.com/r/Tkinter/comments/yo98we/struggling_with_frames_and_using_grid/?utm_source=chatgpt.com))
        self.root.minsize(500, 400)

        self.tasks = load_tasks()

        self.build_ui()
        self.refresh_list()
        self.update_time()

        #start the time update

    def build_ui(self):
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # left frame for task list, with propagation off

        self.left = ttk.Frame(self.root, padding=10)
        self.left.grid(row=0, column=0, sticky='nsew')
        self.left.grid_propagate(False)                   # keep left pane fixed size ([tutorialspoint.com](https://www.tutorialspoint.com/how-to-stop-tkinter-frame-from-shrinking-to-fit-its-contents?utm_source=chatgpt.com))
        self.left.columnconfigure(0, weight=1)
        self.left.rowconfigure(1, weight=1)

        ttk.Label(self.left, text='Your Tasks', font=('Helvetica', 18, 'bold')).grid(row=0, column=0, pady=(0, 10), sticky='w')

        self.tree = ttk.Treeview(
            self.left,
            columns=('Difficulty', 'Description'),
            show='headings',
            bootstyle="secondary"
        )
        self.tree.heading('Difficulty', text='Difficulty')
        self.tree.heading('Description', text='Description')
        self.tree.column('Difficulty', width=80, anchor='center')
        self.tree.grid(row=1, column=0, sticky='nsew')

        # Right frame for controls

        self.right = ttk.Frame(self.root, padding=10)
        self.right.grid(row=0, column=1, sticky='nsew')
        self.right.columnconfigure(0, weight=1)

        ttk.Label(self.right, text='Add New Task', font=('Helvetica', 14)).pack(anchor='w', pady=(0, 5))
        ttk.Label(self.right, text='Description:').pack(anchor='w')
        self.entry = ttk.Entry(self.right)
        self.entry.pack(fill='x', pady=(0, 10))

        ttk.Label(self.right, text='Difficulty:').pack(anchor='w')
        self.combo = ttk.Combobox(self.right, values=DIFFICULTIES, state='readonly', bootstyle=INFO)
        self.combo.set('Medium')
        self.combo.pack(fill='x', pady=(0, 15))

        for text, cmd, style in [
            ('Add Task', self.add_task, PRIMARY),
            ('Delete Task', self.delete_task, DANGER),
            ('Complete Task', self.complete_task, SUCCESS),
            ('Save & Exit', self.on_exit, SECONDARY),
        ]:
            btn = ttk.Button(self.right, text=text, command=cmd, bootstyle=style + "-outline")
            btn.pack(fill='x', pady=5)

        self.theme_button = ttk.Button(self.right, text='Toggle Dark Mode', command=self.toggle_theme, bootstyle=INFO)
        self.theme_button.pack(fill='x', pady=5)

        # Add date and time label

        self.time_var = tk.StringVar()
        self.time_label = ttk.Label(
            self.right,
            textvariable=self.time_var,
            font=('Helvetica', 10, 'italic'),
            bootstyle="secondary"
        )
        self.time_label.pack(anchor='e', padx=5, pady=5)

    def toggle_theme(self):

        # Switch themes without rebuilding the entire UI

        self.current_theme = self.dark_theme if self.current_theme == self.light_theme else self.light_theme
        self.root.style.theme_use(self.current_theme)

        # udate treeview colors to match the new theme

        self.refresh_list()

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        order = {'Hard': 0, 'Medium': 1, 'Easy': 2}
        self.tasks.sort(key=lambda t: order[t['diff']])
        for t in self.tasks:
            tag = DIFF_COLORS[t['diff']]
            self.tree.insert('', 'end', values=(t['diff'], t['desc']), tags=(tag,))

        # Reconfigure tag colors with the current theme's colors

        for style in DIFF_COLORS.values():
            self.tree.tag_configure(style, background=self.root.style.colors.get(style))

    def add_task(self):
        desc = self.entry.get().strip()
        diff = self.combo.get()
        if desc:
            self.tasks.append({'desc': desc, 'diff': diff})
            self.entry.delete(0, 'end')
            self.refresh_list()

    def delete_task(self):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            del self.tasks[idx]
            self.refresh_list()

    def complete_task(self):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            task = self.tasks.pop(idx)
            self.refresh_list()
            messagebox.showinfo(
                'Completed',
                f"You completed: {task['desc']}\n\n{random.choice(QUOTES)}"
            )

    def on_exit(self):
        save_tasks(self.tasks)
        self.root.destroy()

    def update_time(self):
        current_time = datetime.datetime.now().strftime("%A, %B %d, %Y - %I:%M:%S %p")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)  # Update every second

if __name__ == '__main__':
    app = TaskManagerApp()
    app.root.mainloop()
