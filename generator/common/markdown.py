from typing import List, Counter as CounterType
from .utils import format_tile_id_hex
from .types import Tile


def write_tile_table(
    content: List[str],
    tile_counts: CounterType[Tile],
    image_path: str,
    empty_label: str,
) -> None:
    """Write a tile table (map or static) to the content list.

    Args:
        content: List of strings representing lines in the markdown content.
        tile_counts: A Counter of tile occurrences.
        image_path: Path to the images directory (used in markdown).
        empty_label: A markdown label to use if there are no tiles.
    """
    total = sum(tile_counts.values())
    if total > 0:
        # Create the table header
        content.append("| Tile | ID (Hex) | Z | Chance |")
        content.append("|:----:|:--------:|:--:|:------:|")
        for (tile_id, alt_id_mod), count in sorted(
            tile_counts.items(), key=lambda x: int(x[0][0])
        ):
            tile_id_hex = format_tile_id_hex(tile_id)
            chance_str = f"{(count / total) * 100:.0f}%"
            content.append(
                f"| ![{tile_id_hex}]({image_path}/{tile_id_hex}.png) | {tile_id} ({tile_id_hex}) | {alt_id_mod} | {chance_str} |"
            )
        content.append("")
    else:
        content.append(empty_label)
        content.append("")
