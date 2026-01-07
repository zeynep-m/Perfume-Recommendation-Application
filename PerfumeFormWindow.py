import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
from tkinter import scrolledtext
import customtkinter as ctk
import sqlite3
from perfume_db import PerfumeDatabase
from i18n import _

# Configure CustomTkinter theme
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")


class PerfumeFormWindow(ctk.CTkToplevel):
    """Base form class for Add/Edit perfume windows"""
    
    def __init__(self, parent=None, title="Perfume Form"):
        super().__init__(parent)
        self.withdraw()
        self.title(_(title))
        try:
            self.state('normal')
        except Exception:
            pass
        self.geometry("600x680")
        self.resizable(False, False)
        if parent is not None:
            try:
                self.transient(parent)
            except Exception:
                pass
        
        # String variables for form fields
        self.perfume = tk.StringVar()
        self.gender = tk.StringVar()
        self.intensity = tk.StringVar()
        self.season = tk.StringVar()
        self.longevity = tk.StringVar()
        self.collection = tk.StringVar()
        self.classification = tk.StringVar()
        self.subfamily = tk.StringVar()
        
        # Track required fields for validation highlighting
        self.required_fields = {}
        
        self.db = PerfumeDatabase()
        self.build_ui()
        try:
            self._center_on_parent(parent)
        finally:
            self.deiconify()
        # Make the window modal relative to parent
        try:
            if parent is not None:
                self.transient(parent)
                self.grab_set()
            self.focus_set()
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

    def build_ui(self):
        """Build the form UI"""
        # Create a container frame for canvas and scrollbar
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True)

        # Create main canvas with scrollbar for the form
        canvas = tk.Canvas(form_frame, width=580, bg=self._get_bg_color())
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="transparent")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=580)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create the LabelFrame container
        self.main_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Configure grid columns
        self.main_frame.columnconfigure(index=0, weight=1, uniform="eq")
        self.main_frame.columnconfigure(index=1, weight=3, uniform="eq")

        # Define padding settings
        lbl_pad = {"padx": (15, 10), "pady": 8, "sticky": "ne"}
        ent_pad = {"padx": (10, 15), "pady": 8, "sticky": "ew"}

        row = 0

        # Perfume Name
        perfume_lbl = ctk.CTkLabel(self.main_frame, text=_("Perfume Name *"))
        perfume_lbl.grid(column=0, row=row, **lbl_pad)
        perfume_entry = ctk.CTkEntry(self.main_frame, textvariable=self.perfume, width=300)
        perfume_entry.grid(column=1, row=row, **ent_pad)
        self.required_fields['perfume'] = (perfume_entry, perfume_lbl)
        row += 1

        # Gender
        gender_lbl = ctk.CTkLabel(self.main_frame, text=_("Gender *"))
        gender_lbl.grid(column=0, row=row, **lbl_pad)
        gender_combo = ctk.CTkComboBox(self.main_frame, variable=self.gender, width=300,
            values=[_("Unisex"), _("Man"), _("Woman")])
        gender_combo.grid(column=1, row=row, **ent_pad)
        self.required_fields['gender'] = (gender_combo, gender_lbl)
        row += 1

        # Intensity
        intensity_lbl = ctk.CTkLabel(self.main_frame, text=_("Intensity *"))
        intensity_lbl.grid(column=0, row=row, **lbl_pad)
        intensity_combo = ctk.CTkComboBox(self.main_frame, variable=self.intensity, width=300,
                  values=[_("Weak"), _("Moderate"), _("Strong"), _("Very Strong")])
        intensity_combo.grid(column=1, row=row, **ent_pad)
        self.required_fields['intensity'] = (intensity_combo, intensity_lbl)
        row += 1

        # Ingredients/Notes (ScrolledText widget for multiline)
        ctk.CTkLabel(self.main_frame, text=_("Ingredients/Notes")).grid(column=0, row=row, **lbl_pad)
        self.txt_ingredients = scrolledtext.ScrolledText(self.main_frame, height=4, width=40, wrap="word")
        self.txt_ingredients.grid(column=1, row=row, **ent_pad)
        row += 1

        # Season
        ctk.CTkLabel(self.main_frame, text=_("Season")).grid(column=0, row=row, **lbl_pad)
        ctk.CTkEntry(self.main_frame, textvariable=self.season, width=300).grid(column=1, row=row, **ent_pad)
        row += 1

        # Concept (ScrolledText widget for multiline)
        ctk.CTkLabel(self.main_frame, text=_("Concept")).grid(column=0, row=row, **lbl_pad)
        self.txt_concept = scrolledtext.ScrolledText(self.main_frame, height=3, width=40, wrap="word")
        self.txt_concept.grid(column=1, row=row, **ent_pad)
        row += 1

        # Longevity
        ctk.CTkLabel(self.main_frame, text=_("Longevity")).grid(column=0, row=row, **lbl_pad)
        longevity_combo = ctk.CTkComboBox(self.main_frame, variable=self.longevity, width=300,
                   values=[_("Weak"), _("Moderate"), _("Strong"), _("Very Long"), _("Long")])
        longevity_combo.grid(column=1, row=row, **ent_pad)
        row += 1

        # Collection
        ctk.CTkLabel(self.main_frame, text=_("Collection")).grid(column=0, row=row, **lbl_pad)
        ctk.CTkEntry(self.main_frame, textvariable=self.collection, width=300).grid(column=1, row=row, **ent_pad)
        row += 1

        # Classification
        ctk.CTkLabel(self.main_frame, text=_("Classification")).grid(column=0, row=row, **lbl_pad)
        ctk.CTkEntry(self.main_frame, textvariable=self.classification, width=300).grid(column=1, row=row, **ent_pad)
        row += 1
        # Subfamily
        ctk.CTkLabel(self.main_frame, text=_("Subfamily")).grid(column=0, row=row, **lbl_pad)
        ctk.CTkEntry(self.main_frame, textvariable=self.subfamily, width=300).grid(column=1, row=row, **ent_pad)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _highlight_field(self, field_key, error=True):
        """Highlight or unhighlight a required field"""
        if field_key not in self.required_fields:
            return
        field, label = self.required_fields[field_key]
        if error:
            label.configure(text_color="red")
        else:
            label.configure(text_color="white")

    def validate_input(self):
        """Validate required fields with visual feedback"""
        # Reset all highlights
        for key in self.required_fields:
            self._highlight_field(key, False)
        
        # Check perfume name
        if not self.perfume.get().strip():
            self._highlight_field('perfume', True)
            msg.showerror(_("Error"), _("Please enter a perfume name."), parent=self)
            return False

        # Check gender
        if not self.gender.get().strip():
            self._highlight_field('gender', True)
            msg.showerror(_("Error"), _("Please select a gender."), parent=self)
            return False

        # Check intensity
        if not self.intensity.get().strip():
            self._highlight_field('intensity', True)
            msg.showerror(_("Error"), _("Please select an intensity."), parent=self)
            return False

        return True

    def get_ingredients(self):
        """Get ingredients text from ScrolledText widget"""
        return self.txt_ingredients.get("1.0", "end-1c").strip()

    def set_ingredients(self, text):
        """Set ingredients text in ScrolledText widget"""
        self.txt_ingredients.delete("1.0", "end")
        self.txt_ingredients.insert("1.0", text)

    def get_concept(self):
        """Get concept text from ScrolledText widget"""
        return self.txt_concept.get("1.0", "end-1c").strip()

    def set_concept(self, text):
        """Set concept text in ScrolledText widget"""
        self.txt_concept.delete("1.0", "end")
        self.txt_concept.insert("1.0", text)

    def _get_bg_color(self):
        """Get background color based on current theme"""
        if ctk.get_appearance_mode() == "Dark":
            return "#212121"
        return "#f0f0f0"

    def _center_on_parent(self, parent):
        try:
            self.update_idletasks()
            if parent is not None and parent.winfo_ismapped():
                px = parent.winfo_rootx()
                py = parent.winfo_rooty()
                pw = parent.winfo_width()
                ph = parent.winfo_height()
                sw = self.winfo_width()
                sh = self.winfo_height()
                x = px + (pw - sw) // 2
                y = py + (ph - sh) // 2
            else:
                sw = self.winfo_screenwidth()
                sh = self.winfo_screenheight()
                ww = self.winfo_width()
                wh = self.winfo_height()
                x = (sw - ww) // 2
                y = (sh - wh) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _on_close(self):
        try:
            self.grab_release()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass
