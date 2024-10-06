# NASA-Space-Labs-Challenge---Team-Spider-Man-Spider-Woman
A 3-D simulation of the closest exoplanets around Earth in real-time, with navigation lines to each exo-planet from Earth. The navigation lines also tells us the user the time it would take to travel to the corresponding exoplanet. Moreover, each planet has its own pop-up description pane that depicts various characteristics of the planet, such as signs of life, temperature, water, etc. 

The stars have been kept in the background along with a real space-time field to further enhance the simulation giving the user a realistic feel. 

Note:
Make sure to change the file path before running the code, as the path provided in the code is an absolute path. 
# Load the CSV file
csv_file = r"C:\Users\prabd\OneDrive\Desktop\spacedata.csv" // Change this to the location where you have stored your file.
data = pd.read_csv(csv_file)
