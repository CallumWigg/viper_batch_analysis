import os
import subprocess

def run_data_analysis():
    # Get the current directory
    current_dir = os.getcwd()
    
    # Get all subdirectories
    subdirs = [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d))]
    
    # Path to analyse_static_data.py
    analysis_script = os.path.join(current_dir, 'analyse_static_data.py')
    
    # Check if analyse_static_data.py exists
    if not os.path.exists(analysis_script):
        print(f"Error: {analysis_script} not found in the current directory.")
        return
    
    # Iterate through all subdirectories
    for subdir in subdirs:
        # Full path of the subdirectory
        subdir_path = os.path.join(current_dir, subdir)
        
        print(f"Processing directory: {subdir}")
        
        # Change to the subdirectory
        os.chdir(subdir_path)
        
        # Run analyse_static_data.py
        try:
            subprocess.run(['python', analysis_script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running analyse_static_data.py in {subdir}: {e}")
        
        # Change back to the original directory
        os.chdir(current_dir)

if __name__ == "__main__":
    run_data_analysis()