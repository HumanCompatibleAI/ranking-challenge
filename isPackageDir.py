import os

def check_init_py(root_dir):
    for root, dirs, files in os.walk(root_dir):
        # Filter out directories starting with a dot
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        # Check if __init__.py is present in the current directory
        if '__init__.py' not in files:
            print(f"without __init__.py: {root}")

if __name__ == "__main__":
    # Use the current directory as the root path
    root_path = os.getcwd()
    check_init_py(root_path)
