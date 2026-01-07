import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import font as tkfont
import customtkinter as ctk

from ListPerfumes import ListPerfumes
from perfume_db import PerfumeDatabase
from i18n import _, toggle_lang, get_toggle_label, translate_list

# Set CustomTkinter appearance
ctk.set_appearance_mode("system")  # Modes: system, light, dark
ctk.set_default_color_theme("green")  # Themes: blue, dark-blue, green


# ----------------------------
# Matching and data helpers
# ----------------------------

def _safe_value(value, fallback):
    return value if (value is not None and str(value).strip()) else fallback


def _split_notes(notes_text):
    if not notes_text:
        return []
    return [n.strip() for n in str(notes_text).split(",") if n.strip()]


def parse_selected_notes(notes_input):
    """Parse comma-separated notes input into list of individual notes"""
    if not notes_input or not notes_input.strip():
        return []
    return [n.strip() for n in notes_input.split(",") if n.strip()]


def matches_notes(perfume_notes, selected_notes, strict=True):
    """Check if perfume notes match selected notes.
    strict=True: ALL selected notes must be in perfume notes
    strict=False: AT LEAST ONE selected note must be in perfume notes
    """
    if not selected_notes:
        return True
    
    perfume_notes_lower = [n.lower() for n in perfume_notes]
    
    if strict:
        # All selected notes must be present
        for note in selected_notes:
            if not any(note.lower() in pn for pn in perfume_notes_lower):
                return False
        return True
    else:
        # At least one selected note must be present
        for note in selected_notes:
            if any(note.lower() in pn for pn in perfume_notes_lower):
                return True
        return False


def match_score(prod, profile, notes_selected, strict_notes=True):
    """Calculate match score using Java-style logic.
    Returns: (tier, score, total) or None if filtered out
    tier 1 = exact match (all filters match)
    tier 2 = close match (2+ out of 3 non-Any filters match)
    tier 3 = loose match with notes
    tier 4 = very loose
    """
    score = 0
    total = 0
    filters_checked = []

    # Check each basic filter
    if profile["gender"] != "Any":
        filters_checked.append("gender")
        total += 1
        if profile["gender"] == "Unisex" or prod["gender"] == "Unisex" or prod["gender"] == profile["gender"]:
            score += 1

    if profile["intensity"] != "Any":
        filters_checked.append("intensity")
        total += 1
        if prod["intensity"] == profile["intensity"]:
            score += 1

    if profile["season"] != "Any":
        filters_checked.append("season")
        total += 1
        if prod["season"] == profile["season"]:
            score += 1

    if profile["concept"] != "Any":
        filters_checked.append("concept")
        total += 1
        if prod["concept"] == profile["concept"]:
            score += 1

    if profile["longevity"] != "Any":
        filters_checked.append("longevity")
        total += 1
        if prod["longevity"] == profile["longevity"]:
            score += 1

    # Check notes matching
    notes_match = matches_notes(prod["notes"], notes_selected, strict=strict_notes)
    if not notes_match:
        return None

    # Determine tier based on score
    total = total or 1
    match_pct = int((score / total) * 100)
    
    if match_pct == 100:
        tier = 1  # Exact match
    elif score >= 2 or match_pct >= 67:
        tier = 2  # Close match (at least 2 out of 3)
    else:
        tier = 3  # Loose match
    
    return tier, score, total, match_pct


def filter_rank_products(profile, notes_input, sort_mode, products, strict_notes=True):
    """Filter and rank products using Java-style matching logic."""
    notes_selected = parse_selected_notes(notes_input)
    scored = []
    
    for p in products:
        ms = match_score(p, profile, notes_selected, strict_notes=strict_notes)
        if ms is None:
            continue
        tier, score, total, match_pct = ms
        scored.append({**p, "match": match_pct, "_score": score, "_tier": tier})

    # Sort by tier first, then by score
    if sort_mode == _("Best match"):
        scored.sort(key=lambda x: (x["_tier"], -x["_score"]))
    elif sort_mode == _("Name A-Z"):
        scored.sort(key=lambda x: x["name"])
    elif sort_mode == _("Name Z-A"):
        scored.sort(key=lambda x: x["name"], reverse=True)

    return scored


