import logging
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Optional, List
from .types import Tile

logger = logging.getLogger(__name__)

def parse_xml(xml_path: Path) -> Optional[ET.Element]:
    """Parse an XML file and return the root element or None on error."""
    try:
        tree = ET.parse(xml_path)
        return tree.getroot()
    except ET.ParseError as e:
        logger.error(f"Error parsing '{xml_path}': {e}")
        return None

def extract_tiles(element: Optional[ET.Element], tile_tag: str) -> List[Tile]:
    """Extract tile data from a given XML element.

    Args:
        element: XML Element containing tile definitions.
        tile_tag: Tag name ('MapTile' or 'StaticTile') to extract.

    Returns:
        A list of (TileID, AltIDMod) tuples.
    """
    if element is None:
        return []
    return [
        (tile.get("TileID", "0"), tile.get("AltIDMod", "0"))
        for tile in element.findall(tile_tag)
    ]

def serialize_tiles(map_tiles: List[Tile], static_tiles: List[Tile]):
    """Serialize map and static tiles into a hashable key."""
    sorted_map = tuple(sorted(map_tiles))
    sorted_static = tuple(sorted(static_tiles))
    return (sorted_map, sorted_static)

def format_tile_id_hex(tile_id: str) -> str:
    """Format a tile ID into a hexadecimal string."""
    try:
        return f"0x{int(tile_id):04X}"
    except ValueError:
        return "Invalid ID"
