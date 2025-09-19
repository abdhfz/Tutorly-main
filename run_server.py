#!/usr/bin/env python3
"""
Enhanced script to run the Tutorly Flask server with better configuration
"""
import os
import sys
import subprocess
import platform
import webbrowser
from pathlib import Path

def print_banner():
    """Print a nice startup banner"""
    banner = """
    ╭─────────────────────────────────────────╮
    │           🎓 TUTORLY SERVER 🎓          │
    │     AI-Powered Educational Platform     │
    ╰─────────────────────────────────────────╯
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['flask', 'flask_cors', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Installing requirements...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ All packages installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            return False
    else:
        print("✅ All required packages are installed")
        return True

def load_environment():
    """Load environment variables from .env file if it exists"""
    env_file = Path('.env')
    if env_file.exists():
        print("📁 Loading environment variables from .env file")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ Environment variables loaded")
    else:
        print("💡 No .env file found. Using default configuration.")
        print("   You can create a .env file from .env.example for custom settings")

def check_database():
    """Check if database file exists, create if necessary"""
    db_file = Path('tutorly.db')
    if db_file.exists():
        print(f"📊 Database found: {db_file.name} ({db_file.stat().st_size} bytes)")
    else:
        print("📊 Database will be created automatically on first run")

def get_server_config():
    """Get server configuration from environment or defaults"""
    config = {
        'host': os.environ.get('HOST', '0.0.0.0'),
        'port': int(os.environ.get('PORT', 8000)),
        'debug': os.environ.get('DEBUG', 'True').lower() == 'true',
        'flask_env': os.environ.get('FLASK_ENV', 'development')
    }
    return config

def open_browser(url, delay=2):
    """Open browser after a delay"""
    import threading
    import time
    
    def delayed_open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"🌐 Opened browser to {url}")
        except Exception as e:
            print(f"🌐 Could not open browser automatically: {e}")
            print(f"🌐 Please manually open: {url}")
    
    thread = threading.Thread(target=delayed_open)
    thread.daemon = True
    thread.start()

def print_startup_info(config):
    """Print server startup information"""
    print("\n🚀 Starting Tutorly Server...")
    print("=" * 50)
    print(f"🖥️  Host: {config['host']}")
    print(f"🔌 Port: {config['port']}")
    print(f"🐛 Debug: {config['debug']}")
    print(f"🌍 Environment: {config['flask_env']}")
    print("=" * 50)
    print(f"📱 Frontend: http://localhost:{config['port']}/static/")
    print(f"🔌 API Base: http://localhost:{config['port']}/api/")
    print(f"❤️  Health Check: http://localhost:{config['port']}/api/health")
    print("=" * 50)
    print("💡 Tips:")
    print("   • Open index.html in your browser for the frontend")
    print("   • Get your Gemini API key from: https://aistudio.google.com/app/apikey")
    print("   • Configure API settings in the web interface")
    print("   • Press Ctrl+C to stop the server")
    print("=" * 50)

def setup_static_files():
    """Set up static file serving if index.html exists"""
    static_dir = Path('static')
    index_file = Path('index.html')
    
    if index_file.exists():
        # Create static directory if it doesn't exist
        static_dir.mkdir(exist_ok=True)
        
        # Copy index.html to static directory for Flask serving
        static_index = static_dir / 'index.html'
        if not static_index.exists() or index_file.stat().st_mtime > static_index.stat().st_mtime:
            import shutil
            shutil.copy2(index_file, static_index)
            print(f"📋 Copied {index_file} to {static_index}")

def main():
    """Main function to start the server"""
    print_banner()
    
    # Check system requirements
    if not check_python_version():
        return 1
    
    if not check_requirements():
        return 1
    
    # Load configuration
    load_environment()
    config = get_server_config()
    
    # Check database
    check_database()
    
    # Setup static files
    setup_static_files()
    
    # Print startup information
    print_startup_info(config)
    
    # Set Flask environment variables
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = config['flask_env']
    
    # Open browser automatically in development
    if config['debug']:
        frontend_url = f"http://localhost:{config['port']}/static/"
        open_browser(frontend_url)
    
    try:
        # Import and run the Flask app
        from app import app, init_database
        
        # Initialize database
        print("📊 Initializing database...")
        init_database()
        print("✅ Database ready")
        
        print("\n🎯 Server is starting...\n")
        
        # Start the Flask development server
        app.run(
            host=config['host'],
            port=config['port'],
            debug=config['debug'],
            use_reloader=False  # Disable reloader to prevent double startup
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped gracefully")
        return 0
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        print("💡 Make sure app.py exists in the current directory")
        return 1
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)