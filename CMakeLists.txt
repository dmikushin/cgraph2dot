cmake_minimum_required(VERSION 3.10)
project(cgraph2dot)

# Add the directory containing CGraphVisualizer.cmake to the module path
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

add_subdirectory(example)

