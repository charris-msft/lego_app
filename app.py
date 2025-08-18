from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional
import logging
from azure.identity import DefaultAzureCredential
import struct

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Database connection configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'lego-postgres-server.postgres.database.azure.com'),
    'database': os.getenv('DB_NAME', 'lego'),
    'user': os.getenv('AZURE_AD_USER', 'charris@microsoft.com'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'sslmode': os.getenv('DB_SSLMODE', 'require')
}

def get_azure_ad_token():
    """Get Azure AD access token for PostgreSQL"""
    try:
        app.logger.info("Attempting to acquire Azure AD token...")
        
        # Try different credential types in order of preference
        credential = DefaultAzureCredential(
            exclude_visual_studio_code_credential=False,
            exclude_cli_credential=False,
            exclude_environment_credential=False,
            exclude_managed_identity_credential=False,
            exclude_shared_token_cache_credential=False,
            exclude_interactive_browser_credential=True  # Avoid browser popup in web app
        )
        
        token = credential.get_token("https://ossrdbms-aad.database.windows.net")
        app.logger.info("Azure AD token acquired successfully")
        return token.token
    except Exception as e:
        app.logger.error(f"Failed to get Azure AD token: {e}")
        app.logger.error(f"Exception type: {type(e).__name__}")
        return None

def get_db_connection():
    """Get database connection using Azure AD authentication"""
    try:
        app.logger.info(f"Attempting database connection to {DB_CONFIG['host']}")
        
        # Get Azure AD token
        token = get_azure_ad_token()
        if not token:
            app.logger.error("Failed to get Azure AD token")
            return None
        
        app.logger.info(f"Connecting with user: {DB_CONFIG['user']}")
        
        # Create connection with token as password
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=token,
            port=DB_CONFIG['port'],
            sslmode=DB_CONFIG['sslmode'],
            connect_timeout=10
        )
        
        app.logger.info("Database connection successful")
        return conn
        
    except psycopg2.OperationalError as e:
        app.logger.error(f"PostgreSQL Operational Error: {e}")
        if "authentication failed" in str(e).lower():
            app.logger.error("Authentication failed - check if user has proper Azure AD permissions")
        elif "ssl" in str(e).lower():
            app.logger.error("SSL connection issue - check server SSL configuration")
        elif "timeout" in str(e).lower():
            app.logger.error("Connection timeout - check network connectivity and firewall")
        return None
    except Exception as e:
        app.logger.error(f"Database connection error: {e}")
        app.logger.error(f"Exception type: {type(e).__name__}")
        return None

# Forms
class SetForm(FlaskForm):
    set_num = StringField('Set Number', validators=[DataRequired()])
    name = StringField('Set Name', validators=[DataRequired()])
    year = IntegerField('Year', validators=[Optional(), NumberRange(min=1950, max=2030)])
    theme_id = SelectField('Theme', coerce=int, validators=[Optional()])
    num_parts = IntegerField('Number of Parts', validators=[Optional(), NumberRange(min=0)])

class UserInventoryForm(FlaskForm):
    set_num = SelectField('LEGO Set', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    build_status = SelectField('Build Status', choices=[
        ('', 'Select Status'),
        ('unbuilt', 'Unbuilt'),
        ('built', 'Built'),
        ('partial', 'Partially Built')
    ], validators=[Optional()])
    display_location = StringField('Display Location', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])

