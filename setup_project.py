# setup_project.py
import os

# Create project directory structure
directories = [
    'data',
    'static',
    'templates'
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

# Create empty files for the project
files = {
    'app.py': '',
    'generate_data.py': '',
    'static/styles.css': '',
    'static/script.js': '',
    'templates/index.html': '',
    'requirements.txt': ''
}

for file_path, content in files.items():
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"Created file: {file_path}")

print("\nProject structure setup complete!")
print("\nNext steps:")
print("1. Copy the provided code into each file")
print("2. Create a virtual environment: python -m venv venv")
print("3. Activate the virtual environment:")
print("   - Windows: venv\\Scripts\\activate")
print("   - macOS/Linux: source venv/bin/activate")
print("4. Install dependencies: pip install -r requirements.txt")
print("5. Generate sample data: python generate_data.py")
print("6. Run the application: python app.py")
print("7. Open your browser at: http://127.0.0.1:5000/")