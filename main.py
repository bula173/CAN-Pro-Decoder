import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import cantools
import pandas as pd
import threading
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Set

# Matplotlib integration (The part that was missing)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# Local modular imports
from parser_engine import CANParser
from ui_components import ExcelConfigDialog

class CANProAnalyzer:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CAN Pro-Decoder v0.3")
        self.root.geometry("1600x950")
        
        # Internal State
        self.db: Optional[cantools.database.Database] = None
        self.raw_log_data: List[Dict[str, Any]] = []
        self.translation_table: Dict[str, Dict[str, str]] = {}
        self.checked_frames: Set[str] = set()
        self.check_vars: Dict[str, tk.BooleanVar] = {}
        self._is_loading: bool = False

        # Graph State (Kept for UI compatibility, logic removed)
        self.graph_check_vars: Dict[str, tk.BooleanVar] = {}
        self.active_graph_signals: Set[str] = set()

        # Session Paths
        self.dbc_path, self.asc_path, self.xl_path = "", "", ""
        self.current_mapping = {}

        self._init_menu()
        self._init_ui()

    def _init_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load DBC", command=self.load_dbc)
        file_menu.add_command(label="Load ASC", command=self.load_asc)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="XLSM Translation Config", command=self.load_translation)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        self.root.config(menu=menubar)

    def _init_ui(self):
        search_ribbon = tk.Frame(self.root, bg="#2c3e50", height=45)
        search_ribbon.pack(fill=tk.X, side=tk.TOP)
        lbl_style = {"bg": "#2c3e50", "fg": "white", "font": ("Segoe UI", 9, "bold")}
        tk.Label(search_ribbon, text="  SEARCH FILTERS | ", **lbl_style).pack(side=tk.LEFT)
        self.search_frame = tk.StringVar(); self.search_frame.trace_add("write", lambda *_: self.apply_filter())
        tk.Entry(search_ribbon, textvariable=self.search_frame, width=15).pack(side=tk.LEFT, padx=2)

        self.v_split = tk.PanedWindow(self.root, orient=tk.VERTICAL, sashwidth=6, bg="#bdc3c7")
        self.v_split.pack(fill=tk.BOTH, expand=True)
        self.h_split = tk.PanedWindow(self.v_split, orient=tk.HORIZONTAL, sashwidth=6, bg="#bdc3c7")
        self.v_split.add(self.h_split, height=600)

        l_frame = tk.Frame(self.h_split, bg="#f8f9fa")
        self.canvas = tk.Canvas(l_frame, bg="white", highlightthickness=0)
        self.scroll_f = tk.Frame(self.canvas, bg="white")
        scr_l = ttk.Scrollbar(l_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scr_l.set)
        self.canvas.create_window((0,0), window=self.scroll_f, anchor="nw")
        scr_l.pack(side=tk.RIGHT, fill=tk.Y); self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.h_split.add(l_frame, width=300)

        m_frame = tk.Frame(self.h_split)
        self.notebook = ttk.Notebook(m_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_data = tk.Frame(self.notebook)
        self.notebook.add(self.tab_data, text=" 📝 Log Table ")
        self._setup_table_view(self.tab_data)

        self.tab_graph = tk.Frame(self.notebook)
        self.notebook.add(self.tab_graph, text=" 📈 Signal Analysis ")
        self._setup_graph_view(self.tab_graph)

        self.h_split.add(m_frame, width=800)

        r_frame = tk.Frame(self.h_split)
        self.ins_tree = ttk.Treeview(r_frame, columns=("Signal", "Value", "Translation", "Unit"), show="headings")
        scr_r = ttk.Scrollbar(r_frame, orient="vertical", command=self.ins_tree.yview)
        self.ins_tree.configure(yscrollcommand=scr_r.set)
        for c in ("Signal", "Value", "Translation", "Unit"): self.ins_tree.heading(c, text=c)
        self.ins_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); scr_r.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_split.add(r_frame, width=400)

        log_frame = tk.Frame(self.v_split, bg="#2c3e50")
        self.log_text = tk.Text(log_frame, height=8, bg="#1e272e", fg="#00d8d6", font=("Consolas", 9), state='disabled')
        scr_log = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scr_log.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); scr_log.pack(side=tk.RIGHT, fill=tk.Y)
        self.v_split.add(log_frame, height=150)

        self.footer = tk.Frame(self.root, bg="#ecf0f1", bd=1, relief=tk.SUNKEN)
        self.footer.pack(side=tk.BOTTOM, fill=tk.X)
        self.status = tk.Label(self.footer, text="Ready", bg="#ecf0f1", font=("Arial", 8))
        self.status.pack(side=tk.RIGHT, padx=10)

    def _setup_table_view(self, parent):
        parent.columnconfigure(0, weight=1); parent.rowconfigure(0, weight=1)
        self.data_tree = ttk.Treeview(parent, columns=("Time", "ID", "Name", "Raw Data"), show='headings')
        scr_m = ttk.Scrollbar(parent, orient="vertical", command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=scr_m.set)
        for c in ("Time", "ID", "Name", "Raw Data"): 
            self.data_tree.heading(c, text=c); self.data_tree.column(c, anchor="center")
        self.data_tree.grid(row=0, column=0, sticky="nsew"); scr_m.grid(row=0, column=1, sticky="ns")
        self.data_tree.bind("<<TreeviewSelect>>", self.on_select_msg)

    def _setup_graph_view(self, parent):
        self.g_split = tk.PanedWindow(parent, orient=tk.HORIZONTAL, sashwidth=4)
        self.g_split.pack(fill=tk.BOTH, expand=True)

        # Left side: Signal Selection List
        g_side = tk.Frame(self.g_split, bg="#f1f2f6", width=250)
        tk.Label(g_side, text="SELECT SIGNALS", bg="#dfe4ea", font=("Segoe UI", 8, "bold")).pack(fill=tk.X)
        
        self.g_canvas = tk.Canvas(g_side, bg="#f1f2f6", highlightthickness=0)
        self.g_scroll_f = tk.Frame(self.g_canvas, bg="#f1f2f6")
        scr_g = ttk.Scrollbar(g_side, orient="vertical", command=self.g_canvas.yview)
        self.g_canvas.configure(yscrollcommand=scr_g.set)
        self.g_canvas.create_window((0,0), window=self.g_scroll_f, anchor="nw")
        
        scr_g.pack(side=tk.RIGHT, fill=tk.Y); self.g_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.g_split.add(g_side)

        # Right side: The Actual Plot
        g_plot_area = tk.Frame(self.g_split, bg="white")
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Signal Timeline")
        self.ax.set_facecolor('#fdfdfd')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=g_plot_area)
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add the Matplotlib Navigation Toolbar (Zoom, Pan, Save)
        self.toolbar = NavigationToolbar2Tk(self.canvas_plot, g_plot_area)
        self.toolbar.update()
        
        self.g_split.add(g_plot_area)

    def update_graph(self):
        """Redraws the graph based on checked signals in the sidebar."""
        self.ax.clear()
        self.ax.set_title("Signal Analysis")
        self.ax.set_xlabel("Time (s)")
        self.ax.grid(True, alpha=0.3)

        has_data = False
        # Loop through all signals available in the graph sidebar
        for full_name, var in self.graph_check_vars.items():
            if var.get():
                msg_name, sig_name = full_name.split('.')
                times, values = [], []
                
                # Extract data points from the raw log we parsed earlier
                for entry in self.raw_log_data:
                    if entry['name'] == msg_name:
                        if sig_name in entry['phys']:
                            times.append(float(entry['ts']))
                            values.append(entry['phys'][sig_name])
                
                if times:
                    self.ax.plot(times, values, label=sig_name, marker='o', markersize=3, linewidth=1)
                    has_data = True
        
        if has_data:
            self.ax.legend(loc='upper right', fontsize='x-small', frameon=True)
        
        self.fig.tight_layout()
        self.canvas_plot.draw()

    def _populate_graph_signals(self):
        for w in self.g_scroll_f.winfo_children(): w.destroy()
        self.graph_check_vars = {}
        if not self.db: return
        
        for msg in sorted(self.db.messages, key=lambda x: x.name):
            msg_lbl = tk.Label(self.g_scroll_f, text=msg.name, bg="#ced6e0", font=("Segoe UI", 8, "italic"))
            msg_lbl.pack(fill=tk.X, pady=(5,0))
            for sig in msg.signals:
                var = tk.BooleanVar(value=False)
                full_name = f"{msg.name}.{sig.name}"
                self.graph_check_vars[full_name] = var
                cb = tk.Checkbutton(self.g_scroll_f, text=sig.name, variable=var, 
                                    bg="#f1f2f6", command=self.update_graph)
                cb.pack(fill=tk.X, padx=10)

    def _finalize(self, data):
        self.raw_log_data = data; self._is_loading = False
        self.status.config(text=f"Ready | {len(data):,} messages.", fg="black")
        self.log_message(f"Load complete.")
        self._populate_graph_signals() 
        self.apply_filter()

    def load_asc(self, path=None):
        if self._is_loading or not self.db: return
        if not path: path = filedialog.askopenfilename(filetypes=[("ASC", "*.asc")])
        if path:
            self.asc_path = path; self.status.config(text="PARSING...", fg="red")
            threading.Thread(target=self._worker, args=(path,), daemon=True).start()

    def _worker(self, path):
        def thread_safe_log(msg, level="INFO"): self.root.after(0, lambda: self.log_message(msg, level))
        data = CANParser.process_asc(path, self.db, log_func=thread_safe_log)
        self.root.after(0, self._finalize, data)

    def load_dbc(self, path=None):
        if not path: path = filedialog.askopenfilename(filetypes=[("DBC", "*.dbc")])
        if path:
            self.db = cantools.database.load_file(path, strict=False)
            self._populate_sidebar()
            self._populate_graph_signals()

    def _populate_sidebar(self):
        for w in self.scroll_f.winfo_children(): w.destroy()
        self.check_vars = {}
        # NEW: Reset the checked frames set
        self.checked_frames = set() 
        
        for msg in sorted(self.db.messages, key=lambda x: x.name):
            var = tk.BooleanVar(value=True)
            self.check_vars[msg.name] = var
            self.checked_frames.add(msg.name) # Add to set immediately
            cb = tk.Checkbutton(self.scroll_f, text=msg.name, variable=var, 
                                bg="white", anchor="w", command=self._update_filter)
            cb.pack(fill=tk.X)

    def _update_filter(self):
        self.checked_frames = {n for n, v in self.check_vars.items() if v.get()}
        self.apply_filter()

    def apply_filter(self):
        if not self.raw_log_data: 
            print("Debug: No raw data found!") # Check your console
            return
            
        self.data_tree.delete(*self.data_tree.get_children())
        f_q = self.search_frame.get().lower().strip()
        v_count = 0
        
        for idx, item in enumerate(self.raw_log_data):
            # Debug: print(f"Checking {item['name']}") 
            if item['name'] not in self.checked_frames: continue
            
            if f_q and not (f_q in item['name'].lower() or f_q in item['id'].lower()): 
                continue
                
            # Use 'end' without a specific iid to let Tkinter handle it
            self.data_tree.insert("", "end", values=(item['ts'], item['id'], item['name'], item['hex']))
            v_count += 1
            
        self.status.config(text=f"Matches: {v_count}")

    def on_select_msg(self, _):
        if not (sel := self.data_tree.selection()): return
        item = self.raw_log_data[int(sel[0])]
        self.ins_tree.delete(*self.ins_tree.get_children())
        for s_n, p_v in item['phys'].items():
            unit = next((s.unit for s in item['def'].signals if s.name == s_n), "-")
            self.ins_tree.insert("", "end", values=(s_n, p_v, "-", unit))

    def log_message(self, message, level="INFO"):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def load_translation(self): pass

if __name__ == "__main__":
    root = tk.Tk(); app = CANProAnalyzer(root); root.mainloop()