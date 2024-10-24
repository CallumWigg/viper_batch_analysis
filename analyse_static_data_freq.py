import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Set up directory and file paths
full_path = os.getcwd()
folder_name = os.path.basename(full_path)

# Helper function to extract values from folder names
def extract_value(string, pattern):
    match = re.search(pattern + r'([\d\.]+)', string)
    if match:
        return float(match.group(1))
    return None

# Extract simulation parameters
sim_index = extract_value(folder_name, r'(\d+)_Re')
reynolds_num = extract_value(folder_name, r'Re')
mesh_types = ['Low', 'Medium', 'High']
mesh_num = int(extract_value(folder_name, r'm'))
mesh = mesh_types[mesh_num - 1]
poly_order = extract_value(folder_name, r'N')
control_amplitude = extract_value(folder_name, r'A')
control_frequency = extract_value(folder_name, r'o')
control_balance = extract_value(folder_name, r'b')
timestep = extract_value(folder_name, r'dt')

# Parameters
output_dir = f'Simulation_{int(sim_index)}_Results'
os.makedirs(output_dir, exist_ok=True)

# Write simulation parameters to a text file
param_file = os.path.join(output_dir, f'{int(sim_index)}_results.txt')
with open(param_file, 'w') as f:
    f.write(f'Simulation Parameters:\n')
    f.write(f'Simulation Index: {sim_index}\n')
    f.write(f'Reynolds Number: {reynolds_num}\n')
    f.write(f'Mesh Type: {mesh}\n')
    f.write(f'Element Polynomial Order: {poly_order}\n')
    f.write(f'Control Amplitude: {control_amplitude:.4f}\n')
    f.write(f'Control Frequency: {control_frequency:.4f}\n')
    f.write(f'Control Balance: {control_balance:.4f}\n')
    f.write(f'Timestep: {timestep:.6f} s\n')

# Read the data files into pandas dataframes using 'sep' instead of 'delim_whitespace'
int_KE = pd.read_csv('int_KE.dat', sep='\s+')
pressure_outlet_upper = pd.read_csv('pressure_outlet_upper.dat', sep='\s+')
pressure_outlet_lower = pd.read_csv('pressure_outlet_lower.dat', sep='\s+')
flow_outlet_upper = pd.read_csv('flow_outlet_upper.dat', sep='\s+')
flow_outlet_lower = pd.read_csv('flow_outlet_lower.dat', sep='\s+')
flowrate = pd.read_csv('flowrate.dat', sep='\s+')

# Cull the last n_cull rows
n_cull = int(len(int_KE) * 0.05)
int_KE = int_KE.iloc[:-n_cull]
pressure_outlet_upper = pressure_outlet_upper.iloc[:-n_cull]
pressure_outlet_lower = pressure_outlet_lower.iloc[:-n_cull]
flow_outlet_upper = flow_outlet_upper.iloc[:-n_cull]
flow_outlet_lower = flow_outlet_lower.iloc[:-n_cull]
flowrate = flowrate.iloc[:-n_cull]

# Calculate window size based on 5-second average
desired_averaging_time = 5  # seconds
window_size = int(desired_averaging_time / timestep)  # timestep is already extracted earlier from folder name

# Make sure window size is reasonable (greater than 1)
if window_size < 2:
    window_size = 2  # Ensure we have at least a small window

# Calculate window size based on a smaller time window, e.g., 1 second
desired_gain_averaging_time = 1  # seconds for gain smoothing
gain_window_size = int(desired_gain_averaging_time / timestep)  # timestep is already extracted earlier

# Make sure window size is reasonable (greater than 1)
if gain_window_size < 2:
    gain_window_size = 2  # Ensure we have at least a small window

# Apply a rolling mean to the numerator to smooth the output differences
flow_diff = flow_outlet_lower['user_specified_function'] - flow_outlet_upper['user_specified_function']
rolling_numerator = flow_diff.rolling(window=gain_window_size, center=True).mean()

# Use the max amplitude (constant value) as the denominator
amplitude_input = control_amplitude  # This is already extracted from the folder name

# Calculate the signed rolling gain using the max amplitude
rolling_gain = rolling_numerator / amplitude_input