class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, container):
        super().__init__(container, fg_color="transparent")
        self.inner = self  # For compatibility with existing code


class MultiSelectCheckbox(ctk.CTkFrame):
    """Multi-select widget using checkboxes, similar to radiobuttons in layout"""
    def __init__(self, parent, options=None):
        super().__init__(parent, fg_color="transparent")
        self.var_dict = {}  # {option: BooleanVar}
        self.options = options or []
        self.build_ui()
    
    def build_ui(self):
        """Build checkbox layout"""
        for option in self.options:
            var = tk.BooleanVar(value=False)
            self.var_dict[option] = var
            cb = ctk.CTkCheckBox(self, text=option, variable=var)
            cb.pack(anchor="w", pady=2)
    
    def set_options(self, options):
        """Update available options and rebuild checkboxes"""
        # Clear existing checkboxes
        for widget in self.winfo_children():
            widget.destroy()
        
        # Store current selections
        current_selections = self.get_selected()
        
        self.var_dict.clear()
        self.options = options
        self.build_ui()
        
        # Restore previous selections if they still exist in new options
        for selection in current_selections:
            if selection in self.var_dict:
                self.var_dict[selection].set(True)
    
    def get_selected(self):
        """Return list of selected options"""
        return [opt for opt, var in self.var_dict.items() if var.get()]
    
    def clear_selection(self):
        """Deselect all options"""
        for var in self.var_dict.values():
            var.set(False)

# ----------------------------
# Main Window (Filters)
# ----------------------------
root = ctk.CTk()
root.title(_("Perfume Recommender"))
root.geometry("560x760")

db = PerfumeDatabase()

# Shared Treeview style with borders on all rows/headers
tv_style = ttk.Style()
tv_style.configure(
    "Grid.Treeview",
    bordercolor="#c5c5c5",
    borderwidth=1,
    relief="solid",
)
tv_style.configure(
    "Grid.Treeview.Heading",
    bordercolor="#c5c5c5",
    borderwidth=1,
    relief="solid",
)
tv_style.layout(
    "Grid.Treeview",
    [
        (
            "Treeview.border",
            {
                "sticky": "nswe",
                "children": [
                    (
                        "Treeview.padding",
                        {
                            "sticky": "nswe",
                            "children": [("Treeview.treearea", {"sticky": "nswe"})],
                        },
                    )
                ],
            },
        )
    ],
)
tv_style.layout("Grid.Treeview.Heading", tv_style.layout("Treeview.Heading"))


def load_products_from_db():
    products = []
    try:
        rows = db.get_perfumes()
    except Exception:
        rows = []

    for row in rows:
        (
            _pid,
            perfume,
            gender,
            intensity,
            ingredients_notes,
            collection,
            season,
            concept,
            classification,
            longevity,
        ) = row

        notes_list = _split_notes(ingredients_notes)
        desc_parts = []
        if collection:
            desc_parts.append(str(collection))
        if classification:
            desc_parts.append(str(classification))
        if notes_list:
            desc_parts.append(", ".join(notes_list[:4]))
        desc_text = " - ".join(desc_parts) if desc_parts else str(perfume)

        products.append(
            {
                "id": _pid,
                "name": _safe_value(perfume, "Unnamed"),
                "gender": _safe_value(gender, "Unisex"),
                "intensity": _safe_value(intensity, "Moderate"),
                "notes": notes_list,
                "season": _safe_value(season, "Summer"),
                "concept": _safe_value(concept, "Daily"),
                "classification": _safe_value(classification, "Fresh"),
                "longevity": _safe_value(longevity, "Moderate"),
                "collection": _safe_value(collection, ""),
                "desc": _safe_value(desc_text, ""),
            }
        )

    return products

# Create menu bar
menubar = tk.Menu(root)
root.configure(menu=menubar)

