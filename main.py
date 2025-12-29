import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from ListPerfumes import ListPerfumes
from perfume_db import PerfumeDatabase
from i18n import _, toggle_lang, get_toggle_label, translate_list


# ----------------------------
# Matching and data helpers
# ----------------------------

def _safe_value(value, fallback):
    return value if (value is not None and str(value).strip()) else fallback


def _split_notes(notes_text):
    if not notes_text:
        return []
    return [n.strip() for n in str(notes_text).split(",") if n.strip()]


def match_score(prod, profile, name_query, notes_query):
    score = 0
    total = 0

    # Gender match (with Unisex tolerance)
    if profile["gender"] != "Any":
        total += 1
        if profile["gender"] == "Unisex" or prod["gender"] == "Unisex" or prod["gender"] == profile["gender"]:
            score += 1

    # Intensity
    if profile["intensity"] != "Any":
        total += 1
        if prod["intensity"] == profile["intensity"]:
            score += 1

    # Season
    if profile["season"] != "Any":
        total += 1
        if prod["season"] == profile["season"]:
            score += 1

    # Concept / Occasion
    if profile["concept"] != "Any":
        total += 1
        if prod["concept"] == profile["concept"]:
            score += 1

    # Classification (family)
    if profile["classification"] != "Any":
        total += 1
        if prod["classification"] == profile["classification"]:
            score += 1

    # Longevity
    if profile["longevity"] != "Any":
        total += 1
        if prod["longevity"] == profile["longevity"]:
            score += 1

    # Name query filter
    nq = (name_query or "").strip().lower()
    if nq:
        if nq not in prod["name"].lower() and nq not in prod["desc"].lower():
            return None

    # Notes query filter
    lq = (notes_query or "").strip().lower()
    if lq:
        if not any(lq in n.lower() for n in prod["notes"]):
            return None

    total = total or 1  # avoid zero division when everything is "Any"
    return score, total


def filter_rank_products(profile, name_query, notes_query, sort_mode, products):
    scored = []
    for p in products:
        ms = match_score(p, profile, name_query, notes_query)
        if ms is None:
            continue
        score, total = ms
        match_pct = int((score / total) * 100)
        scored.append({**p, "match": match_pct, "_score": score})

    if sort_mode == "Best match":
        scored.sort(key=lambda x: x["_score"], reverse=True)
    elif sort_mode == "Name A-Z":
        scored.sort(key=lambda x: x["name"])
    elif sort_mode == "Name Z-A":
        scored.sort(key=lambda x: x["name"], reverse=True)

    return scored


class ScrollableFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

# ----------------------------
# Main Window (Filters)
# ----------------------------
root = tk.Tk()
root.title(_("Perfume Recommender"))
root.geometry("560x760")

db = PerfumeDatabase()


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
                "name": _safe_value(perfume, "Unnamed"),
                "gender": _safe_value(gender, "Unisex"),
                "intensity": _safe_value(intensity, "Moderate"),
                "notes": notes_list,
                "season": _safe_value(season, "Summer"),
                "concept": _safe_value(concept, "Daily"),
                "classification": _safe_value(classification, "Fresh"),
                "longevity": _safe_value(longevity, "Moderate"),
                "desc": _safe_value(desc_text, ""),
            }
        )

    return products

# Create menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)

TITLE_FONT = ("Arial", 18, "bold")
H2_FONT = ("Arial", 13, "bold")
TEXT_FONT = ("Arial", 11)

top_bar = tk.Frame(root)
top_bar.pack(fill="x")

title_label = tk.Label(top_bar, text=_("Perfume Recommender"), font=("Arial", 20, "bold"))
title_label.pack(side="left", padx=(12, 6), pady=(12, 6))

lang_btn = ttk.Button(top_bar, text=get_toggle_label())
lang_btn.pack(side="right", padx=12, pady=12)

