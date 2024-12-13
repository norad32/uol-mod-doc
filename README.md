<h1 align="center">UOL Mod Doc</h3>

---

<p align="center"> Just the Docs Documentation of UO Landscaper Mod.
    <br> 
</p>

## Table of Contents

- [Table of Contents](#table-of-contents)
- [About](#about)
- [Prerequisites](#prerequisites)
- [Usage](#usage)
  - [Generating Documentation](#generating-documentation)
- [Integration With Just the Docs](#integration-with-just-the-docs)
- [License](#license)

## About

This repository provides documentation for [UO Landscaper Mod](https://github.com/norad32/uo-landscaper-mod/) using the [Just the Docs](https://just-the-docs.github.io/just-the-docs/) theme. It includes pre-structured Markdown files and an automated Python-based generator to produce a comprehensive reference for transitions, terrains, and statics used by the mod.

## Prerequisites

To run the documentation generation scripts, ensure you have:

- **Python 3.7+** installed.

## Usage

### Generating Documentation

1. **Prepare Data**:
   Place your XML data files under the appropriate directories, for example:

- `data/transitions/` for transitions XML files
- `data/statics/` for statics XML files
- `data/system/` for terrain and altitude XML files (terrain.xml and altitudes.xml)

2. **Run the Script**:
   Use `main.py` to generate documentation.
   Example:

```bash
python main.py --generate all
```

Available options:

- `--generate transitions`
- `--generate statics`
- `--generate terrains`
- `--generate all` (default)

The output will be placed in the `pages/` directory as Markdown files.

## Integration With Just the Docs

The `pages/` directory is structured for direct use with the Just the Docs Jekyll theme:

## License

This project is licensed under the MIT License. See the LICENSE file for details.
