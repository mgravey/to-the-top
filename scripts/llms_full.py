"""Plain-Markdown version of the whole article for language models (llms.txt convention).

Converts index.html (headings, paragraphs, lists, figure captions and figure descriptions,
the table, method and sources) to Markdown, so the text always matches the page.
Writes llms-full.txt. Standard library only (runs in the Pages workflow).
"""
import html
import re
import os; ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
URL = 'https://mgravey.com/to-the-top/'

page = open(ROOT + 'index.html').read()
main = page[page.index('<main'):page.index('</footer>')]  # article plus the method footer
main = re.sub(r'<script.*?</script>|<style.*?</style>', '', main, flags=re.S)


def inline(fragment):
    """Inline HTML to Markdown: links, bold, italics; drop the remaining tags."""
    def link(m):
        href, text = m.group(1), inline_text(m.group(2))
        if href.startswith('#'):
            return text
        if href.startswith('/'):
            href = 'https://mgravey.com' + href  # site-root links
        elif not href.startswith('http'):
            href = URL + href
        return f'[{text}]({href})'
    fragment = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', link, fragment, flags=re.S)
    fragment = re.sub(r'<(strong|b)>(.*?)</\1>', r'**\2**', fragment, flags=re.S)
    fragment = re.sub(r'<(em|i)>(.*?)</\1>', r'*\2*', fragment, flags=re.S)
    fragment = re.sub(r'<span class="n">\d+</span>', '', fragment)
    return inline_text(fragment)


def inline_text(fragment):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()


out = []
pattern = re.compile(r'<(h1|h2|h3|p|li|figure|details)\b([^>]*)>(.*?)</\1>|<div class="big">()(.*?)</div>\s*</div>', re.S)
pos = 0
while True:
    m = pattern.search(main, pos)
    if not m:
        break
    tag, attrs, body, _, big = m.groups()
    if tag is None:
        tag, attrs, body = 'div', '', big
    pos = m.end()
    if tag == 'h1':
        out.append(f'# {inline(body)}')
    elif tag in ('h2', 'h3'):
        out.append(f'## {inline(body)}')
    elif tag == 'p':
        cls = re.search(r'class="([^"]+)"', attrs)
        text = inline(body)
        if cls and 'kicker' in cls.group(1):
            continue
        out.append(f'*{text}*' if cls and cls.group(1) in ('sub', 'byline') else text)
    elif tag == 'li':
        out.append(f'- {inline(body)}')
    elif tag.startswith('div'):
        out.append('\n'.join(f'- **{inline(b)}** {inline(t)}' for b, t in re.findall(r'<b>(.*?)</b><span>(.*?)</span>', body, re.S)))
    elif tag == 'figure':
        # one entry per chart; switchable figures pair each chart with the caption of the same view
        captions = {v or '': inline(c) for v, c in re.findall(r'<figcaption(?: data-view="([^"]+)")?[^>]*>(.*?)</figcaption>', body, re.S)}
        body = re.sub(r'(<object\b[^>]*>)\s*<img\b[^>]*>', r'\1', body)  # drop <img> fallbacks inside <object>
        charts = re.findall(r'<(?:object|img)\b(?=[^>]*aria-label|[^>]*\balt=)[^>]*?(?:data-view="([^"]+)")?[^>]*?(?:aria-label|alt)="([^"]+)"', body)
        seen = set()
        for view, label in charts:
            if label in seen:
                continue  # the <img> fallback repeats the <object> description
            seen.add(label)
            caption = captions.get(view or '', captions.get('', ''))
            out.append(f'**Figure.** {html.unescape(label)}' + (f' {caption}' if caption else ''))
    elif tag == 'details':
        rows = re.findall(r'<tr>(.*?)</tr>', body, re.S)
        table = [[inline(c) for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', r, re.S)] for r in rows]
        summary = re.search(r'<summary>(.*?)</summary>', body, re.S)
        if summary:
            out.append(f'**{inline(summary.group(1))}**')
        if table:
            out.append('\n'.join(['| ' + ' | '.join(table[0]) + ' |', '|' + '---|' * len(table[0])] +
                                 ['| ' + ' | '.join(r) + ' |' for r in table[1:]]))
        for note in re.findall(r'<p[^>]*>(.*?)</p>', body, re.S):
            out.append(inline(note))

header = (f'Source page: {URL}\nAuthor: Mathieu Gravey (https://mgravey.com/)\n'
          'Code and data: https://github.com/mgravey/to-the-top\n'
          'This file is generated from the page by scripts/llms_full.py.\n')
text = '\n\n'.join([out[0], header] + out[1:]) + '\n'
open(ROOT + 'llms-full.txt', 'w').write(text)
print(f'llms-full.txt: {len(text.split())} words')
