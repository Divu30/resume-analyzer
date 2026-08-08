"""
gui.py
------
Professional Tkinter frontend for the Intelligent Resume Analyzer.
Uses only the standard library: tkinter, tkinter.ttk, tkinter.filedialog,
tkinter.messagebox, tkinter.scrolledtext, csv, os.

Workflow:
1. Load / paste a Job Description.
2. Load one or more resume files (.txt / .docx) or a whole folder.
3. Click "Analyze Resumes" to rank candidates against the JD.
4. Double-click a result row to see a detailed breakdown.
5. Export ranked results to CSV.
"""

import os
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

from modules.file_reader import load_text, list_resume_files, FileReadError
from modules.jd_analyzer import analyze_jd
from modules.resume_analyzer import analyze_resume
from modules.matcher import rank_candidates

# ---- Color palette (professional, calm) ----
COLOR_BG = "#0f172a"          # slate-900
COLOR_PANEL = "#1e293b"       # slate-800
COLOR_ACCENT = "#38bdf8"      # sky-400
COLOR_ACCENT_DARK = "#0284c7" # sky-600
COLOR_TEXT = "#e2e8f0"        # slate-200
COLOR_MUTED = "#94a3b8"       # slate-400
COLOR_SUCCESS = "#22c55e"     # green-500
COLOR_WARN = "#f59e0b"        # amber-500
COLOR_DANGER = "#ef4444"      # red-500
COLOR_ROW = "#1e293b"
COLOR_ROW_ALT = "#243244"


class ResumeAnalyzerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Intelligent Resume Analyzer")
        self.root.geometry("1180x760")
        self.root.minsize(1000, 650)
        self.root.configure(bg=COLOR_BG)

        self.resume_paths = []      # list of file paths queued for analysis
        self.results = []           # last computed ranking results
        self.jd_data = None

        self._configure_styles()
        self._build_layout()

    # ------------------------------------------------------------------ #
    # Styling
    # ------------------------------------------------------------------ #
    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=COLOR_BG)
        style.configure("Panel.TFrame", background=COLOR_PANEL)

        style.configure(
            "TLabel", background=COLOR_BG, foreground=COLOR_TEXT,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Panel.TLabel", background=COLOR_PANEL, foreground=COLOR_TEXT,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Title.TLabel", background=COLOR_BG, foreground=COLOR_TEXT,
            font=("Segoe UI", 20, "bold"),
        )
        style.configure(
            "Subtitle.TLabel", background=COLOR_BG, foreground=COLOR_MUTED,
            font=("Segoe UI", 10),
        )
        style.configure(
            "SectionHeader.TLabel", background=COLOR_PANEL,
            foreground=COLOR_ACCENT, font=("Segoe UI", 11, "bold"),
        )

        style.configure(
            "Accent.TButton", background=COLOR_ACCENT_DARK,
            foreground="#ffffff", font=("Segoe UI", 10, "bold"),
            padding=8, borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", COLOR_ACCENT)],
        )

        style.configure(
            "Secondary.TButton", background="#334155",
            foreground=COLOR_TEXT, font=("Segoe UI", 9), padding=6,
            borderwidth=0,
        )
        style.map("Secondary.TButton", background=[("active", "#475569")])

        style.configure(
            "Treeview", background=COLOR_ROW, fieldbackground=COLOR_ROW,
            foreground=COLOR_TEXT, rowheight=28, font=("Segoe UI", 9),
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading", background="#334155", foreground=COLOR_TEXT,
            font=("Segoe UI", 9, "bold"), relief="flat",
        )
        style.map("Treeview.Heading", background=[("active", "#475569")])
        style.map("Treeview", background=[("selected", COLOR_ACCENT_DARK)])

    # ------------------------------------------------------------------ #
    # Layout
    # ------------------------------------------------------------------ #
    def _build_layout(self):
        # Header
        header = ttk.Frame(self.root, style="TFrame")
        header.pack(fill="x", padx=24, pady=(20, 10))

        ttk.Label(header, text="Intelligent Resume Analyzer",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Compare resumes against a job description - 100% offline, "
                 "standard-library only.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        # Main body: left (inputs) + right (results)
        body = ttk.Frame(self.root, style="TFrame")
        body.pack(fill="both", expand=True, padx=24, pady=10)
        body.columnconfigure(0, weight=1, minsize=380)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._build_input_panel(body)
        self._build_results_panel(body)

        # Status bar
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, style="Subtitle.TLabel",
            anchor="w", padding=(24, 6),
        )
        status_bar.pack(fill="x", side="bottom")

    def _build_input_panel(self, parent):
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=16)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # --- JD Section ---
        ttk.Label(panel, text="1. Job Description",
                  style="SectionHeader.TLabel").pack(anchor="w")

        jd_btn_row = ttk.Frame(panel, style="Panel.TFrame")
        jd_btn_row.pack(fill="x", pady=(8, 6))
        ttk.Button(jd_btn_row, text="Load JD File", style="Secondary.TButton",
                   command=self.load_jd_file).pack(side="left")
        ttk.Button(jd_btn_row, text="Clear", style="Secondary.TButton",
                   command=self.clear_jd).pack(side="left", padx=(8, 0))

        self.jd_text_box = scrolledtext.ScrolledText(
            panel, height=12, wrap="word", bg="#0b1220", fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT, relief="flat", font=("Consolas", 10),
        )
        self.jd_text_box.pack(fill="both", expand=True, pady=(0, 14))

        # --- Resume Section ---
        ttk.Label(panel, text="2. Resumes",
                  style="SectionHeader.TLabel").pack(anchor="w")

        resume_btn_row = ttk.Frame(panel, style="Panel.TFrame")
        resume_btn_row.pack(fill="x", pady=(8, 6))
        ttk.Button(resume_btn_row, text="Add Files", style="Secondary.TButton",
                   command=self.add_resume_files).pack(side="left")
        ttk.Button(resume_btn_row, text="Add Folder", style="Secondary.TButton",
                   command=self.add_resume_folder).pack(side="left", padx=(8, 0))
        ttk.Button(resume_btn_row, text="Clear List", style="Secondary.TButton",
                   command=self.clear_resumes).pack(side="left", padx=(8, 0))

        list_frame = ttk.Frame(panel, style="Panel.TFrame")
        list_frame.pack(fill="both", expand=False, pady=(0, 14))
        self.resume_listbox = tk.Listbox(
            list_frame, height=8, bg="#0b1220", fg=COLOR_TEXT,
            selectbackground=COLOR_ACCENT_DARK, relief="flat",
            font=("Segoe UI", 9), highlightthickness=0,
        )
        self.resume_listbox.pack(fill="both", expand=True)

        # --- Analyze Button ---
        ttk.Button(panel, text="Analyze Resumes", style="Accent.TButton",
                   command=self.analyze).pack(fill="x", pady=(4, 0))

    def _build_results_panel(self, parent):
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=16)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.rowconfigure(1, weight=1)
        panel.columnconfigure(0, weight=1)

        top_row = ttk.Frame(panel, style="Panel.TFrame")
        top_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(top_row, text="3. Ranked Results",
                  style="SectionHeader.TLabel").pack(side="left")
        ttk.Button(top_row, text="Export CSV", style="Secondary.TButton",
                   command=self.export_csv).pack(side="right")

        columns = ("rank", "name", "score", "matched", "missing", "email")
        self.tree = ttk.Treeview(
            panel, columns=columns, show="headings", selectmode="browse",
        )
        headings = {
            "rank": ("Rank", 50),
            "name": ("Candidate", 160),
            "score": ("Match %", 80),
            "matched": ("Matched Skills", 110),
            "missing": ("Missing Skills", 110),
            "email": ("Email", 200),
        }
        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center" if col in
                              ("rank", "score", "matched", "missing") else "w")

        self.tree.grid(row=1, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", self.show_candidate_detail)

        scrollbar = ttk.Scrollbar(panel, orient="vertical",
                                   command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")

        self.tree.tag_configure("high", foreground=COLOR_SUCCESS)
        self.tree.tag_configure("mid", foreground=COLOR_WARN)
        self.tree.tag_configure("low", foreground=COLOR_DANGER)

        hint = ttk.Label(
            panel, text="Double-click a row to view a detailed breakdown.",
            style="Panel.TLabel", foreground=COLOR_MUTED,
        )
        hint.grid(row=2, column=0, sticky="w", pady=(8, 0))

    # ------------------------------------------------------------------ #
    # JD actions
    # ------------------------------------------------------------------ #
    def load_jd_file(self):
        path = filedialog.askopenfilename(
            title="Select Job Description file",
            filetypes=[("Text/Word files", "*.txt *.docx"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            text = load_text(path)
        except FileReadError as e:
            messagebox.showerror("Error Loading JD", str(e))
            return
        self.jd_text_box.delete("1.0", tk.END)
        self.jd_text_box.insert(tk.END, text)
        self.status_var.set(f"Loaded JD from {os.path.basename(path)}")

    def clear_jd(self):
        self.jd_text_box.delete("1.0", tk.END)

    # ------------------------------------------------------------------ #
    # Resume actions
    # ------------------------------------------------------------------ #
    def add_resume_files(self):
        paths = filedialog.askopenfilenames(
            title="Select resume files",
            filetypes=[("Text/Word files", "*.txt *.docx"), ("All files", "*.*")],
        )
        for p in paths:
            if p not in self.resume_paths:
                self.resume_paths.append(p)
                self.resume_listbox.insert(tk.END, os.path.basename(p))
        if paths:
            self.status_var.set(f"{len(self.resume_paths)} resume(s) queued.")

    def add_resume_folder(self):
        folder = filedialog.askdirectory(title="Select folder containing resumes")
        if not folder:
            return
        try:
            files = list_resume_files(folder)
        except FileReadError as e:
            messagebox.showerror("Error", str(e))
            return
        if not files:
            messagebox.showwarning(
                "No Resumes Found",
                "No .txt or .docx files were found in that folder.",
            )
            return
        for p in files:
            if p not in self.resume_paths:
                self.resume_paths.append(p)
                self.resume_listbox.insert(tk.END, os.path.basename(p))
        self.status_var.set(f"{len(self.resume_paths)} resume(s) queued.")

    def clear_resumes(self):
        self.resume_paths = []
        self.resume_listbox.delete(0, tk.END)

    # ------------------------------------------------------------------ #
    # Analysis
    # ------------------------------------------------------------------ #
    def analyze(self):
        jd_text = self.jd_text_box.get("1.0", tk.END).strip()
        if not jd_text:
            messagebox.showwarning(
                "Missing Job Description",
                "Please load or paste a job description before analyzing.",
            )
            return
        if not self.resume_paths:
            messagebox.showwarning(
                "No Resumes",
                "Please add at least one resume file or folder before analyzing.",
            )
            return

        try:
            self.jd_data = analyze_jd(jd_text)
        except ValueError as e:
            messagebox.showerror("Error Analyzing JD", str(e))
            return

        resumes_data = []
        errors = []
        for path in self.resume_paths:
            try:
                text = load_text(path)
                resumes_data.append(analyze_resume(text, path))
            except (FileReadError, ValueError) as e:
                errors.append(f"{os.path.basename(path)}: {e}")

        if not resumes_data:
            messagebox.showerror(
                "No Valid Resumes",
                "None of the selected resumes could be read.\n\n"
                + "\n".join(errors),
            )
            return

        self.results = rank_candidates(self.jd_data, resumes_data)
        self._populate_results_table()

        msg = f"Analyzed {len(resumes_data)} resume(s)."
        if errors:
            msg += f" {len(errors)} file(s) skipped due to errors."
        self.status_var.set(msg)

        if errors:
            messagebox.showwarning(
                "Some Files Skipped",
                "The following files could not be processed:\n\n"
                + "\n".join(errors),
            )

    def _populate_results_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for idx, r in enumerate(self.results, start=1):
            score = r["overall_score"]
            tag = "high" if score >= 70 else "mid" if score >= 40 else "low"
            self.tree.insert(
                "", tk.END,
                values=(
                    idx,
                    r["candidate_name"],
                    f"{score:.2f}",
                    len(r["matched_skills"]),
                    len(r["missing_skills"]),
                    r["email"],
                ),
                tags=(tag,),
            )

    # ------------------------------------------------------------------ #
    # Detail popup
    # ------------------------------------------------------------------ #
    def show_candidate_detail(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index >= len(self.results):
            return
        r = self.results[index]

        win = tk.Toplevel(self.root)
        win.title(f"Details - {r['candidate_name']}")
        win.geometry("560x520")
        win.configure(bg=COLOR_BG)

        def add_row(label, value, color=COLOR_TEXT):
            frame = ttk.Frame(win, style="TFrame")
            frame.pack(fill="x", padx=20, pady=3)
            ttk.Label(frame, text=label, style="TLabel", width=22,
                      foreground=COLOR_MUTED).pack(side="left")
            tk.Label(frame, text=value, bg=COLOR_BG, fg=color,
                     font=("Segoe UI", 10, "bold"), wraplength=320,
                     justify="left", anchor="w").pack(side="left", fill="x")

        ttk.Label(win, text=r["candidate_name"], style="Title.TLabel").pack(
            anchor="w", padx=20, pady=(16, 4)
        )
        add_row("Overall Match:", f"{r['overall_score']:.2f}%", COLOR_ACCENT)
        add_row("Email:", r["email"])
        add_row("Phone:", r["phone"])
        add_row("Source File:", r["source_file"] or "-")
        add_row("Skill Score:", f"{r['skill_score']:.2f}%")
        add_row("Text Similarity:", f"{r['text_similarity_score']:.2f}%")
        add_row(
            "Experience:",
            f"{r['candidate_experience_years']} yrs "
            f"(required: {r['required_experience_years'] or 'not specified'})",
            COLOR_SUCCESS if r["experience_ok"] else COLOR_DANGER,
        )
        add_row(
            "Education Match:",
            "Meets requirement" if r["education_ok"] else "Below requirement",
            COLOR_SUCCESS if r["education_ok"] else COLOR_DANGER,
        )

        ttk.Separator(win, orient="horizontal").pack(fill="x", padx=20, pady=10)

        ttk.Label(win, text="Matched Skills", style="SectionHeader.TLabel",
                  background=COLOR_BG).pack(anchor="w", padx=20)
        matched_text = ", ".join(r["matched_skills"]) or "None"
        tk.Label(win, text=matched_text, bg=COLOR_BG, fg=COLOR_SUCCESS,
                 wraplength=500, justify="left", anchor="w").pack(
            anchor="w", padx=20, pady=(2, 10)
        )

        ttk.Label(win, text="Missing Skills", style="SectionHeader.TLabel",
                  background=COLOR_BG).pack(anchor="w", padx=20)
        missing_text = ", ".join(r["missing_skills"]) or "None"
        tk.Label(win, text=missing_text, bg=COLOR_BG, fg=COLOR_DANGER,
                 wraplength=500, justify="left", anchor="w").pack(
            anchor="w", padx=20, pady=(2, 10)
        )

        ttk.Button(win, text="Close", style="Secondary.TButton",
                   command=win.destroy).pack(pady=16)

    # ------------------------------------------------------------------ #
    # Export
    # ------------------------------------------------------------------ #
    def export_csv(self):
        if not self.results:
            messagebox.showwarning("No Results", "Run an analysis first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save results as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Rank", "Candidate", "Email", "Phone", "Overall Score (%)",
                    "Skill Score (%)", "Text Similarity (%)",
                    "Experience (yrs)", "Required Experience (yrs)",
                    "Matched Skills", "Missing Skills", "Source File",
                ])
                for idx, r in enumerate(self.results, start=1):
                    writer.writerow([
                        idx, r["candidate_name"], r["email"], r["phone"],
                        r["overall_score"], r["skill_score"],
                        r["text_similarity_score"],
                        r["candidate_experience_years"],
                        r["required_experience_years"] or "",
                        "; ".join(r["matched_skills"]),
                        "; ".join(r["missing_skills"]),
                        r["source_file"],
                    ])
        except OSError as e:
            messagebox.showerror("Export Failed", str(e))
            return
        messagebox.showinfo("Export Complete", f"Results saved to:\n{path}")
        self.status_var.set(f"Results exported to {os.path.basename(path)}")


def launch_app():
    root = tk.Tk()
    app = ResumeAnalyzerApp(root)
    root.mainloop()
