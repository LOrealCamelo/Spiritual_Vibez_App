#!/usr/bin/env python3
"""Create display PNGs from the owner's untouched original deck.

Development only: requires Pillow (not needed to run the app).
Usage: python mobile/scripts/prepare-tarot-images.py --source-dir /path/to/originals
Source names must match backend/data/tarot_images.json. Originals are never written.
"""
import argparse
import hashlib
import json
from pathlib import Path
import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'backend/data/tarot_images.json'
OUTPUT = ROOT / 'mobile/assets/tarot'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--height', type=int, default=1080)
    args = parser.parse_args()
    source_dir = args.source_dir.resolve()
    if source_dir == OUTPUT.resolve() or not 1 <= args.height <= 1810:
        parser.error('Use a separate original-image directory and a height from 1 to 1810.')
    cards = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if len(cards) != 78 or {c['id'] for c in cards} != set(range(78)):
        raise ValueError('Expected the complete canonical 78-card manifest.')
    for card in cards:
        if not (source_dir / card['source_file']).is_file():
            raise FileNotFoundError(source_dir / card['source_file'])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    original_total = display_total = 0
    for card in cards:
        source = source_dir / card['source_file']
        destination = OUTPUT / card['file']
        if source.resolve() == destination.resolve():
            raise ValueError('An output file must not overwrite an original.')
        source_bytes = source.read_bytes()
        with Image.open(source) as original:
            original.load()
            width, height = original.size
            display_height = min(args.height, height)
            display_width = round(width * display_height / height)
            display = original.resize((display_width, display_height), Image.Resampling.LANCZOS)
            # Retain full color (and alpha, where present). No palette reduction,
            # quantization, cropping or changes to the artwork are applied.
            temporary = destination.with_suffix('.png.tmp')
            display.save(temporary, format='PNG', optimize=True, compress_level=9,
                         icc_profile=original.info.get('icc_profile'))
            temporary.replace(destination)
        output_bytes = destination.read_bytes()
        card.update(source_width=width, source_height=height,
                    source_bytes=len(source_bytes), source_sha256=hashlib.sha256(source_bytes).hexdigest(),
                    display_width=display_width, display_height=display_height,
                    display_bytes=len(output_bytes), display_sha256=hashlib.sha256(output_bytes).hexdigest())
        original_total += len(source_bytes)
        display_total += len(output_bytes)
    MANIFEST.write_text(json.dumps(cards, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Prepared {len(cards)} complete PNG cards with Pillow {PIL.__version__}.')
    print(f'Deck: {original_total/1024**2:.1f} MiB → {display_total/1024**2:.1f} MiB '
          f'({100*(1-display_total/original_total):.1f}% smaller).')
    print('Original files were read only; app filenames and URLs are unchanged.')


if __name__ == '__main__':
    main()