class InventoryPartForm(FlaskForm):
    inventory_id = SelectField('Inventory', coerce=int, validators=[DataRequired()])
    part_num = SelectField('Part', validators=[DataRequired()])
    color_id = SelectField('Color', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    is_spare = BooleanField('Is Spare Part')

@app.route('/')
def index():
    """Home page with dashboard"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return render_template('error.html')
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get dashboard statistics
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM lego_sets) as total_sets,
                (SELECT COUNT(*) FROM user_inventory) as user_sets,
                (SELECT COUNT(*) FROM lego_parts) as total_parts,
                (SELECT COUNT(*) FROM lego_inventory_parts) as total_inventory_parts,
                (SELECT COUNT(DISTINCT color_id) FROM lego_inventory_parts) as total_colors,
                (SELECT COUNT(*) FROM lego_themes) as total_themes
        """)
        stats = cursor.fetchone()
        
        # Get recent user inventory
        cursor.execute("""
            SELECT ui.*, ls.name as set_name, lt.name as theme_name
            FROM user_inventory ui
            JOIN lego_sets ls ON ui.set_num = ls.set_num
            LEFT JOIN lego_themes lt ON ls.theme_id = lt.id
            ORDER BY ui.date_acquired DESC NULLS LAST, ui.id DESC
            LIMIT 5
        """)
        recent_inventory = cursor.fetchall()
        
        # Get popular themes
        cursor.execute("""
            SELECT lt.name, COUNT(*) as set_count
            FROM lego_sets ls
            JOIN lego_themes lt ON ls.theme_id = lt.id
            GROUP BY lt.name
            ORDER BY set_count DESC
            LIMIT 5
        """)
        popular_themes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('index.html', 
                             stats=stats, 
                             recent_inventory=recent_inventory,
                             popular_themes=popular_themes)
    except Exception as e:
        app.logger.error(f"Dashboard error: {e}")
        flash(f'Error loading dashboard: {e}', 'error')
        return render_template('error.html')

