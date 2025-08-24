#!/usr/bin/env python3
"""
Simple compatibility test for cgraph2dot with GCC 8 and GCC 11.

Compares generated .dot files with reference files.
"""

import os
import sys
import subprocess
from pathlib import Path

# Import our smart dot comparator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotdiff import compare_dot_files as dotdiff_compare


def get_gcc_version():
    """Get GCC major version."""
    # Use stdout=PIPE, stderr=PIPE instead of capture_output for Python 3.6 compatibility
    # Use universal_newlines instead of text for Python 3.6 compatibility
    result = subprocess.run(['gcc', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # Parse first line like "gcc (GCC) 8.5.0" or "gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0"
    first_line = result.stdout.split('\n')[0]
    # Find first number after "gcc"
    for part in first_line.split():
        if '.' in part and part[0].isdigit():
            return int(part.split('.')[0])
    return None


def compare_dot_files(generated_file, reference_file):
    """
    Compare generated .dot file with reference using smart structural comparison.
    Returns True if graphs are structurally identical.
    Shows differences if graphs don't match.
    """
    # Use our smart dotdiff that compares graph structure, not text
    is_equal, summary = dotdiff_compare(reference_file, generated_file)
    
    if is_equal:
        return True
    
    # Graphs don't match - show structural differences
    print("\n   Structural differences found:")
    print("   " + "=" * 50)
    
    # Print summary with indentation
    for line in summary.split('\n'):
        print(f"   {line}")
    
    print("   " + "=" * 50 + "\n")
    
    return False


def test_c_example():
    """Test C example."""
    gcc_version = get_gcc_version()
    if gcc_version not in [8, 11]:
        print(f"⚠️  Skipping test: GCC {gcc_version} is not a target version (need 8 or 11)")
        return True
    
    # File paths
    project_root = Path(__file__).parent.parent
    build_dir = project_root / 'build'
    generated_file = build_dir / 'examples' / 'c_example' / 'cgraph2dot_c_example.dot'
    reference_file = project_root / 'tests' / 'reference' / f'gcc-{gcc_version}' / 'cgraph2dot_c_example.dot'
    
    # Check that generated file exists
    if not generated_file.exists():
        print(f"❌ C example: generated file not found: {generated_file}")
        print("   Run first: mkdir build && cd build && cmake .. && make")
        return False
    
    # Check that reference file exists
    if not reference_file.exists():
        print(f"❌ C example: reference file not found: {reference_file}")
        return False
    
    # Compare files
    if compare_dot_files(generated_file, reference_file):
        print(f"✅ C example: matches reference for GCC {gcc_version}")
        return True
    else:
        print(f"❌ C example: does NOT match reference for GCC {gcc_version}")
        return False


def test_fortran_example():
    """Test Fortran example."""
    gcc_version = get_gcc_version()
    if gcc_version not in [8, 11]:
        print(f"⚠️  Skipping test: GCC {gcc_version} is not a target version (need 8 or 11)")
        return True
    
    # File paths
    project_root = Path(__file__).parent.parent
    build_dir = project_root / 'build'
    generated_file = build_dir / 'examples' / 'fortran_example' / 'cgraph2dot_fortran_example.dot'
    reference_file = project_root / 'tests' / 'reference' / f'gcc-{gcc_version}' / 'cgraph2dot_fortran_example.dot'
    
    # Check that generated file exists
    if not generated_file.exists():
        print(f"❌ Fortran example: generated file not found: {generated_file}")
        print("   Run first: mkdir build && cd build && cmake .. && make")
        return False
    
    # Check that reference file exists
    if not reference_file.exists():
        print(f"❌ Fortran example: reference file not found: {reference_file}")
        return False
    
    # Compare files
    if compare_dot_files(generated_file, reference_file):
        print(f"✅ Fortran example: matches reference for GCC {gcc_version}")
        return True
    else:
        print(f"❌ Fortran example: does NOT match reference for GCC {gcc_version}")
        return False


def main():
    """Main test function."""
    print("=" * 60)
    print("cgraph2dot GCC compatibility test")
    print("=" * 60)
    
    gcc_version = get_gcc_version()
    print(f"Detected GCC version {gcc_version}")
    print()
    
    # Run tests
    results = []
    results.append(test_c_example())
    results.append(test_fortran_example())
    
    print()
    print("=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()