subtitle = tk.Label(
    root,
    text=_("Select your preferences to generate a personalized Dior profile.\nRecommendations are currently shown as a demo (mock) list."),
    font=TEXT_FONT,
    fg="gray"
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


main_container = ttk.Frame(root)
main_container.pack(fill="both", expand=True)
main_container.columnconfigure(0, weight=0)
main_container.columnconfigure(1, weight=1)
main_container.rowconfigure(0, weight=1)

sidebar = ttk.Frame(main_container, padding=16)
sidebar.grid(row=0, column=0, sticky="nsw")
sidebar.columnconfigure(0, weight=1)

filters_title = ttk.Label(sidebar, text=_("Filters"), font=("Arial", 16, "bold"))
filters_title.grid(row=0, column=0, sticky="w", pady=(0, 10))

perfume_name_label = ttk.Label(sidebar, text=_("Perfume name"))
perfume_name_label.grid(row=1, column=0, sticky="w", pady=(8, 2))
name_var = tk.StringVar()
name_entry = ttk.Entry(sidebar, textvariable=name_var)
name_entry.grid(row=2, column=0, sticky="ew")


def add_filter(r, label, values, default_idx):
    lbl = ttk.Label(sidebar, text=_(label))
    lbl.grid(row=r, column=0, sticky="w", pady=(10, 2))
    var = tk.StringVar()
    translated = translate_list(values)
    cb = ttk.Combobox(sidebar, textvariable=var, state="readonly", values=translated, width=22)
    cb.current(default_idx)
    try:
        var.set(translated[default_idx])
    except Exception:
        pass
    cb.grid(row=r + 1, column=0, sticky="ew")
    return {"label": lbl, "combo": cb, "values": values, "default": default_idx}


gender_filter = add_filter(3, "Gender", gender_values, 0)
intensity_filter = add_filter(5, "Intensity", intensity_values, 0)

notes_var = tk.StringVar()
notes_entry = ttk.Entry(sidebar, textvariable=notes_var)
notes_entry.grid(row=8, column=0, sticky="ew")
notes_label = ttk.Label(sidebar, text=_("Ingredients / Notes (keyword)"))
notes_label.grid(row=7, column=0, sticky="w", pady=(10, 2))

season_filter = add_filter(9, "Season", season_values, 0)
concept_filter = add_filter(11, "Concept", concept_values, 0)
classification_filter = add_filter(13, "Classification", classification_values, 0)
longevity_filter = add_filter(15, "Longevity", longevity_values, 0)

content = ttk.Frame(main_container, padding=(16, 16, 8, 16))
content.grid(row=0, column=1, sticky="nsew")
content.columnconfigure(0, weight=1)
content.rowconfigure(4, weight=1)

header = ttk.Frame(content)
header.grid(row=0, column=0, sticky="ew")
header.columnconfigure(0, weight=1)
header.columnconfigure(1, weight=0)
header_title = ttk.Label(header, text=_("Perfume Recommender"), font=("Arial", 18, "bold"))
header_title.grid(row=0, column=0, sticky="w")
db_header_btn = ttk.Button(header, text=_("Open Perfume DB"))
db_header_btn.grid(row=0, column=1, sticky="e", padx=(10, 0))

controls = ttk.Frame(content)
controls.grid(row=1, column=0, sticky="ew", pady=(10, 6))
controls.columnconfigure(0, weight=1)

global_search_var = tk.StringVar()
placeholder = _("Search")
global_search_entry = ttk.Entry(controls, textvariable=global_search_var)
global_search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

def _on_search_focus_in(event):
    if global_search_var.get() == placeholder:
        global_search_entry.delete(0, tk.END)


def _on_search_focus_out(event):
    if not global_search_var.get().strip():
        global_search_entry.delete(0, tk.END)
        global_search_entry.insert(0, placeholder)


global_search_entry.insert(0, placeholder)
global_search_entry.bind("<FocusIn>", _on_search_focus_in)
global_search_entry.bind("<FocusOut>", _on_search_focus_out)

sort_var = tk.StringVar(value="Best match")
sort_cb = ttk.Combobox(
    controls,
    textvariable=sort_var,
    state="readonly",
    width=14,
    values=("Best match", "Name A-Z", "Name Z-A"),
)
sort_cb.grid(row=0, column=1, sticky="e")

progress = ttk.Progressbar(controls, mode="indeterminate")
progress.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
progress.grid_remove()

chips_row = ttk.Frame(content)
chips_row.grid(row=2, column=0, sticky="w", pady=(0, 10))
chips_label = ttk.Label(chips_row, text="", foreground="gray")
chips_label.pack(anchor="w")

cards_area = ScrollableFrame(content)
cards_area.grid(row=4, column=0, sticky="nsew")

info_lbl = ttk.Label(content, text="", foreground="gray")
info_lbl.grid(row=5, column=0, sticky="w", pady=(10, 0))


def clear_cards():
    for w in cards_area.inner.winfo_children():
        w.destroy()


def get_filter_value(filter_obj):
    idx = filter_obj["combo"].current()
    if idx < 0 or idx >= len(filter_obj["values"]):
        idx = filter_obj["default"]
    return filter_obj["values"][idx]


def build_profile():
    return {
        "gender": get_filter_value(gender_filter),
        "intensity": get_filter_value(intensity_filter),
        "season": get_filter_value(season_filter),
        "concept": get_filter_value(concept_filter),
        "classification": get_filter_value(classification_filter),
        "longevity": get_filter_value(longevity_filter),
    }


def show_product_popup(product):
    win = tk.Toplevel(root)
    win.title(product["name"])
    win.geometry("560x360")

    ttk.Label(win, text=product["name"], font=("Arial", 16, "bold")).pack(anchor="w", padx=16, pady=(16, 6))
    ttk.Label(win, text=f"{_('Match')}: {product['match']}%", foreground="gray").pack(anchor="w", padx=16)

    ttk.Label(win, text=product["desc"], wraplength=520, justify="left").pack(anchor="w", padx=16, pady=(10, 10))

    notes_text = ", ".join(product["notes"])
    meta = (
        f"{_('Gender')}: {_(product['gender'])}\n"
        f"{_('Intensity')}: {_(product['intensity'])}\n"
        f"{_('Season')}: {_(product['season'])}\n"
        f"{_('Concept')}: {_(product['concept'])}\n"
        f"{_('Classification')}: {_(product['classification'])}\n"
        f"{_('Longevity')}: {_(product['longevity'])}\n"
        f"{_('Notes')}: {notes_text}\n"
    )
    ttk.Label(win, text=meta, justify="left").pack(anchor="w", padx=16)

    ttk.Button(win, text=_("Close"), command=win.destroy).pack(pady=12)


def _render_cards_real():
    progress.stop()
    progress.grid_remove()

    clear_cards()
    profile = build_profile()

    chips_label.config(
        text=(
            f"{_('Applied filters')}: {profile['gender']} • {profile['intensity']} • {profile['season']} • "
            f"{profile['concept']} • {profile['classification']} • {profile['longevity']}"
        )
    )

    fname = name_var.get()
    fnotes = notes_var.get()

    gq = global_search_var.get().strip().lower()
    if gq == placeholder.lower():
        gq = ""

    products = load_products_from_db()
    if not products:
        info_lbl.config(text=_("No data in database"))
        empty = ttk.Frame(cards_area.inner, padding=18, relief="solid")
        empty.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        ttk.Label(empty, text=_("No results found"), font=("Arial", 13, "bold")).pack(anchor="w")
        ttk.Label(empty, text=_("Try changing filters or keywords."), foreground="gray").pack(anchor="w", pady=(6, 0))
        return

    items = filter_rank_products(profile, fname, fnotes, sort_var.get(), products)

    if gq:
        items = [p for p in items if (gq in p["name"].lower() or gq in p["desc"].lower())]

    info_lbl.config(text=f"{len(items)} {_('products found')} • {_('Sorted by')} {sort_var.get()}")

    if not items:
        empty = ttk.Frame(cards_area.inner, padding=18, relief="solid")
        empty.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        ttk.Label(empty, text=_("No results found"), font=("Arial", 13, "bold")).pack(anchor="w")
        ttk.Label(empty, text=_("Try changing filters or keywords."), foreground="gray").pack(anchor="w", pady=(6, 0))
        return

    cols = 2
    for i in range(cols):
        cards_area.inner.columnconfigure(i, weight=1, minsize=410)
    
    # Make inner frame fill canvas width
    cards_area.inner.grid_rowconfigure(0, weight=0)
    cards_area.inner.grid_columnconfigure(0, weight=1)
    cards_area.inner.grid_columnconfigure(1, weight=1)

    for idx, p in enumerate(items):
        r = idx // cols
        c = idx % cols

        card = ttk.Frame(cards_area.inner, padding=13, relief="solid")
        card.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)

        def on_enter(e, w=card):
            w.configure(relief="raised")

        def on_leave(e, w=card):
            w.configure(relief="solid")

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        ttk.Label(card, text=p["name"], font=("Arial", 13, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(card, text=f"{_('Match')}: {p['match']}%", foreground="gray", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=(2, 4))

        ttk.Label(card, text=p["desc"], wraplength=340, justify="left", font=("Arial", 10)).grid(row=2, column=0, sticky="ew")

        notes_text = ", ".join(p["notes"])
        ttk.Label(card, text=f"{_('Notes')}: {notes_text}", foreground="gray", wraplength=340, justify="left", font=("Arial", 9)).grid(row=3, column=0, sticky="ew", pady=(4, 0))

        btns = ttk.Frame(card)
        btns.grid(row=4, column=0, sticky="w", pady=(8, 0))
        ttk.Button(btns, text=_("View"), command=lambda prod=p: show_product_popup(prod)).pack(side="left")


def render_cards():
    progress.grid()
    progress.start(10)
    root.after(350, _render_cards_real)


def reset_filters():
    name_var.set("")
    notes_var.set("")
    global_search_var.set(placeholder)

    gender_filter["combo"].current(0)
    intensity_filter["combo"].current(0)
    season_filter["combo"].current(0)
    concept_filter["combo"].current(0)
    classification_filter["combo"].current(0)
    longevity_filter["combo"].current(0)
    render_cards()


side_btns = ttk.Frame(sidebar)
side_btns.grid(row=30, column=0, sticky="ew", pady=(16, 0))
side_btns.columnconfigure(0, weight=1)
side_btns.columnconfigure(1, weight=1)

reset_btn = ttk.Button(side_btns, text=_("Reset"), command=reset_filters)
reset_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))
apply_btn = ttk.Button(side_btns, text=_("Apply Filters"), command=render_cards)
apply_btn.grid(row=0, column=1, sticky="ew")


