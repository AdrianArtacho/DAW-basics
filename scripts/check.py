#!/usr/bin/env python3
"""Validate the actual static deliverable: references, links, images and sample."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import wave

ROOT = Path(__file__).resolve().parents[1]
class Audit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.links=[]; self.images=[]; self.panels=[]; self.operations=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag in ('a','link') and a.get('href'): self.links.append(a['href'])
        if tag in ('script','img','source') and a.get('src'): self.links.append(a['src'])
        if tag=='img': self.images.append(a)
        if 'data-operation' in a: self.operations.append(a['data-operation'])
        if tag=='section' and 'daw-panel' in a.get('class',''): self.panels.append(a['id'])

html=(ROOT/'index.html').read_text()
audit=Audit();audit.feed(html)
assert len(audit.ids)==len(set(audit.ids)), 'Duplicate HTML IDs'
assert len(audit.operations)==20, 'Expected twenty operation pages'
assert len(audit.panels)==100, 'Expected one hundred DAW instructions'
ids=set(audit.ids)
for url in audit.links:
    parts=urlsplit(url)
    if parts.scheme:
        assert parts.scheme=='https', f'Insecure or unexpected external URL: {url}'
        continue
    if parts.netloc: raise AssertionError(f'Unexpected remote URL: {url}')
    if parts.path: assert (ROOT/unquote(parts.path)).is_file(), f'Missing local file: {url}'
    elif parts.fragment: assert unquote(parts.fragment) in ids, f'Broken anchor: {url}'
for image in audit.images:
    assert image.get('alt'), f'Missing image description: {image}'
    assert not urlsplit(image['src']).scheme, f'Image must be stored locally: {image["src"]}'
for daw_id in ['ableton','logic','cubase','flstudio','protools']:
    d=json.loads((ROOT/f'data/{daw_id}.json').read_text())
    source_ids=[s['id'] for s in d['sources']]
    assert len(source_ids)==len(set(source_ids)), f'Duplicate source id in {daw_id}'
    assert set(d['operations'])==set(audit.operations)
    for op,guide in d['operations'].items():
        assert 2<=len(guide['steps'])<=6, f'Unexpected instruction count: {daw_id}/{op}'
        assert set(guide['sources'])<=set(source_ids), f'Unresolved source: {daw_id}/{op}'
with wave.open(str(ROOT/'assets/audio/3-sekunden.wav')) as sample:
    assert sample.getnframes()/sample.getframerate()==3.0
    assert sample.getnchannels()==1
assert 'MUK' in html and 'Elektronische Musik' in html and 'Adrián Artacho' in html
print(f'Checked {len(audit.operations)} operations, {len(audit.panels)} DAW panels, {len(audit.links)} links/assets, {len(audit.images)} image placements, 3-second audio')
