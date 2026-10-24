"""Reusable CustomTkinter widgets."""

import tkinter as tk

import customtkinter as ctk


class ScrollableFrame(ctk.CTkScrollableFrame):
    """Scrollable container retaining the legacy ``inner`` compatibility API."""

    def __init__(self, container):
        super().__init__(container, fg_color="transparent")
        self.inner = self


class MultiSelectCheckbox(ctk.CTkFrame):
    """Checkbox group used for selecting multiple perfume notes."""

    def __init__(self, parent, options=None):
        super().__init__(parent, fg_color="transparent")
        self.var_dict = {}
        self.options = options or []
        self.build_ui()

    def build_ui(self):
        for option in self.options:
            variable = tk.BooleanVar(value=False)
            self.var_dict[option] = variable
            checkbox = ctk.CTkCheckBox(self, text=option, variable=variable)
            checkbox.pack(anchor="w", pady=2)

    def set_options(self, options):
        current_selections = self.get_selected()
        for widget in self.winfo_children():
            widget.destroy()

        self.var_dict.clear()
        self.options = options
        self.build_ui()
        for selection in current_selections:
            if selection in self.var_dict:
                self.var_dict[selection].set(True)

    def get_selected(self):
        return [option for option, variable in self.var_dict.items() if variable.get()]

    def clear_selection(self):
        for variable in self.var_dict.values():
            variable.set(False)