sort_cb.bind("<<ComboboxSelected>>", lambda e: render_cards())
global_search_entry.bind("<Return>", lambda e: render_cards())
name_entry.bind("<Return>", lambda e: render_cards())
notes_entry.bind("<Return>", lambda e: render_cards())

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


db_header_btn.config(command=open_database)

def update_ui():
    root.title(_("Perfume Recommender"))
    title_label.config(text=_("Perfume Recommender"))
    subtitle.config(text=_("Browse and filter perfumes. Use the sidebar to narrow results."))
    filters_title.config(text=_("Filters"))
    perfume_name_label.config(text=_("Perfume name"))
    notes_label.config(text=_("Ingredients / Notes (keyword)"))
    header_title.config(text=_("Perfume Recommender"))
    db_header_btn.config(text=_("Open Perfume DB"))
    reset_btn.config(text=_("Reset"))
    apply_btn.config(text=_("Apply Filters"))
    # Update combo labels and values with translations
    for filt, label_key in [
        (gender_filter, "Gender"),
        (intensity_filter, "Intensity"),
        (season_filter, "Season"),
        (concept_filter, "Concept"),
        (classification_filter, "Classification"),
        (longevity_filter, "Longevity"),
    ]:
        filt["label"].config(text=_(label_key))
        idx = filt["combo"].current()
        if idx < 0:
            idx = 0
        translated_values = translate_list(filt["values"])
        filt["combo"]["values"] = translated_values
        if idx < len(translated_values):
            filt["combo"].current(idx)
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
    lang_btn.config(text=get_toggle_label())
    # Re-render cards to update "View" button text and product details
    _render_cards_real()


def on_toggle_lang():
    toggle_lang()
    update_ui()


lang_btn.config(command=on_toggle_lang)


def show_help():
    """Display help information"""
    help_text = _("""
Perfume Recommender Application Help

Instructions:
1. Use the left sidebar filters (gender, intensity, season, concept, classification, longevity, name, notes) to refine results.
2. Use the top search box to search within results and the sort box to change ordering.
3. Click a card's View button to see details, or "Open Perfume DB" to manage the database.
4. Use the menu bar for Language, Database, and Help options.

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
