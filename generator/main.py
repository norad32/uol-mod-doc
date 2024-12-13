import logging
import argparse
from pathlib import Path

from generators.transitions import traverse_and_generate_transitions
from generators.statics import traverse_and_generate_statics
from generators.terrain import generate_terrain

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Markdown documentation from XML files.")
    
    # What to generate
    parser.add_argument(
        "--generate",
        choices=["transitions", "statics", "terrains", "all"],
        default="all",
        help="Specify what to generate: transitions, statics, terrains, or all."
    )

    # Input and output directories for transitions
    parser.add_argument(
        "--transitions-input",
        type=Path,
        default=Path("../../data/transitions"),
        help="Input directory containing transitions XML files."
    )
    parser.add_argument(
        "--transitions-output",
        type=Path,
        default=Path("../docs/transitions"),
        help="Output directory for transitions Markdown."
    )

    # Input and output directories for statics
    parser.add_argument(
        "--statics-input",
        type=Path,
        default=Path("../../data/statics"),
        help="Input directory containing statics XML files."
    )
    parser.add_argument(
        "--statics-output",
        type=Path,
        default=Path("../docs/statics"),
        help="Output directory for statics Markdown."
    )

    # Input and output directories for terrains
    parser.add_argument(
        "--terrains-input",
        type=Path,
        default=Path("../../data/system"),
        help="Input terrain XML files."
    )
    parser.add_argument(
        "--terrains-output",
        type=Path,
        default=Path("../docs"),
        help="Output directory for terrains Markdown."
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)

    # Generate transitions if requested
    if args.generate in ["transitions", "all"]:
        if not args.transitions_input.exists():
            logger.error(f"Input directory '{args.transitions_input}' does not exist.")
        else:
            args.transitions_output.mkdir(parents=True, exist_ok=True)
            traverse_and_generate_transitions(args.transitions_input, args.transitions_output)
            logger.info("Transitions documentation generation completed.")

    # Generate statics if requested
    if args.generate in ["statics", "all"]:
        if not args.statics_input.exists():
            logger.error(f"Input directory '{args.statics_input}' does not exist.")
        else:
            args.statics_output.mkdir(parents=True, exist_ok=True)
            traverse_and_generate_statics(args.statics_input, args.statics_output)
            logger.info("Statics documentation generation completed.")

    # Generate terrains if requested
    if args.generate in ["terrains", "all"]:
        if not args.terrains_input.exists():
            logger.error(f"Input directory '{args.terrains_input}' does not exist.")
        else:
            generate_terrain(args.terrains_input, args.terrains_output)
            logger.info("Terrain documentation generation completed.")


if __name__ == "__main__":
    main()
