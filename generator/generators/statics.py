import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import os

from common.utils import parse_xml
from common.utils import format_tile_id_hex

logger = logging.getLogger(__name__)

def parse_statics(xml_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Parse a statics XML file to extract descriptions and tile data."""
    root = parse_xml(xml_path)
    if root is None:
        return {}

    statics_data: Dict[str, List[Dict[str, Any]]] = {}

    for statics in root.findall("Statics"):
        description = statics.get("Description", "Unknown")
        freq = int(statics.get("Freq", "0"))
        tiles: List[Dict[str, Any]]= []

        for static in statics.findall("Static"):
            tile_id = static.get("TileID", "0")
            x = static.get("X", "0")
            y = static.get("Y", "0")
            z = static.get("Z", "0")
            hue = static.get("Hue", "0")
            tiles.append(
                {
                    "TileID": tile_id,
                    "X": x,
                    "Y": y,
                    "Z": z,
                    "Hue": hue,
                    "Frequency": freq,
                }
            )

        if description not in statics_data:
            statics_data[description] = []
        statics_data[description].extend(tiles)

    return statics_data


def generate_statics_markdown(xml_path: Path, output_dir: Path) -> None:
    """Generate Markdown documentation for a statics XML file."""
    filename = xml_path.stem
    output_path = output_dir / f"{filename}.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    statics_data = parse_statics(xml_path)

    if not statics_data:
        return

    front_matter = f"""---
title: {filename}
parent: Statics
layout: home
---

# {filename}

_Generated on {timestamp}_
"""

    content = [front_matter]

    for description, tiles in statics_data.items():
        content.append(f"## {description}")
        content.append("")
        content.append("| Item | ID (Hex) | X, Y, Z | Frequency |")
        content.append("|:----:|:--------:|:-------:|:---------:|")

        for tile in tiles:
            tile_id = tile["TileID"]
            tile_id_hex = format_tile_id_hex(tile_id)
            x = tile["X"]
            y = tile["Y"]
            z = tile["Z"]
            frequency = tile["Frequency"]
            image_path = f"../assets/statics/{tile_id_hex}.png"

            content.append(
                f"| ![{tile_id_hex}]({image_path}) | {tile_id} ({tile_id_hex}) | {x}, {y}, {z} | {frequency} |"
            )

        content.append("")

    try:
        output_path.write_text("\n".join(content), encoding="utf-8")
        logger.info(f"Generated '{output_path}'")
    except IOError as e:
        logger.error(f"Error writing to '{output_path}': {e}")


def traverse_and_generate_statics(input_base: Path, output_base: Path) -> None:
    """Traverse the input directory and generate Markdown files for statics XML files."""
    for root, _, files in os.walk(input_base):
        for file in files:
            if file.lower().endswith(".xml"):
                xml_path = Path(root) / file
                generate_statics_markdown(xml_path, output_base)