TITLE_FONT = ("Arial", 18, "bold")
H2_FONT = ("Arial", 13, "bold")
TEXT_FONT = ("Arial", 11)

top_bar = ctk.CTkFrame(root, fg_color="transparent")
top_bar.pack(fill="x")

title_label = ctk.CTkLabel(top_bar, text=_("Perfume Recommender"), font=("Arial", 20, "bold"))
title_label.pack(side="left", padx=(12, 6), pady=(12, 6))

lang_btn = ctk.CTkButton(top_bar, text=get_toggle_label(), width=100)
lang_btn.pack(side="right", padx=12, pady=12)

subtitle = ctk.CTkLabel(
    root,
    text=_("Browse and filter perfumes. Use the sidebar to narrow results."),
    font=TEXT_FONT,
    text_color="gray"
)
subtitle.pack(pady=(0, 18))
# ----------------------------
# Browse & filters (main window)
# ----------------------------

root.geometry("1120x690")

# Filter option sets (logic uses English values)
gender_values = ["Any", "Woman", "Man", "Unisex"]
intensity_values = ["Any", "Light", "Moderate", "Intense"]
season_values = ["Any", "Summer", "Winter", "Spring", "Autumn"]
concept_values = ["Any", "Daily", "Office", "Night Out", "Sport"]
classification_values = ["Any", "Fresh", "Floral", "Woody", "Gourmand", "Powdery", "Spicy"]
longevity_values = ["Any", "Short", "Moderate", "Long"]


def value_index(values, target, fallback=0):
    try:
        return values.index(target)
    except ValueError:
        return fallback


main_container = ctk.CTkFrame(root, fg_color="transparent")
main_container.pack(fill="both", expand=True)
main_container.columnconfigure(0, weight=0)
main_container.columnconfigure(1, weight=1)
main_container.rowconfigure(0, weight=1)

sidebar = ctk.CTkFrame(main_container, width=240, corner_radius=10)
sidebar.grid(row=0, column=0, sticky="nsw", padx=(10, 5), pady=10)
sidebar.columnconfigure(0, weight=1)
sidebar.grid_propagate(False)

filters_title = ctk.CTkLabel(sidebar, text=_("Filters"), font=("Arial", 16, "bold"))
filters_title.grid(row=0, column=0, sticky="w", pady=(0, 10), padx=10)


def add_filter(r, label, values, default_idx):
    lbl = ctk.CTkLabel(sidebar, text=_(label), anchor="w")
    lbl.grid(row=r, column=0, sticky="w", pady=(10, 2), padx=10)
    var = tk.StringVar()
    translated = translate_list(values)
    cb = ctk.CTkComboBox(sidebar, variable=var, state="readonly", values=translated, width=200)
    cb.set(translated[default_idx])
    cb.grid(row=r + 1, column=0, sticky="ew", padx=10)
    return {"label": lbl, "combo": cb, "values": values, "default": default_idx}


gender_filter = add_filter(1, "Gender", gender_values, 0)
intensity_filter = add_filter(3, "Intensity", intensity_values, 0)
season_filter = add_filter(5, "Season", season_values, 0)
concept_filter = add_filter(7, "Concept", concept_values, 0)
longevity_filter = add_filter(9, "Longevity", longevity_values, 0)

# Create frame for notes checkboxes with scrollbar
notes_frame = ctk.CTkScrollableFrame(sidebar, height=120, fg_color="transparent")
notes_frame.grid(row=11, column=0, sticky="ew", pady=(10, 10), padx=10)
notes_frame.columnconfigure(0, weight=1)

notes_inner = notes_frame  # For compatibility

# Notes multi-select widget will be populated after functions are defined
notes_widget = MultiSelectCheckbox(notes_inner, options=[])
notes_widget.pack(fill="both", expand=True)

content = ctk.CTkFrame(main_container, corner_radius=10)
content.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
content.columnconfigure(0, weight=1)
content.rowconfigure(4, weight=1)

