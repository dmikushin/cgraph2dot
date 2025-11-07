#!/usr/bin/env python3
"""
Convert DOT file to interactive HTML visualization using vis.js
Supports clustering, zooming, filtering, and search.
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Set, Tuple


def parse_dot_file(filename: str) -> Tuple[List[Dict], List[Dict], Dict[str, Set[str]]]:
    """Parse DOT file and extract nodes and edges."""
    nodes = []
    edges = []
    node_set = set()

    # Track which functions call which (for clustering)
    calls_map: Dict[str, Set[str]] = {}

    with open(filename, 'r') as f:
        content = f.read()

    # Extract node definitions
    node_pattern = r'"([^"]+)"\s*\[label="([^"]+)"\]'
    for match in re.finditer(node_pattern, content):
        node_id = match.group(1)
        node_label = match.group(2)

        if node_id not in node_set:
            node_set.add(node_id)

            # Categorize nodes for coloring
            group = 0
            if node_id.startswith('__mod_'):
                group = 1  # Module functions
            elif node_id.startswith('_gfortran_') or node_id in ['malloc', 'free', 'memset', 'memmove', 'realloc']:
                group = 2  # System/runtime functions
            elif node_id in ['main', 'MAIN__', 'sqrt', 'lround', 'copysign']:
                group = 3  # Entry points and math
            else:
                group = 4  # User functions

            nodes.append({
                'id': node_id,
                'label': node_label,
                'group': group,
                'title': f'{node_label}\nDouble-click to collapse/expand children'
            })

            calls_map[node_id] = set()

    # Extract edges
    edge_pattern = r'"([^"]+)"\s*->\s*"([^"]+)"'
    for match in re.finditer(edge_pattern, content):
        source = match.group(1)
        target = match.group(2)

        edges.append({
            'from': source,
            'to': target,
            'arrows': 'to'
        })

        if source in calls_map:
            calls_map[source].add(target)

    return nodes, edges, calls_map


def generate_html(nodes: List[Dict], edges: List[Dict], output_file: str, title: str = "Call Graph"):
    """Generate interactive HTML visualization."""

    # Convert nodes and edges to JSON
    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)

    html_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>TITLE_PLACEHOLDER</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        #controls {
            position: fixed;
            top: 10px;
            left: 10px;
            background: white;
            padding: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            max-width: 300px;
            transition: all 0.3s ease;
        }
        #controls.collapsed {
            width: 40px;
            height: 40px;
            padding: 8px;
            overflow: hidden;
            cursor: pointer;
        }
        #controls.collapsed * {
            display: none;
        }
        #controls.collapsed::before {
            content: '☰';
            font-size: 24px;
            display: block;
            text-align: center;
            line-height: 24px;
        }
        #mynetwork {
            width: 100%;
            height: 100vh;
            border: 1px solid lightgray;
        }
        .control-group {
            margin-bottom: 10px;
        }
        label {
            display: block;
            margin-bottom: 3px;
            font-weight: bold;
            font-size: 12px;
        }
        input[type="text"], select {
            width: 100%;
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 3px;
            box-sizing: border-box;
        }
        button {
            padding: 5px 10px;
            margin-right: 5px;
            margin-top: 5px;
            border: 1px solid #ccc;
            border-radius: 3px;
            background: #f0f0f0;
            cursor: pointer;
        }
        button:hover {
            background: #e0e0e0;
        }
        .legend {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #ccc;
        }
        .legend-item {
            margin: 3px 0;
            font-size: 11px;
        }
        .legend-color {
            display: inline-block;
            width: 12px;
            height: 12px;
            margin-right: 5px;
            border: 1px solid #333;
        }
    </style>
</head>
<body>
    <div id="controls">
        <h3 style="margin-top: 0;">Call Graph Controls</h3>

        <div class="control-group">
            <label>Search Function:</label>
            <input type="text" id="searchInput" placeholder="Type to search...">
        </div>

        <div class="control-group">
            <label>Filter by Type:</label>
            <select id="filterSelect">
                <option value="all">Show All</option>
                <option value="user">User Functions Only</option>
                <option value="module">Module Functions Only</option>
                <option value="nolib">Hide System/Library</option>
            </select>
        </div>

        <div class="control-group">
            <button onclick="fitNetwork()">Fit to Screen</button>
            <button onclick="resetView()">Reset View</button>
        </div>

        <div class="control-group">
            <button onclick="togglePhysics()">Toggle Physics</button>
            <button onclick="exportImage()">Export PNG</button>
        </div>

        <div class="legend">
            <div class="legend-item">
                <span class="legend-color" style="background: #97C2FC;"></span>
                <span>Other</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #FFFF99;"></span>
                <span>Module Functions</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #CCCCCC;"></span>
                <span>System/Runtime</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #FB7E81;"></span>
                <span>Entry/Math</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #7BE141;"></span>
                <span>User Functions</span>
            </div>
        </div>

        <div style="margin-top: 10px; font-size: 11px; color: #666;">
            <div>Nodes: <span id="nodeCount">0</span></div>
            <div>Edges: <span id="edgeCount">0</span></div>
            <div>Selected: <span id="selectedNode">None</span></div>
        </div>
    </div>

    <div id="mynetwork"></div>

    <script type="text/javascript">
        // Create nodes and edges data
        var allNodes = NODES_DATA_PLACEHOLDER;
        var allEdges = EDGES_DATA_PLACEHOLDER;

        var nodes = new vis.DataSet(allNodes);
        var edges = new vis.DataSet(allEdges);

        // Create a network
        var container = document.getElementById('mynetwork');
        var data = {
            nodes: nodes,
            edges: edges
        };

        var options = {
            nodes: {
                shape: 'box',
                margin: 10,
                widthConstraint: {
                    maximum: 200
                },
                font: {
                    size: 12
                },
                color: {
                    border: '#2B7CE9',
                    background: '#97C2FC'
                }
            },
            edges: {
                arrows: {
                    to: {
                        enabled: true,
                        scaleFactor: 0.5
                    }
                },
                smooth: {
                    type: 'cubicBezier',
                    forceDirection: 'horizontal',
                    roundness: 0.4
                },
                color: {
                    color: '#848484',
                    highlight: '#FF0000'
                }
            },
            layout: {
                hierarchical: {
                    enabled: true,
                    direction: 'UD',
                    sortMethod: 'directed',
                    levelSeparation: 150,
                    nodeSpacing: 100,
                    treeSpacing: 200,
                    blockShifting: true,
                    edgeMinimization: true,
                    parentCentralization: true
                }
            },
            physics: {
                enabled: false
            },
            interaction: {
                hover: true,
                navigationButtons: true,
                keyboard: true
            },
            groups: {
                0: { color: { background: '#97C2FC', border: '#2B7CE9' } },
                1: { color: { background: '#FFFF99', border: '#FFA500' } },
                2: { color: { background: '#CCCCCC', border: '#666666' } },
                3: { color: { background: '#FB7E81', border: '#B71C1C' } },
                4: { color: { background: '#7BE141', border: '#4CAF50' } }
            }
        };

        var network = new vis.Network(container, data, options);

        // Update counters
        document.getElementById('nodeCount').textContent = nodes.length;
        document.getElementById('edgeCount').textContent = edges.length;

        // Search functionality
        document.getElementById('searchInput').addEventListener('input', function(e) {
            var searchTerm = e.target.value.toLowerCase();
            var nodesToUpdate = [];

            if (searchTerm === '') {
                nodes.forEach(function(node) {
                    nodesToUpdate.push({ id: node.id, hidden: false, borderWidth: 1 });
                });
                nodes.update(nodesToUpdate);
                return;
            }

            var matchingNodes = [];
            nodes.forEach(function(node) {
                if (node.label.toLowerCase().includes(searchTerm)) {
                    matchingNodes.push(node.id);
                    nodesToUpdate.push({ id: node.id, hidden: false, borderWidth: 3 });
                } else {
                    nodesToUpdate.push({ id: node.id, hidden: false, borderWidth: 1 });
                }
            });
            nodes.update(nodesToUpdate);

            if (matchingNodes.length > 0) {
                network.fit({ nodes: matchingNodes, animation: true });
            }
        });

        // Filter functionality
        document.getElementById('filterSelect').addEventListener('change', function(e) {
            var filter = e.target.value;
            var nodesToUpdate = [];

            nodes.forEach(function(node) {
                var show = true;

                if (filter === 'user' && node.group !== 4) {
                    show = false;
                } else if (filter === 'module' && node.group !== 1) {
                    show = false;
                } else if (filter === 'nolib' && node.group === 2) {
                    show = false;
                }

                nodesToUpdate.push({ id: node.id, hidden: !show });
            });
            nodes.update(nodesToUpdate);
        });

        // Node selection
        network.on('selectNode', function(params) {
            if (params.nodes.length > 0) {
                var nodeId = params.nodes[0];
                var node = nodes.get(nodeId);
                document.getElementById('selectedNode').textContent = node.label;
            }
        });

        network.on('deselectNode', function() {
            document.getElementById('selectedNode').textContent = 'None';
        });

        // Collapse/expand on double-click
        var collapsedNodes = {};

        network.on('doubleClick', function(params) {
            if (params.nodes.length > 0) {
                var nodeId = params.nodes[0];

                // Find all children (nodes that this node calls)
                var children = [];
                allEdges.forEach(function(edge) {
                    if (edge.from === nodeId) {
                        children.push(edge.to);
                    }
                });

                if (children.length === 0) {
                    return; // No children to collapse
                }

                // Toggle collapsed state
                if (collapsedNodes[nodeId]) {
                    // Expand: show all children
                    var nodesToUpdate = [];
                    children.forEach(function(childId) {
                        nodesToUpdate.push({ id: childId, hidden: false });
                    });
                    nodes.update(nodesToUpdate);
                    // Reset parent node border
                    nodes.update({ id: nodeId, borderWidth: 1, shapeProperties: { borderDashes: false } });
                    delete collapsedNodes[nodeId];
                } else {
                    // Collapse: hide all children
                    var nodesToUpdate = [];
                    children.forEach(function(childId) {
                        nodesToUpdate.push({ id: childId, hidden: true });
                    });
                    nodes.update(nodesToUpdate);
                    // Mark parent node as collapsed with dashed border
                    nodes.update({ id: nodeId, borderWidth: 3, shapeProperties: { borderDashes: [5, 5] } });
                    collapsedNodes[nodeId] = children;
                }
            }
        });

        // Helper functions
        function fitNetwork() {
            network.fit({ animation: true });
        }

        function resetView() {
            document.getElementById('searchInput').value = '';
            document.getElementById('filterSelect').value = 'all';
            var nodesToUpdate = [];
            nodes.forEach(function(node) {
                nodesToUpdate.push({ id: node.id, hidden: false, borderWidth: 1, shapeProperties: { borderDashes: false } });
            });
            nodes.update(nodesToUpdate);
            collapsedNodes = {}; // Clear collapsed state
            network.fit({ animation: true });
        }

        var physicsEnabled = false;
        function togglePhysics() {
            physicsEnabled = !physicsEnabled;
            network.setOptions({ physics: { enabled: physicsEnabled } });
        }

        function exportImage() {
            var canvas = document.querySelector('#mynetwork canvas');
            var link = document.createElement('a');
            link.download = 'callgraph.png';
            link.href = canvas.toDataURL();
            link.click();
        }

        // Auto-collapse controls
        var controlsPanel = document.getElementById('controls');
        var collapseTimeout;
        var isCollapsed = false;

        function collapseControls() {
            if (!isCollapsed) {
                controlsPanel.classList.add('collapsed');
                isCollapsed = true;
            }
        }

        function expandControls() {
            if (isCollapsed) {
                controlsPanel.classList.remove('collapsed');
                isCollapsed = false;
            }
        }

        function resetCollapseTimeout() {
            clearTimeout(collapseTimeout);
            collapseTimeout = setTimeout(collapseControls, 3000); // Collapse after 3 seconds
        }

        // Expand on hover or click
        controlsPanel.addEventListener('mouseenter', function() {
            expandControls();
            resetCollapseTimeout();
        });

        controlsPanel.addEventListener('mouseleave', function() {
            resetCollapseTimeout();
        });

        controlsPanel.addEventListener('click', function() {
            if (isCollapsed) {
                expandControls();
                resetCollapseTimeout();
            }
        });

        // Reset timeout on any interaction with controls
        controlsPanel.addEventListener('input', resetCollapseTimeout);
        controlsPanel.addEventListener('change', resetCollapseTimeout);

        // Start the auto-collapse timer on page load
        resetCollapseTimeout();

        // Fit on load
        network.once('stabilizationIterationsDone', function() {
            network.fit();
        });
    </script>
</body>
</html>'''

    # Replace placeholders
    html_content = html_template.replace('NODES_DATA_PLACEHOLDER', nodes_json)
    html_content = html_content.replace('EDGES_DATA_PLACEHOLDER', edges_json)
    html_content = html_content.replace('TITLE_PLACEHOLDER', title)

    with open(output_file, 'w') as f:
        f.write(html_content)


def main():
    parser = argparse.ArgumentParser(
        description="Convert DOT file to interactive HTML visualization"
    )
    parser.add_argument('input', help='Input .dot file')
    parser.add_argument('output', help='Output .html file')
    parser.add_argument('--title', default='Call Graph', help='Graph title')

    args = parser.parse_args()

    print(f"Parsing {args.input}...")
    nodes, edges, calls_map = parse_dot_file(args.input)

    print(f"Found {len(nodes)} nodes and {len(edges)} edges")

    print(f"Generating {args.output}...")
    generate_html(nodes, edges, args.output, args.title)

    print(f"Done! Open {args.output} in a web browser.")


if __name__ == '__main__':
    main()
