"""
CLI entry point for smiles-to-3d.

Usage:
    smiles-render --smiles "OCc1ccc(C=O)o1" --output hmf.png
    smiles-render --batch molecules.txt --out-dir ./pngs/
    smiles-render --pathway spec.yaml --img-dir ./pngs/ --output pathway.svg
"""

import argparse
import sys
import os


def cmd_render(args):
    """Render a single SMILES to 3D PNG."""
    from smiles_to_3d.render import smiles_to_png, RenderConfig

    config = RenderConfig(
        width=args.width,
        height=args.height,
        dpi=args.dpi,
        bond_scale=args.bond_scale,
    )

    try:
        result = smiles_to_png(
            args.smiles,
            output_path=args.output,
            config=config,
            add_hydrogens=not args.no_hydrogens,
        )
        print(f"✓ {result['png']}")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}", file=sys.stderr)
        print("  Install: pip install rdkit", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)


def cmd_batch(args):
    """Batch render from a molecule list file."""
    from smiles_to_3d.render import batch_render, RenderConfig

    config = RenderConfig(
        width=args.width, height=args.height,
        dpi=args.dpi, bond_scale=args.bond_scale,
    )

    # Parse input file: each line is "name smiles"
    molecules = []
    with open(args.file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) == 2:
                molecules.append({"name": parts[0], "smiles": parts[1]})
            elif len(parts) == 1:
                molecules.append({"name": f"mol_{len(molecules):03d}", "smiles": parts[0]})

    if not molecules:
        print("No molecules found in input file.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)
    results = batch_render(molecules, args.out_dir, config)

    success = sum(1 for r in results if r["success"])
    print(f"Done: {success}/{len(results)} succeeded")
    for r in results:
        if not r["success"]:
            print(f"  ✗ {r['name']}: {r.get('error', 'unknown')}")


def cmd_pathway(args):
    """Generate a pathway SVG diagram."""
    from smiles_to_3d.pathway import generate_pathway_svg, PathwaySpec

    # Parse from YAML spec
    if args.spec and args.spec.endswith((".yaml", ".yml")):
        import yaml
        with open(args.spec, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        main = data.get("main_chain", [])
        sides = data.get("side_fragments", [])
        spec = PathwaySpec(
            name=data.get("name", "Pathway"),
            main_chain=[n["id"] for n in main],
            side_fragments=[
                (s["id"], s.get("attach_to", 0), s.get("label", s["id"]))
                for s in sides
            ],
            main_labels={
                n["id"]: n.get("label", n["id"]) for n in main
            },
            side_labels={
                s["id"]: s.get("label", s["id"]) for s in sides
            },
        )
    else:
        print("Please provide a YAML spec file with --spec", file=sys.stderr)
        sys.exit(1)

    try:
        result = generate_pathway_svg(
            args.img_dir, spec, args.output,
            layout=args.layout,
        )
        size_kb = os.path.getsize(result) / 1024
        print(f"✓ {result}  ({size_kb:.0f} KB)")
    except Exception as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="smiles-render",
        description="SMILES to 3D molecular structure rendering toolkit",
    )
    sub = parser.add_subparsers(dest="command", help="Subcommand")

    # render
    p_render = sub.add_parser("render", help="Render a single SMILES to 3D PNG")
    p_render.add_argument("--smiles", "-s", required=True, help="SMILES string")
    p_render.add_argument("--output", "-o", required=True, help="Output PNG path")
    p_render.add_argument("--width", type=int, default=2400)
    p_render.add_argument("--height", type=int, default=1800)
    p_render.add_argument("--dpi", type=int, default=300)
    p_render.add_argument("--bond-scale", type=float, default=1.2)
    p_render.add_argument("--no-hydrogens", action="store_true")

    # batch
    p_batch = sub.add_parser("batch", help="Batch render from a molecule list file")
    p_batch.add_argument("--file", "-f", required=True,
                         help="Input file: each line 'name SMILES'")
    p_batch.add_argument("--out-dir", "-o", required=True,
                         help="Output directory for PNGs")
    p_batch.add_argument("--width", type=int, default=2400)
    p_batch.add_argument("--height", type=int, default=1800)
    p_batch.add_argument("--dpi", type=int, default=300)
    p_batch.add_argument("--bond-scale", type=float, default=1.2)

    # pathway
    p_pathway = sub.add_parser("pathway", help="Generate pathway SVG from YAML spec")
    p_pathway.add_argument("--spec", "-s", required=True,
                           help="YAML spec file")
    p_pathway.add_argument("--img-dir", "-i", required=True,
                           help="Directory containing PNG images")
    p_pathway.add_argument("--output", "-o", required=True,
                           help="Output SVG path")
    p_pathway.add_argument("--layout", default="linear",
                           choices=["linear", "ysplit"])

    args = parser.parse_args()

    if args.command == "render":
        cmd_render(args)
    elif args.command == "batch":
        cmd_batch(args)
    elif args.command == "pathway":
        cmd_pathway(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
