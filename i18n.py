current_lang = "en"


def set_lang(lang_code: str):
    global current_lang
    current_lang = "tr" if str(lang_code).lower().startswith("tr") else "en"


def toggle_lang() -> str:
    global current_lang
    current_lang = "tr" if current_lang == "en" else "en"
    return current_lang


def get_toggle_label() -> str:
    return "Türkçe" if current_lang == "en" else "English"


def _(text: str) -> str:
    if current_lang == "en":
        return text
    return TR_MAP.get(text, text)


def translate_list(values):
    return [_(v) for v in values]


# English → Turkish map
TR_MAP = {
    # Generic / navigation
    "Perfume Recommender": "Parfüm Önerici",
    "Perfume Recommendation Application": "Parfüm Öneri Uygulaması",
    "Open Perfume DB": "Parfüm Veritabanını Aç",
    "Project Info": "Proje Bilgisi",
    "Clear": "Temizle",
    "Get Recommendation": "Öneri Al",
    "Results": "Sonuçlar",
    "Your Results": "Sonuçlarınız",
    "Selected Profile": "Seçilen Profil",
    "Recommended Dior Perfumes (Demo)": "Önerilen Dior Parfümleri (Demo)",
    "Close": "Kapat",
    "Project Information": "Proje Bilgileri",
    "Overview": "Genel Bakış",

    # Main subtitle
    "Select your preferences to generate a personalized Dior profile.\nRecommendations are currently shown as a demo (mock) list.":
        "Kişisel Dior profilinizi oluşturmak için tercihlerinizi seçin.\nÖneriler şu anda demo (örnek) liste olarak gösterilmektedir.",

    # Main inputs (labels)
    "Select Gender:": "Cinsiyet Seçin:",
    "Select Occasion:": "Kullanım Amacı Seçin:",
    "Select Season:": "Mevsim Seçin:",
    "Select Longevity:": "Kalıcılık Seçin:",
    "Select Sensitivity:": "Hassasiyet Seçin:",
    "Select Classification:": "Sınıflandırma Seçin:",

    # Main input values
    "Woman": "Kadın",
    "Man": "Erkek",
    "Unisex": "Uniseks",
    "Daily": "Günlük",
    "Office": "Ofis",
    "Night Out": "Gece",
    "Sport": "Spor",
    "Summer": "Yaz",
    "Winter": "Kış",
    "Spring": "İlkbahar",
    "Autumn": "Sonbahar",
    "Short": "Kısa",
    "Moderate": "Orta",
    "Long": "Uzun",
    "Low": "Düşük",
    "Medium": "Orta",
    "High": "Yüksek",
    "Light": "Hafif",
    "Intense": "Yoğun",

    # List window
    "Search:": "Ara:",
    "ID": "ID",
    "Perfume Name": "Parfüm Adı",
    "Gender": "Cinsiyet",
    "Intensity": "Yoğunluk",
    "Ingredients/Notes": "İçerik/Notlar",
    "Collection": "Koleksiyon",
    "Season": "Mevsim",
    "Concept": "Kavram",
    "Classification": "Sınıflandırma",
    "Longevity": "Kalıcılık",
    "Occasion": "Kullanım",
    "Sensitivity": "Hassasiyet",
    "Displaying {} of {} perfumes  |  Ctrl+I: Add  |  Double-click: Edit  |  Delete: Remove  |  F1: Help  |  F2: Stats":
        "Toplam {} parfümden {} gösteriliyor  |  Ctrl+I: Ekle  |  Çift tık: Düzenle  |  Delete: Sil  |  F1: Yardım  |  F2: İstatistik",
    "Confirm Delete": "Silmeyi Onayla",
    "Are you sure you want to delete the selected perfume?": "Seçili parfümü silmek istediğinizden emin misiniz?",
    "Perfume Details": "Parfüm Detayları",
    "Perfume Statistics": "Parfüm İstatistikleri",
    "PERFUME DATABASE STATISTICS\n\n": "PARFÜM VERİTABANI İSTATİSTİKLERİ\n\n",
    "Total Perfumes: {}\n\n": "Toplam Parfüm: {}\n\n",
    "By Gender:\n": "Cinsiyete Göre:\n",
    "\nBy Intensity:\n": "\nYoğunluğa Göre:\n",
    "\nTop 5 Classifications:\n": "\nEn Çok 5 Sınıflandırma:\n",
    "Help": "Yardım",
    """
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
        """: """
PARFÜM ÖNERİ UYGULAMASI - YARDIM

Klavye Kısayolları:
  • Ctrl+I: Yeni parfüm ekle
  • Çift tık: Seçili parfümü düzenle
  • Delete: Seçili parfümü sil
  • F1: Bu yardım penceresini göster
  • F2: Veritabanı istatistiklerini göster

Özellikler:
  • Veritabanındaki tüm parfümleri görüntüleme
  • Parfümleri ada, cinsiyete, sınıflandırmaya, içeriğe veya mevsime göre arama/filtreleme
  • Koleksiyona yeni parfüm ekleme
  • Var olan parfüm ayrıntılarını düzenleme
  • Parfümleri veritabanından silme
  • Cinsiyet, yoğunluk ve sınıflandırmaya göre istatistikleri görüntüleme
        """,

    # Form window
    "Perfume Form": "Parfüm Formu",
    "Perfume Details": "Parfüm Detayları",
    "Perfume Name *": "Parfüm Adı *",
    "Gender *": "Cinsiyet *",
    "Ingredients/Notes": "İçerik/Notlar",
    "Concept": "Kavram",
    "Collection": "Koleksiyon",
    "Classification": "Sınıflandırma",
    "Subfamily": "Alt aile",
    # Shared values
    "Weak": "Zayıf",
    "Strong": "Güçlü",
    "Very Strong": "Çok Güçlü",
    "Very Long": "Çok Uzun",

    # Buttons/messages
    "Add New Perfume": "Yeni Parfüm Ekle",
    "Edit Perfume": "Parfümü Düzenle",
    "Save Perfume": "Parfümü Kaydet",
    "Update Perfume": "Parfümü Güncelle",
    "Success": "Başarılı",
    "Perfume added successfully!": "Parfüm başarıyla eklendi!",
    "Perfume updated successfully!": "Parfüm başarıyla güncellendi!",
    "Database Error": "Veritabanı Hatası",
    "Error": "Hata",
    "Please enter a perfume name.": "Lütfen bir parfüm adı girin.",
    "Please select a gender.": "Lütfen bir cinsiyet seçin.",
    "Please select an intensity.": "Lütfen bir yoğunluk seçin.",

    # Results window note
    "Note: This list is a mock output. The database + matching logic will be integrated by the data module.":
        "Not: Bu liste örnek amaçlıdır. Veritabanı ve eşleştirme mantığı daha sonra eklenecektir.",
}
