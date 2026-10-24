from tkinter import messagebox as msg
import customtkinter as ctk
from PerfumeFormWindow import PerfumeFormWindow
import sqlite3
from i18n import _
from infrastructure.repository_protocol import PerfumeRepositoryProtocol


class EditPerfume(PerfumeFormWindow):
    """Window for editing an existing perfume"""
    
    def __init__(
        self,
        parent,
        perfume_data,
        db: PerfumeRepositoryProtocol | None = None,
    ):
        """
        Initialize edit window with existing perfume data
        perfume_data is a tuple from the database with all fields
        """
        self.perfume_id = perfume_data[0]
        super().__init__(parent, _("Edit Perfume"), db=db)
        
        # Populate fields with existing data
        self.perfume.set(perfume_data[1])
        self.gender.set(perfume_data[2])
        self.intensity.set(perfume_data[3])
        self.set_ingredients(perfume_data[4] or "")
        self.season.set(perfume_data[5] or "")
        self.set_concept(perfume_data[6] or "")
        self.longevity.set(perfume_data[7] or "")
        self.collection.set(perfume_data[8] or "")
        self.classification.set(perfume_data[9] or "")
        self.subfamily.set(perfume_data[10] or "")

    def build_ui(self):
        super().build_ui()
        # Add Update button
        self.btn_update = ctk.CTkButton(self, text=_("Update Perfume"), command=self.update_perfume)
        self.btn_update.pack(side="bottom", pady=10, padx=10)

    def update_perfume(self):
        """Update perfume in database"""
        if not self.validate_input():
            return

        try:
            self.db.update_perfume(
                perfume_id=self.perfume_id,
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
            msg.showinfo(_("Success"), _("Perfume updated successfully!"), parent=self)
            # Fire custom event to notify listeners
            self.event_generate("<<PerfumeUpdated>>")
            self.destroy()  # Close window after success
        except sqlite3.Error as e:
            msg.showerror(_("Database Error"), f"Database error occurred: {e}", parent=self)
