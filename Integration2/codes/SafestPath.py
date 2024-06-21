import networkx as nx
import pandas as pd
from PIL import Image, ImageDraw
import os


# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)

# Find the index of the "Integration2" part in the path
integration2_index = current_file_path.find("Integration2")

# Extract up to the end of "Integration2\\" (note the addition to include the folder name itself)
default_path = current_file_path[:integration2_index] + "Integration2\\"

f = open(f"{default_path}assets\\SafestPath\\fire_room.txt", "r")
fire_room = f.read()
print(fire_room)

# Define the graph
G = nx.Graph()

# Add nodes for rooms, corridors, and EXITs
G.add_nodes_from([
    "lab 4", "library", "lab 5", "lab M", 
    "corridor (comp)", "corridor (main)", "corridor (first year)", 
    "EXIT(MultiP Hall)", "EXIT(Main Stairs)", "EXIT(MBA side)", "EXIT(first gate)"
])

# Add edges representing the connections between nodes
G.add_edges_from([
    ("lab 4", "corridor (comp)"),
    ("corridor (comp)", "EXIT(MultiP Hall)"),
    ("corridor (comp)", "EXIT(Main Stairs)"),
    ("library", "corridor (main)"), 
    ("corridor (main)", "EXIT(Main Stairs)"),
    ("corridor (main)", "corridor (first year)"),
    ("lab 5", "corridor (first year)"),
    ("lab M", "corridor (first year)"),
    ("corridor (first year)", "EXIT(MBA side)"),
    ("corridor (first year)", "EXIT(first gate)")
])


# Define the EXIT nodes
exits = ["EXIT(MultiP Hall)", "EXIT(MBA side)", "EXIT(first gate)","EXIT(Main Stairs)"]

# Remove the fire node and associated edges
G.remove_node(fire_room)

# Find and print the shortest path from each node to each EXIT
with open(f"{default_path}assets\\SafestPath\\escape_paths.txt", "w") as file:
    for start_node in G.nodes():
        for exit_node in exits:
            if exit_node in G and start_node in G:  # Check if both nodes exist
                try:
                    path = nx.shortest_path(G, source=start_node, target=exit_node)
                    output_line = f"Path from {start_node} to {exit_node}: {path}\n"
                    print(output_line.strip())
                    file.write(output_line)  # Write to file
                except nx.NetworkXNoPath:
                    # print(f"No path found from {start_node} to {exit_node}.")
                    continue
            else:
                # print(f"One or both of the nodes '{start_node}' or '{exit_node}' do not exist in the graph.")
                continue




# Read the room name from "fire_room.txt"
with open(f'{default_path}assets\\SafestPath\\fire_room.txt', 'r') as file:
    room_name = file.readline().strip()

# Load the Excel sheet
excel_path = f'{default_path}assets\\SafestPath\\coordinates.xlsx'  # Replace with the path to your Excel file
df = pd.read_excel(excel_path)

# Find the row with the matching room name and extract the coordinates
row = df.loc[df['A'] == room_name]
x = row['B'].values[0]
y = row['C'].values[0]

# Load the image
image_path = f'{default_path}assets\\SafestPath\\comp floor.jpg'
image = Image.open(image_path)

# Draw a red circle at the given coordinates
draw = ImageDraw.Draw(image)
radius = 10  # Radius of the circle
draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline='red', width=3,fill='red')

# Save the modified image to a new file
modified_image_path = f'{default_path}assets\\SafestPath\\FireAt.jpg'
image.save(modified_image_path)

# Provide the path to the modified image
modified_image_path

