import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
import AddNewPerfume
import EditPerfume
from perfume_db import PerfumeDatabase


class ListPerfumes(tk.Tk):
    """Main window for displaying perfumes in a Treeview"""
    
    def __init__(self):
        super().__init__()
        self.title("Perfume Recommendation Application")
        self.geometry("1600x600")  # Wider window for more columns
        self.db = PerfumeDatabase()
        self.build_ui()
        self.list_perfumes()

    def build_ui(self):
        """Build the user interface"""
        # Create a top frame for search functionality
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)

        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side="left", padx=5)

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
        self.tv.heading("id", text="ID", anchor="center")
        self.tv.heading("perfume", text="Perfume Name", anchor="center")
        self.tv.heading("gender", text="Gender", anchor="center")
        self.tv.heading("intensity", text="Intensity", anchor="center")
        self.tv.heading("ingredients", text="Ingredients/Notes", anchor="center")
        self.tv.heading("collection", text="Collection", anchor="center")
        self.tv.heading("season", text="Season", anchor="center")
        self.tv.heading("concept", text="Concept", anchor="center")
        self.tv.heading("classification", text="Classification", anchor="center")
        self.tv.heading("longevity", text="Longevity", anchor="center")

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

        # Create an info label at the bottom
        self.info_label = tk.Label(self, text="", fg="gray")
        self.info_label.pack(side="bottom", pady=5)

        # Bind events
        self.tv.bind("<<TreeviewSelect>>", self.on_item_select)
        self.tv.bind("<Double-1>", self.show_edit_window)  # Double-click to edit
        self.tv.bind("<BackSpace>", self.delete_perfume)  # Delete/Backspace key to remove
        self.bind("<F1>", self.show_help)
        self.bind("<F2>", self.show_statistics)  # F2 for statistics
        self.bind("<Control-i>", self.show_add_window)  # Ctrl+I to add new

    def list_perfumes(self, perfumes=None):
        """Populate the Treeview with perfume data"""
        # Clear existing items
        for item in self.tv.get_children():
            self.tv.delete(item)

        # Get perfumes from database if not provided
        if perfumes is None:
            perfumes = self.db.get_perfumes()

        # Add perfumes to Treeview
        for perfume in perfumes:
            self.tv.insert(parent="", index="end", values=perfume)

        # Update info label
        total = self.db.get_total_count()
        displayed = len(perfumes)
        self.info_label.config(text=f"Displaying {displayed} of {total} perfumes  |  Ctrl+I: Add  |  Double-click: Edit  |  Delete: Remove  |  F1: Help  |  F2: Stats")

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
        add_win.grab_set()
        # Wait for the add window to close
        self.wait_window(add_win)
        # Refresh the list
        self.list_perfumes()

        # Scroll to the newly added item (last item)
        children = self.tv.get_children()
        if children:
            last_item = children[-1]
            self.tv.see(last_item)

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
            edit_win.grab_set()
            # Wait for the edit window to close
            self.wait_window(edit_win)
            # Refresh the list
            self.list_perfumes()

    def delete_perfume(self, event):
        """Delete selected perfume"""
        if not self.tv.selection():
            return

        answer = msg.askyesno(title="Confirm Delete", 
                             message="Are you sure you want to delete the selected perfume?")
        if answer:
            for i in self.tv.selection():
                selected_row = self.tv.item(i)["values"]
                perfume_id = selected_row[0]
                # Delete from database
                self.db.delete_perfume(perfume_id)
                # Remove from treeview
                self.tv.delete(i)
            
            # Update the info label
            total = self.db.get_total_count()
            displayed = len(self.tv.get_children())
            self.info_label.config(text=f"Displaying {displayed} of {total} perfumes  |  Ctrl+I: Add  |  Double-click: Edit  |  Delete: Remove  |  F1: Help")

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
        details_window.title("Perfume Details")
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
        for col_name, value in zip(columns, perfume_data):
            # Skip the sources column
            if col_name == "sources":
                continue
                
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill="x", padx=5, pady=5)

            label = ttk.Label(frame, text=f"{col_name.replace('_', ' ').title()}:", 
                            font=("Arial", 10, "bold"), width=20)
            label.pack(side="left")

            value_label = ttk.Label(frame, text=str(value), wraplength=350, justify="left")
            value_label.pack(side="left", padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_statistics(self, event=None):
        """Show statistics about perfumes in the database"""
        stats = self.db.get_statistics()
        
        # Build statistics message
        stats_text = f"PERFUME DATABASE STATISTICS\n\n"
        stats_text += f"Total Perfumes: {stats['total']}\n\n"
        
        stats_text += "By Gender:\n"
        for gender, count in stats['gender']:
            stats_text += f"  • {gender}: {count}\n"
        
        stats_text += "\nBy Intensity:\n"
        for intensity, count in stats['intensity']:
            stats_text += f"  • {intensity}: {count}\n"
        
        stats_text += "\nTop 5 Classifications:\n"
        for classification, count in stats['classification']:
            stats_text += f"  • {classification}: {count}\n"
        
        msg.showinfo("Perfume Statistics", stats_text)

    def show_help(self, event=None):
        """Show help information"""
        help_text = """
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
        """
        msg.showinfo("Help", help_text)


if __name__ == "__main__":
    app = ListPerfumes()
    app.mainloop()
