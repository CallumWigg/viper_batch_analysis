import os
import shutil

# Define the root directory and the destination directory
root_dir = os.getcwd()  # Change this to your actual root path
destination_dir = os.path.join(root_dir, "Frequency Results")

# Ensure the destination directory exists
if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

# Traverse through the root directory
for folder_name in os.listdir(root_dir):
    folder_path = os.path.join(root_dir, folder_name)

    # Check if it's a directory
    if os.path.isdir(folder_path):
        
        # Look for Simulation_X_Results inside each subfolder
        sim_results_folder = os.path.join(folder_path, "Simulation_" + folder_name.split('_')[0] + "_Results")
        
        # If the Simulation_X_Results folder exists
        if os.path.exists(sim_results_folder):
            # Construct the new name for the folder inside Frequency Results
            new_folder_name = f"Simulation_{folder_name}_Results"
            new_folder_path = os.path.join(destination_dir, new_folder_name)

            # Copy the Simulation_X_Results folder to Frequency Results with the new name
            print(f"Copying {sim_results_folder} to {new_folder_path} ...")
            shutil.copytree(sim_results_folder, new_folder_path)

print("All folders copied successfully!")
