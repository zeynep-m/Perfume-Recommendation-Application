"""Product card presentation for the recommendation window."""

import customtkinter as ctk

from i18n import _


class ProductCardView:
    """Render one perfume recommendation card."""

    def __init__(self, parent, product, on_view):
        self.card = ctk.CTkFrame(parent, corner_radius=10, border_width=1)
        self.card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.card,
            text=product["name"],
            font=("Arial", 13, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=13, pady=(13, 2))
        ctk.CTkLabel(
            self.card,
            text=f"{_('Match')}: {product['match']}%",
            text_color="gray",
            font=("Arial", 10),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=13, pady=(2, 4))
        ctk.CTkLabel(
            self.card,
            text=product["desc"],
            wraplength=340,
            justify="left",
            font=("Arial", 10),
            anchor="w",
        ).grid(row=2, column=0, sticky="ew", padx=13)

        notes_text = ", ".join(product["notes"])
        ctk.CTkLabel(
            self.card,
            text=f"{_('Notes')}: {notes_text}",
            text_color="gray",
            wraplength=340,
            justify="left",
            font=("Arial", 9),
            anchor="w",
        ).grid(row=3, column=0, sticky="ew", padx=13, pady=(4, 0))

        buttons = ctk.CTkFrame(self.card, fg_color="transparent")
        buttons.grid(row=4, column=0, sticky="w", padx=13, pady=(8, 13))
        ctk.CTkButton(
            buttons,
            text=_("View"),
            command=lambda: on_view(product),
            width=80,
        ).pack(side="left")
