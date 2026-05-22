# FAQ

## General

**Q: What file formats does this tool produce?**

A: Three output formats:
- **PNG** — individual 3D molecule renders (2400×1800, 300 DPI)
- **SVG** — self-contained pathway diagrams (base64-embedded, LaTeX-ready)
- **PDF/PNG** — via the Matplotlib pipeline
- **PPTX** — editable PowerPoint diagrams

**Q: Does this tool require a GPU?**

A: No. PyMOL CPU rendering is used. Each molecule takes 3–10 seconds on a modern CPU.

**Q: Can I use this without PyMOL?**

A: No. PyMOL is required for the 3D ball-and-stick rendering. There is no pure-Python fallback
that produces comparable quality.

## SMILES & Chemistry

**Q: My SMILES has radicals — does it work?**

A: Yes. Radical SMILES like `[CH2]OC=CO` and `[OH]` are supported.
Use brackets for explicit electron counts: `[CH2]` (radical methylene) vs `C` (normal carbon).

**Q: The rendered structure looks wrong — atoms overlap.**

A: Try:
1. Use `random_seed` parameter to try different conformers
2. Check that your SMILES is chemically valid
3. For large rings, ETKDG may struggle — try `AllChem.EmbedMolecule(mol, useRandomCoords=True)`

**Q: CH₂O and CH₃O look different — why?**

A: They are different species:
- CH₂O (formaldehyde): `C=O` — neutral, MW=30
- CH₃O (methoxy radical): `[CH2]O` — radical, MW=31
Always verify SMILES against your reaction network data.

## Rendering

**Q: PyMOL produces a 16 KB blank PNG.**

A: This is the most common issue. PyMOL's `fetch smiles=...` doesn't work in CLI mode.
Use the RDKit → SDF → PyMOL pipeline instead (this is what smiles-to-3d does by default).

**Q: Can I change atom colors?**

A: Yes:
```python
from smiles_to_3d import RenderConfig
config = RenderConfig(
    carbon_color="slate",
    oxygen_color="red",
    hydrogen_color="white",
)
```

**Q: The PNG is too large / small.**

A: Adjust resolution:
```python
config = RenderConfig(width=1200, height=900, dpi=150)
```

**Q: Can I render without hydrogen atoms?**

A: Yes:
```python
result = smiles_to_png(smiles, output_path, add_hydrogens=False)
```
But the ball-and-stick style looks better with hydrogens visible.

## Pathway Diagrams

**Q: My pathway has a Y-split / convergent topology. Can I use this?**

A: The linear layout algorithm works for simple sequential pathways.
For complex topologies:
1. Use the pure SVG pipeline with custom coordinates
2. See `scripts/gen_pathway_svg.py` for Y-split examples (cellulose pathway)

**Q: Can I edit the SVG in Inkscape?**

A: Yes. All SVGs are pure SVG (no HTML wrapper), with editable `<text>` elements
and logical `<g>` grouping layers.

**Q: The SVG arrows don't show in my PDF viewer.**

A: Some PDF viewers don't render SVG markers. Convert with:
```bash
# Option 1: Inkscape
inkscape pathway.svg --export-filename=pathway.pdf

# Option 2: rsvg-convert
rsvg-convert -f pdf -o pathway.pdf pathway.svg

# Option 3: cairosvg (Python)
pip install cairosvg
python -c "import cairosvg; cairosvg.svg2pdf(url='pathway.svg', write_to='pathway.pdf')"
```

## Troubleshooting

**Q: `ImportError: No module named 'rdkit'`**

A: RDKit can be tricky to install via pip on some systems. Try conda:
```bash
conda install -c conda-forge rdkit
```

**Q: PyMOL crashes with "Segmentation fault"**

A: This can happen with certain SDF files. Try:
- Use RDKit instead of OpenBabel for SDF generation
- Reduce the molecule size (split polymers into monomers)
- Update PyMOL to the latest version
