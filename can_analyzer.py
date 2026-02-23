import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import cantools
import os
from datetime import datetime

class CANProAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("CAN Pro-Decoder v1.0")
        self.root.geometry("1400x900")

        # Add this line to set the window icon
        # Ensure 'app_icon.ico' is in the same folder as your script
        try:
            self.root.iconbitmap("app_icon.ico")
        except:
            pass # If icon is missing, the app will still run with default icon
        
        # Data storage
        self.db = None
        self.raw_log_data = [] 
        self.filtered_indices = []
        
        self.setup_styles()
        self.setup_ui()
        self.log("System Initialized. Load a DBC to begin.")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", rowheight=25, font=('Segoe UI', 9))
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        style.map("Treeview", background=[('selected', '#347083')])

    def setup_ui(self):
        # --- TOP TOOLBAR ---
        toolbar = tk.Frame(self.root, bg="#2c3e50", height=50)
        toolbar.pack(fill=tk.X, side=tk.TOP)

        # File Controls
        self.btn_dbc = tk.Button(toolbar, text="LOAD DBC", command=self.load_dbc, bg="#27ae60", fg="white", relief="flat", padx=10)
        self.btn_dbc.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.btn_asc = tk.Button(toolbar, text="LOAD ASC", command=self.load_asc, bg="#2980b9", fg="white", relief="flat", padx=10)
        self.btn_asc.pack(side=tk.LEFT, padx=5, pady=10)

        # Search
        search_lbl = tk.Label(toolbar, text="SEARCH:", bg="#2c3e50", fg="white", font=("Arial", 9, "bold"))
        search_lbl.pack(side=tk.LEFT, padx=(30, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.apply_filter)
        self.search_entry = tk.Entry(toolbar, textvariable=self.search_var, width=40, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, pady=10)

        # --- MAIN PANELS ---
        self.main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=4)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # Left Panel (DBC Tree)
        left_frame = tk.Frame(self.main_paned, bg="#f8f9fa")
        tk.Label(left_frame, text="DBC EXPLORER", bg="#f8f9fa", font=("Arial", 9, "bold")).pack(pady=5)
        self.dbc_tree = ttk.Treeview(left_frame, show="tree")
        self.dbc_tree.pack(fill=tk.BOTH, expand=True)
        self.main_paned.add(left_frame, width=300)

        # Middle Panel (Table)
        mid_frame = tk.Frame(self.main_paned)
        self.data_tree = ttk.Treeview(mid_frame, columns=("Time", "ID", "Name", "DLC"), show='headings')
        for col in ("Time", "ID", "Name", "DLC"):
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=100, anchor="center")
        self.data_tree.column("Name", width=250, anchor="w")
        self.data_tree.pack(fill=tk.BOTH, expand=True)
        self.data_tree.bind("<<TreeviewSelect>>", self.on_select_msg)
        self.main_paned.add(mid_frame, width=600)

        # Right Panel (Inspector)
        right_frame = tk.Frame(self.main_paned, bg="#ffffff")
        tk.Label(right_frame, text="SIGNAL INSPECTOR", font=("Arial", 9, "bold")).pack(pady=5)
        self.ins_tree = ttk.Treeview(right_frame, columns=("Signal", "Value", "Unit"), show="headings")
        self.ins_tree.heading("Signal", text="Signal")
        self.ins_tree.heading("Value", text="Value")
        self.ins_tree.heading("Unit", text="Unit")
        self.ins_tree.column("Value", anchor="center", width=100)
        self.ins_tree.column("Unit", width=60)
        self.ins_tree.pack(fill=tk.BOTH, expand=True)
        self.main_paned.add(right_frame, width=450)

        # --- BOTTOM LOGS & STATUS ---
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.log_widget = scrolledtext.ScrolledText(self.root, height=6, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9))
        self.log_widget.pack(fill=tk.X, side=tk.BOTTOM)

    def log(self, msg):
        self.log_widget.config(state='normal')
        self.log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_widget.see(tk.END)
        self.log_widget.config(state='disabled')

    def update_status(self, text):
        self.status_bar.config(text=text)

    def load_dbc(self):
        path = filedialog.askopenfilename(filetypes=[("DBC", "*.dbc")])
        if not path: return
        try:
            self.db = cantools.database.load_file(path, strict=False)
            self.log(f"Loaded DBC: {os.path.basename(path)}")
            self.btn_dbc.config(text=f"DBC: {os.path.basename(path)[:15]}...")
            
            # Populate Explorer Tree
            for i in self.dbc_tree.get_children(): self.dbc_tree.delete(i)
            for msg in sorted(self.db.messages, key=lambda x: x.name):
                node = self.dbc_tree.insert("", "end", text=msg.name, open=False)
                for sig in msg.signals:
                    self.dbc_tree.insert(node, "end", text=f"• {sig.name}")
            
            self.update_status(f"DBC Active: {len(self.db.messages)} messages")
        except Exception as e:
            self.log(f"Error: {e}")

    def load_asc(self):
        if not self.db:
            messagebox.showwarning("DBC Missing", "Please load a DBC file before importing logs.")
            return
        path = filedialog.askopenfilename(filetypes=[("ASC", "*.asc")])
        if not path: return
        self.process_asc(path)

    def process_asc(self, path):
        self.log(f"--- Debugging ASC: {os.path.basename(path)} ---")
        self.raw_log_data = []
        count = 0
        line_num = 0
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line_num += 1
                p = line.split()
                
                # Skip header/empty lines
                if len(p) < 5 or p[0] in ['date', 'base', 'begin', '//']:
                    continue

                # LOG THE FIRST DATA LINE FOR DEBUGGING
                if count == 0 and line_num < 15:
                    self.log(f"Line {line_num} Raw Content: {' '.join(p[:10])}")

                try:
                    # 1. FIND THE CAN ID
                    # In Vector ASC, the ID is usually the first hex-looking thing after the channel
                    # We'll try index 2 first (Standard), then fallback to index 1
                    id_candidate = ""
                    if 'Rx' in p or 'Tx' in p:
                        idx_dir = p.index('Rx') if 'Rx' in p else p.index('Tx')
                        id_candidate = p[idx_dir - 1] # ID is usually right before Rx/Tx
                    else:
                        id_candidate = p[2] # Fallback to 3rd column
                    
                    clean_id = id_candidate.lower().replace('x', '').replace('h', '')
                    can_id = int(clean_id, 16)
                    
                    # 2. FIND THE DATA BYTES
                    # We look for 'd' (Data Length) and take what follows
                    if 'd' in p:
                        d_idx = p.index('d')
                        dlc = int(p[d_idx+1])
                        data_hex = "".join(p[d_idx+2 : d_idx+2+dlc])
                    else:
                        continue # Skip lines without data markers

                    data_bytes = bytes.fromhex(data_hex)

                    # 3. MATCH WITH DBC
                    try:
                        msg_def = self.db.get_message_by_frame_id(can_id)
                        decoded = self.db.decode_message(can_id, data_bytes)
                        
                        self.raw_log_data.append({
                            'ts': p[0],
                            'id': hex(can_id),
                            'name': msg_def.name,
                            'dlc': dlc,
                            'signals': decoded,
                            'msg_def': msg_def
                        })
                        count += 1
                    except KeyError:
                        # ID not in DBC - we skip quietly but keep going
                        continue
                except Exception as e:
                    # If we fail to parse a specific line, log it once
                    if count == 0 and line_num == 10:
                        self.log(f"Parsing error on line {line_num}: {e}")
                    continue
        
        self.log(f"--- Finished ---")
        self.log(f"Matches found: {count} (Total lines checked: {line_num})")
        self.apply_filter()

    def apply_filter(self, *args):
        query = self.search_var.get().lower()
        for i in self.data_tree.get_children(): self.data_tree.delete(i)
        
        # Performance: Only show first 1000 matches in GUI
        visible_count = 0
        for idx, item in enumerate(self.raw_log_data):
            if query in item['name'].lower() or query in item['id'].lower():
                self.data_tree.insert("", "end", values=(item['ts'], item['id'], item['name'], item['dlc']), iid=idx)
                visible_count += 1
                if visible_count > 1000: break
        
        self.update_status(f"Displaying {visible_count} of {len(self.raw_log_data)} total matches")

    def on_select_msg(self, event):
        selected = self.data_tree.selection()
        if not selected: return
        
        # Get index from iid
        data_idx = int(selected[0])
        entry = self.raw_log_data[data_idx]
        
        for i in self.ins_tree.get_children(): self.ins_tree.delete(i)
        
        for sig_name, val in entry['signals'].items():
            # Lookup unit from msg_def
            unit = ""
            for s in entry['msg_def'].signals:
                if s.name == sig_name:
                    unit = s.unit if s.unit else "-"
                    break
            
            # Format value
            display_val = f"{val:.3f}" if isinstance(val, float) else val
            self.ins_tree.insert("", "end", values=(sig_name, display_val, unit))

if __name__ == "__main__":
    root = tk.Tk()
    app = CANProAnalyzer(root)
    root.mainloop()