#!/usr/bin/env python3
"""
Smart .dot file comparator that compares graph structure, not text.
Ignores order of edges and nodes.
"""

import re
import sys
from pathlib import Path


def parse_dot_file(filepath):
    """
    Parse a .dot file and extract nodes and edges.
    Returns a dict with 'nodes' (set) and 'edges' (set).
    """
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract nodes (lines with [label=...])
    node_pattern = r'"([^"]+)"\s*\[label="([^"]+)"\]'
    nodes = set()
    for match in re.finditer(node_pattern, content):
        node_id = match.group(1)
        node_label = match.group(2)
        nodes.add((node_id, node_label))
    
    # Extract edges (lines with ->)
    edge_pattern = r'"([^"]+)"\s*->\s*"([^"]+)"'
    edges = set()
    for match in re.finditer(edge_pattern, content):
        from_node = match.group(1)
        to_node = match.group(2)
        edges.add((from_node, to_node))
    
    return {
        'nodes': nodes,
        'edges': edges
    }


def compare_dot_files(file1, file2):
    """
    Compare two .dot files by their graph structure.
    Returns (is_equal, differences_description).
    """
    graph1 = parse_dot_file(file1)
    graph2 = parse_dot_file(file2)
    
    differences = []
    
    # Compare nodes
    nodes1 = graph1['nodes']
    nodes2 = graph2['nodes']
    
    nodes_only_in_1 = nodes1 - nodes2
    nodes_only_in_2 = nodes2 - nodes1
    
    if nodes_only_in_1:
        differences.append(f"Nodes only in reference file:")
        for node_id, node_label in sorted(nodes_only_in_1):
            differences.append(f"  - {node_id} [label={node_label}]")
    
    if nodes_only_in_2:
        differences.append(f"Nodes only in generated file:")
        for node_id, node_label in sorted(nodes_only_in_2):
            differences.append(f"  + {node_id} [label={node_label}]")
    
    # Compare edges
    edges1 = graph1['edges']
    edges2 = graph2['edges']
    
    edges_only_in_1 = edges1 - edges2
    edges_only_in_2 = edges2 - edges1
    
    if edges_only_in_1:
        differences.append(f"Edges only in reference file:")
        for from_node, to_node in sorted(edges_only_in_1):
            differences.append(f"  - {from_node} -> {to_node}")
    
    if edges_only_in_2:
        differences.append(f"Edges only in generated file:")
        for from_node, to_node in sorted(edges_only_in_2):
            differences.append(f"  + {from_node} -> {to_node}")
    
    is_equal = len(differences) == 0
    
    # Add summary
    if is_equal:
        summary = "Graphs are structurally identical"
    else:
        summary = f"Graphs differ:\n"
        summary += f"  Reference: {len(nodes1)} nodes, {len(edges1)} edges\n"
        summary += f"  Generated: {len(nodes2)} nodes, {len(edges2)} edges\n"
        if differences:
            summary += "\nDifferences:\n" + "\n".join(differences)
    
    return is_equal, summary


def main():
    """Main function for standalone usage."""
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <reference.dot> <generated.dot>")
        sys.exit(1)
    
    reference_file = Path(sys.argv[1])
    generated_file = Path(sys.argv[2])
    
    if not reference_file.exists():
        print(f"Error: Reference file not found: {reference_file}")
        sys.exit(1)
    
    if not generated_file.exists():
        print(f"Error: Generated file not found: {generated_file}")
        sys.exit(1)
    
    is_equal, summary = compare_dot_files(reference_file, generated_file)
    
    print(summary)
    
    if is_equal:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()