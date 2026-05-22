# SMILES → 3D Rendering Workflow

This document describes the complete pipeline from a SMILES string to a
publication-quality 3D molecular structure PNG.

## Pipeline Overview

```
SMILES string
    │
    ▼  RDKit: Chem.MolFromSmiles()
Mol object
    │
    ▼  RDKit: AddHs() → EmbedMolecule() → MMFFOptimizeMolecule()
3D SDF file  (with optimized coordinates)
    │
    ▼  PyMOL: load SDF → stick+sphere → ray trace
PNG file  (2400×1800 @ 300 DPI, orthographic)
```

## Why RDKit → SDF → PyMOL?

PyMOL has a built-in `fetch smiles=...` command, but it **does not work** in
headless CLI mode (`pymol -c`). It silently produces ~16 KB blank PNGs.

RDKit provides:
- Robust SMILES parsing
- ETKDG conformer embedding (experimentally validated)
- MMFF94 force field optimization
- Reliable SDF output that PyMOL can load

## Step-by-Step

### 1. Python API (Recommended)

```python
from smiles_to_3d import smiles_to_png

result = smiles_to_png("OCc1ccc(C=O)o1", "hmf.png")
print(result["png"])  # /absolute/path/to/hmf.png
```

### 2. CLI

```bash
smiles-render render --smiles "OCc1ccc(C=O)o1" --output hmf.png
```

### 3. Manual (RDKit)

```python
from rdkit import Chem
from rdkit.Chem import AllChem

smiles = "OCc1ccc(C=O)o1"
mol = Chem.MolFromSmiles(smiles)
mol = Chem.AddHs(mol)
AllChem.EmbedMolecule(mol, randomSeed=42)
AllChem.MMFFOptimizeMolecule(mol)

writer = Chem.SDWriter("molecule.sdf")
writer.write(mol)
writer.close()
```

### 4. Manual (PyMOL)

```pml
# render.pml
load molecule.sdf, mol
hide everything
show sticks, mol
show spheres, mol
color gray55, elem C
color red, elem O
color white, elem H
set orthoscopic, on
bg_color white
viewport 2400, 1800
ray 2400, 1800
png output.png, dpi=300
quit
```

```bash
pymol -c -q render.pml
```

## Rendering Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Image size | 2400 × 1800 px | Equivalent to 8" × 6" at 300 DPI |
| DPI | 300 | Publication standard |
| Bond length scaling | 1.2× | Expands from centroid, improves visual clarity |
| Projection | Orthographic | No perspective distortion |
| Stick radius | 0.13 | Thinner than PyMOL default |
| Sphere scale | 0.25 | Smaller atom spheres |

### Atom Colors

| Element | PyMOL Color | Hex |
|---------|------------|-----|
| Carbon (C) | `gray55` | #8C8C8C |
| Oxygen (O) | `red` | #FF0000 |
| Hydrogen (H) | `white` | #FFFFFF |
| Nitrogen (N) | `blue` | #0000FF |
| Sulfur (S) | `yellow` | #FFFF00 |

Customize with `RenderConfig`:
```python
from smiles_to_3d import RenderConfig
config = RenderConfig(carbon_color="slate", oxygen_color="red")
```

## Verification

After rendering, verify the output:

1. **File size**: PNG must be > 50 KB. ~16 KB = failed render.
2. **Visual check**: Open the PNG and confirm atoms are visible (not blank white).
3. **Atom count**: `mol.GetNumAtoms()` should match expected atoms (including H).

## Common Issues

### PNG is 16 KB (blank)

PyMOL failed to load the SDF. Check:
- SDF file ends with `M  END` + `$$$$`
- PyMOL working directory contains the SDF (use absolute paths)

### RDKit fails to parse SMILES

Some SMILES strings contain non-standard characters. Try:
```python
from rdkit import Chem
mol = Chem.MolFromSmiles(smiles, sanitize=False)  # Skip validation
Chem.SanitizeMol(mol)  # Manual sanitize
```

### "No module named 'rdkit'"

```bash
pip install rdkit
# or if that fails:
conda install -c conda-forge rdkit
```

### PyMOL not found

```bash
which pymol
# If nothing: install from https://pymol.org
# If installed but not on PATH: pass pymol_bin="/path/to/pymol"
```
