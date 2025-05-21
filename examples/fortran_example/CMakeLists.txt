cmake_minimum_required(VERSION 3.10)

project(cgraph2dot_fortran_example LANGUAGES Fortran)

# Create an executable target
add_executable(${PROJECT_NAME} main.f90 my_module.f90)

# Enable callgraph visualization for the target
# and specify the filter file
add_callgraph_visualization(${PROJECT_NAME}
    FILTER_FILE ${CMAKE_CURRENT_SOURCE_DIR}/filters.json
)

# Optional: Generate a PNG image of the callgraph
# Requires Graphviz to be installed
add_callgraph_image(${PROJECT_NAME} png)
