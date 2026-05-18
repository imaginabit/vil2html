#!/usr/bin/env python3
"""vil2html — Ferris Sweep .vil → standalone HTML keymap visualizer.

Usage:
    python3 vil2html.py input.vil [output.html]
"""

import json
import sys
from pathlib import Path

from renderer import build_html


def main():
    if len(sys.argv) < 2:
        print(f'Usage: {Path(sys.argv[0]).name} input.vil [output.html]',
              file=sys.stderr)
        sys.exit(1)

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix('.html')

    try:
        vil = json.loads(src.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f'Error reading {src}: {e}', file=sys.stderr)
        sys.exit(1)

    dst.write_text(build_html(vil, src.stem), encoding='utf-8')
    print(f'✓  {dst}')


if __name__ == '__main__':
    main()