@app.route('/sets')
def sets():
    """View all LEGO sets"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    theme_filter = request.args.get('theme', '')
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return render_template('error.html')
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build query with filters
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append("(ls.name ILIKE %s OR ls.set_num ILIKE %s)")
            params.extend([f'%{search}%', f'%{search}%'])
        
        if theme_filter:
            where_conditions.append("lt.name = %s")
            params.append(theme_filter)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Get total count
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM lego_sets ls
            LEFT JOIN lego_themes lt ON ls.theme_id = lt.id
            {where_clause}
        """, params)
        total = cursor.fetchone()['count']
        
        # Get sets for current page
        cursor.execute(f"""
            SELECT ls.*, lt.name as theme_name
            FROM lego_sets ls
            LEFT JOIN lego_themes lt ON ls.theme_id = lt.id
            {where_clause}
            ORDER BY ls.year DESC, ls.set_num
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        sets_data = cursor.fetchall()
        
        # Get themes for filter dropdown
        cursor.execute("SELECT DISTINCT name FROM lego_themes ORDER BY name")
        themes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        total_pages = (total + per_page - 1) // per_page
        
        return render_template('sets.html', 
                             sets=sets_data, 
                             page=page, 
                             total_pages=total_pages,
                             search=search,
                             theme_filter=theme_filter,
                             themes=themes)
    except Exception as e:
        app.logger.error(f"Sets view error: {e}")
        flash(f'Error loading sets: {e}', 'error')
        return render_template('error.html')

@app.route('/user_inventory')
def user_inventory():
    """View user's inventory"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return render_template('error.html')
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT ui.*, ls.name as set_name, ls.year, ls.num_parts, lt.name as theme_name
            FROM user_inventory ui
            JOIN lego_sets ls ON ui.set_num = ls.set_num
            LEFT JOIN lego_themes lt ON ls.theme_id = lt.id
            ORDER BY ui.date_acquired DESC NULLS LAST, ui.id DESC
        """)
        inventory = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('user_inventory.html', inventory=inventory)
    except Exception as e:
        app.logger.error(f"User inventory error: {e}")
        flash(f'Error loading user inventory: {e}', 'error')
        return render_template('error.html')

@app.route('/user_inventory/add', methods=['GET', 'POST'])
def add_user_inventory():
    """Add set to user inventory"""
    form = UserInventoryForm()
    
    # Populate set choices
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return redirect(url_for('user_inventory'))
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT set_num, name FROM lego_sets ORDER BY name")
        sets = cursor.fetchall()
        form.set_num.choices = [('', 'Select a Set')] + [(s['set_num'], f"{s['set_num']} - {s['name']}") for s in sets]
        
        if form.validate_on_submit():
            cursor.execute("""
                INSERT INTO user_inventory (set_num, quantity, build_status, display_location, notes, date_acquired)
                VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
            """, (form.set_num.data, form.quantity.data, form.build_status.data or None, 
                  form.display_location.data or None, form.notes.data or None))
            conn.commit()
            flash('Set added to inventory successfully!', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('user_inventory'))
        
        cursor.close()
        conn.close()
        return render_template('add_user_inventory.html', form=form)
    except Exception as e:
        app.logger.error(f"Add inventory error: {e}")
        flash(f'Error adding to inventory: {e}', 'error')
        return redirect(url_for('user_inventory'))

@app.route('/parts')
def parts():
    """View all parts"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return render_template('error.html')
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build query with filters
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append("(lp.name ILIKE %s OR lp.part_num ILIKE %s)")
            params.extend([f'%{search}%', f'%{search}%'])
        
        if category_filter:
            where_conditions.append("lpc.name = %s")
            params.append(category_filter)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Get total count
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM lego_parts lp
            JOIN lego_part_categories lpc ON lp.part_cat_id = lpc.id
            {where_clause}
        """, params)
        total = cursor.fetchone()['count']
        
        # Get parts for current page
        cursor.execute(f"""
            SELECT lp.*, lpc.name as category_name
            FROM lego_parts lp
            JOIN lego_part_categories lpc ON lp.part_cat_id = lpc.id
            {where_clause}
            ORDER BY lp.name
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        parts_data = cursor.fetchall()
        
        # Get categories for filter dropdown
        cursor.execute("SELECT DISTINCT name FROM lego_part_categories ORDER BY name")
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        total_pages = (total + per_page - 1) // per_page
        
        return render_template('parts.html', 
                             parts=parts_data, 
                             page=page, 
                             total_pages=total_pages,
                             search=search,
                             category_filter=category_filter,
                             categories=categories)
    except Exception as e:
        app.logger.error(f"Parts view error: {e}")
        flash(f'Error loading parts: {e}', 'error')
        return render_template('error.html')

@app.route('/inventory_parts')
def inventory_parts():
    """View inventory parts"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return render_template('error.html')
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build search query
        where_clause = ""
        params = []
        if search:
            where_clause = "WHERE (lp.name ILIKE %s OR lp.part_num ILIKE %s OR lc.name ILIKE %s)"
            params = [f'%{search}%', f'%{search}%', f'%{search}%']
        
        # Get total count
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM lego_inventory_parts lip
            JOIN lego_parts lp ON lip.part_num = lp.part_num
            JOIN lego_colors lc ON lip.color_id = lc.id
            JOIN lego_inventories li ON lip.inventory_id = li.id
            {where_clause}
        """, params)
        total = cursor.fetchone()['count']
        
        # Get inventory parts for current page
        cursor.execute(f"""
            SELECT lip.*, lp.name as part_name, lpc.name as category_name,
                   lc.name as color_name, lc.rgb as color_rgb,
                   li.set_num, li.version
            FROM lego_inventory_parts lip
            JOIN lego_parts lp ON lip.part_num = lp.part_num
            JOIN lego_part_categories lpc ON lp.part_cat_id = lpc.id
            JOIN lego_colors lc ON lip.color_id = lc.id
            JOIN lego_inventories li ON lip.inventory_id = li.id
            {where_clause}
            ORDER BY lip.inventory_id, lp.name
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        inventory_parts_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        total_pages = (total + per_page - 1) // per_page
        
        return render_template('inventory_parts.html', 
                             inventory_parts=inventory_parts_data, 
                             page=page, 
                             total_pages=total_pages,
                             search=search)
    except Exception as e:
        app.logger.error(f"Inventory parts view error: {e}")
        flash(f'Error loading inventory parts: {e}', 'error')
        return render_template('error.html')

@app.route('/colors')
def colors():
    """View all colors"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return render_template('error.html')
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT lc.*, COUNT(lip.color_id) as usage_count
            FROM lego_colors lc
            LEFT JOIN lego_inventory_parts lip ON lc.id = lip.color_id
            GROUP BY lc.id, lc.name, lc.rgb, lc.is_trans
            ORDER BY usage_count DESC, lc.name
        """)
        colors_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('colors.html', colors=colors_data)
    except Exception as e:
        app.logger.error(f"Colors view error: {e}")
        flash(f'Error loading colors: {e}', 'error')
        return render_template('error.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_message="Internal server error"), 500

if __name__ == '__main__':
    app.run(debug=True)
