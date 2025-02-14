import sys
import subprocess
import pkg_resources
import os
from pkg_resources import parse_version
import json

def create_watchdog_directory():
    """Create C:/watchdog directory if it doesn't exist"""
    directory = "C:/watchdog"
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory already exists: {directory}")
    except Exception as e:
        print(f"Error creating directory {directory}: {e}")
        sys.exit(1)

def check_python_version():
    """Verify Python version is 3.12.2 or later"""
    required_version = parse_version("3.12.2")
    current_version = parse_version(sys.version.split()[0])
    
    if current_version < required_version:
        print(f"Error: Python {required_version} or later is required")
        print(f"Current Python version: {current_version}")
        sys.exit(1)
    
    print(f"Python version check passed: {current_version}")

def parse_requirements():
    """Parse package requirements from config.json"""
    try:
        with open('config/config.json', 'r') as file:
            config = json.load(file)
            if 'dependencies' in config:
                return [f"{pkg}=={ver}" for pkg, ver in config['dependencies'].items()]
            else:
                print("Error: No dependencies found in config.json")
                sys.exit(1)
    except FileNotFoundError:
        print("Error: config.json not found in config directory")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json")
        sys.exit(1)

def install_packages(packages):
    """Install required packages using pip"""
    print("\nInstalling required packages...")
    
    for package in packages:
        try:
            print(f"\nInstalling {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            sys.exit(1)

def verify_installations(packages):
    """Verify that all packages were installed correctly"""
    print("\nVerifying installations...")
    
    for package_spec in packages:
        package = package_spec.split('==')[0]  # Extract package name without version
        required_version = package_spec.split('==')[1]  # Extract required version
        try:
            installed_version = pkg_resources.get_distribution(package).version
            print(f"✓ {package} {installed_version} installed (required: {required_version})")
            
            # Optional warning if versions don't match
            if installed_version != required_version:
                print(f"  Note: Installed version differs from required version")
                
        except pkg_resources.DistributionNotFound:
            print(f"✗ {package} installation failed")
            sys.exit(1)

def main():
    print("Starting installation process...\n")

    # Creating watchdog environment
    create_watchdog_directory()
    
    # Check Python version
    check_python_version()
    
    # Get required packages
    packages = parse_requirements()
    
    # Install packages
    install_packages(packages)
    
    # Verify installations
    verify_installations(packages)
    
    print("\nInstallation completed successfully!")

if __name__ == "__main__":
    main()