header = ctk.CTkFrame(content, fg_color="transparent")
header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 0))
header.columnconfigure(0, weight=1)
header.columnconfigure(1, weight=0)
header_title = ctk.CTkLabel(header, text=_("Perfume Recommender"), font=("Arial", 18, "bold"))
header_title.grid(row=0, column=0, sticky="w")
db_header_btn = ctk.CTkButton(header, text=_("Open Perfume DB"), width=140)
db_header_btn.grid(row=0, column=1, sticky="e", padx=(10, 0))

controls = ctk.CTkFrame(content, fg_color="transparent")
controls.grid(row=1, column=0, sticky="ew", pady=(10, 6), padx=16)
controls.columnconfigure(0, weight=1)

global_search_var = tk.StringVar()
placeholder = _("Search")
global_search_entry = ctk.CTkEntry(controls, textvariable=global_search_var, placeholder_text=placeholder)
global_search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

sort_var = tk.StringVar(value=_("Best match"))
sort_cb = ctk.CTkComboBox(
    controls,
    variable=sort_var,
    state="readonly",
    width=140,
    values=(_("Best match"), _("Name A-Z"), _("Name Z-A")),
)
sort_cb.grid(row=0, column=1, sticky="e")

progress = ctk.CTkProgressBar(controls, mode="indeterminate")
progress.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
progress.grid_remove()

chips_row = ctk.CTkFrame(content, fg_color="transparent")
chips_row.grid(row=2, column=0, sticky="w", pady=(0, 10), padx=16)
chips_label = ctk.CTkLabel(chips_row, text="", text_color="gray")
chips_label.pack(anchor="w")

cards_area = ScrollableFrame(content)
cards_area.grid(row=4, column=0, sticky="nsew", padx=16)

info_lbl = ctk.CTkLabel(content, text="", text_color="gray")
info_lbl.grid(row=5, column=0, sticky="w", pady=(10, 0), padx=16)


def clear_cards():
    for w in cards_area.inner.winfo_children():
        w.destroy()


def get_filter_value(filter_obj):
    val = filter_obj["combo"].get()
    # Translate back to English
    translated = translate_list(filter_obj["values"])
    try:
        idx = translated.index(val)
        return filter_obj["values"][idx]
    except (ValueError, IndexError):
        return filter_obj["values"][filter_obj["default"]]


def build_profile():
    return {
        "gender": get_filter_value(gender_filter),
        "intensity": get_filter_value(intensity_filter),
        "season": get_filter_value(season_filter),
        "concept": get_filter_value(concept_filter),
        "longevity": get_filter_value(longevity_filter),
    }


def has_active_filters(profile, notes_query):
    """Check if any filter is active (not 'Any') or notes keyword is entered"""
    if notes_query and notes_query.strip():
        return True
    for key, value in profile.items():
        if value != "Any":
            return True
    return False


def get_unique_notes_from_products(products):
    """Extract all unique notes from a list of products"""
    unique_notes = set()
    for p in products:
        for note in p.get("notes", []):
            if note:
                unique_notes.add(note)
    return sorted(list(unique_notes))


def group_by_match_percentage(items):
    """Group items by match percentage, return sorted list of (percentage, items) tuples"""
    from collections import defaultdict
    groups = defaultdict(list)
    for item in items:
        match_pct = item.get("match", 0)
        if match_pct > 0:  # Exclude 0% matches
            groups[match_pct].append(item)
    # Sort by percentage descending
    return sorted(groups.items(), key=lambda x: x[0], reverse=True)


