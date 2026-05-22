# smiles-to-3d

**SMILES → 3D Molecular Structure Rendering & Reaction Pathway Diagram Toolkit**

Convert SMILES strings to publication-quality 3D ball-and-stick images, then
assemble them into annotated reaction pathway diagrams — everything you need to
create figures for your chemistry paper.

---

## Quick Start

```bash
# Install
git clone https://github.com/mako-star/smiles-to-3d.git
cd smiles-to-3d
pip install -e .

# Prerequisites (see docs/installation.md for details)
pip install rdkit          # or: conda install -c conda-forge rdkit
# PyMOL: https://pymol.org/

# Render a single molecule
smiles-render render --smiles "OCc1ccc(C=O)o1" --output hmf.png
```

Or use the Python API:

```python
from smiles_to_3d import smiles_to_png
result = smiles_to_png("OCc1ccc(C=O)o1", "hmf.png")
```

Batch rendering:

```bash
# Create molecules.txt: each line "name SMILES"
echo "HMF OCc1ccc(C=O)o1" > molecules.txt
echo "CH2O C=O" >> molecules.txt
smiles-render batch --file molecules.txt --out-dir ./pngs/
```

---

## What It Does

```
┌─────────────────────────────────────────────────────────┐
│  SMILES strings                                          │
│  "OCc1ccc(C=O)o1", "C=O", "[CH2]OC=CO", ...            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │  RDKit          │  Embed 3D coords +
              │  EmbedMolecule  │  MMFF optimization
              │  → SDF          │
              └───────┬────────┘
                      │
                      ▼
              ┌────────────────┐
              │  PyMOL          │  Orthographic projection
              │  Ball+Stick     │  2400×1800 @ 300 DPI
              │  → PNG          │  C=gray / O=red / H=white
              └───────┬────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Pre-rendered PNGs  →  Pathway SVG Assembly              │
│                                                          │
│  HMF ──→ C₃H₅O₂ ──→ CH₂O                               │
│   │               │                                      │
│   └──→ C₃HO      └──→ C₂H₃O                            │
│                                                          │
│  Self-contained SVG, base64-embedded, LaTeX-ready        │
└─────────────────────────────────────────────────────────┘
```

### Three Output Formats

| Format | Tool | Best for |
|--------|------|----------|
| **Pure SVG** | `pathway.py` | Publication figures, LaTeX `\includesvg`, Inkscape editing |
| **PNG/PDF** | `pathway_mpl.py` | Batch automation, data-figure style |
| **PPTX** | `pathway_pptx.py` | Manual tweaking, collaboration, PowerPoint export |

---

## Core API

### SMILES → 3D PNG

```python
from smiles_to_3d import smiles_to_png, RenderConfig

config = RenderConfig(
    width=2400, height=1800, dpi=300,
    bond_scale=1.2,
    carbon_color="gray55",
    oxygen_color="red",
    hydrogen_color="white",
)

result = smiles_to_png("OCc1ccc(C=O)o1", "hmf.png", config)
# result = {"png": "/abs/path/to/hmf.png"}
```

### Batch Rendering

```python
from smiles_to_3d.render import batch_render

results = batch_render([
    {"name": "HMF",    "smiles": "OCc1ccc(C=O)o1"},
    {"name": "CH2O",   "smiles": "C=O"},
    {"name": "C3HO",   "smiles": "[CH]=C1[C]O1"},
], "./pngs/")
```

### Pathway SVG Assembly

```python
from smiles_to_3d.pathway import PathwaySpec, generate_pathway_svg

spec = PathwaySpec(
    name="My Pathway",
    main_chain=["HMF", "C3H5O2", "CH2O"],
    side_fragments=[("C3HO", 0, "C₃HO"), ("C2H3O", 1, "C₂H₃O")],
    viewbox=(0, 0, 1100, 430),
    main_labels={"HMF": "HMF", "C3H5O2": "C₃H₅O₂", "CH2O": "CH₂O"},
)

generate_pathway_svg("./pngs/", spec, "pathway.svg")
```

### Matplotlib / PPTX Assembly (YAML-driven)

```bash
# Matplotlib
python -m smiles_to_3d.pathway_mpl spec.yaml --img-dir ./pngs/ -o pathway.pdf

# PowerPoint (editable)
python -m smiles_to_3d.pathway_pptx spec.yaml --img-dir ./pngs/ -o pathway.pptx
```

