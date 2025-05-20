# FindCGraphs.cmake - Script to find .cgraph files and run cgraph2dot

# Find all .cgraph files in the build directory
set(SEARCH_DIRS
  "${BUILD_DIR}"
  "${BUILD_DIR}/CMakeFiles/${TARGET}.dir"
)

if(DEFINED CONFIG AND NOT CONFIG STREQUAL "")
  foreach(DIR ${SEARCH_DIRS})
    list(APPEND CONFIG_SEARCH_DIRS "${DIR}/${CONFIG}")
  endforeach()
  list(APPEND SEARCH_DIRS ${CONFIG_SEARCH_DIRS})
endif()

set(CGRAPH_FILES "")
foreach(DIR ${SEARCH_DIRS})
  if(EXISTS "${DIR}")
    file(GLOB_RECURSE DIR_CGRAPH_FILES "${DIR}/*.cgraph")
    list(APPEND CGRAPH_FILES ${DIR_CGRAPH_FILES})
  endif()
endforeach()

# If no .cgraph files were found, try a broader search
if(NOT CGRAPH_FILES)
  file(GLOB_RECURSE CGRAPH_FILES "${BUILD_DIR}/*.cgraph")
endif()

# Check if we found any .cgraph files
list(LENGTH CGRAPH_FILES CGRAPH_FILES_COUNT)
if(CGRAPH_FILES_COUNT EQUAL 0)
  message(WARNING "No .cgraph files found for target ${TARGET}")
  return()
endif()

message(STATUS "Found ${CGRAPH_FILES_COUNT} .cgraph files for target ${TARGET}")

# Run cgraph2dot
execute_process(
  COMMAND "${PYTHON_EXECUTABLE}" "${CGRAPH2DOT_SCRIPT}" "${OUTPUT_DOT}" ${CGRAPH_FILES}
  RESULT_VARIABLE CGRAPH2DOT_RESULT
  OUTPUT_VARIABLE CGRAPH2DOT_OUTPUT
  ERROR_VARIABLE CGRAPH2DOT_ERROR
)

# Check if cgraph2dot ran successfully
if(NOT CGRAPH2DOT_RESULT EQUAL 0)
  message(WARNING "cgraph2dot failed with exit code ${CGRAPH2DOT_RESULT}")
  if(CGRAPH2DOT_ERROR)
    message(WARNING "${CGRAPH2DOT_ERROR}")
  endif()
else()
  message(STATUS "Callgraph generated: ${OUTPUT_DOT}")
  message(STATUS "${CGRAPH2DOT_OUTPUT}")
endif()
