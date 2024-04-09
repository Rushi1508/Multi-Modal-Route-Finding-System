
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
import cv2
import numpy as np
from skimage.morphology import skeletonize
from skimage import img_as_bool
import networkx as nx
from utilities import *

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
def image_based_mode():
    """Functionality for finding routes based on image input"""
    uploaded_file = st.sidebar.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="image_uploader")

    if uploaded_file is not None:
        st.session_state['output_generated'] = True
        bytes_data = uploaded_file.read()
        nparr = np.frombuffer(bytes_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        st.image(image, caption="Uploaded Image")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(bytes_data)
            temp_image_path = tmp.name

        if st.sidebar.button("Select Start and End Points", key="select_points_button"):
            points = select_points(temp_image_path)
            process_image_based_mode(uploaded_file, points, temp_image_path)

def process_image_based_mode(uploaded_file, points, temp_image_path):
    """Function to process the uploaded image and find a path between selected points"""
    if len(points) == 2:
        st.session_state['output_generated'] = True
        binary_image = preprocess_image(cv2.imread(temp_image_path, cv2.IMREAD_GRAYSCALE))
        skeleton = perform_skeletonization(img_as_bool(binary_image))
        G = find_nodes_and_edges(skeleton)
        adjusted_start_point, adjusted_end_point = [closest_graph_node(G, point) for point in points]
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
        os.unlink(temp_image_path)
    else:
        st.error("Please select exactly two points.")
