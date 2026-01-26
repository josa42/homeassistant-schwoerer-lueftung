#!/usr/bin/env python3
"""Sort translation files alphabetically."""

import json
from pathlib import Path


def sort_dict_recursive(obj):
    """
    Recursively sort dictionary keys alphabetically.
    
    - Dict values: sort by keys
    - List values: keep as-is
    - Other values: keep as-is
    """
    if isinstance(obj, dict):
        return {k: sort_dict_recursive(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        return obj
    else:
        return obj


def sort_translation_file(file_path: Path) -> None:
    """Sort a translation file alphabetically."""
    print(f"Sorting {file_path.relative_to(Path.cwd())}...")
    
    # Read the file
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Sort recursively
    sorted_data = sort_dict_recursive(data)
    
    # Write back with proper formatting
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
        f.write("\n")  # Add trailing newline
    
    print(f"  ✓ Sorted")


def main():
    """Sort all translation files."""
    base_path = Path(__file__).parent.parent
    component_path = base_path / "custom_components" / "schwoerer_lueftung"
    
    translation_files = [
        component_path / "strings.json",
        component_path / "translations" / "en.json",
        component_path / "translations" / "de.json",
    ]
    
    print("=== Sorting Translation Files ===\n")
    
    for file_path in translation_files:
        if file_path.exists():
            sort_translation_file(file_path)
        else:
            print(f"  ⚠ File not found: {file_path.relative_to(Path.cwd())}")
    
    print("\n✅ All translation files sorted!")


if __name__ == "__main__":
    main()
