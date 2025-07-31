# LEGO Collection Manager 🧱

A modern Flask web application for managing your LEGO collection with a beautiful, responsive interface.

## Features ✨

- **Dashboard**: Overview of your collection with statistics and recent additions
- **Sets Management**: Browse and search through all LEGO sets
- **Personal Collection**: Track your owned sets with build status and location
- **Parts Explorer**: View individual LEGO parts with detailed information
- **Inventory Parts**: Comprehensive view of parts within set inventories
- **Color Palette**: Explore LEGO colors with visual swatches and usage statistics

## Screenshots 📸

The application features a modern, responsive design with:
- Beautiful gradient backgrounds and card-based layouts
- Interactive color swatches showing actual LEGO colors
- Comprehensive search and filtering capabilities
- Mobile-friendly responsive design
- Bootstrap 5 styling with custom LEGO-themed colors

## Technology Stack 🛠️

- **Backend**: Flask (Python)
- **Database**: PostgreSQL (Azure)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Forms**: Flask-WTF, WTForms
- **Database Connection**: psycopg2

## Installation 🚀

1. Clone the repository:
```bash
git clone <repository-url>
cd lego_app
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Run the application:
```bash
python app.py
```

6. Open your browser to `http://localhost:5000`

## Database Configuration 🗄️

Update the `.env` file with your PostgreSQL connection details:

```env
DB_HOST=your-postgres-server.postgres.database.azure.com
DB_NAME=lego
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432
SECRET_KEY=your-secret-key
```

## Database Schema 📋

The application works with a LEGO database containing the following tables:
- `lego_sets`: LEGO set information
- `lego_parts`: Individual LEGO parts
- `lego_colors`: Available colors with RGB values
- `lego_themes`: Set themes and categories
- `lego_inventories`: Set inventories
- `lego_inventory_parts`: Parts within set inventories
- `user_inventory`: User's personal collection

## Features in Detail 🔍

### Dashboard
- Collection statistics and overview
- Recent additions to your collection
- Popular themes analysis
- Quick action buttons

### Sets Browser
- Paginated set listings
- Search by name or set number
- Filter by theme
- Detailed set information

### Personal Collection
- Track owned sets with quantities
- Build status management (built/unbuilt/partial)
- Display location tracking
- Personal notes for each set
- Collection statistics

### Parts Explorer
- Browse all LEGO parts
- Search and filter by category
- Detailed part information
- Visual part representation

### Colors Viewer
- Visual color swatches with RGB values
- Transparent color indicators
- Usage statistics
- Most popular colors

## Development 💻

The application is structured as follows:
```
lego_app/
├── app.py              # Main Flask application
├── templates/          # Jinja2 templates
│   ├── base.html      # Base template with navigation
│   ├── index.html     # Dashboard
│   ├── sets.html      # Sets browser
│   ├── user_inventory.html  # Personal collection
│   ├── parts.html     # Parts explorer
│   ├── inventory_parts.html # Inventory parts
│   ├── colors.html    # Colors viewer
│   └── error.html     # Error page
├── requirements.txt   # Python dependencies
├── .env.example      # Environment variables template
└── README.md         # This file
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License 📄

This project is for educational and personal use. LEGO® is a trademark of the LEGO Group.

## Future Enhancements 🔮

- [ ] Set image integration
- [ ] Advanced search with filters
- [ ] Export collection to CSV/PDF
- [ ] Price tracking and valuation
- [ ] Set recommendations
- [ ] Mobile app companion
- [ ] Collection sharing
- [ ] Wishlist functionality
