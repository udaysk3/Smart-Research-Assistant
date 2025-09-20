#!/usr/bin/env python3
"""
Smart Research Assistant - Setup Script
Automated setup for the complete Smart Research Assistant system
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd
        )
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    try:
        python_version = subprocess.check_output(["python", "--version"], text=True).strip()
        print(f"✅ Python: {python_version}")
    except:
        print("❌ Python not found. Please install Python 3.8+")
        return False
    
    # Check Node.js
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        print(f"✅ Node.js: {node_version}")
    except:
        print("❌ Node.js not found. Please install Node.js 16+")
        return False
    
    # Check npm
    try:
        npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
        print(f"✅ npm: {npm_version}")
    except:
        print("❌ npm not found. Please install npm")
        return False
    
    return True

def setup_backend():
    """Set up the backend"""
    print("\n🚀 Setting up backend...")
    
    # Create virtual environment
    if not run_command("python -m venv venv", "Creating virtual environment", "backend"):
        return False
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python dependencies", "backend"):
        return False
    
    # Create .env file if it doesn't exist
    env_file = Path("backend/.env")
    if not env_file.exists():
        env_example = Path("backend/env.example")
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
            print("⚠️  Please edit backend/.env with your API keys")
        else:
            print("❌ env.example not found")
            return False
    
    # Initialize database
    if not run_command(f"{pip_cmd} -c \"from models.database import init_database; init_database()\"", "Initializing database", "backend"):
        print("⚠️  Database initialization failed, but continuing...")
    
    return True

def setup_frontend():
    """Set up the frontend"""
    print("\n🚀 Setting up frontend...")
    
    if not run_command("npm install", "Installing Node.js dependencies", "frontend"):
        return False
    
    return True

def create_startup_scripts():
    """Create startup scripts for easy development"""
    print("\n📝 Creating startup scripts...")
    
    # Backend startup script
    backend_script = """#!/bin/bash
echo "🚀 Starting Smart Research Assistant Backend..."
cd backend
source venv/bin/activate
python main.py
"""
    
    with open("start_backend.sh", "w") as f:
        f.write(backend_script)
    os.chmod("start_backend.sh", 0o755)
    
    # Frontend startup script
    frontend_script = """#!/bin/bash
echo "🚀 Starting Smart Research Assistant Frontend..."
cd frontend
npm start
"""
    
    with open("start_frontend.sh", "w") as f:
        f.write(frontend_script)
    os.chmod("start_frontend.sh", 0o755)
    
    # Windows batch files
    backend_bat = """@echo off
echo 🚀 Starting Smart Research Assistant Backend...
cd backend
venv\\Scripts\\activate
python main.py
pause
"""
    
    with open("start_backend.bat", "w") as f:
        f.write(backend_bat)
    
    frontend_bat = """@echo off
echo 🚀 Starting Smart Research Assistant Frontend...
cd frontend
npm start
pause
"""
    
    with open("start_frontend.bat", "w") as f:
        f.write(frontend_bat)
    
    print("✅ Startup scripts created")
    return True

def show_next_steps():
    """Show next steps to the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Edit backend/.env with your API keys:")
    print("   - GEMINI_API_KEY (required)")
    print("   - FLEXPRICE_API_KEY (required)")
    print("   - NEWS_API_KEY (optional)")
    print("   - SERPAPI_API_KEY (optional)")
    
    print("\n2. Start the services:")
    if os.name == 'nt':  # Windows
        print("   - Backend: double-click start_backend.bat")
        print("   - Frontend: double-click start_frontend.bat")
    else:  # Unix/Linux/macOS
        print("   - Backend: ./start_backend.sh")
        print("   - Frontend: ./start_frontend.sh")
    
    print("\n3. Access the application:")
    print("   - Frontend: http://localhost:3000")
    print("   - Backend API: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Database Admin: http://localhost:8080")
    
    print("\n4. Test the system:")
    print("   - Register a new account")
    print("   - Upload a document")
    print("   - Ask a research question")
    
    print("\n📚 Documentation:")
    print("   - Main README: README.md")
    print("   - Frontend: frontend/README.md")
    print("   - Backend: backend/README.md")

def main():
    """Main setup function"""
    print("🚀 Smart Research Assistant - Setup Script")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please install required tools.")
        sys.exit(1)
    
    # Set up backend
    if not setup_backend():
        print("\n❌ Backend setup failed.")
        sys.exit(1)
    
    # Set up frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed.")
        sys.exit(1)
    
    # Create startup scripts
    if not create_startup_scripts():
        print("\n❌ Failed to create startup scripts.")
        sys.exit(1)
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()

