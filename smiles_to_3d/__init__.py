"""
smiles-to-3d: SMILES → 3D Molecular Structure Rendering & Pathway Diagram Toolkit

Convert SMILES strings to publication-quality 3D molecular structure images,
then assemble them into annotated reaction pathway diagrams (SVG / PNG / PPTX).

Core workflow:
  1. SMILES → 3D SDF  (RDKit: EmbedMolecule + MMFF optimization)
  2. 3D SDF → PNG      (PyMOL: orthographic, 2400×1800 @ 300 DPI, ball+stick)
  3. PNGs → SVG        (pure SVG: base64-embedded, Style 11/D5 arrows)
"""

__version__ = "1.0.0"
__author__ = "HMF Reaction Network Team"
