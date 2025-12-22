import tkinter as tk
from tkinter import ttk

from ListPerfumes import ListPerfumes
from perfume_db import PerfumeDatabase
from i18n import _, toggle_lang, get_toggle_label, translate_list

# ----------------------------
# Main Window (Filters)
# ----------------------------
root = tk.Tk()
root.title(_("Perfume Recommender"))
root.geometry("560x760")

db = PerfumeDatabase()

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



def make_combo(label_text, values, default_index):
    label = tk.Label(root, text=_(label_text), font=TEXT_FONT)
    label.pack()

    var = tk.StringVar()
    combo = ttk.Combobox(root, textvariable=var, state="readonly")
    combo["values"] = translate_list(values)
    combo.current(default_index)
    combo.pack(pady=6)
    return {"label": label, "combo": combo, "values": values, "default": default_index}



# Inputs

combos = {}
combos["gender"] = make_combo("Select Gender:", ["Woman", "Man", "Unisex"], 0)
combos["occasion"] = make_combo("Select Occasion:", ["Daily", "Office", "Night Out", "Sport"], 0)
combos["season"] = make_combo("Select Season:", ["Summer", "Winter", "Spring", "Autumn"], 0)
combos["longevity"] = make_combo("Select Longevity:", ["Short", "Moderate", "Long"], 1)
combos["sensitivity"] = make_combo("Select Sensitivity:", ["Low", "Medium", "High"], 1)
combos["classification"] = make_combo("Select Classification:", ["Light", "Moderate", "Intense"], 1)

def get_combo_var(key):
    return combos[key]["combo"].get()



# Window 2: Results Window

def show_selection():
    chosen_gender = get_combo_var("gender")
    chosen_occasion = get_combo_var("occasion")
    chosen_season = get_combo_var("season")
    chosen_longevity = get_combo_var("longevity")
    chosen_sensitivity = get_combo_var("sensitivity")
    chosen_classification = get_combo_var("classification")

    # Demo recommendations – database teammate will replace later
    mock_recommendations = [
        "Dior Sauvage (Demo)",
        "Dior Homme (Demo)",
        "Miss Dior (Demo)"
    ]

    result_window = tk.Toplevel(root)
    result_window.title(_("Results"))
    result_window.geometry("520x460")

    header = tk.Label(result_window, text=_("Your Results"), font=("Arial", 16, "bold"))
    header.pack(pady=(15, 10))

    # Profile box 
    profile_frame = tk.LabelFrame(result_window, text=_("Selected Profile"), font=H2_FONT, padx=12, pady=10)
    profile_frame.pack(padx=18, pady=10, fill="x")

    profile_text = (
        f"{_('Gender')}: {chosen_gender}\n"
        f"{_('Occasion')}: {chosen_occasion}\n"
        f"{_('Season')}: {chosen_season}\n"
        f"{_('Longevity')}: {chosen_longevity}\n"
        f"{_('Sensitivity')}: {chosen_sensitivity}\n"
        f"{_('Classification')}: {chosen_classification}"
    )

    profile_label = tk.Label(profile_frame, text=profile_text, justify="left", anchor="w", font=TEXT_FONT)
    profile_label.pack(fill="x")

    # Recommendations box
    rec_frame = tk.LabelFrame(result_window, text=_("Recommended Dior Perfumes (Demo)"), font=H2_FONT, padx=12, pady=10)
    rec_frame.pack(padx=18, pady=10, fill="both", expand=True)

    rec_list = tk.Listbox(rec_frame, height=6, font=TEXT_FONT)
    rec_list.pack(fill="both", expand=True)

    for item in mock_recommendations:
        rec_list.insert(tk.END, "• " + item)

    note = tk.Label(
        result_window,
        text=_("Note: This list is a mock output. The database + matching logic will be integrated by the data module."),
        fg="gray",
        font=("Arial", 10)
    )
    note.pack(pady=(5, 10), padx=18)

    btns = tk.Frame(result_window)
    btns.pack(pady=10)

    close_btn = tk.Button(btns, text=_("Close"), width=12, command=result_window.destroy)
    close_btn.pack(side="left", padx=8)



# Window 3: Project Info / About

def open_about():
    about_window = tk.Toplevel(root)
    about_window.title(_("Project Information"))
    about_window.geometry("560x520")

    header = tk.Label(about_window, text=_("Project Information"), font=("Arial", 16, "bold"))
    header.pack(pady=(15, 10))

    info_frame = tk.LabelFrame(about_window, text=_("Overview"), font=H2_FONT, padx=12, pady=10)
    info_frame.pack(padx=18, pady=10, fill="both", expand=True)

    info_text = (
        "Project: Dior Perfume Recommender\n"
        "Course: Python GUI Programming\n"
        "Team: Sinemis Aksoy & Zeynep Mamoori\n\n"
        "Goal:\n"
        "• Collect user preferences via a clean GUI\n"
        "• Generate a recommendation output based on matching rules\n\n"
        "How it works (UI module):\n"
        "• Main Window: collects inputs (gender, occasion, season, longevity, sensitivity, classification)\n"
        "• Results Window: displays the selected profile + a demo recommendation list\n"
        "• This window: explains the project and system design\n\n"
        "Future Work:\n"
        "• Integrate a Dior perfume dataset (database module)\n"
        "• Replace demo recommendations with real matching results"
    )

    lbl = tk.Label(info_frame, text=info_text, justify="left", anchor="w", font=TEXT_FONT)
    lbl.pack(fill="both", expand=True)

    close_btn = tk.Button(about_window, text=_("Close"), width=12, command=about_window.destroy)
    close_btn.pack(pady=12)


def open_database():
    db_window = ListPerfumes(root, db=db)
    db_window.grab_set()



def clear_inputs():
    # reset to defaults by index to be language-agnostic
    for key, data in combos.items():
        data["combo"].current(data["default"])



# Buttons (Main Window)

buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=24)

db_button = tk.Button(buttons_frame, text=_("Open Perfume DB"), width=16, command=open_database)
db_button.pack(side="left", padx=10)

about_button = tk.Button(buttons_frame, text=_("Project Info"), width=14, command=open_about)
about_button.pack(side="left", padx=10)

clear_button = tk.Button(buttons_frame, text=_("Clear"), width=10, command=clear_inputs)
clear_button.pack(side="left", padx=10)

select_button = tk.Button(buttons_frame, text=_("Get Recommendation"), width=18, command=show_selection)
select_button.pack(side="left", padx=10)


def update_ui():
    root.title(_("Perfume Recommender"))
    title_label.config(text=_("Perfume Recommender"))
    subtitle.config(text=_("Select your preferences to generate a personalized Dior profile.\nRecommendations are currently shown as a demo (mock) list."))
    for key, data in combos.items():
        # remember current index
        idx = data["combo"].current()
        data["label"].config(text=_(
            {
                "gender": "Select Gender:",
                "occasion": "Select Occasion:",
                "season": "Select Season:",
                "longevity": "Select Longevity:",
                "sensitivity": "Select Sensitivity:",
                "classification": "Select Classification:",
            }[key]
        ))
        data["combo"]["values"] = translate_list(data["values"])
        data["combo"].current(idx)
    db_button.config(text=_("Open Perfume DB"))
    about_button.config(text=_("Project Info"))
    clear_button.config(text=_("Clear"))
    select_button.config(text=_("Get Recommendation"))
    lang_btn.config(text=get_toggle_label())


def on_toggle_lang():
    toggle_lang()
    update_ui()


lang_btn.config(command=on_toggle_lang)

root.mainloop()
