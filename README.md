# cgraph2dot

A Python utility that converts GCC's callgraph dump files (.cgraph) to DOT format for visualization.

`cgraph2dot` processes `.cgraph` files produced by GCC's `-fdump-ipa-cgraph` option, extracts callgraph information, consolidates it, and generates a DOT file that can be visualized using Graphviz or other graph visualization tools.

![](./example/cgraph2dot_example.png)

This tool helps developers analyze and understand the call relationships between functions in their codebase, making it easier to:

- Visualize complex code structures
- Identify dependencies between modules
- Optimize code by understanding call patterns
- Document code architecture

CMake integrations are available to build call graphs of CMake targets.


## Prerequisites

- Python 3.6 or higher
- Graphviz (optional, for visualization)


## Setup

Clone this repository:

```
git clone https://github.com/dmikushin/cgraph2dot.git
```


## Usage

### Command Line

```bash
./cgraph2dot output.dot input1.cgraph input2.cgraph ...
```

Parameters:

- `output.dot` - The name of the DOT file to be generated
- `input1.cgraph`, `input2.cgraph`, ... - One or more `.cgraph` files from GCC

### CMake Integration

For seamless integration with CMake projects, use the provided `CGraphVisualizer.cmake` module:

1. Place `CGraphVisualizer.cmake` in your project's `cmake` directory
2. Place `cgraph2dot` in your project's `cmake` or root directory
3. Add the following to your CMakeLists.txt:

```cmake
# Add the directory containing CGraphVisualizer.cmake to the module path
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

# Include the CGraphVisualizer module
include(CGraphVisualizer)

# Enable callgraph visualization for a target
add_callgraph_visualization(my_target)

# Optional: Generate a PNG image of the callgraph
add_callgraph_image(my_target png)
```

This will:
- Automatically add the `-fdump-ipa-cgraph` compiler option to your target
- Run the cgraph2dot tool after building to generate a `.dot` file
- Optionally create an image file using Graphviz (requires Graphviz to be installed)

### Generating .cgraph files manually

To produce the input files for this tool manually, compile your code with GCC using the `-fdump-ipa-cgraph` option:

```bash
gcc -fdump-ipa-cgraph source.c -o program
```

This will generate a `.cgraph` file for each compiled source file.


## Examples

### Manual Example

1. Compile your code with callgraph dumping enabled:

```bash
gcc -fdump-ipa-cgraph *.c -o myprogram
```

2. Process the generated `.cgraph` files:

```bash
python cgraph2dot callgraph.dot *.cgraph
```

3. Visualize the resulting DOT file:

```bash
dot -Tpng callgraph.dot -o callgraph.png
```

### CMake Example

```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)

# Add the directory containing CGraphVisualizer.cmake to the module path
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

# Include the CGraphVisualizer module
include(CGraphVisualizer)

# Create an executable target
add_executable(my_app main.c util.c)

# Enable callgraph visualization for the target
add_callgraph_visualization(my_app)

# Optional: Generate a PNG image of the callgraph
add_callgraph_image(my_app png)
```

After building the `my_app` target, a `my_app.dot` file will be automatically generated in the build directory. If you enabled image generation, a `my_app.png` will also be created.


## Features

### Command Line Tool
- Processes multiple `.cgraph` files at once
- Extracts function names and their calling relationships
- Consolidates information from different compilation units
- Generates DOT format graph for visualization

### CMake Integration
- Seamless integration with CMake build systems
- Automatically adds required compiler flags
- Generates callgraphs as part of the normal build process
- Supports both single and multi-configuration generators
- Optional automatic image generation with Graphviz
- Works with any target (executables, static libraries, shared libraries)


## Visualization Options

### PNG Image

```bash
dot -Tpng callgraph.dot -o callgraph.png
```

### SVG (Scalable Vector Graphics)

```bash
dot -Tsvg callgraph.dot -o callgraph.svg
```

### PDF Document

```bash
dot -Tpdf callgraph.dot -o callgraph.pdf
```

### Interactive Graph with xdot

```bash
xdot callgraph.dot
```


## Limitations

- The tool relies on GCC's dump format, which may change between compiler versions.
- Very large codebases may produce complex graphs that are difficult to visualize effectively.
- The tool analyzes static call relationships and cannot capture dynamic function calls through function pointers or virtual methods.


## Files

The project consists of the following files:

- `cgraph2dot` - The main Python script that processes `.cgraph` files
- `CGraphVisualizer.cmake` - CMake module for integration with CMake build systems

### cgraph2dot

This is the core Python script that does the actual work of parsing `.cgraph` files and generating the DOT output.

### CGraphVisualizer.cmake

This CMake module provides:

- `add_callgraph_visualization(TARGET)` - Main function to enable callgraph generation for a target
- `add_callgraph_image(TARGET FORMAT)` - Optional function to also generate an image in the specified format

