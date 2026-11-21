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
        self.ids=[]; self.links=[]; self.images=[]; self.panels=[]; self.operations=[]; self.chooser=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag in ('a','link') and a.get('href'): self.links.append(a['href'])
        if tag in ('script','img','source') and a.get('src'): self.links.append(a['src'])
        if tag=='img': self.images.append(a)
        if tag=='button' and 'daw-button' in a.get('class','').split(): self.chooser.append(a['data-daw'])
        if 'data-operation' in a: self.operations.append(a['data-operation'])
        if tag=='section' and 'daw-panel' in a.get('class',''): self.panels.append(a['id'])

html=(ROOT/'index.html').read_text()
audit=Audit();audit.feed(html)
assert len(audit.ids)==len(set(audit.ids)), 'Duplicate HTML IDs'
assert len(audit.operations)==20, 'Expected twenty operation pages'
course=json.loads((ROOT/'data/operations.json').read_text())
daw_ids=course['daws']
assert audit.chooser==daw_ids and len(daw_ids)==len(set(daw_ids)), 'DAW selector/registry mismatch'
assert audit.operations==[op['id'] for op in course['operations']], 'Operation order mismatch'
expected={(op,daw) for op in audit.operations for daw in daw_ids}
assert set(audit.panels)=={f'{op}-{daw}-panel' for op,daw in expected}, 'DAW instruction matrix mismatch'
assert {f'{op}-{daw}-tab' for op,daw in expected}<=set(audit.ids), 'DAW tab missing'
assert {f'?daw={daw}#{op}' for op,daw in expected}<=set(audit.links), 'Glossary link missing'
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
for daw_id in daw_ids:
    d=json.loads((ROOT/f'data/{daw_id}.json').read_text())
    assert d['id']==daw_id, f'DAW filename/ID mismatch: {daw_id}'
    source_ids=[s['id'] for s in d['sources']]
    assert len(source_ids)==len(set(source_ids)), f'Duplicate source id in {daw_id}'
    assert set(d['operations'])==set(audit.operations)
    for op,guide in d['operations'].items():
        assert 2<=len(guide['steps'])<=6, f'Unexpected instruction count: {daw_id}/{op}'
        assert guide['sources'] and set(guide['sources'])<=set(source_ids), f'Unresolved source: {daw_id}/{op}'
with wave.open(str(ROOT/'assets/audio/3-sekunden.wav')) as sample:
    assert sample.getnframes()/sample.getframerate()==3.0
    assert sample.getnchannels()==1
assert 'MUK' in html and 'Elektronische Musik' in html and 'Adrián Artacho' in html
print(f'Checked {len(audit.operations)} operations, {len(audit.panels)} DAW panels, {len(audit.links)} links/assets, {len(audit.images)} image placements, 3-second audio')
