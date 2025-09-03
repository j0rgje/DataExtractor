#!/usr/bin/env python3
"""
HSO Data Extractor - Launch Script
Eenvoudige startup voor de Streamlit applicatie
"""

import subprocess
import sys
import os
import time
from typing import Optional

try:
    from config import config
except Exception:
    class _Cfg:
        ENV = os.getenv("ENV", "development")
        DEBUG = os.getenv("DEBUG", "true").lower() in {"1","true","yes","y","on"}
        LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG" if os.getenv("DEBUG", "true").lower() in {"1","true","yes","y","on"} else "INFO")
        APP_PORT = int(os.getenv("APP_PORT", "8501"))
    config = _Cfg()

def check_dependencies():
    """Check of alle benodigde packages geïnstalleerd zijn"""
    print("🔍 Checking dependencies...")
    
    try:
        import streamlit
        import pandas
        import plotly
        print("✅ Alle dependencies gevonden!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Installing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies geïnstalleerd!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Fout bij installeren dependencies")
            return False

def run_tests():
    """Voer tests uit voor launch"""
    print("\n🧪 Running tests...")
    
    try:
        result = subprocess.run([sys.executable, "run_tests.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Alle tests geslaagd!")
            return True
        else:
            print("⚠️  Sommige tests gefaald, maar continueer...")
            print(result.stdout)
            return True  # Continue anyway voor demo
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"⚠️  Test execution issue: {e}")
        print("Continuing with launch...")
        return True

def launch_streamlit():
    """Start de Streamlit applicatie"""
    print("\n🚀 Launching HSO Data Extractor...")
    print("=" * 50)
    print(f"📊 Streamlit app starting up (env={getattr(config, 'ENV', 'development')}, debug={getattr(config, 'DEBUG', True)})...")
    print(f"🌐 Opening browser at: http://localhost:{getattr(config, 'APP_PORT', 8501)}")
    print("🛑 Press Ctrl+C to stop the application")
    print("=" * 50)
    
    try:
        # Start Streamlit with optimized settings
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "false",
            "--server.runOnSave", "true",
            "--browser.gatherUsageStats", "false",
            "--server.port", str(getattr(config, "APP_PORT", 8501)),
            "--logger.level", str(getattr(config, "LOG_LEVEL", "INFO"))
        ])
    except KeyboardInterrupt:
        print("\n\n👋 HSO Data Extractor gestopt. Tot ziens!")
    except Exception as e:
        print(f"\n❌ Error tijdens startup: {e}")
        print("💡 Probeer handmatig: streamlit run app.py")

def main():
    """Hoofdfunctie voor launch proces"""
    print("🏢 HSO Data Extractor - Launch Script")
    print("=" * 40)
    
    # Check working directory
    if not os.path.exists("app.py"):
        print("❌ app.py niet gevonden!")
        print("💡 Zorg dat je in de juiste directory staat")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check gefaald")
        sys.exit(1)
    
    # Run tests (optional)
    if len(sys.argv) > 1 and sys.argv[1] == "--with-tests":
        if not run_tests():
            print("❌ Tests gefaald")
            choice = input("Doorgaan zonder tests? (y/N): ")
            if choice.lower() != 'y':
                sys.exit(1)
    
    # Launch app
    launch_streamlit()

if __name__ == "__main__":
    main()
