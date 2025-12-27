import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
import AddNewPerfume
import EditPerfume
from perfume_db import PerfumeDatabase
from i18n import _, toggle_lang, get_toggle_label
from datetime import datetime
import locale


class ListPerfumes(tk.Toplevel):
    """Child window for displaying perfumes in a Treeview"""

    def __init__(self, parent, db=None):
        super().__init__(parent)
        self.title(_("Perfume Recommendation Application"))
        self.geometry("1600x600")  # Wider window for more columns
        self.db = db or PerfumeDatabase()
        self.build_ui()
        self.list_perfumes()
        self.update_ui()

    def build_ui(self):
        """Build the user interface"""
        # Create a top toolbar frame with buttons and menus
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(fill="x", padx=10, pady=10)

        # Add button
        self.add_btn = ttk.Button(toolbar_frame, text=_("Add (Ctrl+I)"), command=self.show_add_window)
        self.add_btn.pack(side="left", padx=5)
        
        # Delete button
        self.delete_btn = ttk.Button(toolbar_frame, text=_("Delete"), command=self.delete_perfume_action)
        self.delete_btn.pack(side="left", padx=5)
        
        # Help button
        self.help_btn = ttk.Button(toolbar_frame, text=_("❕"), command=self.show_help)
        self.help_btn.pack(side="left", padx=5)
        
        # Statistics button
        self.stats_btn = ttk.Button(toolbar_frame, text=_("Statistics (F2)"), command=self.show_statistics)
        self.stats_btn.pack(side="left", padx=5)
        
        # Language toggle button (right side)
        self.lang_btn = ttk.Button(toolbar_frame, text=get_toggle_label(), command=self.on_toggle_lang)
        self.lang_btn.pack(side="right", padx=5)

        # Create a search frame below the toolbar
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.search_label = ttk.Label(search_frame, text=_("Search:"))
        self.search_label.pack(side="left", padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)

        self.clear_btn = ttk.Button(search_frame, text=_("Clear"), command=self.clear_search)
        self.clear_btn.pack(side="left", padx=5)

        # Create a container frame for Treeview and Scrollbars
        container = tk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Create a Treeview widget
        self.tv = ttk.Treeview(container, height=20, show="headings")
        self.tv["columns"] = ("id", "perfume", "gender", "intensity", "ingredients", "collection", "season", "concept", "classification", "longevity")
        self.tv["selectmode"] = "browse"

        # Create Scrollbar widgets (vertical and horizontal)
        self.tv_scroll_y = ttk.Scrollbar(container, orient="vertical", command=self.tv.yview)
        self.tv_scroll_x = ttk.Scrollbar(container, orient="horizontal", command=self.tv.xview)

        # Link Scrollbars and Treeview
        self.tv.configure(yscrollcommand=self.tv_scroll_y.set, xscrollcommand=self.tv_scroll_x.set)

        # Add headings for each column
        self.tv.heading("id", text=_("ID"), anchor="center")
        self.tv.heading("perfume", text=_("Perfume Name"), anchor="center")
        self.tv.heading("gender", text=_("Gender"), anchor="center")
        self.tv.heading("intensity", text=_("Intensity"), anchor="center")
        self.tv.heading("ingredients", text=_("Ingredients/Notes"), anchor="center")
        self.tv.heading("collection", text=_("Collection"), anchor="center")
        self.tv.heading("season", text=_("Season"), anchor="center")
        self.tv.heading("concept", text=_("Concept"), anchor="center")
        self.tv.heading("classification", text=_("Classification"), anchor="center")
        self.tv.heading("longevity", text=_("Longevity"), anchor="center")

        # Configure each column
        self.tv.column("id", anchor="center", width=40, stretch=False)
        self.tv.column("perfume", anchor="w", width=200, stretch=False)
        self.tv.column("gender", anchor="center", width=80, stretch=False)
        self.tv.column("intensity", anchor="center", width=90, stretch=False)
        self.tv.column("ingredients", anchor="w", width=250, stretch=False)
        self.tv.column("collection", anchor="w", width=150, stretch=False)
        self.tv.column("season", anchor="center", width=150, stretch=False)
        self.tv.column("concept", anchor="w", width=200, stretch=False)
        self.tv.column("classification", anchor="center", width=120, stretch=False)
        self.tv.column("longevity", anchor="center", width=100, stretch=False)

        # Use grid layout for proper scrollbar positioning
        self.tv.grid(row=0, column=0, sticky="nsew")
        self.tv_scroll_y.grid(row=0, column=1, sticky="ns")
        self.tv_scroll_x.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights so treeview expands
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Create an info label at the bottom (just count)
        self.info_label = tk.Label(self, text="", fg="gray")
        self.info_label.pack(side="bottom", pady=5)

        # Bind events
        self.tv.bind("<<TreeviewSelect>>", self.on_item_select)
        self.tv.bind("<Double-1>", self.show_edit_window)  # Double-click to edit
        self.tv.bind("<BackSpace>", self.delete_perfume)  # Delete/Backspace key to remove
        self.bind("<F1>", self.show_help)
        self.bind("<F2>", self.show_statistics)  # F2 for statistics
        self.bind("<Control-i>", self.show_add_window)  # Ctrl+I to add new

    def translate_compound_text(self, text):
        """Translate compound text by translating individual words"""
        if not text:
            return text
        # Split by common delimiters and translate each word
        import re
        words = re.split(r'(\s+|/|-|,|\(|\))', str(text))
        translated_words = []
        for word in words:
            # Skip empty strings and delimiters
            if word.strip() and word not in (' ', '/', '-', ',', '(', ')'):
                translated_words.append(_(word))
            else:
                translated_words.append(word)
        return ''.join(translated_words)

    def translate_perfume_row(self, row):
        """Translate categorical values in a perfume row"""
        # row format: (id, perfume, gender, intensity, ingredients, collection, season, concept, classification, longevity)
        translated = list(row)
        # Translate gender (index 2)
        if len(translated) > 2:
            translated[2] = _(str(translated[2])) if translated[2] else translated[2]
        # Translate intensity (index 3)
        if len(translated) > 3:
            translated[3] = _(str(translated[3])) if translated[3] else translated[3]
        # Translate ingredients (index 4) - compound text
        if len(translated) > 4:
            translated[4] = self.translate_compound_text(translated[4])
        # Translate season (index 6) - compound text
        if len(translated) > 6:
            translated[6] = self.translate_compound_text(translated[6])
        # Translate concept (index 7) - compound text
        if len(translated) > 7:
            translated[7] = self.translate_compound_text(translated[7])
        # Translate classification (index 8) - compound text
        if len(translated) > 8:
            translated[8] = self.translate_compound_text(translated[8])
        # Translate longevity (index 9)
        if len(translated) > 9:
            translated[9] = _(str(translated[9])) if translated[9] else translated[9]
        return tuple(translated)

    def list_perfumes(self, perfumes=None):
        """Populate the Treeview with perfume data"""
        # Clear existing items
        for item in self.tv.get_children():
            self.tv.delete(item)

        # Get perfumes from database if not provided
        if perfumes is None:
            perfumes = self.db.get_perfumes()

        # Add perfumes to Treeview with translated categorical values
        for perfume in perfumes:
            translated_row = self.translate_perfume_row(perfume)
            self.tv.insert(parent="", index="end", values=translated_row)

        # Update info label (just count)
        total = self.db.get_total_count()
        displayed = len(perfumes)
        self.info_label.config(text=_("Displaying {} of {} perfumes").format(displayed, total))

    def on_search_change(self, *args):
        """Called when search text changes"""
        search_term = self.search_var.get()
        if search_term:
            results = self.db.search_perfumes(search_term)
            self.list_perfumes(results)
        else:
            self.list_perfumes()

    def clear_search(self):
        """Clear the search box and show all perfumes"""
        self.search_var.set("")

    def on_item_select(self, event):
        """Called when a Treeview item is selected"""
        selected = self.tv.selection()
        if selected:
            item_id = selected[0]
            values = self.tv.item(item_id)["values"]
            print(f"Selected: {values[1]} (ID: {values[0]})")

    def show_add_window(self, event=None):
        """Show window to add a new perfume"""
        add_win = AddNewPerfume.AddNewPerfume(parent=self)
        # Listen for custom save event
        add_win.bind("<<PerfumeSaved>>", self._on_perfume_saved)

    def show_edit_window(self, event):
        """Show window to edit selected perfume"""
        # Check if the clicked region is a cell
        region = self.tv.identify("region", event.x, event.y)
        if region != "cell":
            return

        selected = self.tv.selection()
        if not selected:
            return

        selected_id = selected[0]
        values = self.tv.item(selected_id)["values"]
        perfume_id = values[0]

        # Get full details from database
        perfume_data = self.db.get_perfume_details(perfume_id)
        
        if perfume_data:
            # Open edit window
            edit_win = EditPerfume.EditPerfume(parent=self, perfume_data=perfume_data)
            # Listen for custom update event
            edit_win.bind("<<PerfumeUpdated>>", self._on_perfume_updated)

    def _on_perfume_saved(self, event):
        """Called when a perfume is saved"""
        self.list_perfumes()
        children = self.tv.get_children()
        if children:
            last_item = children[-1]
            self.tv.see(last_item)

    def _on_perfume_updated(self, event):
        """Called when a perfume is updated"""
        self.list_perfumes()
    def delete_perfume_action(self):
        """Wrapper for delete perfume button (no event)"""
        self.delete_perfume(None)

    def delete_perfume(self, event):
        """Delete selected perfume"""
        if not self.tv.selection():
            msg.showwarning(_("No Selection"), _("Please select a perfume to delete."), parent=self)
            return

        answer = msg.askyesno(title=_("Confirm Delete"), 
                     message=_("Are you sure you want to delete the selected perfume?"))
        if answer:
            for i in self.tv.selection():
                selected_row = self.tv.item(i)["values"]
                perfume_id = selected_row[0]
                # Delete from database
                self.db.delete_perfume(perfume_id)
                # Remove from treeview
                self.tv.delete(i)
            
            # Update the info label (just show count)
            total = self.db.get_total_count()
            displayed = len(self.tv.get_children())
            self.info_label.config(text=_("Displaying {} of {} perfumes").format(displayed, total))

    def show_details(self, event):
        """Show full details of selected perfume in a popup window"""
        # Check if the clicked region is a cell
        region = self.tv.identify("region", event.x, event.y)
        if region != "cell":
            return

        selected = self.tv.selection()
        if not selected:
            return

        selected_id = selected[0]
        values = self.tv.item(selected_id)["values"]
        perfume_id = values[0]

        # Get full details from database
        details = self.db.get_perfume_details(perfume_id)
        
        if details:
            self.show_perfume_details_window(details)

    def show_perfume_details_window(self, perfume_data):
        """Display perfume details in a new window"""
        # Column names from the database
        columns = ["id", "perfume", "gender", "intensity", "ingredients_notes", 
                  "season", "concept", "longevity", "collection", "classification", 
                  "subfamily"]

        # Create a new window
        details_window = tk.Toplevel(self)
        details_window.title(_("Perfume Details"))
        details_window.geometry("600x500")

        # Create a frame with scrollbar for details
        container = ttk.Frame(details_window)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(container, bg="white")
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Display perfume details
        display_map = {
            "id": _("ID"),
            "perfume": _("Perfume Name"),
            "gender": _("Gender"),
            "intensity": _("Intensity"),
            "ingredients_notes": _("Ingredients/Notes"),
            "season": _("Season"),
            "concept": _("Concept"),
            "longevity": _("Longevity"),
            "collection": _("Collection"),
            "classification": _("Classification"),
            "subfamily": _("Subfamily"),
            "sources": "sources",
        }

        for col_name, value in zip(columns, perfume_data):
            # Skip the sources column
            if col_name == "sources":
                continue
                
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill="x", padx=5, pady=5)

            disp = display_map.get(col_name, col_name.replace('_', ' ').title())
            label = ttk.Label(frame, text=f"{disp}:", 
                            font=("Arial", 10, "bold"), width=20)
            label.pack(side="left")

            value_label = ttk.Label(frame, text=str(value), wraplength=350, justify="left")
            value_label.pack(side="left", padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_statistics(self, event=None):
        """Show statistics about perfumes in the database with localized formatting"""
        stats = self.db.get_statistics()
        
        # Build statistics message with localized date
        now = datetime.now()
        # Try to format date in current language locale
        try:
            date_fmt = now.strftime("%d %B %Y")
        except:
            date_fmt = now.strftime("%Y-%m-%d")
        
        stats_text = _("PERFUME DATABASE STATISTICS\n\n")
        stats_text += f"({date_fmt})\n\n"
        stats_text += _("Total Perfumes: {}\n\n").format(stats['total'])
        
        stats_text += _("By Gender:\n")
        for gender, count in stats['gender']:
            stats_text += f"  • {gender}: {count}\n"
        
        stats_text += _("\nBy Intensity:\n")
        for intensity, count in stats['intensity']:
            stats_text += f"  • {intensity}: {count}\n"
        
        stats_text += _("\nTop 5 Classifications:\n")
        for classification, count in stats['classification']:
            stats_text += f"  • {classification}: {count}\n"
        
        msg.showinfo(_("Perfume Statistics"), stats_text)

    def show_help(self, event=None):
        """Show help information"""
        help_text = _("""
PERFUME RECOMMENDATION APPLICATION - HELP

Keyboard Shortcuts:
  • Ctrl+I: Add new perfume
  • Double-click: Edit selected perfume
  • Delete: Remove selected perfume
  • F1: Show this help message
  • F2: Show database statistics

Features:
  • View all perfumes in the database
  • Search and filter perfumes by name, gender, classification, ingredients, or season
  • Add new perfumes to the collection
  • Edit existing perfume details
  • Delete perfumes from the database
  • View statistics breakdown by gender, intensity, and classification
        """)
        msg.showinfo(_("Help"), help_text)

    def on_toggle_lang(self):
        toggle_lang()
        self.update_ui()

    def update_ui(self):
        self.title(_("Perfume Recommendation Application"))
        # Update column headings
        self.tv.heading("id", text=_("ID"))
        self.tv.heading("perfume", text=_("Perfume Name"))
        self.tv.heading("gender", text=_("Gender"))
        self.tv.heading("intensity", text=_("Intensity"))
        self.tv.heading("ingredients", text=_("Ingredients/Notes"))
        self.tv.heading("collection", text=_("Collection"))
        self.tv.heading("season", text=_("Season"))
        self.tv.heading("concept", text=_("Concept"))
        self.tv.heading("classification", text=_("Classification"))
        self.tv.heading("longevity", text=_("Longevity"))
        # Update toolbar and search labels
        self.add_btn.config(text=_("Add (Ctrl+I)"))
        self.delete_btn.config(text=_("Delete"))
        self.help_btn.config(text=_("❕"))
        self.stats_btn.config(text=_("Statistics (F2)"))
        self.search_label.config(text=_("Search:"))
        self.clear_btn.config(text=_("Clear"))
        # Update language button label
        self.lang_btn.config(text=get_toggle_label())
        # Reload the perfume list to apply translations to cell values and count label
        self.list_perfumes()