def show_product_popup(product):
    win = ctk.CTkToplevel(root)
    win.withdraw()
    win.title(product["name"])
    win.geometry("900x340")
    win.resizable(False, False)  # Prevent window expansion
    try:
        win.transient(root)
    except Exception:
        pass

    ctk.CTkLabel(win, text=product["name"], font=("Arial", 16, "bold")).pack(anchor="w", padx=16, pady=(12, 4))
    ctk.CTkLabel(win, text=f"{_('Match')}: {product['match']}%", text_color="gray").pack(anchor="w", padx=16)

    # Pull full DB row so we can mirror the Perfume DB table layout
    detail_row = None
    try:
        if "id" in product:
            detail_row = db.get_perfume_details(product["id"])
    except Exception:
        detail_row = None

    # Pivot table: rows become field/value pairs for easier reading
    columns = ("field", "value")
    table_frame = ctk.CTkFrame(win)
    table_frame.pack(fill="both", expand=True, padx=12, pady=(8, 6))

    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14, style="Grid.Treeview")
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.heading("field", text=_("Field"), anchor="w")
    tree.heading("value", text=_("Value"), anchor="w")
    tree.column("field", width=150, anchor="w", stretch=False)
    tree.column("value", width=680, anchor="w", stretch=True)

    display_map = {
        "id": _("ID"),
        "perfume": _("Perfume Name"),
        "gender": _("Gender"),
        "intensity": _("Intensity"),
        "ingredients": _("Ingredients/Notes"),
        "collection": _("Collection"),
        "season": _("Season"),
        "concept": _("Concept"),
        "classification": _("Classification"),
        "longevity": _("Longevity"),
        "subfamily": _("Subfamily"),
    }

    def translate_compound_value(text):
        """Translate compound text by translating individual words"""
        if not text:
            return text
        import re
        words = re.split(r'(\s+|/|-|,|\(|\))', str(text))
        translated_words = []
        for word in words:
            if word.strip() and word not in (' ', '/', '-', ',', '(', ')'):
                translated_words.append(_(word))
            else:
                translated_words.append(word)
        return ''.join(translated_words)

    def build_rows():
        def _str(val):
            return "" if val is None else str(val)
        
        def _translate_val(val):
            """Translate categorical values"""
            if val is None or val == "":
                return ""
            return _(str(val))

        if detail_row:
            # detail_row layout: (id, perfume, gender, intensity, ingredients_notes, season, concept, longevity, collection, classification, subfamily)
            return [
                (display_map["id"], _str(detail_row[0])),
                (display_map["perfume"], _str(detail_row[1])),
                (display_map["gender"], _translate_val(detail_row[2])),
                (display_map["intensity"], _translate_val(detail_row[3])),
                (display_map["ingredients"], translate_compound_value(detail_row[4])),
                (display_map["collection"], _str(detail_row[8])),
                (display_map["season"], translate_compound_value(detail_row[5])),
                (display_map["concept"], translate_compound_value(detail_row[6])),
                (display_map["classification"], translate_compound_value(detail_row[9])),
                (display_map["longevity"], _translate_val(detail_row[7])),
                (display_map["subfamily"], _str(detail_row[10]) if len(detail_row) > 10 else ""),
            ]

        # Fallback to in-memory card data
        return [
            (display_map["id"], _str(product.get("id", "-"))),
            (display_map["perfume"], _str(product.get("name", ""))),
            (display_map["gender"], _translate_val(product.get("gender", ""))),
            (display_map["intensity"], _translate_val(product.get("intensity", ""))),
            (display_map["ingredients"], translate_compound_value(", ".join(product.get("notes", [])))),
            (display_map["collection"], _str(product.get("collection", ""))),
            (display_map["season"], translate_compound_value(product.get("season", ""))),
            (display_map["concept"], translate_compound_value(product.get("concept", ""))),
            (display_map["classification"], translate_compound_value(product.get("classification", ""))),
            (display_map["longevity"], _translate_val(product.get("longevity", ""))),
        ]

    for row in build_rows():
        tree.insert("", "end", values=row)

    # Auto-size value column to fit content/heading, capped to window width
    try:
        font = tkfont.nametofont(tree.cget("font"))
        pad = 24
        max_w = 1000
        max_px = font.measure(tree.heading("value")["text"]) + pad
        for item in tree.get_children(""):
            text = str(tree.set(item, "value"))
            max_px = max(max_px, font.measure(text) + pad)
        max_px = min(max_px, max_w)
        tree.column("value", width=max_px)
    except Exception:
        pass

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkButton(win, text=_("Close"), command=win.destroy).pack(pady=(6, 10))
    
    win.deiconify()  # Show window after everything is built


