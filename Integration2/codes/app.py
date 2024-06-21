import streamlit as st
from PIL import Image
import os
import networkx as nx
import matplotlib.pyplot as plt

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)

# Find the index of the "Integration2" part in the path
integration2_index = current_file_path.find("Integration2")

# Extract up to the end of "Integration2\\" (note the addition to include the folder name itself)
default_path = current_file_path[:integration2_index] + "Integration2\\"

# Function from the first script
def load_escape_paths():
    paths = {}
    with open(f"{default_path}assets\\SafestPath\\escape_paths.txt", "r") as file:
        for line in file:
            parts = line.strip().split(": ")
            if len(parts) == 2:
                src_dest, path_str = parts
                src, dest = src_dest[5:].split(" to ")
                path_list = path_str.strip("[]").replace("'", "").split(", ")
                if src not in paths:
                    paths[src] = {}
                paths[src][dest] = path_list
    return paths

def load_image(image_name):
    folder_path = f"{default_path}assets\\SafestPath"  # Replace with your images folder path
    image_path = os.path.join(folder_path, f"{image_name}.jpg")  # Adjust file extension if necessary
    if os.path.exists(image_path):
        return Image.open(image_path)
    else:
        return None  # Return None if the image does not exist
    
def construct_floor_plan_data(escape_paths):
    floor_plan_data = {}
    for src, dest_paths in escape_paths.items():
        for dest, path in dest_paths.items():
            for i in range(len(path)-1):
                if path[i] not in floor_plan_data:
                    floor_plan_data[path[i]] = []
                if path[i+1] not in floor_plan_data[path[i]]:
                    floor_plan_data[path[i]].append(path[i+1])

                if path[i+1] not in floor_plan_data:
                    floor_plan_data[path[i+1]] = []
                if path[i] not in floor_plan_data[path[i+1]]:
                    floor_plan_data[path[i+1]].append(path[i])
    return floor_plan_data


node_coordinates = {
    "lab 4": (103.0909, 403.2879),
    "library": (350.3333, 395.8333),
    "lab 5": (175.1515, 275.3182),
    "lab M": (340.3939, 165.9848),
    "corridor (comp)": (152.7879, 374.7121),
    "corridor (main)": (275.7879, 290.2273),
    "corridor (first year)": (301.8788, 214.4394),
    "EXIT(MultiP Hall)": (44.69697, 373.4697),
    "EXIT(Main Stairs)": (244.7273, 346.1364),
    "EXIT(MBA side)": (167.69697, 49.19697),
    "EXIT(first gate)": (417.4242, 252.9545)
}


def display_custom_floor_plan():
    st.title("Custom Floor Plan Display")

    # Display the custom floor plan image
    custom_floor_plan_image_path = f"{default_path}assets\\SafestPath\\fireAt.jpg"
    custom_floor_plan_image = Image.open(custom_floor_plan_image_path)
    st.image(custom_floor_plan_image, use_column_width=True, caption="Custom Floor Plan")


    # Load escape paths
    escape_paths = load_escape_paths()
    floor_plan_data = construct_floor_plan_data(escape_paths)

    if escape_paths:
        src_options = list(escape_paths.keys())
        selected_src = st.selectbox("Select Source", src_options)

        if selected_src in escape_paths:
            dest_options = list(escape_paths[selected_src].keys())
            selected_dest = st.selectbox("Select Destination", dest_options)

            if selected_dest:
                path_list = escape_paths[selected_src][selected_dest]
                formatted_path = " -> ".join(path_list)
                st.write(f"Path from {selected_src} to {selected_dest}: {formatted_path}")

                # Create a graph using NetworkX
                G = nx.Graph()
                for src, dests in floor_plan_data.items():
                    for dest in dests:
                        G.add_edge(src, dest)

                # Generate highlighted nodes and edges based on the path list
                highlighted_nodes = path_list
                highlighted_edges = [(path_list[i], path_list[i+1]) for i in range(len(path_list)-1)]

                # Draw the graph on the image using Matplotlib
                fig, ax = plt.subplots()
                ax.imshow(custom_floor_plan_image)

                # Draw nodes
                for node, (x, y) in node_coordinates.items():
                    color = 'red' if node in highlighted_nodes else 'lightblue'
                    ax.scatter(x, y, s=100, c=color, edgecolors='black', linewidths=2, label=node)

                # Draw edges
                for edge in G.edges():
                    start = node_coordinates[edge[0]]
                    end = node_coordinates[edge[1]]
                    color = 'red' if edge in highlighted_edges else 'gray'
                    ax.plot([start[0], end[0]], [start[1], end[1]], color=color, linestyle='-', linewidth=2)

                # Display the graph
                st.pyplot(fig)


def display_fire_escape_path_viewer():
    st.title("Fire Escape Path Viewer")

    f = open(f"{default_path}assets\\SafestPath\\fire_room.txt", "r")
    fire_room = f.read()

    # Load and display the static image
    static_image_path = "FireAt"  # Replace with your static image file name
    static_image = load_image(static_image_path)
    if static_image:
        st.image(static_image, caption=(f"Fire At ::: {fire_room}"), use_column_width=True)
    else:
        st.write("No static image available.")

    escape_paths = load_escape_paths()

    if escape_paths:
        src_options = list(escape_paths.keys())
        selected_src = st.selectbox("Select Source", src_options)

        if selected_src in escape_paths:
            dest_options = list(escape_paths[selected_src].keys())
            selected_dest = st.selectbox("Select Destination", dest_options)

            if selected_dest:
                path_list = escape_paths[selected_src][selected_dest]
                formatted_path = " -> ".join(path_list)
                st.write(f"Path from {selected_src} to {selected_dest}: {formatted_path}")

                for location in path_list:
                    image = load_image(location)
                    if image:
                        st.image(image, caption=location, use_column_width=True)
                    else:
                        st.write(f"No image available for {location}")
    else:
        st.write("No escape paths available.")

# Sidebar options
sidebar_options = ["Fire Escape Path Viewer", "Custom Floor Plan Display"]
selected_option = st.sidebar.radio("Select an option", sidebar_options)

# Display the selected option
if selected_option == "Fire Escape Path Viewer":
    display_fire_escape_path_viewer()
elif selected_option == "Custom Floor Plan Display":
    display_custom_floor_plan()

