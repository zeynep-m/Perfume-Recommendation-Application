import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
from tkinter import scrolledtext
import sqlite3
from perfume_db import PerfumeDatabase


class PerfumeFormWindow(tk.Toplevel):
    """Base form class for Add/Edit perfume windows"""
    
    def __init__(self, parent=None, title="Perfume Form"):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x700")
        self.resizable(False, False)
        
        # String variables for form fields
        self.perfume = tk.StringVar()
        self.gender = tk.StringVar()
        self.intensity = tk.StringVar()
        self.season = tk.StringVar()
        self.longevity = tk.StringVar()
        self.collection = tk.StringVar()
        self.classification = tk.StringVar()
        self.subfamily = tk.StringVar()
        self.sources = tk.StringVar()
        
        self.db = PerfumeDatabase()
        self.build_ui()

    def build_ui(self):
        """Build the form UI"""
        # Create main canvas with scrollbar for the form
        canvas = tk.Canvas(self, width=580)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=580)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create the LabelFrame container
        self.main_frame = ttk.LabelFrame(scrollable_frame, text="Perfume Details")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Configure grid columns
        self.main_frame.columnconfigure(index=0, weight=1, uniform="eq")
        self.main_frame.columnconfigure(index=1, weight=3, uniform="eq")

        # Define padding settings
        lbl_pad = {"padx": (15, 10), "pady": 8, "sticky": "ne"}
        ent_pad = {"padx": (10, 15), "pady": 8, "sticky": "ew"}

        row = 0

        # Perfume Name
        tk.Label(self.main_frame, text="Perfume Name *").grid(column=0, row=row, **lbl_pad)
        ttk.Entry(self.main_frame, textvariable=self.perfume, width=40).grid(column=1, row=row, **ent_pad)
        row += 1

        # Gender
        tk.Label(self.main_frame, text="Gender *").grid(column=0, row=row, **lbl_pad)
        gender_combo = ttk.Combobox(self.main_frame, textvariable=self.gender, width=37, 
                                    values=["Unisex", "Men", "Women"])
        gender_combo.grid(column=1, row=row, **ent_pad)
        row += 1

        # Intensity
        tk.Label(self.main_frame, text="Intensity *").grid(column=0, row=row, **lbl_pad)
        intensity_combo = ttk.Combobox(self.main_frame, textvariable=self.intensity, width=37,
                                      values=["Weak", "Moderate", "Strong", "Very Strong"])
        intensity_combo.grid(column=1, row=row, **ent_pad)
        row += 1

        # Ingredients/Notes (Text widget for multiline)
        tk.Label(self.main_frame, text="Ingredients/Notes").grid(column=0, row=row, **lbl_pad)
        self.txt_ingredients = tk.Text(self.main_frame, height=4, width=40, wrap="word")
        self.txt_ingredients.grid(column=1, row=row, **ent_pad)
        row += 1

        # Season
        tk.Label(self.main_frame, text="Season").grid(column=0, row=row, **lbl_pad)
        ttk.Entry(self.main_frame, textvariable=self.season, width=40).grid(column=1, row=row, **ent_pad)
        row += 1

        # Concept (Text widget for multiline)
        tk.Label(self.main_frame, text="Concept").grid(column=0, row=row, **lbl_pad)
        self.txt_concept = tk.Text(self.main_frame, height=3, width=40, wrap="word")
        self.txt_concept.grid(column=1, row=row, **ent_pad)
        row += 1

        # Longevity
        tk.Label(self.main_frame, text="Longevity").grid(column=0, row=row, **lbl_pad)
        longevity_combo = ttk.Combobox(self.main_frame, textvariable=self.longevity, width=37,
                                       values=["Weak", "Moderate", "Strong", "Very Long", "Long"])
        longevity_combo.grid(column=1, row=row, **ent_pad)
        row += 1

        # Collection
        tk.Label(self.main_frame, text="Collection").grid(column=0, row=row, **lbl_pad)
        ttk.Entry(self.main_frame, textvariable=self.collection, width=40).grid(column=1, row=row, **ent_pad)
        row += 1

        # Classification
        tk.Label(self.main_frame, text="Classification").grid(column=0, row=row, **lbl_pad)
        ttk.Entry(self.main_frame, textvariable=self.classification, width=40).grid(column=1, row=row, **ent_pad)
        row += 1

        # Subfamily
        tk.Label(self.main_frame, text="Subfamily").grid(column=0, row=row, **lbl_pad)
        ttk.Entry(self.main_frame, textvariable=self.subfamily, width=40).grid(column=1, row=row, **ent_pad)
        row += 1

        # Sources
        tk.Label(self.main_frame, text="Sources").grid(column=0, row=row, **lbl_pad)
        ttk.Entry(self.main_frame, textvariable=self.sources, width=40).grid(column=1, row=row, **ent_pad)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def validate_input(self):
        """Validate required fields"""
        if not self.perfume.get().strip():
            msg.showerror("Error", "Please enter a perfume name.", parent=self)
            return False

        if not self.gender.get().strip():
            msg.showerror("Error", "Please select a gender.", parent=self)
            return False

        if not self.intensity.get().strip():
            msg.showerror("Error", "Please select an intensity.", parent=self)
            return False

        return True

    def get_ingredients(self):
        """Get ingredients text from Text widget"""
        return self.txt_ingredients.get("1.0", "end-1c").strip()

    def set_ingredients(self, text):
        """Set ingredients text in Text widget"""
        self.txt_ingredients.delete("1.0", "end")
        self.txt_ingredients.insert("1.0", text)

    def get_concept(self):
        """Get concept text from Text widget"""
        return self.txt_concept.get("1.0", "end-1c").strip()

    def set_concept(self, text):
        """Set concept text in Text widget"""
        self.txt_concept.delete("1.0", "end")
        self.txt_concept.insert("1.0", text)
