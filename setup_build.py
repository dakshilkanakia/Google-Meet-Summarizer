# setup_build_fixed.py - Fixed version without emoji issues
import os
import subprocess
import sys

def setup_environment():
    """Setup everything needed to build the executable"""
    
    print("Meeting Summarizer - Complete Setup")
    print("=" * 50)
    
    # Step 1: Install required packages
    print("Step 1: Installing required packages...")
    packages = [
        "google-generativeai",
        "pyinstaller"
    ]
    
    for package in packages:
        try:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
            print(f"   SUCCESS: {package} installed")
        except Exception as e:
            print(f"   ERROR: Failed to install {package}: {e}")
            return False
    
    # Step 2: Check required files
    print("\nStep 2: Checking required files...")
    required_files = [
        "meeting_summarizer.py",
        "vtt_parser.py", 
        "gemini_summarizer.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   FOUND: {file}")
        else:
            print(f"   MISSING: {file}")
            return False
    
    # Step 3: Create build script
    print("\nStep 3: Creating build script...")
    create_simple_build_script()
    
    # Step 4: Build executable
    print("\nStep 4: Building executable...")
    return build_executable_simple()

def create_simple_build_script():
    """Create a simplified build script"""
    build_script = '''import subprocess
import sys
import os

def build():
    try:
        # Simple PyInstaller command
        cmd = [
            "pyinstaller", 
            "--onefile",
            "--name=MeetingSummarizer",
            "--clean",
            "meeting_summarizer.py"
        ]
        
        print("Building executable...")
        subprocess.run(cmd, check=True)
        
        if os.path.exists("dist/MeetingSummarizer.exe"):
            print("SUCCESS: Executable created at dist/MeetingSummarizer.exe")
        else:
            print("ERROR: Build failed")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build()
'''
    
    try:
        with open("simple_build.py", "w", encoding='utf-8') as f:
            f.write(build_script)
        print("   SUCCESS: Build script created")
    except Exception as e:
        print(f"   ERROR: Could not create build script: {e}")

def build_executable_simple():
    """Build the executable with simple settings"""
    try:
        # Clean previous builds
        if os.path.exists("dist"):
            import shutil
            shutil.rmtree("dist")
        if os.path.exists("build"):
            import shutil
            shutil.rmtree("build")
            
        # Build command (simplified for compatibility)
        build_command = [
            "pyinstaller",
            "--onefile",                    # Single file
            "--name=MeetingSummarizer",     # Name
            "--clean",                      # Clean build
            "meeting_summarizer.py"         # Main file
        ]
        
        print("   Running PyInstaller...")
        result = subprocess.run(build_command, 
                              capture_output=True, 
                              text=True, 
                              check=True)
        
        # Check result
        exe_path = "dist/MeetingSummarizer.exe"
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"   SUCCESS: Executable created! ({file_size:.1f} MB)")
            print(f"   Location: {os.path.abspath(exe_path)}")
            return True
        else:
            print("   ERROR: Executable not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"   ERROR: Build failed")
        print(f"   Details: {e.stderr}")
        return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def create_distribution_package():
    """Create a complete package for distribution"""
    if not os.path.exists("dist/MeetingSummarizer.exe"):
        print("ERROR: No executable found to package")
        return
    
    print("\nStep 5: Creating distribution package...")
    
    # Create distribution folder
    dist_folder = "MeetingSummarizer_Distribution"
    if os.path.exists(dist_folder):
        import shutil
        shutil.rmtree(dist_folder)
    
    os.makedirs(dist_folder)
    
    # Copy executable
    import shutil
    shutil.copy("dist/MeetingSummarizer.exe", f"{dist_folder}/MeetingSummarizer.exe")
    
    # Create README
    readme_content = """# Meeting Summarizer

## How to Use:
1. Double-click MeetingSummarizer.exe to start
2. On first run, you'll need to setup your Google Gemini API key:
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Create new API key
   - Enter it in the app
3. Select your VTT files (Google Meet transcripts)
4. Click "AI Summarize"
5. Save the results

## System Requirements:
- Windows 10/11 or macOS
- Internet connection (for AI summarization)
- Google account (for free API key)

## Troubleshooting:
- If app doesn't start, try running as administrator
- If API key doesn't work, generate a new one
- For support, contact your IT administrator

Generated with Python + Google Gemini AI
"""
    
    try:
        with open(f"{dist_folder}/README.txt", "w", encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"   SUCCESS: Distribution package created: {dist_folder}/")
        print(f"   Contents:")
        print(f"      - MeetingSummarizer.exe")
        print(f"      - README.txt")
        
        print(f"\nCOMPLETE! Your supervisor can now:")
        print(f"   1. Copy the '{dist_folder}' folder to any computer")
        print(f"   2. Run MeetingSummarizer.exe")
        print(f"   3. No installation required!")
        
    except Exception as e:
        print(f"   ERROR: Could not create README: {e}")

if __name__ == "__main__":
    success = setup_environment()
    
    if success:
        create_distribution_package()
        print(f"\nAll done! Ready for distribution.")
    else:
        print(f"\nSetup failed. Please check the errors above.")