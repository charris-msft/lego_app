#!/usr/bin/env python3
"""
Azure AD Authentication Test Script for LEGO Manager
This script helps diagnose Azure AD authentication issues.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'lego-postgres-server.postgres.database.azure.com',
    'database': 'lego',
    'user': 'charris@microsoft.com',  # Your Azure AD user
    'port': 5432,
    'sslmode': 'require'
}

def test_azure_cli_login():
    """Check if user is logged into Azure CLI"""
    print("🔍 Checking Azure CLI authentication...")
    try:
        import subprocess
        result = subprocess.run(['az', 'account', 'show'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            import json
            account_info = json.loads(result.stdout)
            print(f"✅ Azure CLI authenticated as: {account_info.get('user', {}).get('name', 'Unknown')}")
            print(f"📋 Subscription: {account_info.get('name', 'Unknown')}")
            print(f"🆔 Tenant: {account_info.get('tenantId', 'Unknown')}")
            return True
        else:
            print(f"❌ Azure CLI not authenticated: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Azure CLI not found. Please install Azure CLI.")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Azure CLI command timed out.")
        return False
    except Exception as e:
        print(f"❌ Error checking Azure CLI: {e}")
        return False

def test_azure_identity_import():
    """Test if azure-identity can be imported"""
    print("\\n🔍 Testing Azure Identity library...")
    try:
        from azure.identity import DefaultAzureCredential
        print("✅ Azure Identity library imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Azure Identity: {e}")
        print("💡 Try: pip install azure-identity")
        return False

def test_azure_ad_token():
    """Test Azure AD token acquisition"""
    print("\\n🔍 Testing Azure AD token acquisition...")
    try:
        from azure.identity import DefaultAzureCredential
        
        # Create credential with verbose settings
        credential = DefaultAzureCredential(
            exclude_visual_studio_code_credential=False,
            exclude_cli_credential=False,
            exclude_environment_credential=False,
            exclude_managed_identity_credential=False,
            exclude_shared_token_cache_credential=False,
            exclude_interactive_browser_credential=True
        )
        
        print("🔐 Attempting to get token for PostgreSQL...")
        token = credential.get_token("https://ossrdbms-aad.database.windows.net")
        
        if token and token.token:
            print(f"✅ Azure AD token acquired successfully!")
            print(f"🕒 Token expires at: {token.expires_on}")
            print(f"📏 Token length: {len(token.token)} characters")
            return token.token
        else:
            print("❌ Token is None or empty")
            return None
            
    except Exception as e:
        print(f"❌ Failed to get Azure AD token: {e}")
        print(f"Exception type: {type(e).__name__}")
        
        # Provide specific troubleshooting
        if "AADSTS" in str(e):
            print("💡 This looks like an Azure AD error. Check your permissions.")
        elif "credential" in str(e).lower():
            print("💡 Credential issue. Make sure you're logged into Azure CLI.")
        elif "network" in str(e).lower() or "timeout" in str(e).lower():
            print("💡 Network issue. Check your internet connection.")
            
        return None

def test_postgresql_connection():
    """Test PostgreSQL connection with Azure AD token"""
    print("\\n🔍 Testing PostgreSQL connection...")
    
    # First check if psycopg2 can be imported
    try:
        import psycopg2
        print("✅ psycopg2 imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import psycopg2: {e}")
        print("💡 Try: pip install psycopg2-binary")
        return False
    
    # Get token
    token = test_azure_ad_token()
    if not token:
        print("❌ Cannot test database connection without valid token")
        return False
    
    print(f"🔌 Attempting to connect to PostgreSQL...")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    print(f"   Port: {DB_CONFIG['port']}")
    print(f"   SSL Mode: {DB_CONFIG['sslmode']}")
    
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=token,
            port=DB_CONFIG['port'],
            sslmode=DB_CONFIG['sslmode'],
            connect_timeout=15
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Database connection successful!")
        print(f"🐘 PostgreSQL version: {version[0]}")
        
        # Test permissions
        cursor.execute("SELECT current_user, current_database();")
        user_info = cursor.fetchone()
        print(f"👤 Connected as user: {user_info[0]}")
        print(f"🗄️ Connected to database: {user_info[1]}")
        
        # Check if tables exist
        cursor.execute("""
            SELECT COUNT(*) as table_count 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        print(f"📊 Found {table_count} tables in the database")
        
        if table_count > 0:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name 
                LIMIT 10
            """)
            tables = cursor.fetchall()
            print("📋 Sample tables:")
            for table in tables:
                print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        
        error_str = str(e).lower()
        if "authentication failed" in error_str:
            print("💡 Authentication failed. Possible issues:")
            print("   - User not configured as Azure AD admin on PostgreSQL server")
            print("   - User doesn't have login permissions to the database")
            print("   - Token might be invalid or expired")
        elif "ssl" in error_str:
            print("💡 SSL connection issue:")
            print("   - Check if SSL is properly configured on the server")
            print("   - Verify SSL certificates")
        elif "timeout" in error_str or "refused" in error_str:
            print("💡 Connection issue:")
            print("   - Check if server is running and accessible")
            print("   - Verify firewall settings allow your IP")
            print("   - Check if the server name is correct")
        elif "database" in error_str:
            print("💡 Database issue:")
            print("   - Check if the database 'lego' exists")
            print("   - Verify user has access to this database")
            
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"Exception type: {type(e).__name__}")
        return False

def main():
    """Main diagnostic function"""
    print("🧪 Azure AD Authentication Diagnostic Tool for LEGO Manager")
    print("=" * 60)
    
    # Run all tests
    cli_ok = test_azure_cli_login()
    identity_ok = test_azure_identity_import()
    
    if not identity_ok:
        print("\\n❌ Cannot proceed without Azure Identity library")
        return False
    
    db_ok = test_postgresql_connection()
    
    print("\\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print(f"Azure CLI Login: {'✅ Success' if cli_ok else '❌ Failed'}")
    print(f"Azure Identity Library: {'✅ Success' if identity_ok else '❌ Failed'}")
    print(f"Database Connection: {'✅ Success' if db_ok else '❌ Failed'}")
    
    if db_ok:
        print("\\n🎉 All tests passed! Your LEGO Manager app should work with Azure AD authentication.")
        print("\\n🚀 You can now start your Flask app with:")
        print("   python app.py")
    else:
        print("\\n❌ Some tests failed. Please address the issues above.")
        print("\\n💡 Common solutions:")
        print("1. Login to Azure CLI: az login")
        print("2. Install missing packages: pip install azure-identity psycopg2-binary")
        print("3. Check your PostgreSQL server firewall settings")
        print("4. Verify your user is configured as Azure AD admin on the PostgreSQL server")
        print("5. Make sure the database 'lego' exists and you have access")
    
    return db_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)