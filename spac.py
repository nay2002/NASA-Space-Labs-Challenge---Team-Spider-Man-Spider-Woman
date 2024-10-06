import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

# Load the CSV file
csv_file = r"C:\Users\prabd\OneDrive\Desktop\spacedata.csv"
data = pd.read_csv(csv_file)

# Extract relevant columns for visualization
planet_names = data['pl_name'].head(30)  # Limiting to first 10 planets for visualization
distances = data['sy_dist'].head(30)  # Distance from Earth in parsecs

# Create or assume data columns for detailed planet information (mocking for now)
if 'habitability_percent' not in data.columns:
    data['habitability_percent'] = np.random.uniform(0, 100, len(data))  # Mock data for habitability
if 'sign_of_life' not in data.columns:
    data['sign_of_life'] = np.random.uniform(0, 10, len(data))  # Mock data for life signs
if 'water_presence' not in data.columns:
    data['water_presence'] = np.random.choice([True, False], len(data))  # Random water presence
if 'temperature' not in data.columns:
    data['temperature'] = np.random.uniform(-150, 50, len(data))  # Random temperature in Celsius

# Limit to first 10 planets
habitability = data['habitability_percent'].head(30)
life_signs = data['sign_of_life'].head(30)
water_presence = data['water_presence'].head(30)
temperature = data['temperature'].head(30)

# Convert distances from parsecs to light years (1 parsec ≈ 3.262 light years)
distances_ly = distances * 3.262

# Generate random angles for placing planets in 3D space
np.random.seed(42)  # For consistent random numbers
theta = np.random.uniform(0, 2 * np.pi, len(distances_ly))  # Random angle around Z-axis
phi = np.random.uniform(0, np.pi, len(distances_ly))  # Random angle from Z-axis

# Convert spherical coordinates (distance, theta, phi) to Cartesian (x, y, z)
planet_x = distances_ly * np.sin(phi) * np.cos(theta)
planet_y = distances_ly * np.sin(phi) * np.sin(theta)
planet_z = distances_ly * np.cos(phi)

# Generate random star positions spread across a larger 3D space (1000 random stars)
num_stars = 1000
star_distances = np.random.uniform(50, 1000, num_stars)  # Spread the stars across a larger range
star_theta = np.random.uniform(0, 2 * np.pi, num_stars)
star_phi = np.random.uniform(0, np.pi, num_stars)
star_x = star_distances * np.sin(star_phi) * np.cos(star_theta)
star_y = star_distances * np.sin(star_phi) * np.sin(star_theta)
star_z = star_distances * np.cos(star_phi)

# Create the Dash app
app = Dash(__name__)

# Define the layout with interactive options
app.layout = html.Div([
    dcc.Graph(
        id='planet-simulation',
        style={'height': '100vh', 'width': '100vw'},
        config={'scrollZoom': True}  # Enable scroll zoom for better interaction
    ),  # Full-screen graph
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0),  # Animation refresh rate
    dcc.Store(id='camera-store', data=None, storage_type='local'),  # Store camera position in localStorage
    dcc.Store(id='line-clicked-store', data=None),  # Store clicked line details
    html.Div(id='line-click-info', style={'color': 'white'})  # Div to show clicked line info
], style={'height': '100vh', 'width': '100vw', 'margin': '0', 'padding': '0'})  # Full-screen container

# Function to calculate estimated travel time based on distance
def calculate_travel_time(distance):
    speed_of_light = 1  # Assuming speed of light in light years per year
    return distance / speed_of_light  # Time in years