def _render_cards_real(tiers_to_show=1, strict_notes=True):
    progress.set(1)  # Set to complete
    progress.grid_remove()

    clear_cards()
    profile = build_profile()

    # Get selected notes from checkbox widget
    selected_notes = notes_widget.get_selected()
    fnotes = ", ".join(selected_notes) if selected_notes else ""
    
    # Check if user has active filters
    filters_active = has_active_filters(profile, fnotes)

    gq_raw = global_search_var.get().strip()
    gq = gq_raw.lower()
    if gq == placeholder.lower():
        gq = ""
        gq_raw = ""

    chips_label.configure(text="")

    products = load_products_from_db()
    if not products:
        info_lbl.configure(text=_("No data in database"))
        empty = ctk.CTkFrame(cards_area.inner, corner_radius=10)
        empty.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        ctk.CTkLabel(empty, text=_("No data in database"), font=("Arial", 13, "bold")).pack(anchor="w", padx=18, pady=18)
        return

    items = filter_rank_products(profile, fnotes, sort_var.get(), products, strict_notes=strict_notes)

    if gq:
        items = [p for p in items if (gq in p["name"].lower() or gq in p["desc"].lower())]

    info_lbl.configure(text=f"{len(items)} {_('products found')} • {_('Sorted by')} {sort_var.get()}")

    if not items:
        empty = ctk.CTkFrame(cards_area.inner, fg_color="#f0f0f0", corner_radius=10)
        empty.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        ctk.CTkLabel(empty, text=_("No matches found. Please select different preferences."), font=("Arial", 13, "bold")).pack(anchor="w", padx=18, pady=18)
        return

    cols = 2
    for i in range(cols):
        cards_area.inner.columnconfigure(i, weight=1, minsize=410)
    
    # Make inner frame fill canvas width
    cards_area.inner.grid_rowconfigure(0, weight=0)
    cards_area.inner.grid_columnconfigure(0, weight=1)
    cards_area.inner.grid_columnconfigure(1, weight=1)

    # Tier-based filtering when filters are active
    if filters_active:
        # Group by match percentage and exclude 0%
        tiers = group_by_match_percentage(items)
        if not tiers:
            empty = ctk.CTkFrame(cards_area.inner, corner_radius=10)
            empty.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
            ctk.CTkLabel(empty, text=_("No matches found. Please select different preferences."), font=("Arial", 13, "bold")).pack(anchor="w", padx=18, pady=18)
            return
        
        # Show tiers up to tiers_to_show
        items_to_show = []
        for tier_idx, (match_pct, tier_items) in enumerate(tiers):
            if tier_idx < tiers_to_show:
                items_to_show.extend(tier_items)
        
        total_tiers = len(tiers)
        has_more_tiers = tiers_to_show < total_tiers
    else:
        items_to_show = items  # Browse all mode: show everything
        has_more_tiers = False
        total_tiers = 0

    for idx, p in enumerate(items_to_show):
        r = idx // cols
        c = idx % cols

        card = ctk.CTkFrame(cards_area.inner, corner_radius=10, border_width=1)
        card.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=p["name"], font=("Arial", 13, "bold"), anchor="w").grid(row=0, column=0, sticky="w", padx=13, pady=(13, 2))
        ctk.CTkLabel(card, text=f"{_('Match')}: {p['match']}%", text_color="gray", font=("Arial", 10), anchor="w").grid(row=1, column=0, sticky="w", padx=13, pady=(2, 4))

        ctk.CTkLabel(card, text=p["desc"], wraplength=340, justify="left", font=("Arial", 10), anchor="w").grid(row=2, column=0, sticky="ew", padx=13)

        notes_text = ", ".join(p["notes"])
        ctk.CTkLabel(card, text=f"{_('Notes')}: {notes_text}", text_color="gray", wraplength=340, justify="left", font=("Arial", 9), anchor="w").grid(row=3, column=0, sticky="ew", padx=13, pady=(4, 0))

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=4, column=0, sticky="w", padx=13, pady=(8, 13))
        ctk.CTkButton(btns, text=_("View"), command=lambda prod=p: show_product_popup(prod), width=80).pack(side="left")

    # Show buttons when filters are active
    if filters_active:
        row_btn = (len(items_to_show) + cols - 1) // cols
        buttons_frame = ctk.CTkFrame(cards_area.inner, fg_color="transparent")
        buttons_frame.grid(row=row_btn, column=0, columnspan=cols, sticky="ew", padx=6, pady=(4, 10))
        
        # Show similar button (for loose note matching) if strict mode and notes were selected
        if strict_notes and fnotes.strip():
            ctk.CTkButton(buttons_frame, text=_("Show similar"), 
                      command=lambda: render_cards(tiers_to_show=1, strict_notes=False), width=120).pack(side="left", padx=5)
        
        # Show more button (for next tier) if there are more tiers
        if has_more_tiers:
            next_tier_count = tiers_to_show + 1
            ctk.CTkButton(buttons_frame, text=_("Show more"), 
                      command=lambda: render_cards(tiers_to_show=next_tier_count, strict_notes=strict_notes), width=120).pack(side="left", padx=5)


