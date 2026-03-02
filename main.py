import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import cantools
import pandas as pd
import threading
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Set

# Local modular imports
from parser_engine import CANParser
from ui_components import ExcelConfigDialog

class CANProAnalyzer:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CAN Pro-Decoder v0.2")
        self.root.geometry("1600x950")
        
        # Internal State
        self.db: Optional[cantools.database.Database] = None
        self.raw_log_data: List[Dict[str, Any]] = []
        self.translation_table: Dict[str, Dict[str, str]] = {}
        self.checked_frames: Set[str] = set()
        self.check_vars: Dict[str, tk.BooleanVar] = {}
        self._is_loading: bool = False

        # Session Paths
        self.dbc_path, self.asc_path, self.xl_path = "", "", ""
        self.current_mapping = {}

        self._init_menu()
        self._init_ui()

    def _init_menu(self):
        """Creates a professional top-level Menu Bar."""
        menubar = tk.Menu(self.root)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load DBC", command=self.load_dbc)
        file_menu.add_command(label="Load ASC", command=self.load_asc)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="XLSM Translation Config", command=self.load_translation)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Session Menu
        session_menu = tk.Menu(menubar, tearoff=0)
        session_menu.add_command(label="Save Project Session", command=self.save_session)
        session_menu.add_command(label="Load Project Session", command=self.load_session)
        menubar.add_cascade(label="Session", menu=session_menu)

        self.root.config(menu=menubar)

    def _init_ui(self):
        # --- ADVANCED SEARCH RIBBON ---
        search_ribbon = tk.Frame(self.root, bg="#2c3e50", height=45)
        search_ribbon.pack(fill=tk.X, side=tk.TOP)
        
        lbl_style = {"bg": "#2c3e50", "fg": "white", "font": ("Segoe UI", 9, "bold")}
        ent_cfg = {"font": ("Consolas", 10)}

        tk.Label(search_ribbon, text="  SEARCH FILTERS | ", **lbl_style).pack(side=tk.LEFT)
        
        tk.Label(search_ribbon, text="FRAME/ID:", **lbl_style).pack(side=tk.LEFT, padx=5)
        self.search_frame = tk.StringVar()
        self.search_frame.trace_add("write", lambda *_: self.apply_filter())
        tk.Entry(search_ribbon, textvariable=self.search_frame, width=15, **ent_cfg).pack(side=tk.LEFT, padx=2)

        tk.Label(search_ribbon, text="SIGNAL:", **lbl_style).pack(side=tk.LEFT, padx=5)
        self.search_signal = tk.StringVar()
        self.search_signal.trace_add("write", lambda *_: self.apply_filter())
        tk.Entry(search_ribbon, textvariable=self.search_signal, width=20, **ent_cfg).pack(side=tk.LEFT, padx=2)

        tk.Label(search_ribbon, text="VALUE:", **lbl_style).pack(side=tk.LEFT, padx=5)
        self.search_value = tk.StringVar()
        self.search_value.trace_add("write", lambda *_: self.apply_filter())
        tk.Entry(search_ribbon, textvariable=self.search_value, width=10, **ent_cfg).pack(side=tk.LEFT, padx=2)

        # Main Vertical Split
        self.v_split = tk.PanedWindow(self.root, orient=tk.VERTICAL, sashwidth=6, bg="#bdc3c7")
        self.v_split.pack(fill=tk.BOTH, expand=True)

        # Horizontal Split for Top Views
        self.h_split = tk.PanedWindow(self.v_split, orient=tk.HORIZONTAL, sashwidth=6, bg="#bdc3c7")
        self.v_split.add(self.h_split, height=600)

        # --- SIDEBAR (DBC Checkboxes) ---
        l_frame = tk.Frame(self.h_split, bg="#f8f9fa")
        hdr = tk.Frame(l_frame, bg="#f8f9fa"); hdr.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(hdr, text="ACTIVE MESSAGES", bg="#f8f9fa", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.menu_btn = tk.Button(hdr, text="≡ Options", command=self._show_menu, relief="flat", font=("Segoe UI", 8)); self.menu_btn.pack(side=tk.RIGHT)
        
        sidebar_content = tk.Frame(l_frame, bg="white")
        sidebar_content.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(sidebar_content, bg="white", highlightthickness=0)
        self.scroll_f = tk.Frame(self.canvas, bg="white")
        scr_l = ttk.Scrollbar(sidebar_content, orient="vertical", command=self.canvas.yview)
        
        self.canvas.configure(yscrollcommand=scr_l.set)
        self.canvas_win = self.canvas.create_window((0,0), window=self.scroll_f, anchor="nw")
        self.scroll_f.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_win, width=e.width))
        
        scr_l.pack(side=tk.RIGHT, fill=tk.Y); self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sidebar_content.bind("<Enter>", lambda _: self.canvas.bind_all("<MouseWheel>", self._on_mw))
        sidebar_content.bind("<Leave>", lambda _: self.canvas.unbind_all("<MouseWheel>"))
        self.h_split.add(l_frame, width=320)

        # --- DATA TABLE (Middle) ---
        m_frame = tk.Frame(self.h_split)
        
        # Define the Grid weights: 
        # Column 0 (Tree) expands. Column 1 (Scrollbar) stays fixed.
        m_frame.columnconfigure(0, weight=1)
        m_frame.rowconfigure(0, weight=1)

        self.data_tree = ttk.Treeview(m_frame, columns=("Time", "ID", "Name", "Raw Data"), show='headings')
        
        # Using a standard tk.Scrollbar can sometimes be more visible than ttk
        scr_m = ttk.Scrollbar(m_frame, orient="vertical", command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=scr_m.set)

        for c in ("Time", "ID", "Name", "Raw Data"): 
            self.data_tree.heading(c, text=c)
            self.data_tree.column(c, anchor="center", width=100)

        # GRID PLACEMENT:
        # sticky="nsew" keeps the tree filling the entire left cell
        self.data_tree.grid(row=0, column=0, sticky="nsew")
        
        # sticky="ns" keeps the scrollbar stretched from top to bottom on the right
        scr_m.grid(row=0, column=1, sticky="ns")

        self.data_tree.bind("<<TreeviewSelect>>", self.on_select_msg)
        self.h_split.add(m_frame, width=650)

        # --- SIGNAL INSPECTOR ---
        r_frame = tk.Frame(self.h_split)
        self.ins_tree = ttk.Treeview(r_frame, columns=("Signal", "Value", "Translation", "Unit"), show="headings")
        scr_r = ttk.Scrollbar(r_frame, orient="vertical", command=self.ins_tree.yview)
        self.ins_tree.configure(yscrollcommand=scr_r.set)
        for c in ("Signal", "Value", "Translation", "Unit"):
            self.ins_tree.heading(c, text=c, anchor="w"); self.ins_tree.column(c, anchor="w")
        self.ins_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scr_r.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_split.add(r_frame, width=600)

        # --- SYSTEM LOG (Bottom Panel) ---
        log_frame = tk.Frame(self.v_split, bg="#2c3e50")
        self.log_text = tk.Text(log_frame, height=8, bg="#1e272e", fg="#00d8d6", font=("Consolas", 9), state='disabled')
        scr_log = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scr_log.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scr_log.pack(side=tk.RIGHT, fill=tk.Y)
        self.v_split.add(log_frame, height=150)

        # Footer
        self.footer = tk.Frame(self.root, bg="#ecf0f1", bd=1, relief=tk.SUNKEN)
        self.footer.pack(side=tk.BOTTOM, fill=tk.X)
        self.lbl_dbc = tk.Label(self.footer, text="DBC: None", bg="#ecf0f1", fg="#27ae60", font=("Arial", 8, "bold"))
        self.lbl_dbc.pack(side=tk.LEFT, padx=10)
        self.lbl_asc = tk.Label(self.footer, text="ASC: None", bg="#ecf0f1", fg="#2980b9", font=("Arial", 8, "bold"))
        self.lbl_asc.pack(side=tk.LEFT, padx=10)
        self.status = tk.Label(self.footer, text="Ready", bg="#ecf0f1", font=("Arial", 8), anchor="w")
        self.status.pack(side=tk.RIGHT, padx=10)

        self.ctx = tk.Menu(self.root, tearoff=0)
        self.ctx.add_command(label="Select All", command=self._select_all)
        self.ctx.add_command(label="Deselect All", command=self._deselect_all)
        self.ctx.add_command(label="Invert Selection", command=self._invert)

    def log_message(self, message: str, level: str = "INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"[{ts}] {level}: {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')

    def _on_mw(self, e): self.canvas.yview_scroll(int(-1*(e.delta/120)), "units")

    # --- ADVANCED MULTI-FIELD FILTER ---
    
    def apply_filter(self):
        if not self.raw_log_data: return
        f_q = self.search_frame.get().lower().strip()
        s_q = self.search_signal.get().lower().strip()
        v_q = self.search_value.get().lower().strip()
        
        self.data_tree.delete(*self.data_tree.get_children())
        if not self.checked_frames: return

        v_count = 0
        for idx, item in enumerate(self.raw_log_data):
            if item['name'] not in self.checked_frames: continue

            # Filter logic: AND operation between all non-empty fields
            f_match = not f_q or (f_q in item['name'].lower() or f_q in item['id'].lower())
            sv_match = True
            if s_q or v_q:
                sv_match = False
                for s_name, p_val in item['phys'].items():
                    s_hit = not s_q or s_q in s_name.lower()
                    v_hit = not v_q or v_q in str(p_val).lower()
                    if s_hit and v_hit:
                        sv_match = True; break
            
            if f_match and sv_match:
                self.data_tree.insert("", "end", values=(item['ts'], item['id'], item['name'], item['hex']), iid=idx)
                v_count += 1
        self.status.config(text=f"Matches: {v_count}")

    # --- LOADING & WORKER METHODS ---
    def load_asc(self, path=None):
        if self._is_loading or not self.db: return
        if not path: path = filedialog.askopenfilename(filetypes=[("ASC", "*.asc")])
        if path:
            self.asc_path = path; self.lbl_asc.config(text=f"ASC: {os.path.basename(path)}")
            self._is_loading = True; self.status.config(text="PARSING...", fg="red")
            self.log_message(f"Processing {os.path.basename(path)}...")
            threading.Thread(target=self._worker, args=(path,), daemon=True).start()

    def _worker(self, path):
        # We create a thread-safe wrapper for the logging function
        def thread_safe_log(msg, level="INFO"):
            self.root.after(0, lambda: self.log_message(msg, level))

        # Pass the logger to the parser
        data = CANParser.process_asc(path, self.db, log_func=thread_safe_log)
        
        self.root.after(0, self._finalize, data)

    def _finalize(self, data):
        self.raw_log_data = data; self._is_loading = False
        self.status.config(text=f"Ready | {len(data):,} messages.", fg="black")
        self.log_message(f"Load complete.")
        self.apply_filter()

    def load_dbc(self, path=None):
        if not path: path = filedialog.askopenfilename(filetypes=[("DBC", "*.dbc")])
        if path:
            self.db = cantools.database.load_file(path, strict=False)
            self.dbc_path = path; self.lbl_dbc.config(text=f"DBC: {os.path.basename(path)}")
            self.log_message(f"Database loaded: {os.path.basename(path)}")
            self._populate_sidebar()

    def _populate_sidebar(self):
        for w in self.scroll_f.winfo_children(): w.destroy()
        self.check_vars = {}
        for msg in sorted(self.db.messages, key=lambda x: x.name):
            var = tk.BooleanVar(value=True); self.check_vars[msg.name] = var
            cb = tk.Checkbutton(self.scroll_f, text=msg.name, variable=var, bg="white", anchor="w", command=self._update_filter)
            cb.pack(fill=tk.X); cb.bind("<Button-3>", lambda e: self.ctx.post(e.x_root, e.y_root))
        self._update_filter()

    def _update_filter(self):
        self.checked_frames = {n for n, v in self.check_vars.items() if v.get()}
        self.apply_filter()

    def load_translation(self):
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xls *.xlsx *.xlsm")])
        if path:
            xl = pd.ExcelFile(path)
            dlg = ExcelConfigDialog(self.root, xl); self.root.wait_window(dlg)
            if dlg.result:
                self.xl_path = path; self.current_mapping = dlg.result
                df = xl.parse(dlg.result["tab"])
                self.translation_table = {}
                for _, r in df.iterrows():
                    fid = str(r[dlg.result["ID"]]).strip().upper().replace("0X", "")
                    rv = str(r[dlg.result["Hex"]]).strip().lower()
                    self.translation_table.setdefault(fid, {})[rv] = str(r[dlg.result["Meaning"]])
                self.log_message("Translation table updated.")

    def on_select_msg(self, _):
        if not (sel := self.data_tree.selection()): return
        item = self.raw_log_data[int(sel[0])]
        self.ins_tree.delete(*self.ins_tree.get_children())
        f_id = item['id'].lstrip('0').upper()
        for s_n, p_v in item['phys'].items():
            raw_v = int(item['raw'].get(s_n, 0))
            keys = [str(raw_v), f"0x{raw_v:x}", f"0b{bin(raw_v)[2:].zfill(3)}"]
            trans = "-"
            if f_id in self.translation_table:
                for k in keys:
                    if k in self.translation_table[f_id]: trans = self.translation_table[f_id][k]; break
            unit = next((s.unit for s in item['def'].signals if s.name == s_n), "-")
            self.ins_tree.insert("", "end", values=(s_n, p_v, trans, unit))

    def save_session(self):
        d = {"dbc": self.dbc_path, "asc": self.asc_path, "xl": self.xl_path, "mapping": self.current_mapping, "filters": list(self.checked_frames)}
        if p := filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Project", "*.json")]):
            with open(p, 'w') as f: json.dump(d, f, indent=4)
            self.log_message("Session saved.")

    def load_session(self):
        if p := filedialog.askopenfilename(filetypes=[("JSON Project", "*.json")]):
            with open(p, 'r') as f: d = json.load(f)
            if os.path.exists(d.get("dbc", "")): self.load_dbc(d["dbc"])
            saved_f = d.get("filters", [])
            for n, v in self.check_vars.items(): v.set(n in saved_f)
            self._update_filter(); self.log_message("Session restored.")

    def _show_menu(self): self.ctx.post(self.menu_btn.winfo_rootx(), self.menu_btn.winfo_rooty() + 25)
    def _select_all(self): [v.set(True) for v in self.check_vars.values()]; self._update_filter()
    def _deselect_all(self): [v.set(False) for v in self.check_vars.values()]; self._update_filter()
    def _invert(self): [v.set(not v.get()) for v in self.check_vars.values()]; self._update_filter()

if __name__ == "__main__":
    root = tk.Tk(); app = CANProAnalyzer(root); root.mainloop()