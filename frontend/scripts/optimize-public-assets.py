"""Optional maintainer utility: pip install pillow fonttools brotli.

No resize, crop, palette change or lossy encoding. Original PNGs/TTFs stay intact.
Generated files are committed so hosts need no image service or build dependency.
"""
from pathlib import Path
import json
from PIL import Image, ImageChops
from fontTools.ttLib import TTFont

root = Path(__file__).resolve().parents[1]
names = ['home-mystic-room-arabic', 'home-light-portal', 'home-tarot-moon',
         'home-feature-icons', 'spiritual-vibz-logo-compact',
         'cartoon_me_transparent1', 'neurospicy-mystic-logo']
output = root / 'assets' / 'optimized'
output.mkdir(exist_ok=True)
report = []
for name in names:
    source = root / 'assets' / (name + '.png')
    target = output / (name + '.webp')
    with Image.open(source) as image:
        rgba = image.convert('RGBA')
        rgba.save(target, 'WEBP', lossless=True, exact=True, method=6)
        with Image.open(target) as encoded:
            assert encoded.size == rgba.size
            assert ImageChops.difference(rgba, encoded.convert('RGBA')).getbbox(alpha_only=False) is None
    assert target.stat().st_size < source.stat().st_size
    report.append({'source': source.relative_to(root).as_posix(),
                   'optimized': target.relative_to(root).as_posix(),
                   'before_bytes': source.stat().st_size, 'after_bytes': target.stat().st_size})
for source in sorted((root / 'assets' / 'fonts').glob('*.ttf')):
    font = TTFont(source)
    font.flavor = 'woff2'
    target = source.with_suffix('.woff2')
    font.save(target)
    report.append({'source': source.relative_to(root).as_posix(),
                   'optimized': target.relative_to(root).as_posix(),
                   'before_bytes': source.stat().st_size, 'after_bytes': target.stat().st_size})
(output / 'sizes.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
