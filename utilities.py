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