def render_cards(tiers_to_show=1, strict_notes=True):
    progress.grid()
    progress.set(0)  # Reset progress bar
    root.after(350, lambda: _render_cards_real(tiers_to_show, strict_notes))


def reset_filters():
    notes_widget.clear_selection()  # Clear checkbox selections
    global_search_var.set("")

    # Reset comboboxes to their defaults
    for filt in [gender_filter, intensity_filter, season_filter, concept_filter, longevity_filter]:
        translated = translate_list(filt["values"])
        filt["combo"].set(translated[filt["default"]])
    render_cards()


side_btns = ctk.CTkFrame(sidebar, fg_color="transparent")
side_btns.grid(row=30, column=0, sticky="ew", pady=(16, 0), padx=10)
side_btns.columnconfigure(0, weight=1)
side_btns.columnconfigure(1, weight=1)

reset_btn = ctk.CTkButton(side_btns, text=_("Reset"), command=reset_filters)
reset_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
apply_btn = ctk.CTkButton(side_btns, text=_("Apply Filters"), command=render_cards)
apply_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))

sort_cb.bind("<<ComboboxSelected>>", lambda e: render_cards())
global_search_entry.bind("<Return>", lambda e: render_cards())

# Populate notes widget with all available notes
all_products = load_products_from_db()
all_notes = get_unique_notes_from_products(all_products)
notes_widget.set_options(all_notes)

# Bind mousewheel to root and check if mouse is over cards area
def _on_root_mousewheel(event):
    # Get canvas position in root window
    try:
        canvas_x = cards_area.canvas.winfo_rootx()
        canvas_y = cards_area.canvas.winfo_rooty()
        canvas_width = cards_area.canvas.winfo_width()
        canvas_height = cards_area.canvas.winfo_height()
        
        # Check if mouse is within canvas bounds
        if (canvas_x <= event.x_root <= canvas_x + canvas_width and
            canvas_y <= event.y_root <= canvas_y + canvas_height):
            if event.delta > 0:
                cards_area.canvas.yview_scroll(-3, "units")
            else:
                cards_area.canvas.yview_scroll(3, "units")
    except Exception:
        pass

root.bind("<MouseWheel>", _on_root_mousewheel)
root.bind("<Button-4>", lambda e: cards_area.canvas.yview_scroll(-1, "units") if _is_mouse_over_canvas() else None)
root.bind("<Button-5>", lambda e: cards_area.canvas.yview_scroll(1, "units") if _is_mouse_over_canvas() else None)

