import csv
import os
import shutil
import subprocess
import time
import math
import sys
import re

# --- Configuration ---
parameters_file = "parameters.csv"
viper_exe = "viper.exe"
libiomp5md_dll = "libiomp5md.dll"
max_iterations = 1000000
max_dt_reductions = 4

# --- Functions ---

def check_file_exists(file_path):
    """Check if a file exists without printing."""
    return os.path.isfile(file_path)

def create_run_directory(base_dir, parameters, index, dt):
    """Creates a unique, concisely named directory for each simulation run."""
    directory_name = f"{index + 1}_Re{parameters['Reynolds number']}_m{parameters['mesh_file']}_N{parameters['Polynomial order']}_A{parameters['Control amplitude']}_o{parameters['Control frequency']}_b{parameters['Control up-down balance']}_dt{dt}"
    full_path = os.path.join(base_dir, directory_name)

    if os.path.exists(full_path) and parameters['Override'] != 'y':
        print(f"Skipping index {index + 1} - directory '{directory_name}' already exists.")
        return None
    else:
        os.makedirs(full_path, exist_ok=True)
        return full_path

def modify_file(template_file, parameters, output_file, replacements):
    """Modifies a template file with the given parameters"""
    with open(template_file, "r") as f_in, open(output_file, "w") as f_out:
        for line in f_in:
            modified_line = line
            for key, value in replacements.items():
                if key in modified_line:
                    modified_line = modified_line.replace(key, str(value))
            f_out.write(modified_line)

def analyze_viper_output(stdout, stderr):
    """Analyzes the output from viper.exe and returns a summary if it crashed."""
    crash_indicators = [
        r"Huge value .* at index \d+ of \d+",
        r"\*\*\*\*\* Proc 0: Divergence in .* field\. \*\*\*\*\*",
        r"\*\*\*\*\* Viper terminating .* \*\*\*\*\*"
    ]
    
    crash_summary = []
    for line in stdout.split('\n') + stderr.split('\n'):
        for indicator in crash_indicators:
            if re.search(indicator, line):
                crash_summary.append(line.strip())
    
    if crash_summary:
        return "\n".join(crash_summary)
    return None

def run_viper(directory, macro_file, viper_path):
    """Runs viper.exe with the given macro file in the specified directory."""
    macro_path = os.path.join(directory, macro_file)
    
    if not check_file_exists(viper_path) or not check_file_exists(macro_path):
        return None, "Error: Required files not found"
    
    original_dir = os.getcwd()
    os.chdir(directory)
    with open(macro_file, 'r') as macro_input:
        try:
            process = subprocess.Popen([viper_path], stdin=macro_input, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            crash_summary = analyze_viper_output(stdout, stderr)
        except Exception as e:
            crash_summary = f"Error running Viper: {str(e)}"
        finally:
            os.chdir(original_dir)
    
    return process, crash_summary

def calculate_loops(dt, end_time):
    """Calculate the number of loops needed to reach the end time."""
    return math.ceil(end_time / (dt * 10))

def modify_macro_txt(template_file, parameters, output_file, dt):
    """Modifies the macro.txt template with the given parameters."""
    replacements = {
        "DT": dt,
        "STEP_COUNT": "10" if parameters.get('Verbose', 'y').lower() == 'y' else "500"
    }
    
    if 'Convergence criteria' in parameters:
        replacements["CRIT"] = parameters['Convergence criteria']
        replacements["LOOP_COUNT"] = max_iterations  # Arbitrarily large for convergence criteria
    elif 'End time' in parameters:
        end_time = float(parameters['End time'])
        loops = calculate_loops(dt, end_time)
        replacements["CRIT"] = "0"  # Disable convergence criteria
        replacements["LOOP_COUNT"] = str(loops)
    
    modify_file(template_file, parameters, output_file, replacements)

# --- Main Script ---

if __name__ == "__main__":
    original_directory = os.getcwd()
    viper_path = os.path.join(original_directory, viper_exe)

    required_files = [viper_exe, libiomp5md_dll, parameters_file, "viper.cfg", "macro.txt", "macro_animation.txt"]
    for file in required_files:
        if not check_file_exists(file):
            print(f"Error: {file} not found in the current directory.")
            sys.exit(1)

    with open(parameters_file, "r") as f:
        reader = csv.DictReader(f)
        next(reader) # Skip the description row

        for index, row in enumerate(reader):
            print(f"\nProcessing index {index + 1}")
            
            dt = float(row['Time step'])
            dt_reduction_count = 0
            
            while dt_reduction_count <= max_dt_reductions:
                directory = create_run_directory(original_directory, row, index, dt)
                if directory is None:
                    break

                modify_file(os.path.join(original_directory, "viper.cfg"), row, os.path.join(directory, "viper.cfg"), {
                    "REYNOLDS": row['Reynolds number'],
                    "MESH": row['mesh_file'],
                    "ORDER": row['Polynomial order'],
                    "AMP": row['Control amplitude'],
                    "FREQ": row['Control frequency'],
                    "BAL": row['Control up-down balance'],
                })

                modify_macro_txt(os.path.join(original_directory, "macro.txt"), row, os.path.join(directory, f"macro{row['Index']}.txt"), dt)

                modify_file(os.path.join(original_directory, "macro_animation.txt"), row, os.path.join(directory, f"macro_animation{row['Index']}.txt"), {
                    "DT": dt,
                    "LOOPS": row['Animation loops']
                })

                mesh_file = f"fluidic_amplifier_res_{row['mesh_file']}.msh"
                mesh_path = os.path.join(original_directory, mesh_file)
                if check_file_exists(mesh_path):
                    shutil.copy(mesh_path, os.path.join(directory, mesh_file))
                else:
                    print(f"Error: Mesh file {mesh_file} not found. Skipping this simulation.")
                    break

                print(f"Running static simulation for index {index + 1} with macro{row['Index']}.txt")
                process, crash_summary = run_viper(directory, f"macro{row['Index']}.txt", viper_path)
                if crash_summary:
                    if "try a smaller time step" in crash_summary.lower():
                        if dt_reduction_count < max_dt_reductions:
                            dt /= 2
                            dt_reduction_count += 1
                            print(f"Reducing time step to {dt} and retrying.")
                            continue
                        else:
                            print(f"Maximum number of time step reductions reached. Moving to next parameter set.")
                            break
                    else:
                        print(f"Simulation crashed. See crash_summary.txt in the output directory for details.")
                        break
                
                print(f"Running animation simulation for index {index + 1} with macro_animation{row['Index']}.txt")
                animation_process, animation_crash_summary = run_viper(directory, f"macro_animation{row['Index']}.txt", viper_path)
                if animation_crash_summary:
                    print(f"Animation crashed. See crash_summary.txt in the output directory for details.")

                break

    print("\nAll simulations completed.")