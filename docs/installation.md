# Installation

## Requirements

| Requirement | Purpose | Install |
|------------|---------|---------|
| Python ≥ 3.8 | Runtime | [python.org](https://python.org) |
| RDKit | SMILES parsing + 3D coords | `pip install rdkit` or `conda install -c conda-forge rdkit` |
| PyMOL | 3D rendering | [pymol.org](https://pymol.org) |
| Pillow | Image I/O | `pip install pillow` |

### Optional

| Package | Purpose | Install |
|---------|---------|---------|
| matplotlib + numpy | Matplotlib pipeline | `pip install smiles-to-3d[mpl]` |
| python-pptx + lxml | PowerPoint pipeline | `pip install smiles-to-3d[pptx]` |

## Install from PyPI (coming soon)

```bash
pip install smiles-to-3d
pip install smiles-to-3d[all]   # with all optional deps
```

## Install from source

```bash
git clone https://github.com/mako-star/smiles-to-3d.git
cd smiles-to-3d
pip install -e .
```

This installs in "editable" mode — changes to the source code take effect immediately.

## Verify installation

```bash
smiles-render --help
```

Expected output:
```
usage: smiles-render [-h] {render,batch,pathway} ...

positional arguments:
  {render,batch,pathway}
    render              Render a single SMILES to 3D PNG
    batch               Batch render from a molecule list file
    pathway             Generate pathway SVG from YAML spec
```

Or in Python:

```python
>>> from smiles_to_3d import smiles_to_png, PathwaySpec
>>> print("OK")
```

## RDKit on different platforms

**Linux (pip)**:
```bash
pip install rdkit
```

**macOS (conda recommended)**:
```bash
conda install -c conda-forge rdkit
```

**Windows**:
```bash
conda install -c conda-forge rdkit
```

## PyMOL

PyMOL must be installed separately and available on your PATH. Download from [pymol.org](https://pymol.org).

Verify:
```bash
pymol -c -q -d "print('pymol OK'); quit"
```