---

## Rendering Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| Resolution | 2400 × 1800 px | 8" × 6" at 300 DPI |
| DPI | 300 | Publication standard |
| Bond scaling | 1.2× | Expands bonds from centroid |
| Projection | Orthographic | No perspective distortion |
| Style | Ball + Stick | `stick_radius=0.13`, `sphere_scale=0.25` |
| Carbon | `gray55` | #8C8C8C |
| Oxygen | `red` | #FF0000 |
| Hydrogen | `white` | #FFFFFF |

### Arrow Styles (SVG)

- **Solid arrows**: Style 11 chevron (`#2c2c2c`, stroke-width 1.6)
- **Dashed arrows**: Style D5 chevron (`#aaaaaa`, stroke-dasharray 6,4)
- **Typography**: Times New Roman, 14–16pt, editable `<text>` elements

---

## Project Structure

```
smiles-to-3d/
├── smiles_to_3d/           # Python package
│   ├── __init__.py
│   ├── render.py           # SMILES → 3D PNG (RDKit + PyMOL)
│   ├── pathway.py          # SVG pathway assembly
│   ├── pathway_mpl.py      # Matplotlib pathway composer
│   └── pathway_pptx.py     # PowerPoint pathway composer
├── templates/
│   ├── pathway-template.svg
│   └── spec-template.yaml
├── examples/
│   ├── basic_render.py     # Simple single-molecule render
│   ├── pathway_demo.py     # SVG pathway assembly demo
│   └── spec_example.yaml   # YAML spec for mpl/pptx pipelines
├── scripts/
│   ├── batch_render.py     # Batch SMILES → PNG
│   └── gen_pathway_svg.py  # Full pathway SVG generator
├── docs/
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## Dependencies

| Package | Purpose | Required? |
|---------|---------|-----------|
| `rdkit` | SMILES parsing + 3D coordinate generation | **Yes** |
| PyMOL | High-quality 3D rendering | **Yes** |
| `pillow` | Image loading/resizing | Yes |
| `pyyaml` | Spec file parsing | For mpl/pptx |
| `matplotlib` | Matplotlib pipeline | Optional |
| `python-pptx` + `lxml` | PowerPoint pipeline | Optional |

Install all with:

```bash
pip install smiles-to-3d[all]
```

---

## Known Limitations

- **PyMOL CLI `fetch smiles` does not work** — SMILES must be converted to SDF
  via RDKit first. PyMOL's built-in `fetch` silently produces blank PNGs.
- **Convergent topologies** (where a product has multiple precursors) require
  custom Y-split or mesh layouts. The linear layout algorithm cannot express them.
- **CH₂O ≠ CH₃O** — formaldehyde and methoxy radical are different species.
  Always verify SMILES against your reaction network data.
- **PNG < 50 KB = failed render** — if PyMOL output is suspiciously small,
  check that the SDF loaded correctly.

---

## FAQ

**Q: PyMOL produces a 16 KB blank PNG. What's wrong?**
A: You're using PyMOL's `fetch smiles=...` which doesn't work in CLI mode.
Use RDKit to generate the SDF first, then `load` it in PyMOL.

**Q: How do I customize atom colors?**
A: Pass a `RenderConfig` with your color names:
```python
config = RenderConfig(carbon_color="slate", oxygen_color="red", hydrogen_color="white")
```

**Q: Can I render without hydrogens?**
A: Yes: `smiles_to_png(smiles, add_hydrogens=False)`. But ball+stick style
looks better with hydrogens visible.

**Q: The SVG arrows don't render in my viewer.**
A: Ensure the `<marker>` elements are inside `<defs>` and `marker-end` URLs
use the correct `id`. Our template handles this.

---

## Documentation

Full docs at [docs/](docs/):
- [Installation](docs/installation.md)
- [SMILES → 3D Workflow](docs/workflow.md)
- [Pathway Spec Format](docs/spec-format.md)
- [FAQ](docs/faq.md)

## Citation

If you use smiles-to-3d in your research, please cite:

```
@software{smiles-to-3d,
  title = {smiles-to-3d: SMILES to 3D Molecular Structure Rendering Toolkit},
  year = {2026},
  author = {mako-star},
  url = {https://github.com/mako-star/smiles-to-3d}
}
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
