import os
import subprocess

def run_tecplot_export():
    # Get the current directory
    current_dir = os.getcwd()
    
    # Get all subdirectories
    subdirs = [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d))]
    
    # Path to tecplot_export.py
    tecplot_script = os.path.join(current_dir, 'tecplot_export.py')
    
    # Check if tecplot_export.py exists
    if not os.path.exists(tecplot_script):
        print(f"Error: {tecplot_script} not found in the current directory.")
        return
    
    # Iterate through all subdirectories
    for subdir in subdirs:
        # Full path of the subdirectory
        subdir_path = os.path.join(current_dir, subdir)
        
        print(f"Processing directory: {subdir}")
        
        # Change to the subdirectory
        os.chdir(subdir_path)
        
        # Run tecplot_export.py
        try:
            subprocess.run(['python', tecplot_script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running tecplot_export.py in {subdir}: {e}")
        
        # Change back to the original directory
        os.chdir(current_dir)

if __name__ == "__main__":
    run_tecplot_export()