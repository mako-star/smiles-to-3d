# Pathway Spec YAML Format

Used by `smiles-render pathway` and the Matplotlib/PPTX pipelines.

## Full Example

```yaml
canvas:
  dpi: 300
  bg: "#ffffff"

main_chain:
  - id: HMF
    png: HMF_bond1.2.png
    label: "HMF"
    label_cn: "羟甲基糠醛"
    arrow_label: "+C₃HO"

  - id: C3H5O2
    png: C3H5O2_bond1.2.png
    label: "C₃H₅O₂"
    arrow_label: "+C₂H₃O"

  - id: CH2O
    png: CH2O_bond1.2.png
    label: "CH₂O"
    label_cn: "甲醛"

side_fragments:
  - id: C3HO
    png: C3HO_bond1.2.png
    label: "C₃HO"
    attach_to: 0
    position: above

  - id: C2H3O
    png: C2H3O_bond1.2.png
    label: "C₂H₃O"
    attach_to: 1
    position: above
```

## Field Reference

### `canvas` (optional)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `dpi` | int | 300 | Output resolution |
| `bg` | str | `"#ffffff"` | Background color (hex) |

### `main_chain[]` (required)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | **Yes** | Unique node identifier (ASCII, no spaces) |
| `png` | string | **Yes** | PNG filename relative to `--img-dir` |
| `label` | string | **Yes** | Chemical formula label (e.g. `"C₆H₆O₃"`) |
| `label_cn` | string | No | Chinese name (requires Noto Sans SC font) |
| `arrow_label` | string | No | Text on the arrow after this node (e.g. `"+H·"`) |

### `side_fragments[]` (optional)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | **Yes** | Unique fragment identifier |
| `png` | string | **Yes** | PNG filename |
| `label` | string | **Yes** | Chemical formula label |
| `attach_to` | int | **Yes** | 0-based index of main-chain parent node |
| `position` | string | No | `"above"` or `"below"` (default: `"above"`) |
| `arrow_label` | string | No | Text on dashed arrow |

## Usage

```bash
# SVG pathway (Python API)
python -c "
from smiles_to_3d import PathwaySpec, generate_pathway_svg
spec = PathwaySpec(...)
generate_pathway_svg('./pngs/', spec, 'output.svg')
"

# SVG pathway (CLI)
smiles-render pathway --spec spec.yaml --img-dir ./pngs/ --output pathway.svg

# Matplotlib pipeline
python -m smiles_to_3d.pathway_mpl spec.yaml --img-dir ./pngs/ -o pathway.pdf

# PowerPoint pipeline
python -m smiles_to_3d.pathway_pptx spec.yaml --img-dir ./pngs/ -o pathway.pptx
```

## Layout Notes

- Main chain nodes are placed **evenly spaced horizontally**
- Side fragments are placed **above** the main chain, connected by dashed S-curve arrows
- If the total width exceeds the canvas, the Matplotlib pipeline auto-scales
- For complex topologies (Y-split, convergent), use the pure SVG pipeline with custom coordinates
