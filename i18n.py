import gettext
import os

current_lang = "en"
_translator = gettext.gettext


def set_lang(lang_code: str):
    global current_lang
    current_lang = "tr" if str(lang_code).lower().startswith("tr") else "en"
    _load_language(current_lang)


def toggle_lang() -> str:
    global current_lang
    current_lang = "tr" if current_lang == "en" else "en"
    _load_language(current_lang)
    return current_lang


def get_toggle_label() -> str:
    return "Türkçe" if current_lang == "en" else "English"


def _load_language(lang_code: str):
    global _translator
    
    if lang_code == "en":
        _translator = gettext.gettext
    else:
        try:
            locale_dir = os.path.join(os.path.dirname(__file__), "locales")
            translator = gettext.translation(
                domain="messages",
                localedir=locale_dir,
                languages=[lang_code]
            )
            _translator = translator.gettext
        except FileNotFoundError:
            _translator = gettext.gettext


def _(text: str) -> str:
    return _translator(text)


def translate_list(values):
    return [_(v) for v in values]