# Update the 3D plot dynamically and store the camera position in localStorage
@app.callback(
    [Output('planet-simulation', 'figure'),
     Output('camera-store', 'data')],
    [Input('interval-component', 'n_intervals'),
     Input('planet-simulation', 'relayoutData')],
    [State('camera-store', 'data')]
)
def update_planet_and_camera(n_intervals, relayoutData, stored_camera):
    # Orbital motion (simple circular orbit with time)
    orbital_speed = 0.01  # Control speed of orbit

    # Update planet positions based on the interval (animation)
    current_theta = theta + orbital_speed * n_intervals
    updated_x = distances_ly * np.sin(phi) * np.cos(current_theta)
    updated_y = distances_ly * np.sin(phi) * np.sin(current_theta)

    # Create Plotly 3D scatter plot
    fig = go.Figure()

    # Plot Earth at (0, 0, 0)
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=10, color='blue'),
        name='Earth'
    ))

    # Plot exoplanets with updated positions and show detailed hovertext with line breaks
    fig.add_trace(go.Scatter3d(
        x=updated_x, y=updated_y, z=planet_z,
        mode='markers+text',
        marker=dict(size=5, color='red'),
        text=planet_names,
        hovertext=[f'<b>{name}</b><br>'
                   f'Distance: {dist:.2f} light years<br>'
                   f'Habitability: {habit:.2f}%<br>'
                   f'Signs of Life: {life:.2f}%<br>'
                   f'Water: {"Yes" if water else "No"}<br>'
                   f'Temperature: {temp:.2f}°C'
                   for name, dist, habit, life, water, temp in
                   zip(planet_names, distances_ly, habitability, life_signs, water_presence, temperature)],
        hoverinfo="text",  # Display custom hovertext
        textposition="top center",
        name='Exoplanets'
    ))

    # Plot random stars spread throughout the 3D space
    fig.add_trace(go.Scatter3d(
        x=star_x, y=star_y, z=star_z,
        mode='markers',
        marker=dict(size=1, color='white', opacity=0.8),
        name='Stars',
        hoverinfo='none'  # No hover text for stars
    ))

    # Add lines from Earth to each exoplanet (Navigation paths)
    for i in range(len(planet_x)):
        travel_time = calculate_travel_time(distances_ly[i])
        fig.add_trace(go.Scatter3d(
            x=[0, updated_x[i]], y=[0, updated_y[i]], z=[0, planet_z[i]],
            mode='lines',
            line=dict(color='white', width=2),
            hoverinfo='text',  # Only show hover information when hovering
            hovertext=f'Time to {planet_names[i]}: {travel_time:.2f} years',  # Hover details
            showlegend=False,  # Hide lines from legend
            name=f'To {planet_names[i]}'  # Name the line (useful for clicks)
        ))

    # Default camera position
    default_camera = {
        'eye': dict(x=0.002, y=0.002, z=0.002),
        'center': dict(x=0, y=0, z=0),
        'up': dict(x=0, y=0, z=1)
    }

    # Use relayoutData for camera if available, otherwise fall back to stored camera
    if relayoutData and 'scene.camera' in relayoutData:
        camera_position = relayoutData['scene.camera']
    elif stored_camera:
        camera_position = stored_camera
    else:
        camera_position = default_camera

    fig.update_layout(
        scene=dict(
            xaxis_title='X (Light Years)',
            yaxis_title='Y (Light Years)',
            zaxis_title='Z (Light Years)',
            xaxis=dict(backgroundcolor='black', showgrid=False, zeroline=False),
            yaxis=dict(backgroundcolor='black', showgrid=False, zeroline=False),
            zaxis=dict(backgroundcolor='black', showgrid=False, zeroline=False),
            camera=camera_position  # Use the updated camera position
        ),
        paper_bgcolor='black',  # Set the overall background to black
        title={
            'text': "Interactive Space Simulation: Earth and Nearby Exoplanets",
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(color='white')
        },
        font=dict(color='white'),  # Change font color to white for better visibility
        showlegend=True
    )

    return fig, camera_position

# Callback for handling clicks on the lines
@app.callback(
    Output('line-clicked-store', 'data'),
    Input('planet-simulation', 'clickData')
)
def show_clicked_line_details(clickData):
    if clickData and 'points' in clickData:
        # Extract the name of the planet or the travel time info from clickData
        clicked_point = clickData['points'][0]
        if 'hovertext' in clicked_point:
            return clicked_point['hovertext']  # Store clicked line's hovertext (travel time, planet name)

    return None

# Callback to update the div with the clicked line info
@app.callback(
    Output('line-click-info', 'children'),
    Input('line-clicked-store', 'data')
)
def update_click_info(data):
    if data:
        return f'Details: {data}'
    return 'Click on a line to see details...'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)