import argparse
import sys
import json
from .generator import generate_module_zip


def main():
    p = argparse.ArgumentParser(description="TF Wizard CLI - generate terraform module zip from JSON spec")
    p.add_argument("spec", nargs="?", help="Path to JSON spec file (defaults to stdin)")
    p.add_argument("-o", "--output", help="Output zip path (defaults to stdout)")
    args = p.parse_args()

    if args.spec:
        with open(args.spec, "r", encoding="utf-8") as f:
            spec = json.load(f)
    else:
        spec = json.load(sys.stdin)

    zip_bytes = generate_module_zip(spec)

    if args.output:
        with open(args.output, "wb") as f:
            f.write(zip_bytes)
    else:
        # write to stdout (binary)
        sys.stdout.buffer.write(zip_bytes)


if __name__ == "__main__":
    main()
