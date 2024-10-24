import os
import csv
import re

# Output CSV file name
output_csv = 'simulation_data.csv'

# Regex pattern to find files named "#_results.txt"
file_pattern = re.compile(r'(\d+)_results\.txt')

# Regex pattern to capture all the simulation parameters
parameters_pattern = re.compile(
    r'Simulation Index:\s*([\d.]+).*?Reynolds Number:\s*([\d.]+).*?Mesh Type:\s*(\w+).*?Element Polynomial Order:\s*([\d.]+).*?Control Amplitude:\s*([\d.]+).*?Control Frequency:\s*([\d.]+).*?Control Balance:\s*([\d.]+).*?Timestep:\s*([\d.]+)',
    re.DOTALL
)

# Regex pattern to capture all the statistics (average, median, etc.)
statistics_pattern = re.compile(
    r'Statistics for (.*?) \(Last 25% of Data\):.*?Average:\s*(-?\d+\.\d+).*?Median:\s*(-?\d+\.\d+).*?Minimum:\s*(-?\d+\.\d+).*?Maximum:\s*(-?\d+\.\d+).*?Standard Deviation:\s*(-?\d+\.\d+).*?25th Percentile:\s*(-?\d+\.\d+).*?75th Percentile:\s*(-?\d+\.\d+)',
    re.DOTALL
)

# ========== ADJUST THESE LISTS ========== #

# Simulation parameters to include
included_parameters = [
    'Simulation Index', 'Reynolds Number', 'Mesh Type', 'Element Polynomial Order', 
    'Control Amplitude', 'Control Frequency', 'Control Balance', 'Timestep'
]

# Statistics sections to include
included_sections = [
    'Internal Kinetic Energy', 'Pressure Outlet Upper', 'Pressure Outlet Lower',
    'Upper Outlet Flow', 'Lower Outlet Flow', 'System Gain'
]
# 'Power Stream (Q_{stream})', 'Upper Control Jet (Q_{C1})', 'Lower Control Jet (Q_{C2})',

# Specific statistics to include (you can exclude any by removing it from this list)
included_stats = [
    'Average', 'Median', 'Standard Deviation', 
]

#  'Minimum', 'Maximum', '25th Percentile', '75th Percentile'

# ========== NO NEED TO MODIFY BELOW ========== #

# Map of simulation parameters to the order they appear in the text file
parameter_keys = {
    'Simulation Index': 0, 'Reynolds Number': 1, 'Mesh Type': 2, 'Element Polynomial Order': 3, 
    'Control Amplitude': 4, 'Control Frequency': 5, 'Control Balance': 6, 'Timestep': 7
}

# List to store extracted data
data = []

# Walk through the current directory and subdirectories
for root, dirs, files in os.walk('.'):
    for file in files:
        # Check if file matches the "#_results.txt" pattern
        match = file_pattern.match(file)
        if match:
            file_number = match.group(1)  # Extract the number from the file name
            file_path = os.path.join(root, file)

            # Open and read the file
            with open(file_path, 'r') as f:
                content = f.read()

                # Extract simulation parameters
                parameters_match = re.search(parameters_pattern, content)
                if parameters_match:
                    parameters = parameters_match.groups()

                # Extract statistics for all sections
                stats_matches = re.findall(statistics_pattern, content)

                # Create a dictionary to store stats by section
                stats_dict = {}
                for section, avg, median, min_val, max_val, std_dev, p25, p75 in stats_matches:
                    stats_dict[section] = {
                        'Average': avg,
                        'Median': median,
                        'Minimum': min_val,
                        'Maximum': max_val,
                        'Standard Deviation': std_dev,
                        '25th Percentile': p25,
                        '75th Percentile': p75
                    }

                # Combine all the data for this file into a row
                row = [file_number]

                # Append simulation parameters based on the included_parameters list
                for param in included_parameters:
                    row.append(parameters[parameter_keys[param]])

                # Append statistics for each included section (if found)
                for section in included_sections:
                    if section in stats_dict:
                        for stat in included_stats:
                            row.append(stats_dict[section][stat])
                    else:
                        # Fill with empty values if section not found
                        row += [''] * len(included_stats)

                data.append(row)

# Sort the data by file number
data.sort(key=lambda x: int(x[0]))

# Define headers for the CSV
headers = ['File Number'] + included_parameters

# Add headers for each included statistics section
for section in included_sections:
    for stat in included_stats:
        headers.append(f'{section} {stat}')

# Write the extracted data to the CSV file
with open(output_csv, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    # Write the header
    writer.writerow(headers)

    # Write each row of data
    for row in data:
        writer.writerow(row)

print(f"Data successfully written to {output_csv}")
