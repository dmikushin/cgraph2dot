# CGraphVisualizer.cmake - CMake module for callgraph visualization
# Integrates with GCC/Clang's -fdump-ipa-cgraph option to produce call graphs

# Make sure the module is included only once
if(DEFINED _CGRAPH_VISUALIZER_INCLUDED)
  return()
endif()
set(_CGRAPH_VISUALIZER_INCLUDED TRUE)

# Get the directory where this module is located
get_filename_component(_CGRAPH_VISUALIZER_DIR "${CMAKE_CURRENT_LIST_FILE}" DIRECTORY)

# Function to find the cgraph2dot script
function(_cgraph_find_script RESULT_VAR)
  # First, check if the script is in the same directory as this module
  set(SCRIPT_PATH "${_CGRAPH_VISUALIZER_DIR}/../cgraph2dot")
  
  if(EXISTS "${SCRIPT_PATH}")
    set(${RESULT_VAR} "${SCRIPT_PATH}" PARENT_SCOPE)
    return()
  endif()
  
  # Not found
  set(${RESULT_VAR} "" PARENT_SCOPE)
endfunction()

# Main function to attach callgraph visualization to a target
function(add_callgraph_visualization TARGET)
  # Check if the target exists
  if(NOT TARGET ${TARGET})
    message(FATAL_ERROR "Target '${TARGET}' does not exist")
  endif()
  
  # Only support GCC and Clang compilers
  if(NOT (CMAKE_C_COMPILER_ID MATCHES "GNU|Clang" OR CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang" OR CMAKE_Fortran_COMPILER_ID MATCHES "GNU|Clang"))
    message(FATAL_ERROR "Callgraph visualization is only supported with GCC and Clang compilers. Target: ${TARGET}")
    return()
  endif()
  
  # Find cgraph2dot script
  _cgraph_find_script(CGRAPH2DOT_SCRIPT)
  if(NOT CGRAPH2DOT_SCRIPT)
    message(FATAL_ERROR "Could not find cgraph2dot script. Please place it in the same directory as CGraphVisualizer.cmake, in PATH, or in the project's source directory.")
  endif()
  
  # Ensure Python is available
  find_package(Python COMPONENTS Interpreter REQUIRED)
  
  # Add the compiler option to generate .cgraph files
  target_compile_options(${TARGET} PRIVATE -fdump-ipa-cgraph)
  
  # Locate FindCGraphs.cmake
  set(FIND_CGRAPHS_SCRIPT "${_CGRAPH_VISUALIZER_DIR}/FindCGraphs.cmake")
    
  # Handle multi-config generators (like Visual Studio)
  if(CMAKE_CONFIGURATION_TYPES)
    foreach(CONFIG ${CMAKE_CONFIGURATION_TYPES})
      add_custom_command(
        TARGET ${TARGET} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E echo "Generating callgraph for ${TARGET} (${CONFIG})..."
        COMMAND ${CMAKE_COMMAND}
          -D TARGET=${TARGET}
          -D BUILD_DIR=${CMAKE_BINARY_DIR}
          -D CONFIG=${CONFIG}
          -D CGRAPH2DOT_SCRIPT=${CGRAPH2DOT_SCRIPT}
          -D PYTHON_EXECUTABLE=${Python_EXECUTABLE}
          -D OUTPUT_DOT=${CMAKE_CURRENT_BINARY_DIR}/${TARGET}_${CONFIG}.dot
          -P ${FIND_CGRAPHS_SCRIPT}
        VERBATIM
      )
    endforeach()
  else()
    # Single-config generator
    add_custom_command(
      TARGET ${TARGET} POST_BUILD
      COMMAND ${CMAKE_COMMAND} -E echo "Generating callgraph for ${TARGET}..."
      COMMAND ${CMAKE_COMMAND}
        -D TARGET=${TARGET}
        -D BUILD_DIR=${CMAKE_BINARY_DIR}
        -D CGRAPH2DOT_SCRIPT=${CGRAPH2DOT_SCRIPT}
        -D PYTHON_EXECUTABLE=${Python_EXECUTABLE}
        -D OUTPUT_DOT=${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.dot
        -P ${FIND_CGRAPHS_SCRIPT}
      VERBATIM
    )
  endif()
  
  message(STATUS "Callgraph visualization enabled for target: ${TARGET}")
  message(STATUS "The DOT file will be generated after building the target")
endfunction()

# Optional function to add visualization using Graphviz
function(add_callgraph_image TARGET FORMAT)
  # Check if Graphviz is available
  find_program(DOT_EXECUTABLE dot)
  if(NOT DOT_EXECUTABLE)
    message(WARNING "Graphviz's 'dot' tool not found. Cannot generate ${FORMAT} image for callgraph.")
    return()
  endif()
  
  # Add a custom command to generate an image from the DOT file
  set(DOT_FILE "${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.dot")
  set(IMAGE_FILE "${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.${FORMAT}")

  add_custom_command(
    OUTPUT ${IMAGE_FILE}
    COMMAND ${DOT_EXECUTABLE} -T${FORMAT} ${DOT_FILE} -o ${IMAGE_FILE}
    DEPENDS ${DOT_FILE}
    COMMENT "Generating ${FORMAT} image of callgraph for ${TARGET}"
    VERBATIM
  )

  add_custom_target(${TARGET}_callgraph_image ALL
    DEPENDS ${IMAGE_FILE}
  )

  add_dependencies(${TARGET}_callgraph_image ${TARGET})

  message(STATUS "Callgraph ${FORMAT} image will be generated: ${IMAGE_FILE}")
endfunction()
