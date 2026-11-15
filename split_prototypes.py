#!/usr/bin/env python3
"""Extract two standalone source files from the locally saved deployment.

Usage: python3 split_prototypes.py
No server, build dependencies, or network access required.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f'Expected exactly one source marker: {old[:90]!r}')
    return text.replace(old, new, 1)


def extract(source, group, number):
    # Strip the hosting platform's recording and page-view injection, not lab telemetry.
    text = re.sub(r'<script data-arena-[^>]*>[\s\S]*?</script>\s*', '', source)
    text = replace_once(text, '<title>SOOVEŔ — HCI Dark Patterns Lab</title>',
                        f'<title>SOOVEŔ — Prototype {number} ({"Control" if group == "A" else "Dark Patterns"})</title>')
    text = replace_once(text, "var view = 'A';        // 'A' | 'B' | 'side' | 'telemetry'",
                        f"var view = '{group}';        // Fixed prototype; telemetry remains available.")
    # Retain only this prototype's product renderer.
    unwanted = 'productB' if group == 'A' else 'productA'
    text, count = re.subn(r'    function ' + unwanted + r'\(s\)\{[\s\S]*?\n    \}\n', '', text)
    if count != 1:
        raise ValueError(f'Could not isolate {unwanted}')
    text = replace_once(text, "case 1: return s.prototype === 'A' ? productA(s) : productB(s);",
                        f'case 1: return product{group}(s);')
    start = text.index('    function stageHTML(){')
    end = text.index('    function researcherLayout(){', start)
    text = text[:start] + f'''    function stageHTML(){{
      if(view === 'telemetry') return telemetryHTML();
      var s = ensureSession('{group}');
      return '<div class="single-wrap"><div class="side-col">' + website(s) + caption(s) + '</div></div>';
    }}

''' + text[end:]
    start = text.index("        + '<button class=\"tab '")
    end = text.index("        + '<button class=\"tab ' + (view==='telemetry'", start)
    text = text[:start] + f'''        + '<button class="tab ' + (view==='{group}'?'active':'') + '" data-view="{group}">Prototype {number} ({"Control" if group == "A" else "Dark Patterns"})</button>'
''' + text[end:]
    text = replace_once(text, "var s = ensureSession(view === 'B' ? 'B' : 'A');",
                        f"var s = ensureSession('{group}');")
    text = replace_once(text, "if(blind && view !== 'A' && view !== 'B') view = 'A';",
                        f"if(blind) view = '{group}';")
    text = replace_once(text, "var groupParam = (params.get('group') || 'A').toUpperCase();\n      view = (groupParam === 'A' || groupParam === 'B') ? groupParam : 'A';",
                        f"// This file always runs prototype {number}; group query overrides are ignored.\n      view = '{group}';")
    # Correct an existing mismatch between the completion log and its average parser.
    text = replace_once(text, r'/Final=৳(\d+)/', r'/Final\s*=\s*৳(\d+)/')
    text = replace_once(text, "a.download = 'atelier-noir-telemetry.csv';",
                        f"a.download = 'prototype-{number}-telemetry.csv';")
    # Bundle the original product images to avoid a runtime hosting dependency.
    for name, remote_id in [('hero', '042f2a76-1d0e-4ff9-bc2f-eb5ae7dc8c0d'),
                            ('alt1', 'eb2cc76b-4481-4981-83c2-329655ce78c9'),
                            ('alt2', 'a2926828-7ef3-41c9-aab5-d8fc0fad893c')]:
        import base64
        image = ROOT / 'source_assets' / f'{name}.png'
        if not image.is_file():
            raise FileNotFoundError(f'Missing original image: {image}')
        data = base64.b64encode(image.read_bytes()).decode('ascii')
        text = replace_once(text, f'https://www.designarena.ai/u/{remote_id}',
                            'data:image/png;base64,' + data)
    # System font fallbacks are already defined in the original stylesheet.
    text = re.sub(r'  <link[^>]+(?:fonts.googleapis.com|fonts.gstatic.com)[^>]*>\n', '', text)
    return text


def main():
    source = (ROOT / 'deployment.html').read_text(encoding='utf-8')
    for number, group in [(1, 'A')]:
        output = ROOT / 'index.html'
        output.write_text(extract(source, group, number), encoding='utf-8')
        print(f'Created {output.name}: {output.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
