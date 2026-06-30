"""inspect_template.py — Print template structure so the agent knows what's inside.

Usage:
    python scripts/inspect_template.py <path-to-template.pptx>

Prints layout names + indices, slide size, demo slide count, and the role mapping
that `find_layout_by_role()` will resolve to. Run this FIRST when working with
any new template, before generating any slide code.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from slide_helpers import inspect_template, load_clean_template, find_layout_by_role


def main(template_path: str) -> None:
    info = inspect_template(template_path)
    prs = load_clean_template(template_path)

    print("\n── Role mapping (find_layout_by_role) ──")
    for role in ("cover", "section", "content", "closing"):
        layout = find_layout_by_role(prs, role, template_info=info)
        idx = info["layouts"].index(layout.name) if layout.name in info["layouts"] else "?"
        print(f"  {role:8s} → [{idx}] {layout.name}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/inspect_template.py <template.pptx>")
    main(sys.argv[1])
