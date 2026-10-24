"""Filter controls used by the recommendation window."""

import tkinter as tk

import customtkinter as ctk

from i18n import _, translate_list
from ui.widgets import MultiSelectCheckbox


class FilterPanel:
    """Build and expose the recommendation filters in the left sidebar."""

    def __init__(self, parent):
        self.frame = ctk.CTkFrame(parent, width=240, corner_radius=10)
        self.frame.grid(row=0, column=0, sticky="nsw", padx=(10, 5), pady=10)
        self.frame.columnconfigure(0, weight=1)
        self.frame.grid_propagate(False)

        self.title = ctk.CTkLabel(
            self.frame,
            text=_("Filters"),
            font=("Arial", 16, "bold"),
        )
        self.title.grid(row=0, column=0, sticky="w", pady=(0, 10), padx=10)

        self.gender = self._add_filter(
            1, "Gender", ["Any", "Woman", "Man", "Unisex"], 0
        )
        self.intensity = self._add_filter(
            3, "Intensity", ["Any", "Light", "Moderate", "Intense"], 0
        )
        self.season = self._add_filter(
            5, "Season", ["Any", "Summer", "Winter", "Spring", "Autumn"], 0
        )
        self.concept = self._add_filter(
            7, "Concept", ["Any", "Daily", "Office", "Night Out", "Sport"], 0
        )
        self.longevity = self._add_filter(
            9, "Longevity", ["Any", "Short", "Moderate", "Long"], 0
        )

        notes_frame = ctk.CTkScrollableFrame(
            self.frame,
            height=120,
            fg_color="transparent",
        )
        notes_frame.grid(row=11, column=0, sticky="ew", pady=(10, 10), padx=10)
        notes_frame.columnconfigure(0, weight=1)

        self.notes = MultiSelectCheckbox(notes_frame, options=[])
        self.notes.pack(fill="both", expand=True)

    def _add_filter(self, row, label, values, default_index):
        label_widget = ctk.CTkLabel(self.frame, text=_(label), anchor="w")
        label_widget.grid(
            row=row,
            column=0,
            sticky="w",
            pady=(10, 2),
            padx=10,
        )
        variable = tk.StringVar()
        translated_values = translate_list(values)
        combo = ctk.CTkComboBox(
            self.frame,
            variable=variable,
            state="readonly",
            values=translated_values,
            width=200,
        )
        combo.set(translated_values[default_index])
        combo.grid(row=row + 1, column=0, sticky="ew", padx=10)
        return {
            "label": label_widget,
            "combo": combo,
            "values": values,
            "default": default_index,
        }

    def filters(self):
        return {
            "gender": self.gender,
            "intensity": self.intensity,
            "season": self.season,
            "concept": self.concept,
            "longevity": self.longevity,
        }
