import os
import re
import tecplot as tp
from tecplot.constant import ExportRegion, JPEGEncoding, PlotType

# Get the current folder name and extract the identifier
current_folder = os.path.basename(os.getcwd())
identifier = re.match(r'(\d+)_', current_folder)
if identifier:
    identifier = identifier.group(1)
else:
    identifier = "unknown"

# Create output folder
output_folder = f"Simulation_{identifier}_Results"
os.makedirs(output_folder, exist_ok=True)

# Function to save contour plot
def save_contour_plot(frame, var_index, var_name, show_mesh=False, show_vectors=False):
    try:
        # Set the active plot and apply necessary settings
        plot = tp.active_frame().plot()
        plot.show_mesh = show_mesh
        plot.show_contour = True
        plot.show_edge = False
        plot.show_shade = False
        plot.contour(0).variable_index = var_index
        plot.contour(0).colormap_name = "Sequential - Viridis"

        # Set axes limits
        plot.axes.x_axis.min = -9.56551
        plot.axes.x_axis.max = 19.3116
        plot.axes.y_axis.min = -7.5
        plot.axes.y_axis.max = 7.5
        plot.view.fit()  # Ensure the plot fits within the view
        
        # Configure the legend
        legend = plot.contour(0).legend
        legend.show = True
        legend.auto_resize = True
        legend.label_step = 10
        legend.overlay_bar_grid = False
        legend.position = (99, 70)  # Frame percentages

        tp.macro.execute_command('$!RedrawAll')  # Redraw to apply changes

        # Generate the file name based on the specified criteria
        mods = []
        if show_mesh:
            mods.append("msh")
        if show_vectors:
            mods.append("vect")
        
        mod_str = "_".join(mods) if mods else ""
        image_filename = f"{output_folder}/{identifier}_{'vel' if var_name == 'user_specified' else var_name}{'_' + mod_str if mod_str else ''}.jpeg"
        
        if os.path.exists(image_filename):
            print(f"File already exists: {image_filename}")
            return
        
        tp.export.save_jpeg(image_filename, width=3840, region=ExportRegion.CurrentFrame, supersample=2, quality=100, encoding=JPEGEncoding.Progressive)
        print(f"Saved: {image_filename}")
    except Exception as e:
        print(f"Error saving contour plot for {var_name}: {str(e)}")

# Process tec_out.plt file
try:
    dataset = tp.data.load_tecplot("tec_out.plt")
    #print("Successfully loaded tec_out.plt")
except Exception as e:
    print(f"Error loading tec_out.plt: {str(e)}")
    exit(1)

# Ensure we have a plot and apply initial settings
plot = tp.active_frame().plot()
plot.show_shade = False
plot.rgb_coloring.red_variable_index = 2
plot.rgb_coloring.green_variable_index = 2
plot.rgb_coloring.blue_variable_index = 2

# Execute the Pick and FrameControl commands from the macro
tp.macro.execute_command('''$!Pick AddAtPosition
  X = 4.15525291829
  Y = 0.530155642023
  ConsiderStyle = Yes''')
tp.macro.execute_command('''$!Pick AddAtPosition
  X = 5.5373540856
  Y = 0.25
  ConsiderStyle = Yes''')
tp.macro.execute_command('''$!FrameControl ActivateByNumber
  Frame = 1''')
tp.macro.execute_command('''$!Pick Shift
  X = 0
  Y = 3.2373540856
  PickSubposition = Top''')

variables = [
    #2,  # U 
    #3,  # V 
    #4,  # P 
    #5,  # vort_z 
    6,  # user_specified
    7   # psi
]  
var_names = [
    #"U", 
    #"V", 
    #"P", 
    #"vort_z", 
    "user_specified", 
    "psi"
]

# Generating contour plots for each variable
for var_index, var_name in zip(variables, var_names):
    if var_index < dataset.num_variables:
        save_contour_plot(0, var_index, var_name, show_mesh=False)  # All without mesh
    else:
        print(f"Warning: Variable index {var_index} is out of range. Skipping.")

# Special cases for user_specified and psi
user_specified_index = 6
save_contour_plot(0, user_specified_index, "vel", show_mesh=True)

# Psi with and without U/V vectors
psi_index = 7
# Set U and V vectors for psi
tp.active_frame().plot(PlotType.Cartesian2D).vector.u_variable_index = 2
tp.active_frame().plot(PlotType.Cartesian2D).vector.v_variable_index = 3
tp.active_frame().plot().show_vector = True
save_contour_plot(0, psi_index, "psi_vec", show_mesh=False)

# Now, psi without vectors
tp.active_frame().plot().show_vector = False
save_contour_plot(0, psi_index, "psi_vec", show_mesh=False)

# Animation Logic for each contour variable
for var_index, var_name in zip(variables, var_names):
    animation_files = sorted([f for f in os.listdir() if f.startswith("tec_animation_frame_") and f.endswith(".plt")])

    if animation_files:
        print(f"Found {len(animation_files)} animation frames for {var_name}.")
        animation_filename = f'{output_folder}/{identifier}_{"vel" if var_name == "user_specified" else var_name}_anim.mp4' 
        if os.path.exists(animation_filename):
            print(f"Animation file already exists: {animation_filename}")
            continue
        try:
            # Import each animation frame into a new layout
            for frame_file in animation_files:
                tp.data.load_tecplot(frame_file, reset_style=False)

                # Set the viewport similar to static images
                plot = tp.active_frame().plot()
                plot.show_mesh = False
                plot.show_contour = True
                plot.show_edge = True
                plot.show_shade = False
                plot.contour(0).variable_index = var_index  # Set to current variable
                plot.contour(0).colormap_name = "Sequential - Viridis"

                # Set axes limits
                plot.axes.x_axis.min = -9.56551
                plot.axes.x_axis.max = 19.3116
                plot.axes.y_axis.min = -7.5
                plot.axes.y_axis.max = 7.5
                plot.view.fit()  # Ensure the plot fits within the view

                # Configure the legend
                legend = plot.contour(0).legend
                legend.show = True
                legend.auto_resize = True
                legend.label_step = 10
                legend.overlay_bar_grid = False
                legend.position = (99, 70)  # Frame percentages

                tp.macro.execute_command('$!RedrawAll')  # Redraw to apply changes

            # Export animation settings
            tp.macro.execute_command('''$!ExportSetup 
              ExportFormat = MPEG4''')
            tp.macro.execute_command('''$!ExportSetup 
              ImageWidth = 3840''')  # Set to 3840 as requested
            tp.macro.execute_command('''$!ExportSetup 
              UseSuperSampleAntiAliasing = Yes''')
            tp.macro.execute_command(f'''$!ExportSetup 
              ExportFName = '{animation_filename}' ''')

            # Animate the frames
            tp.macro.execute_command('''$!AnimateZones 
              ZoneAnimationMode = StepByNumber
              Start = 1
              End = {}  # Use len(animation_files) here
              Skip = 1
              CreateMovieFile = Yes
              LimitScreenSpeed = Yes
              MaxScreenSpeed = 12'''.format(len(animation_files))) 
            
            print(f"Animation for {var_name} exported successfully.")
        except Exception as e:
            print(f"Error processing animation frames for {var_name}: {str(e)}")
    else:
        print(f"No animation frames found for {var_name}.")

print("Processing complete. Check the output folder for results.")