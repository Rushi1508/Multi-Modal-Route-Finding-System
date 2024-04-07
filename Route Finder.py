import streamlit as st
import requests
import base64
import folium
from streamlit_folium import folium_static
import cv2
import numpy as np
import networkx as nx
from skimage.morphology import skeletonize
from skimage import img_as_bool
from PIL import Image
import matplotlib.pyplot as plt
import io
import tempfile
import os

# Function to geocode location name to latitude and longitude
def geocode_location(location_name):
    url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json"
    response = requests.get(url)
    if response.ok:
        data = response.json()
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
    return None

# Function to request route from OSRM, return route geometry, total distance, and estimated time
def get_route_geometry(start_location, goal_location):
    url = f"http://router.project-osrm.org/route/v1/driving/{start_location[1]},{start_location[0]};{goal_location[1]},{goal_location[0]}?overview=full&geometries=geojson"
    response = requests.get(url)
    if response.ok:
        data = response.json()
        if 'routes' in data and data['routes']:
            route = data['routes'][0]
            if 'geometry' in route and 'distance' in route and 'duration' in route:
                geometry = route['geometry']
                total_distance = route['distance'] / 1000  # Convert meters to kilometers
                estimated_time = route['duration'] / 60  # Convert seconds to minutes
                return geometry, total_distance, estimated_time
    return None, None, None

# Function to select points using Tkinter
def select_points(image_path):
    points = []

    def click_event(event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            if len(points) == 2:  # Capture only two points and then close the window
                cv2.destroyAllWindows()

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    cv2.imshow('Image', img)
    cv2.setMouseCallback('Image', click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return points

# Your other provided functions for image preprocessing and pathfinding
def preprocess_image(image):
    _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    return binary_image

def perform_skeletonization(binary_image):
    binary_image_bool = img_as_bool(binary_image)
    skeleton = skeletonize(binary_image_bool)
    return skeleton

def find_nodes_and_edges(skeleton):
    y, x = np.where(skeleton)
    points = np.column_stack((x, y))
    G = nx.Graph()
    for point in points:
        G.add_node(tuple(point))
    for point in points:
        neighbors = [
            tuple(point + np.array([-1, 0])),
            tuple(point + np.array([1, 0])),
            tuple(point + np.array([0, -1])),
            tuple(point + np.array([0, 1])),
            tuple(point + np.array([-1, -1])),
            tuple(point + np.array([-1, 1])),
            tuple(point + np.array([1, -1])),
            tuple(point + np.array([1, 1]))
        ]
        for neighbor in neighbors:
            if neighbor in G:
                G.add_edge(tuple(point), neighbor)
    return G

def euclidean_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def a_star_search(graph, start, goal):
    open_set = {start}
    came_from = {}
    g_score = {node: float('inf') for node in graph.nodes}
    g_score[start] = 0
    f_score = {node: float('inf') for node in graph.nodes}
    f_score[start] = euclidean_distance(start, goal)
    while open_set:
        current = min(open_set, key=lambda node: f_score[node])
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
        open_set.remove(current)
        for neighbor in graph.neighbors(current):
            tentative_g_score = g_score[current] + euclidean_distance(current, neighbor)
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + euclidean_distance(neighbor, goal)
                if neighbor not in open_set:
                    open_set.add(neighbor)
    return None

def closest_graph_node(graph, point):
    closest_node = None
    min_distance = float('inf')
    for node in graph.nodes:
        distance = np.sqrt((node[0] - point[0]) ** 2 + (node[1] - point[1]) ** 2)
        if distance < min_distance:
            closest_node = node
            min_distance = distance
    return closest_node

# Main Streamlit app function
def main():
    st.set_page_config(page_title="Combined Route Finder", layout="wide")
    st.title("Combined Route Finder")

    st.sidebar.header("Select Mode")
    mode = st.sidebar.radio("Mode", ("Text-based", "Image-based"))

    if mode == "Text-based":
        st.sidebar.subheader("Enter Locations")
        start_location_name = st.sidebar.text_input("Starting Location")
        goal_location_name = st.sidebar.text_input("Goal Location")
        
        if st.sidebar.button("Find Route"):
            start_location = geocode_location(start_location_name)
            goal_location = geocode_location(goal_location_name)

            if start_location and goal_location:
                geometry, total_distance, estimated_time = get_route_geometry(start_location, goal_location)

                if geometry:
                    m = folium.Map(location=start_location, zoom_start=10)
                    folium.Marker(start_location, icon=folium.Icon(color='green'), tooltip=start_location_name).add_to(m)
                    folium.Marker(goal_location, icon=folium.Icon(color='red'), tooltip=goal_location_name).add_to(m)
                    folium.features.GeoJson(geometry, style_function=lambda x: {'color': 'blue'}).add_to(m)
                    st.success("Route found! See the map below:")
                    st.subheader("Route Statistics:")
                    st.write(f"Total Distance: {total_distance:.2f} km")
                    st.write(f"Estimated Time: {estimated_time:.2f} minutes")
                    folium_static(m)
                else:
                    st.warning("Route not found! Please try again with different locations.")
            else:
                st.error("Please enter valid starting and goal locations.")

    elif mode == "Image-based":
        st.sidebar.subheader("Upload Image")
        uploaded_file = st.sidebar.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            nparr = np.frombuffer(bytes_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            st.image(image, channels="GRAY", caption="Uploaded Image")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(bytes_data)
                temp_image_path = tmp.name

            if st.sidebar.button("Select Start and End Points"):
                points = select_points(temp_image_path)
                if len(points) == 2:
                    binary_image = preprocess_image(image)
                    skeleton = perform_skeletonization(binary_image)
                    G = find_nodes_and_edges(skeleton)
                    adjusted_start_point = closest_graph_node(G, points[0])
                    adjusted_end_point = closest_graph_node(G, points[1])
                    path = a_star_search(G, adjusted_start_point, adjusted_end_point)
                    if path:
                        original_image = Image.open(uploaded_file)
                        plt.figure(figsize=(10, 10))
                        plt.imshow(original_image, cmap='gray')
                        x_coords, y_coords = zip(*path)
                        plt.plot(x_coords, y_coords, color='red', linewidth=3)
                        start_x, start_y = adjusted_start_point
                        end_x, end_y = adjusted_end_point
                        plt.scatter(start_x, start_y, color='green', marker='o', label='Start Point', s=200)
                        plt.scatter(end_x, end_y, color='blue', marker='o', label='End Point', s=200)
                        plt.axis('off')
                        st.pyplot(plt)
                    else:
                        st.error("No path found between the selected points.")
                else:
                    st.error("Please select exactly two points.")
                os.unlink(temp_image_path)

if __name__ == "__main__":
    main()
