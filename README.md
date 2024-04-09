# Multi-Modal-Route-Finding-System

This project combines text-based and image-based route finding functionalities into a single Streamlit application.

## Overview

The Combined Route Finder allows users to find routes between locations using text inputs or by uploading images with maps. It integrates functionalities from two separate Streamlit applications: one for text-based route finding and another for image-based route finding.

## Features

- Text-based route finding: Users can input starting and goal locations as text and find the route between them.

- Image-based route finding: Users can upload images with maps and select start and end points on the map to find the route.
  Currently it works only on a few maps.

- Voice-based mode- User can speak the name of the location and the system will recognize it and find the route.

- Generative Image based - Uses stable diffusion to generate images which can be used as reference for locations.

- Interactive UI: The application provides an interactive user interface with map visualization and route statistics.

## Installation

1. Clone the repository:git clone https://github.com/Rushi1508/Multi-Modal-Route-Finding-System.git

## Requirements

pip install -r requirements.txt

## Usage

To run the Combined Route Finder, execute the following command:

streamlit run Route Finder.py

## Condition for Generative Image

In current usage, the user needs to install Stable diffusion in this system as the generative image mode uses its local api for producing sample images.
you can download stable diffusion via the following link: https://github.com/AUTOMATIC1111/stable-diffusion-webui

You also need to download a model for generating images. We are using DreamShaper Model for image generation.


