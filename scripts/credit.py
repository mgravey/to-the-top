"""Credit and licence line added to the bottom of every figure.

with_credit(svg) makes the drawing CREDIT_HEIGHT taller (viewBox and background) and writes
the credit below everything else, so existing layouts are untouched. Idempotent.
"""
import re

CREDIT = '© 2026 Mathieu Gravey · mgravey.com/to-the-top · CC BY-SA 4.0'
LICENSE_URL = 'https://creativecommons.org/licenses/by-sa/4.0/'
CREDIT_HEIGHT = 20


def with_credit(svg):
    if 'data-credit' in svg:
        return svg
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    width, height = m.group(1), m.group(2)
    new_height = f'{float(height) + CREDIT_HEIGHT:g}'
    svg = svg.replace(m.group(0), f'viewBox="0 0 {width} {new_height}"', 1)
    svg = svg.replace(f'<rect class="bg" width="{width}" height="{height}"/>',
                      f'<rect class="bg" width="{width}" height="{new_height}"/>', 1)
    line = (f'<text data-credit="" class="m" x="16" y="{float(height) + 12:g}" font-size="11">'
            f'{CREDIT}<title>Licence: {LICENSE_URL}</title></text>')
    end = svg.rindex('</svg>')
    return svg[:end] + line + '\n' + svg[end:]
