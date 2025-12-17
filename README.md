# Perfume Recommendation Application

A desktop application for managing and browsing perfume collections with full CRUD functionality.

## Features

- **Browse Perfumes**: View all perfumes in an organized table with 10 columns
- **Search & Filter**: Real-time search across perfume names, genders, classifications, ingredients, and seasons
- **Add New Perfumes**: Add perfumes with detailed information (Ctrl+I)
- **Edit Perfumes**: Double-click any perfume to edit its details
- **Delete Perfumes**: Remove perfumes with confirmation (Delete key)
- **Statistics**: View database statistics breakdown by gender, intensity, and classification (F2)
- **Scrollable Interface**: Both vertical and horizontal scrolling for large datasets

## Technologies

- **Python 3**
- **Tkinter** - GUI framework
- **SQLite** - Database
- **JSON** - Initial data format

## Project Structure

```
Perfume Recommendation Application/
│
├── ListPerfumes.py          # Main application window
├── perfume_db.py            # Database management class
├── PerfumeFormWindow.py     # Base form for add/edit windows
├── AddNewPerfume.py         # Add new perfume window
├── EditPerfume.py           # Edit perfume window
├── perfumes.json            # Initial perfume data
├── json_to_sqlite.py        # Database initialization script
└── view_database.py         # Simple database viewer
```

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd "Perfume Recommendation Application"
```

2. (Optional) Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

3. Run the application:
```bash
python3 ListPerfumes.py
```

The application will automatically create and populate the database from `perfumes.json` on first run.

## Usage

### Keyboard Shortcuts
- **Ctrl+I**: Add new perfume
- **Double-click**: Edit selected perfume
- **Delete**: Remove selected perfume
- **F1**: Show help
- **F2**: Show statistics

### Database Schema

The application uses SQLite with the following schema:

```sql
CREATE TABLE perfumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    perfume TEXT,
    gender TEXT,
    intensity TEXT,
    ingredients_notes TEXT,
    season TEXT,
    concept TEXT,
    longevity TEXT,
    collection TEXT,
    classification TEXT,
    subfamily TEXT,
    sources TEXT
);
```

## Development

This application was built following the MVC pattern with:
- **Model**: `perfume_db.py` - Database operations
- **View**: `ListPerfumes.py`, `PerfumeFormWindow.py` - UI components
- **Controller**: Event handlers and business logic

The application follows Week 8/9 patterns from a GUI Programming course, demonstrating:
- Object-Oriented Programming
- Inheritance (PerfumeFormWindow → AddNewPerfume/EditPerfume)
- Event-driven programming
- Modal dialogs
- Database integration

## License

This project is for educational purposes.
