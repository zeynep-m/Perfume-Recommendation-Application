from tkinter import ttk
from tkinter import messagebox as msg
from PerfumeFormWindow import PerfumeFormWindow
import sqlite3


class AddNewPerfume(PerfumeFormWindow):
    """Window for adding a new perfume"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Add New Perfume")

    def build_ui(self):
        super().build_ui()
        # Add Save button
        self.btn_save = ttk.Button(self, text="Save Perfume", command=self.save_perfume)
        self.btn_save.pack(side="bottom", pady=10, padx=10)

    def save_perfume(self):
        """Save new perfume to database"""
        if not self.validate_input():
            return

        try:
            self.db.add_perfume(
                perfume=self.perfume.get(),
                gender=self.gender.get(),
                intensity=self.intensity.get(),
                ingredients_notes=self.get_ingredients(),
                season=self.season.get(),
                concept=self.get_concept(),
                longevity=self.longevity.get(),
                collection=self.collection.get(),
                classification=self.classification.get(),
                subfamily=self.subfamily.get()
            )
            msg.showinfo("Success", "Perfume added successfully!", parent=self)
            self.destroy()  # Close window after success
        except sqlite3.Error as e:
            msg.showerror("Database Error", f"Database error occurred: {e}", parent=self)