# Create plots
fig, axs = plt.subplots(2, 2, figsize=(15, 10))

# Plot 1: Internal Kinetic Energy
axs[0, 0].plot(int_KE['t'], int_KE['integral'], linewidth=2, label='Internal Kinetic Energy')
rolling_ke = int_KE['integral'].rolling(window=window_size, center=True).mean()  # Rolling mean based on calculated window
axs[0, 0].plot(int_KE['t'], rolling_ke, color='blue', linestyle='--', linewidth=1, alpha=0.5)  # Rolling average (no label here)
axs[0, 0].set_title('Internal Kinetic Energy vs Time')
axs[0, 0].set_xlabel('Time')
axs[0, 0].set_ylabel('Internal Kinetic Energy')
axs[0, 0].legend()
axs[0, 0].grid(True)

# Plot 2: System Gain (with smoothed rolling gain)
axs[0, 1].plot(flowrate['t'], rolling_gain, linewidth=2, label='Signed Rolling Gain (based on amplitude input)')
axs[0, 1].set_title('System Gain vs Time')
axs[0, 1].set_xlabel('Time')
axs[0, 1].set_ylabel('Signed Gain')
axs[0, 1].legend()
axs[0, 1].grid(True)

# Plot 3: Pressure Outlets
axs[1, 0].plot(pressure_outlet_upper['t'], pressure_outlet_upper['user_specified_function'], color='green', linewidth=2, label='Upper Outlet')
axs[1, 0].plot(pressure_outlet_lower['t'], pressure_outlet_lower['user_specified_function'], color='red', linewidth=2, label='Lower Outlet')

rolling_pressure_upper = pressure_outlet_upper['user_specified_function'].rolling(window=window_size, center=True).mean()
rolling_pressure_lower = pressure_outlet_lower['user_specified_function'].rolling(window=window_size, center=True).mean()

axs[1, 0].plot(pressure_outlet_upper['t'], rolling_pressure_upper, color='green', linestyle='--', linewidth=1, alpha=0.5)  # Rolling average
axs[1, 0].plot(pressure_outlet_lower['t'], rolling_pressure_lower, color='red', linestyle='--', linewidth=1, alpha=0.5)  # Rolling average

axs[1, 0].set_title('Pressure Outlets vs Time')
axs[1, 0].set_xlabel('Time')
axs[1, 0].set_ylabel('Pressure')
axs[1, 0].legend()
axs[1, 0].grid(True)

# Plot 4: Flow Outlets and Flowrates
axs[1, 1].plot(flow_outlet_upper['t'], flow_outlet_upper['user_specified_function'], color='blue', linewidth=2, label=r'$Q_{O1}$ (Upper)')
axs[1, 1].plot(flow_outlet_lower['t'], flow_outlet_lower['user_specified_function'], color='purple', linewidth=2, label=r'$Q_{O2}$ (Lower)')
axs[1, 1].plot(flowrate['t'], flowrate['bndry001'], color='green', linewidth=2, label=r'$Q_{stream}$')
axs[1, 1].plot(flowrate['t'], flowrate['bndry002'], color='cyan', linewidth=2, label=r'$Q_{C1}$ (Upper Control Jet)')
axs[1, 1].plot(flowrate['t'], flowrate['bndry003'], color='magenta', linewidth=2, label=r'$Q_{C2}$ (Lower Control Jet)')

rolling_flow_upper = flow_outlet_upper['user_specified_function'].rolling(window=window_size, center=True).mean()
rolling_flow_lower = flow_outlet_lower['user_specified_function'].rolling(window=window_size, center=True).mean()
rolling_bndry001 = flowrate['bndry001'].rolling(window=window_size, center=True).mean()
rolling_bndry002 = flowrate['bndry002'].rolling(window=window_size, center=True).mean()
rolling_bndry003 = flowrate['bndry003'].rolling(window=window_size, center=True).mean()

axs[1, 1].plot(flow_outlet_upper['t'], rolling_flow_upper, color='blue', linestyle='--', linewidth=1, alpha=0.5)  # Rolling average
axs[1, 1].plot(flow_outlet_lower['t'], rolling_flow_lower, color='purple', linestyle='--', linewidth=1, alpha=0.5)  # Rolling average
axs[1, 1].plot(flowrate['t'], rolling_bndry001, color='green', linestyle='--', linewidth=1, alpha=0.5)  # Rolling average
axs[1, 1].plot(flowrate['t'], rolling_bndry002, color='cyan', linestyle='--', linewidth=1, alpha=0.5)  # Rolling average
axs[1, 1].plot(flowrate['t'], rolling_bndry003, color='magenta', linestyle='--', linewidth=1, alpha=0.5)  # Rolling average

axs[1, 1].set_title('Flow Outlets and Flowrates vs Time')
axs[1, 1].set_xlabel('Time')
axs[1, 1].set_ylabel('Flow Rate')
axs[1, 1].legend()
axs[1, 1].grid(True)

# Add a single legend entry for the rolling average (dashed line, black)
fig.legend([plt.Line2D([0], [0], color='black', linestyle='--', linewidth=2)], 
           ['Rolling Average'], loc='lower center', bbox_to_anchor=(0.5, -0.05), 
           fancybox=True, shadow=True, ncol=1)

# Adjust layout to avoid title overlap and add more space at the top
plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust the figure's layout, reserve 5% space for the title

# Create a string with key simulation parameters for the title
sim_info = f'Re: {reynolds_num}, Mesh: {mesh}, N: {poly_order}, A: {control_amplitude}, f: {control_frequency}, b: {control_balance}, dt: {timestep}'

# Add a super-title (overall title) above the plots with more space
plt.suptitle(f'Data Analysis Results - Simulation {int(sim_index)}\n{sim_info}', fontsize=16)
plt.savefig(os.path.join(output_dir, (f'{int(sim_index)}_plot.png')), dpi=400)
plt.savefig(os.path.join(output_dir, (f'{int(sim_index)}_plot.pdf')))
plt.close(fig)

# Function to calculate statistics
def calculate_stats(data):
    return {
        'average': np.mean(data),
        'median': np.median(data),
        'minimum': np.min(data),
        'maximum': np.max(data),
        'std_dev': np.std(data),
        'percentile_25': np.percentile(data, 25),
        'percentile_75': np.percentile(data, 75),
    }

# Write statistics for each dataset
datasets = [
    (int_KE['integral'], 'Internal Kinetic Energy'),
    (pressure_outlet_upper['user_specified_function'], 'Pressure Outlet Upper'),
    (pressure_outlet_lower['user_specified_function'], 'Pressure Outlet Lower'),
    (flow_outlet_upper['user_specified_function'], 'Upper Outlet Flow'),
    (flow_outlet_lower['user_specified_function'], 'Lower Outlet Flow'),
    (flowrate['bndry001'], 'Power Stream (Q_{stream})'),
    (flowrate['bndry002'], 'Upper Control Jet (Q_{C1})'),
    (flowrate['bndry003'], 'Lower Control Jet (Q_{C2})'),
    (rolling_gain, 'System Gain')
]

with open(param_file, 'a') as f:
    for data, name in datasets:
        start_index = int(0.75 * len(data))
        last_25_percent_data = data[start_index:]
        stats = calculate_stats(last_25_percent_data)
        f.write(f'\nStatistics for {name} (Last 25% of Data):\n')
        f.write(f"Average: {stats['average']:.4f}\n")
        f.write(f"Median: {stats['median']:.4f}\n")
        f.write(f"Minimum: {stats['minimum']:.4f}\n")
        f.write(f"Maximum: {stats['maximum']:.4f}\n")
        f.write(f"Standard Deviation: {stats['std_dev']:.4f}\n")
        f.write(f"25th Percentile: {stats['percentile_25']:.4f}\n")
        f.write(f"75th Percentile: {stats['percentile_75']:.4f}\n")

# Save processed data
processed_data = {
    'int_KE': int_KE,
    'pressure_outlet_upper': pressure_outlet_upper,
    'pressure_outlet_lower': pressure_outlet_lower,
    'flow_outlet_upper': flow_outlet_upper,
    'flow_outlet_lower': flow_outlet_lower,
    'flowrate': flowrate,
    'gain': rolling_gain
}
processed_data_file = os.path.join(output_dir, 'processed_data.npz')
np.savez(processed_data_file, **processed_data)