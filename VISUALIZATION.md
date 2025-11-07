# Advanced Visualization Options for Call Graphs

This document describes various methods to visualize large call graphs more effectively than the standard DOT output.

## Problem with Standard DOT Visualization

The standard `dot -Tpng` command creates very wide graphs that are difficult to navigate:
- Horizontal layout can extend thousands of pixels
- Difficult to see overview and details simultaneously
- No interactivity or filtering

## Solution 1: Interactive HTML Visualization ⭐ **Recommended**

### Features
- **Interactive zoom and pan** - Navigate large graphs easily
- **Hierarchical layout** - Top-to-bottom organization that's more compact
- **Search functionality** - Find functions by name
- **Filter by type** - Show/hide system functions, modules, user code
- **Color coding** - Visual differentiation of function types:
  - 🟦 Other functions
  - 🟨 Module functions (`__mod_*`)
  - ⬜ System/Runtime (`_gfortran_*`, `malloc`, etc.)
  - 🟥 Entry points and math functions
  - 🟩 User functions
- **Node selection** - Click to highlight and explore dependencies
- **Export to PNG** - Save current view as image
- **Responsive** - Works on any screen size

### Usage

```bash
# Generate interactive HTML from DOT file
python3 ThirdParty/cgraph2dot/dot2interactive.py input.dot output.html --title "My Project"

# Example:
python3 ThirdParty/cgraph2dot/dot2interactive.py blytsy_ftest.dot blytsy_callgraph.html --title "BLYTSY Call Graph"
```

Then open `output.html` in any modern web browser (Chrome, Firefox, Safari, Edge).

### Controls
- **Mouse wheel** - Zoom in/out
- **Click and drag** - Pan around
- **Search box** - Type function name to highlight and focus
- **Filter dropdown** - Select view mode:
  - Show All
  - User Functions Only
  - Module Functions Only
  - Hide System/Library
- **Fit to Screen** - Reset zoom to show entire graph
- **Toggle Physics** - Enable/disable force-directed layout animation
- **Export PNG** - Save current view as image

## Solution 2: Optimized DOT Layouts

### Compact Top-to-Bottom Layout

```bash
dot -Tpng -Grankdir=TB -Granksep=0.5 -Gnodesep=0.3 input.dot -o output_compact.png
```

Options:
- `-Grankdir=TB` - Top-to-bottom instead of left-to-right
- `-Granksep=0.5` - Reduce vertical spacing between ranks
- `-Gnodesep=0.3` - Reduce horizontal spacing between nodes

### Circular Layout

```bash
circo -Tpng input.dot -o output_circular.png
```

Good for seeing overall structure and finding clusters.

### Force-Directed Layout

```bash
neato -Tpng input.dot -o output_neato.png
```

Positions nodes based on edge forces - can reveal natural groupings.

### Hierarchical with Clusters

```bash
dot -Tpng -Gconcentrate=true -Gsplines=ortho input.dot -o output_clustered.png
```

Options:
- `-Gconcentrate=true` - Merge multiple edges between same nodes
- `-Gsplines=ortho` - Orthogonal edges for cleaner look

## Solution 3: SVG for Scalability

Generate SVG instead of PNG for infinite zoom without pixelation:

```bash
dot -Tsvg input.dot -o output.svg
```

Modern browsers can open SVG files and allow zooming. For interactivity, convert to HTML:

```bash
# Create standalone HTML with embedded SVG
dot -Tsvg input.dot | sed 's/^/<div style="width:100%;height:100vh;overflow:auto">/' | sed 's/$/<\/div>/' > output.html
```

## Solution 4: Multi-Page PDF

For very large graphs, split into multiple pages:

```bash
# Generate multi-page PDF
dot -Tpdf -Gsize="8.5,11" -Gpage="8.5,11" input.dot -o output.pdf
```

## Solution 5: Filter DOT File Before Visualization

Reduce graph size by filtering out less interesting nodes:

```bash
# Remove system/library functions
grep -v '_gfortran_\|malloc\|free\|memset' input.dot > filtered.dot
dot -Tpng filtered.dot -o output_filtered.png
```

## Solution 6: Use JSON Filter with cgraph2dot

Create a `filters.json` file to control what appears in the graph:

```json
{
  "removal-filters": [
    "^_gfortran_",
    "^malloc$",
    "^free$",
    "^memset$",
    "^memmove$",
    "^realloc$"
  ],
  "keep-filters": [
    "^blytsy_",
    "^__mod_"
  ],
  "rewrite-filters": [
    {
      "pattern": "^__mod_common_gpu_MOD_",
      "replacement": "mod::"
    }
  ]
}
```

Then regenerate with filters:

```bash
python3 cgraph2dot --filters filters.json output.dot input1.cgraph input2.cgraph ...
```

## Comparison Table

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Interactive HTML** | Zoom, pan, search, filter, color-coded | Requires browser | Large graphs, exploration |
| Compact DOT | Simple, no dependencies | Still static | Medium graphs |
| Circular layout | Shows structure | Can be cluttered | Finding patterns |
| SVG | Infinite zoom | Large file size | Detailed inspection |
| Multi-page PDF | Printable | Disconnected views | Documentation |
| Filtered DOT | Smaller graphs | May miss connections | Focused analysis |

## Recommended Workflow

1. **Start with interactive HTML** - Best for initial exploration:
   ```bash
   python3 dot2interactive.py graph.dot graph.html
   ```

2. **Use filters** to focus on relevant code:
   - Remove system functions if not interested in internals
   - Keep only user functions for high-level overview
   - Search for specific functions

3. **Export specific views** as PNG for documentation:
   - Filter to show only user functions
   - Click "Export PNG" button

4. **Use JSON filters** for generating focused graphs in CI/CD:
   ```bash
   python3 cgraph2dot --filters focus.json output.dot *.cgraph
   ```

## Tips for Very Large Graphs (>1000 nodes)

1. **Use hierarchical filtering**:
   - Start with high-level view (only entry points and main functions)
   - Drill down into specific modules as needed

2. **Split by module**:
   - Generate separate graphs for each major component
   - Use `keep-filters` to isolate modules

3. **Consider database approach**:
   - Import call graph into SQLite/PostgreSQL
   - Query for specific call chains
   - Visualize subgraphs on demand

4. **Use graph analysis tools**:
   - NetworkX (Python) for programmatic analysis
   - Gephi for advanced graph analysis and visualization
   - Cytoscape for biological-style network visualization

## Examples

### Generate everything for a project

```bash
# Build project with callgraph generation
cmake -B build
cmake --build build

# Generate interactive visualization
python3 ThirdParty/cgraph2dot/dot2interactive.py \
    build/my_target.dot \
    docs/callgraph.html \
    --title "MyProject Call Graph"

# Also generate compact PNG for README
dot -Tpng -Grankdir=TB \
    -Granksep=0.5 \
    -Gnodesep=0.3 \
    build/my_target.dot \
    -o docs/callgraph_compact.png
```

### Filter to show only user functions interactively

1. Open HTML visualization
2. Select "User Functions Only" from filter dropdown
3. Use search to find your function
4. Click "Export PNG" to save the view

## Browser Compatibility

The interactive HTML visualization requires:
- Modern browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- JavaScript enabled
- No installation or server required - works offline

## Future Enhancements

Potential improvements to explore:
- Collapsible function clusters by module
- Call depth filtering (show only N levels deep)
- Path highlighting (show all paths between two functions)
- Time-based animation showing call sequence
- Integration with code coverage data
- Side-by-side code viewer
