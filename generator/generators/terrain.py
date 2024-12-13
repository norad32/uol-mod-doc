import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from common.utils import parse_xml, format_tile_id_hex

logger = logging.getLogger(__name__)


def parse_terrain(xml_path: Path) -> List[Dict[str, Any]]:
    """Parse a terrain XML file to extract terrain details."""
    root = parse_xml(xml_path)
    if root is None:
        return []

    terrains: List[Dict[str, Any]] = []

    for terrain in root.findall("Terrain"):
        terrains.append(
            {
                "Name": terrain.get("Name", "Unknown"),
                "ID": terrain.get("ID", "0"),
                "TileID": terrain.get("TileID", "0"),
                "R": int(terrain.get("R", "0")),
                "G": int(terrain.get("G", "0")),
                "B": int(terrain.get("B", "0")),
                "Base": terrain.get("Base", "0"),
                "Random": terrain.get("Random", "False"),
            }
        )

    return terrains
  
def parse_altitudes(altitude_xml_path: Path) -> List[Dict[str, Any]]:
    """Parse an altitudes XML file to extract altitude details."""
    root = parse_xml(altitude_xml_path)
    if root is None:
        return []

    altitudes: List[Dict[str, Any]] = []

    for altitude in root.findall("Altitude"):
        altitudes.append({
            "Key": altitude.get("Key", "0"),
            "Type": altitude.get("Type", "Unknown"),
            "Altitude": altitude.get("Altitude", "0"),
            "R": int(altitude.get("R", "0")),
            "G": int(altitude.get("G", "0")),
            "B": int(altitude.get("B", "0"))
        })

    return altitudes


def generate_altitude_markdown(altitudes: List[Dict[str, Any]], output_dir: Path) -> None:
    """Generate Markdown documentation for the given altitudes."""
    output_path = output_dir / "altitude.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not altitudes:
        return

    front_matter = f"""---
title: Altitude
layout: home
nav_order: 5
---

# Altitude

_Generated on {timestamp}_
"""

    content = [front_matter]

    # Group altitudes by Type
    altitudes_by_type: Dict[str, List[Dict[str, Any]]] = {}
    for alt in altitudes:
        t = alt["Type"]
        if t not in altitudes_by_type:
            altitudes_by_type[t] = []
        altitudes_by_type[t].append(alt)

    # Generate sections
    for ttype, alts in altitudes_by_type.items():
        content.append(f"## {ttype}")
        content.append("")
        content.append("|  ID | Altitude | Color |")
        content.append("|:---:|:---------:|:------:|")

        for alt in alts:
            key = alt["Key"]
            altitude_val = alt["Altitude"]
            r, g, b = alt["R"], alt["G"], alt["B"]
            rgb_hex = f"#{r:02X}{g:02X}{b:02X}"

            # Compute luminance and decide text color
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            text_color = "#000000" if luminance > 128 else "#FFFFFF"
            color_style = f"background-color:{rgb_hex}; color:{text_color};"

            content.append(
                f"| {key} | {altitude_val} | <span style='{color_style}'>{rgb_hex}</span> |"
            )

        content.append("")

    try:
        output_path.write_text("\n".join(content), encoding="utf-8")
        logger.info(f"Generated '{output_path}'")
    except IOError as e:
        logger.error(f"Error writing to '{output_path}': {e}")



def generate_terrain_markdown(xml_path: Path, output_dir: Path, altitude_xml_path: Path) -> None:
    """Generate Markdown documentation for a terrain XML file and link to altitude data."""
    output_path = output_dir / "terrain.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    terrains = parse_terrain(xml_path)

    # Parse altitudes and generate altitude.md
    altitudes = parse_altitudes(altitude_xml_path)
    generate_altitude_markdown(altitudes, output_dir)

    # Create a lookup dictionary for altitudes keyed by their "Key"
    altitude_lookup = {a["Key"]: a for a in altitudes}

    if not terrains:
        return

    front_matter = f"""---
title: Terrain
layout: home
nav_order: 4
---

# Terrain

_Generated on {timestamp}_
"""

    content = [front_matter]

    content.append("| Terrain | ID | Name | Tile ID (Hex) | Color | Base  | Random |")
    content.append("|:-------:|:--:|:----:|:-------------:|:-----:|:-----:|:------:|")

    for terrain in terrains:
        tile_id = terrain["TileID"]
        tile_id_hex = format_tile_id_hex(tile_id)
        r, g, b = terrain["R"], terrain["G"], terrain["B"]
        rgb_hex = f"#{r:02X}{g:02X}{b:02X}"

        # Compute luminance (using a standard approximation)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        text_color = "#000000" if luminance > 128 else "#FFFFFF"

        color_style = f"background-color:{rgb_hex}; color:{text_color};"
        image_path = f"assets/tiles/{tile_id_hex}.png"
        
        # Resolve Base field via altitude data if available
        base_key = terrain['Base']
        base_display = base_key
        if base_key in altitude_lookup:
            base_alt = altitude_lookup[base_key]
            base_type = base_alt["Type"]
            base_alt_val = base_alt["Altitude"]
            # Link to altitude section
            # For convenience, convert Type to lowercase for linking to the heading
            base_link = f"[{base_type} {base_alt_val}](altitude#{base_type.lower()})"
            base_display = base_link

        content.append(
            f"| ![{tile_id_hex}]({image_path}) | {terrain['ID']} | {terrain['Name']} | {terrain['TileID']} ({tile_id_hex}) | <span style='{color_style}'>{rgb_hex}</span> | {base_display} | {terrain['Random']} |"
        )

    content.append("")

    try:
        output_path.write_text("\n".join(content), encoding="utf-8")
        logger.info(f"Generated '{output_path}'")
    except IOError as e:
        logger.error(f"Error writing to '{output_path}': {e}")


def generate_terrain(input_base: Path, output_base: Path) -> None:
    """Generate Markdown files for terrain XML files and altitude data."""
    # We assume 'altitude.xml' is in the input_base directory
    altitude_xml_path = input_base / "altitude.xml"

    # First handle the main terrain XML (assuming a single terrain file named something like 'terrain.xml')
    # If there are multiple terrain files, you can adapt this code accordingly.
    # For now, let's assume only one terrain XML file named 'terrain.xml'.
    terrain_xml_path = input_base / "terrain.xml"
    
    generate_terrain_markdown(terrain_xml_path, output_base, altitude_xml_path)
