cmake_minimum_required(VERSION 3.10)

project(cgraph2dot_example LANGUAGES C)

# Include the CGraphVisualizer module
include(CGraphVisualizer)

# Create an executable target
add_executable(${PROJECT_NAME} main.c util.c)

# Enable callgraph visualization for the target
add_callgraph_visualization(${PROJECT_NAME})

# Optional: Generate a PNG image of the callgraph
# Requires Graphviz to be installed
add_callgraph_image(${PROJECT_NAME} png)
