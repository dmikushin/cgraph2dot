cmake_minimum_required(VERSION 3.10)
project(cgraph2dot)

# Add the directory containing CGraphVisualizer.cmake to the module path
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

# Get the directory where this module is located
set(_CGRAPH_VISUALIZER_DIR "${CMAKE_CURRENT_SOURCE_DIR}" CACHE INTERNAL "CGraph Visualizer directory")

# Include the CGraphVisualizer module
include(CGraphVisualizer)

add_subdirectory(examples)

