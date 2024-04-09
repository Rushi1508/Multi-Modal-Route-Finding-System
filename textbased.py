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

def get_route_geometry(start_location, goal_location, profile='mode'):
    url = f"http://router.project-osrm.org/route/v1/{profile}/{start_location[1]},{start_location[0]};{goal_location[1]},{goal_location[0]}?overview=full&geometries=geojson"
    response = requests.get(url)
    if response.ok:
        data = response.json()
        if 'routes' in data and data['routes']:
            route = data['routes'][0]
            if 'geometry' in route and 'distance' in route and 'duration' in route:
                geometry = route['geometry']
                total_distance = route['distance'] / 1000  # Convert meters to kilometers
                duration_seconds = route['duration']  # Duration in seconds
                if profile == 'walking':
                    duration_minutes = (duration_seconds / 60)*10
                elif profile == 'cycling':
                    duration_minutes = (duration_seconds / 60)*4
                else:
                    duration_minutes = duration_seconds / 60
                return geometry, total_distance, duration_minutes
    return None, None, None

def text_based_mode():
    """Functionality for finding routes based on text input"""
    profile = st.sidebar.radio("Transportation Mode", ("Driving", "Walking", "Cycling"), key="transport_mode")
    profile = profile.lower() if profile != "Driving" else 'driving'
    
    start_location_name = st.sidebar.text_input("Starting Location", key="start_location")
    goal_location_name = st.sidebar.text_input("Goal Location", key="goal_location")

    if st.sidebar.button("Find Route", key="find_route_button"):
        st.session_state['output_generated'] = True
        find_route_text_mode(start_location_name, goal_location_name, profile)
         # Generate and display images for the locations after displaying the route map
        start_image = generate_location_image(start_location_name)
        goal_image = generate_location_image(goal_location_name)
        
        if start_image:
            st.image(start_image, caption=f"Generated Image for {start_location_name}")
        if goal_image:
            st.image(goal_image, caption=f"Generated Image for {goal_location_name}")

def find_route_text_mode(start_location_name, goal_location_name, profile):
    """Function to find and display the route based on the provided locations and profile"""
    start_location = geocode_location(start_location_name)
    goal_location = geocode_location(goal_location_name)

    if start_location and goal_location:
        geometry, total_distance, duration_minutes = get_route_geometry(start_location, goal_location, profile)
        if geometry:
            display_route_map(geometry, start_location, goal_location, start_location_name, goal_location_name, total_distance, duration_minutes)
        else:
            st.warning("Route not found! Please try again with different locations.")
    else:
        st.error("Please enter valid starting and goal locations.")

def display_route_map(geometry, start_location, goal_location, start_location_name, goal_location_name, total_distance, duration_minutes):
    """Function to display the route map and statistics"""
    st.session_state['output_generated'] = True
    m = folium.Map(location=start_location, zoom_start=10)
    folium.Marker(start_location, icon=folium.Icon(color='green'), tooltip=start_location_name).add_to(m)
    folium.Marker(goal_location, icon=folium.Icon(color='red'), tooltip=goal_location_name).add_to(m)
    folium.features.GeoJson(geometry, style_function=lambda x: {'color': 'blue'}).add_to(m)
    st.success("Route found! See the map below:")
    st.subheader("Route Statistics:")
    st.write(f"Total Distance: {total_distance:.2f} km")
    st.write(f"Estimated Time: {duration_minutes:.2f} minutes")
    folium_static(m)

def generate_location_image(prompt):
    url = "http://127.0.0.1:7860"
    endpoint = "txt2img"

    # Assuming default values for steps and denoise strength
    nsteps = 20
    denoise = 0.75

    payload = {
        "prompt": prompt,
        "steps": nsteps,
        "denoising_strength": denoise
    }

    response = requests.post(url=f'{url}/sdapi/v1/{endpoint}', json=payload)
    if response.status_code == 200:
        r = response.json()
        generated_image = "data:image/png;base64," + r['images'][0]
        return generated_image
    else:
        st.error(f"Failed to generate image for {prompt}. Server responded with status code: {response.status_code}")
        return None
