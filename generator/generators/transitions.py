import logging
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List

from common.utils import parse_xml, extract_tiles, serialize_tiles
from common.markdown import write_tile_table
from common.types import TileKey

logger = logging.getLogger(__name__)


def generate_markdown_from_xml(xml_path: Path, output_dir: Path) -> None:
    """Parse an XML file and generate a corresponding Markdown file."""
    filename = xml_path.stem
    if "_To_" not in filename:
        generate_index_markdown_from_xml(xml_path, output_dir)
    else:
        generate_transition_markdown_from_xml(xml_path, output_dir)


def generate_index_markdown_from_xml(xml_path: Path, output_dir: Path) -> None:
    """Parse an XML file and generate a corresponding Markdown file for the index."""
    filename = xml_path.stem
    source = filename.replace("_", " ")
    if "-" not in source:
        logger.debug(f"Skipping '{xml_path}': Missing '-' in source part.")
        return
    source_prefix, source_name = source.split("-", 1)

    md_dir = output_dir / source_name
    md_dir.mkdir(parents=True, exist_ok=True)
    md_path = md_dir / "index.md"

    root_xml = parse_xml(xml_path)
    if root_xml is None:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    front_matter = f"""---
title: {source_name}
parent: Transitions
layout: home
nav_order: {source_prefix}
---

# {source_name}

_Generated on {timestamp}_
"""

    groups: Dict[TileKey, List[str]] = defaultdict(list)
    file: Dict[TileKey, str] = defaultdict(str)

    # Group TransInfo elements by their (map_tiles, static_tiles) combination
    for trans_info in root_xml.findall("TransInfo"):
        description = trans_info.get("Description", "Unknown")
        map_tiles_element = trans_info.find("MapTiles")
        static_tiles_element = trans_info.find("StaticTiles")

        map_tiles = extract_tiles(map_tiles_element, "MapTile")
        static_tiles = extract_tiles(static_tiles_element, "StaticTile")

        group_key = serialize_tiles(map_tiles, static_tiles)
        groups[group_key].append(description)
        
        # Check for File attribute
        file_attr = trans_info.get("File")
        if file_attr:
            file[group_key] = (file_attr)

    content = [front_matter]

    for group_key, _ in groups.items():
        map_tiles_group, static_tiles_group = group_key

        content.append("## Tiles")
        content.append("")
        write_tile_table(
            content, Counter(map_tiles_group), "../../assets/tiles", "_None_"
        )

        content.append("## Statics")
        content.append("")
        write_tile_table(
            content, Counter(static_tiles_group), "../../assets/statics", "_None_"
        )
        
        # If file is present for this group_key, add Random Statics section
        if file[group_key]:
            content.append("## Random Statics")
            content.append("")
            
            # Convert filename e.g. Cave.xml -> cave for the link
            base_name = file[group_key].rsplit('.', 1)[0]  # Remove .xml
            # Link to ../../statics/{link_target}
            content.append(f"- [{base_name}](../../statics/{base_name})")
            content.append("")

    try:
        md_path.write_text("\n".join(content), encoding="utf-8")
        logger.info(f"Generated '{md_path}'")
    except IOError as e:
        logger.error(f"Error writing to '{md_path}': {e}")


def generate_transition_markdown_from_xml(xml_path: Path, output_dir: Path) -> None:
    """Parse an XML file and generate a corresponding Markdown file for a transition."""
    filename = xml_path.stem
    source_part, target_part = filename.split("_To_", 1)
    source = source_part.replace("_", " ")
    target = target_part.replace("_", " ")

    if "-" not in source:
        logger.debug(f"Skipping '{xml_path}': Missing '-' in source part.")
        return
    _, source_name = source.split("-", 1)

    if "-" not in target:
        logger.debug(f"Skipping '{xml_path}': Missing '-' in target part.")
        return
    target_prefix, target_name = target.split("-", 1)

    md_dir = output_dir / source_name
    md_dir.mkdir(parents=True, exist_ok=True)
    md_path = md_dir / f"{target_name}.md"

    root_xml = parse_xml(xml_path)
    if root_xml is None:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    front_matter = f"""---
title: {target_name}
parent: {source_name}
grand_parent: Transitions
layout: home
nav_order: {target_prefix}
---

# {source_name} to {target_name}

_Generated on {timestamp}_
"""

    groups: Dict[TileKey, List[str]] = defaultdict(list)
    file: Dict[TileKey, str] = defaultdict(str)

    # Group TransInfo elements by their (map_tiles, static_tiles) combination
    for trans_info in root_xml.findall("TransInfo"):
        description = trans_info.get("Description", "Unknown")
        map_tiles_element = trans_info.find("MapTiles")
        static_tiles_element = trans_info.find("StaticTiles")

        map_tiles = extract_tiles(map_tiles_element, "MapTile")
        static_tiles = extract_tiles(static_tiles_element, "StaticTile")

        group_key = serialize_tiles(map_tiles, static_tiles)
        groups[group_key].append(description)
        
        # Check for File attribute
        file_attr = trans_info.get("File")
        if file_attr:
            file[group_key] = (file_attr)

    content = [front_matter]

    for group_key, descriptions in groups.items():
        map_tiles_group, static_tiles_group = group_key

        # Just get all unique descriptions and join them by comma
        unique_descriptions = list(dict.fromkeys(descriptions))
        description_str = ", ".join(unique_descriptions)

        content.append(f"## {description_str}")
        content.append("")
        content.append("### Tiles")
        content.append("")
        write_tile_table(
            content, Counter(map_tiles_group), "../../assets/tiles", "_None_"
        )

        content.append("### Statics")
        content.append("")
        write_tile_table(
            content, Counter(static_tiles_group), "../../assets/statics", "_None_"
        )
        
        # If file is present for this group_key, add Random Statics section
        if file[group_key]:
            content.append("### Random Statics")
            content.append("")
            
            # Convert filename e.g. Cave.xml -> cave for the link
            base_name = file[group_key].rsplit('.', 1)[0]  # Remove .xml
            # Link to ../../../statics/{link_target}
            content.append(f"- [{base_name}](../../../statics/{base_name})")
            content.append("")

    try:
        md_path.write_text("\n".join(content), encoding="utf-8")
        logger.info(f"Generated '{md_path}'")
    except IOError as e:
        logger.error(f"Error writing to '{md_path}': {e}")


def traverse_and_generate_transitions(input_base: Path, output_base: Path) -> None:
    """Traverse the input directory to find XML files and generate Markdown documentation for transitions."""
    for root, _, files in os.walk(input_base):
        for file in files:
            if file.lower().endswith(".xml"):
                xml_path: Path = Path(root) / file
                generate_markdown_from_xml(xml_path, output_base)