def _is_mouse_over_canvas():
    try:
        canvas_x = cards_area.canvas.winfo_rootx()
        canvas_y = cards_area.canvas.winfo_rooty()
        canvas_width = cards_area.canvas.winfo_width()
        canvas_height = cards_area.canvas.winfo_height()
        root_x = root.winfo_pointerx()
        root_y = root.winfo_pointery()
        return (canvas_x <= root_x <= canvas_x + canvas_width and
                canvas_y <= root_y <= canvas_y + canvas_height)
    except Exception:
        return False

render_cards()



def open_database():
    db_window = ListPerfumes(root, db=db)
    db_window.grab_set()


db_header_btn.configure(command=open_database)

def update_ui():
    root.title(_("Perfume Recommender"))
    title_label.configure(text=_("Perfume Recommender"))
    subtitle.configure(text=_("Browse and filter perfumes. Use the sidebar to narrow results."))
    filters_title.configure(text=_("Filters"))
    header_title.configure(text=_("Perfume Recommender"))
    db_header_btn.configure(text=_("Open Perfume DB"))
    reset_btn.configure(text=_("Reset"))
    apply_btn.configure(text=_("Apply Filters"))
    # Update combo labels and values with translations
    for filt, label_key in [
        (gender_filter, "Gender"),
        (intensity_filter, "Intensity"),
        (season_filter, "Season"),
        (concept_filter, "Concept"),
        (longevity_filter, "Longevity"),
    ]:
        filt["label"].configure(text=_(label_key))
        # CTkComboBox doesn't support .current(); use value-based selection
        try:
            current_values = filt["combo"].cget("values")
        except Exception:
            current_values = []
        current_value = None
        try:
            current_value = filt["combo"].get()
        except Exception:
            current_value = None
        if current_value in current_values:
            idx = current_values.index(current_value)
        else:
            idx = 0
        translated_values = translate_list(filt["values"])
        try:
            # Set new values list for CTkComboBox
            filt["combo"].configure(values=translated_values)
        except Exception:
            # Fallback to mapping-style if available
            try:
                filt["combo"]["values"] = translated_values
            except Exception:
                pass
        if 0 <= idx < len(translated_values):
            try:
                filt["combo"].set(translated_values[idx])
            except Exception:
                pass
    global placeholder
    old_placeholder = placeholder
    placeholder = _("Search")
    if global_search_var.get() in (old_placeholder, old_placeholder.lower()):
        global_search_entry.delete(0, tk.END)
        global_search_entry.insert(0, placeholder)
    lang_btn.configure(text=get_toggle_label())
    # Re-render cards to update "View" button text and product details
    _render_cards_real()


def on_toggle_lang():
    toggle_lang()
    update_ui()


lang_btn.configure(command=on_toggle_lang)


def show_help():
    """Display help information"""
    help_text = _("""
Perfume Recommender Application Help

Instructions:
1. Use the left sidebar filters (gender, intensity, season, concept, longevity) to refine results.
2. Click "Show Relevant Notes" button to see notes matching your current filters. Check boxes for multiple notes.
3. "Apply Filters" shows exact matches. Use "Show similar" to see perfumes with at least one matching note.
4. "Show more" reveals additional match tiers. Use the top search box and sort options as needed.
5. Click a card's View button to see details, or "Open Perfume DB" to manage the database.

Keyboard Shortcuts (database window):
• Ctrl+I: Add new perfume
• Double-click: Edit perfume
• Delete: Remove perfume
• F1: Show help
• F2: Show statistics

Features:
• Browse all perfumes with filtering and sorting
• Search by name/description and notes keyword
• View detailed perfume info
• Manage the database (add, edit, delete)
• Toggle between English and Turkish
    """)
    messagebox.showinfo(_("Help"), help_text, parent=root)


# Menu bar callbacks
def menu_toggle_lang():
    on_toggle_lang()

def menu_open_db():
    open_database()

def menu_show_help():
    show_help()

# Language menu
lang_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label=_("Language"), menu=lang_menu)
lang_menu.add_command(label="Türkçe", command=menu_toggle_lang)

# Database menu
db_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label=_("Database"), menu=db_menu)
db_menu.add_command(label=_("Open Perfume DB"), command=menu_open_db)

root.mainloop()
