import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from typing import Optional, Dict

class ExcelConfigDialog(tk.Toplevel):
    """Encapsulated UI for Excel translation configuration."""
    def __init__(self, parent, xl_file: pd.ExcelFile):
        super().__init__(parent)
        self.title("Translation Configuration")
        self.geometry("400x400")
        self.xl = xl_file
        self.result: Optional[Dict[str, str]] = None
        self._setup_ui()
        self.transient(parent)
        self.grab_set()

    def _setup_ui(self):
        container = tk.Frame(self, padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text="Select Sheet:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.tab_var = tk.StringVar()
        self.tab_cb = ttk.Combobox(container, textvariable=self.tab_var, values=self.xl.sheet_names, state="readonly")
        self.tab_cb.pack(fill=tk.X, pady=(0, 15))
        self.tab_cb.bind("<<ComboboxSelected>>", self._on_tab_select)

        self.col_vars = {k: tk.StringVar() for k in ["ID", "Hex", "Meaning"]}
        for label, var in [("Frame ID Column:", "ID"), ("Coding Column:", "Hex"), ("Meaning Column:", "Meaning")]:
            tk.Label(container, text=label).pack(anchor="w")
            cb = ttk.Combobox(container, textvariable=self.col_vars[var], state="readonly")
            cb.pack(fill=tk.X, pady=2)
            setattr(self, f"cb_{var.lower()}", cb)

        tk.Button(container, text="Apply Configuration", bg="#8e44ad", fg="white", 
                  command=self._submit, relief="flat", pady=5).pack(fill=tk.X, pady=(20, 0))

    def _on_tab_select(self, _):
        df = self.xl.parse(self.tab_var.get(), nrows=1)
        cols = df.columns.tolist()
        self.cb_id.config(values=cols)
        self.cb_hex.config(values=cols)
        self.cb_meaning.config(values=cols)

    def _submit(self):
        if not all([self.tab_var.get(), self.col_vars["ID"].get(), self.col_vars["Hex"].get()]):
            return messagebox.showwarning("Incomplete", "Please map required columns.")
        self.result = {k: v.get() for k, v in self.col_vars.items()}
        self.result["tab"] = self.tab_var.get()
        self.destroy()