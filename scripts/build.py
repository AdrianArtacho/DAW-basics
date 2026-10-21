#!/usr/bin/env python3
"""Build the self-contained teaching site from the reviewed JSON content (stdlib only)."""
from pathlib import Path
from html import escape
import json
import math
import hashlib

ROOT = Path(__file__).resolve().parents[1]
DAW_IDS = ["ableton", "logic", "cubase", "flstudio", "protools"]
SHORT = {"ableton": "Ableton Live", "logic": "Logic Pro", "cubase": "Cubase", "flstudio": "FL Studio", "protools": "Pro Tools"}
e = lambda value: escape(str(value), quote=True)


def link(url, text, cls=""):
    return f'<a href="{e(url)}" class="{e(cls)}" target="_blank" rel="noopener noreferrer">{e(text)}</a>'


def wave(x, y, width, height, color="#8873d4", reverse=False, fade=False):
    lines = []
    for i in range(int(width // 3)):
        t = i / max(1, width / 3 - 1)
        envelope = .18 + .8 * math.exp(-3 * (1 - t if reverse else t))
        if fade:
            envelope *= min(1, t * 5, (1 - t) * 5)
        amp = height * envelope * (.25 + .75 * abs(math.sin(i * 2.3) * math.cos(i * .71))) / 2
        lines.append(f'<path d="M{x+i*3:.1f} {y-amp:.1f}v{amp*2:.1f}" stroke="{color}" stroke-width="1.6"/>')
    return ''.join(lines)


def diagram(kind, title):
    text = lambda x,y,t,col="#7b8075": f'<text x="{x}" y="{y}" fill="{col}" font-size="10" font-family="sans-serif">{e(t)}</text>'
    box = lambda x,y,w,c="#ece8fa": f'<rect x="{x}" y="{y}" width="{w}" height="32" rx="4" fill="{c}"/>'
    out = text(12,16,"AUSGANGSMATERIAL") + box(12,26,145) + wave(17,42,135,25)
    out += '<path d="M181 34v14m-4-4 4 4 4-4" stroke="#a5aa9f" fill="none"/>'
    label = "EINE MÖGLICHE VERWANDLUNG"
    if kind == "form":
        out = text(12,16,"FORMENTWURF · 0:00 BIS 3:00")
        widths = [48,72,72,64,32]
        names = ["Anfang", "Wandel", "Kontrast", "Dichte", "Ende"]
        x = 12
        for i,(w,n) in enumerate(zip(widths,names)):
            out += box(x,35,w-3,["#e5e1f4","#cbbfea","#a28dce","#7a61af","#ded8eb"][i]) + text(x+3,84,n)
            x += w
        out += text(12,112,"0:00") + text(122,112,"1:15") + text(270,112,"3:00")
    elif kind in {"chain", "sends", "render", "export"}:
        out = text(12,16,{"chain":"DIE REIHENFOLGE MACHT EINEN UNTERSCHIED","sends":"ZWEI WEGE · EIN GEMEINSAMER AUSGANG","render":"BEARBEITUNG WIRD NEUES MATERIAL","export":"DAS PROJEKT WIRD EINE AUDIODATEI"}[kind])
        labels = {"chain":["Klang","Filter","Verzerrung"],"sends":["Spur","Send → Hall","Summe"],"render":["Klang + FX","Render","Neuer Clip"],"export":["Arrangement","Master","Stereo-WAV"]}[kind]
        for i,t in enumerate(labels):
            out += box(12+i*99,45,88) + text(20+i*99,65,t,"#65558e")
            if i<2: out += '<path d="M'+str(103+i*99)+' 61h6m-3-3 3 3-3 3" stroke="#8a8e82" fill="none"/>'
        if kind=="sends": out += '<path d="M55 44v-13h198v13" stroke="#9ca48f" fill="none"/>' + text(120,27,"Dry")
        if kind=="chain": out += text(12,106,"Vergleiche auch: Klang → Verzerrung → Filter")
        if kind=="render": out += text(12,106,"Danach: schneiden, drehen, dehnen …")
        if kind=="export": out += text(12,106,"Anfang, Summe und Ausklang kontrollieren")
    else:
        out += text(12,78,label)
        if kind in {"cut","repeat","layers"}:
            if kind=="cut": chunks=[(12,56),(83,88),(187,54)]
            elif kind=="repeat": chunks=[(12+i*48,34) for i in range(6)]
            else: chunks=[(12,141),(105,141)]
            for i,(x,w) in enumerate(chunks):
                y=87+(i*12 if kind=="layers" else 0)
                out += box(x,y,w,"#ece8fa" if i%2==0 else "#e0ebd7") + wave(x+4,y+16,w-8,24,"#8977b1" if i%2==0 else "#7c9665")
        elif kind in {"stretch","speed"}:
            out += box(12,87,286) + wave(17,103,276,25)
            out += text(174,54,"länger + tiefer" if kind=="speed" else "länger · gleiche Tonhöhe","#65558e")
        elif kind=="warp":
            out += box(12,87,210) + wave(17,103,200,25)
            out += '<path d="M15 85v36M145 85v36M220 85v36" stroke="#5e4799" stroke-width="2"/>'
            out += '<path d="M71 73h68m-4-4 4 4-4 4" fill="none" stroke="#5e4799"/>'
        elif kind=="automation":
            out += box(12,87,286) + wave(17,103,276,22,"#c8c1d4")
            out += '<path d="M17 115 80 110 135 92 210 93 290 114" fill="none" stroke="#7555b6" stroke-width="2"/>'
            for x,y in [(17,115),(80,110),(135,92),(210,93),(290,114)]:
                out+=f'<circle cx="{x}" cy="{y}" r="3" fill="#7555b6"/>'
        elif kind=="echo":
            for i in range(4): out += box(12+i*73,87,63) + wave(16+i*73,103,55,28*(.65**i))
        elif kind=="filter":
            out += box(12,87,286) + '<path d="M22 98h115q25 0 40 17h110" fill="none" stroke="#8873d4" stroke-width="3"/>'
            out+=text(205,54,"Tiefpass","#65558e")
        else:
            h=13 if kind=="gain" else 24
            out += box(12,87,145) + wave(17,103,135,h,reverse=kind=="reverse",fade=kind=="fade")
            if kind=="pitch": out += text(177,108,"+7 Halbtöne","#65558e")
            elif kind=="dynamics": out += text(177,108,"Hüllkurve formen","#65558e")
            elif kind=="source": out += text(177,108,"Kopie behalten","#65558e")
            elif kind=="gain": out += text(177,108,"Pegel verändern","#65558e")
            elif kind=="fade": out += '<path d="M16 117 48 89h74l32 28" fill="none" stroke="#7655b8" stroke-width="1.6"/>'
            elif kind=="reverse": out += text(177,108,"Ende → Anfang","#65558e")
    return f'<figure class="schematic"><svg viewBox="0 0 310 132" role="img" aria-label="{e(title)}: schematische Darstellung">{out}</svg><figcaption>Prinzipdarstellung · keine DAW-Oberfläche</figcaption></figure>'


def hero_visual():
    out = '<svg class="visual" viewBox="0 0 470 230" role="img" aria-label="Aus einem dreisekündigen Klang entstehen kurze Impulse, Schichten und eine gedehnte Fläche.">'
    out += '<g stroke="#3d4142" stroke-width="1">'+''.join(f'<path d="M{x} 14v195"/>' for x in range(20,470,45))+'</g>'
    out += '<text x="6" y="12" fill="#9ca49f" font-size="10" font-family="monospace">QUELLE / 3 SEKUNDEN</text>'
    out += '<rect x="7" y="27" width="171" height="48" rx="5" fill="#453e60"/>'+wave(14,51,157,39,"#bea6fa")
    out += '<path d="M194 51h52m-7-7 7 7-7 7" stroke="#8e948e" fill="none"/>'
    out += '<text x="265" y="47" fill="#d7dad6" font-size="11" font-family="monospace">SCHNEIDEN</text><text x="265" y="64" fill="#9ca49f" font-size="11" font-family="monospace">VERWANDELN</text>'
    for i,(x,w) in enumerate([(7,45),(73,32),(125,51),(206,34),(271,43),(336,40),(401,53)]):
        out+=f'<rect x="{x}" y="105" width="{w}" height="31" rx="4" fill="#394c42"/>'+wave(x+4,120,w-8,24,"#a6c3a2")
    out+='<rect x="74" y="146" width="303" height="39" rx="4" fill="#453e60"/>'+wave(82,165,286,33,"#b099df",reverse=True)
    out+='<rect x="337" y="188" width="118" height="25" rx="4" fill="#59513b"/>'+wave(343,200,105,20,"#cfb97c")
    out+='<text x="7" y="229" fill="#9ca49f" font-size="10" font-family="monospace">KOMPOSITION / 3 MINUTEN</text></svg>'
    return out


def daw_panel(daw, op):
    item=daw['operations'][op['id']]
    sources={s['id']:s for s in daw['sources']}
    image_data={im['id']:im for im in daw.get('images',[])}
    imgs=[]
    if item.get('image') in image_data: imgs=[image_data[item['image']]]
    elif not item.get('image'): imgs=[im for im in daw.get('images',[]) if op['id'] in im.get('operations',[])][:1]
    figures=''
    for im in imgs:
        src=im.get('local',im['src'])
        figures+=f'''<details class="manual-image"><summary>Abbildung aus dem Handbuch: {e(im['title'])}</summary><figure><a href="{e(src)}" target="_blank" rel="noopener" class="image-open"><img src="{e(src)}" alt="{e(im['alt'])}" loading="lazy" decoding="async" referrerpolicy="no-referrer"></a><figcaption>{e(im['credit'])} {link(im['sourceUrl'],'Original und Erklärung ↗')} · Abbildungsstand kann von deiner Version abweichen.</figcaption></figure></details>'''
    source_html=''.join(link(sources[s]['url'], sources[s]['title']+' ↗') for s in item['sources'])
    intro='<p class="daw-intro">'+e(daw['intro'])+'</p>' if op['id']=='setup' else ''
    return f'''<section class="daw-panel" data-daw="{e(daw['id'])}" id="{op['id']}-{daw['id']}-panel" role="tabpanel" tabindex="0" aria-labelledby="{op['id']}-{daw['id']}-tab" {'hidden' if daw['id']!='ableton' else ''}>
      <div class="panel-daw eyebrow">{e(daw['name'])}</div><div class="panel-meta"><h4>{e(item['term'])}</h4><small>{e(daw['version'])}</small></div>
      {intro}<ol>{''.join('<li>'+e(t)+'</li>' for t in item['steps'])}</ol>
      <aside class="tip"><b>Darauf achten</b>{e(item['tip'])}</aside>{figures}
      <div class="source-links"><span class="eyebrow">Offizielles Handbuch</span>{source_html}</div>
    </section>'''


def operation_html(op, i, ops, daws):
    tabs=''.join(f'<button class="daw-tab" id="{op["id"]}-{d["id"]}-tab" role="tab" data-daw="{d["id"]}" aria-selected="{str(d["id"]=="ableton").lower()}" aria-controls="{op["id"]}-{d["id"]}-panel" tabindex="{0 if d["id"]=="ableton" else -1}">{e(SHORT[d["id"]])}</button>' for d in daws)
    previous=f'<a class="prev" href="#{ops[i-1]["id"]}"><b>← Vorheriger Schritt</b>{e(ops[i-1]["short"])}</a>' if i else '<a class="prev" href="#unterricht"><b>Zur Orientierung</b>Unterrichtsplan</a>'
    next_=f'<a class="next" href="#{ops[i+1]["id"]}"><b>Nächster Schritt →</b>{e(ops[i+1]["short"])}</a>' if i+1<len(ops) else '<a class="next" href="#unterricht"><b>Zum Abschluss</b>Gemeinsam hören →</a>'
    return f'''<article class="operation" id="{op['id']}" data-operation="{op['id']}" {'hidden' if i else ''} aria-labelledby="title-{op['id']}">
      <div class="operation-head"><span class="eyebrow">Schritt {i+1:02d} / {len(ops):02d}</span><div class="step-meta"><span class="badge">{e(op['level'])}</span><span>ca. {op['minutes']} Min.</span></div></div>
      <h2 id="title-{op['id']}" tabindex="-1">{e(op['title'])}</h2><p class="summary">{e(op['summary'])}</p>
      <div class="concept-row"><div><h3>Was wir verändern</h3><p>{e(op['concept'])}</p></div>{diagram(op['diagram'],op['title'])}</div>
      <section class="task"><h3>Dein Versuch</h3><ol>{''.join('<li>'+e(t)+'</li>' for t in op['task'])}</ol><p class="listen"><b>Hörfrage</b>{e(op['listen'])}</p></section>
      <section class="instruction-section"><div class="instruction-heading"><h3>So geht’s in deiner DAW</h3><label class="compare-label"><input type="checkbox" class="compare-toggle"> Alle DAWs vergleichen</label></div>
      <div class="daw-tabs" role="tablist" aria-label="DAW für {e(op['title'])}">{tabs}</div>{''.join(daw_panel(d,op) for d in daws)}</section>
      <div class="checkpoint"><input type="checkbox" id="done-{op['id']}" data-complete="{op['id']}"><label for="done-{op['id']}"><strong>Bereit für den nächsten Schritt?</strong>{e(op['checkpoint'])}</label></div>
      <details class="bonus"><summary>Wenn du schon weiter bist</summary><p>{e(op['bonus'])}</p></details>
      <nav class="step-footer" aria-label="Schrittnavigation">{previous}<button class="share" data-share="{op['id']}">Schritt-Link kopieren ↗</button>{next_}</nav>
    </article>'''


def lesson():
    return '''<section class="page-view" id="unterricht" hidden><span class="eyebrow">Gemeinsam arbeiten · individuell vertiefen</span><h2>Ein Klang wird ein Stück.</h2>
    <p class="summary">Die Klasse arbeitet an derselben Operation. Jede Person setzt sie in ihrer eigenen DAW um — und entscheidet nach Gehör, was daraus wird.</p>
    <div class="callout"><h3>Die Aufgabe</h3><p>Komponiere aus einer ungefähr drei Sekunden langen Aufnahme ein etwa dreiminütiges Stück. Verwende Ausschnitte, Wiederholungen und Bearbeitungen dieses Materials. Wähle bewusst, welche Verwandlungen du brauchst. Neue Klangquellen sind für diese Übung nicht nötig.</p><p><b>Abgabe:</b> Stereo-WAV und ein gesichertes Projekt mit Audiodateien. Bei einer exakten Dauer von 3:00 muss der letzte Hall bereits innerhalb dieser Zeit ausklingen.</p></div>
    <h3>Ein möglicher Ablauf für 90 Minuten</h3>
    <div class="table-wrap"><table><thead><tr><th>Zeit</th><th>Gemeinsamer Fokus</th><th>Schritte</th></tr></thead><tbody>
    <tr><td>0–10 Min.</td><td>Quelle hören, Projekt einrichten, Eigenschaften sammeln.</td><td><a href="#setup">01 · Projekt & Material</a></td></tr>
    <tr><td>10–30 Min.</td><td>Fragmente, Schichten, saubere Ränder und Pegel.</td><td><a href="#cut">02–05 · Grundoperationen</a></td></tr>
    <tr><td>30–45 Min.</td><td>Reverse und je eine Tonhöhen- und Zeitvariante. Repitch kurz gemeinsam mit Stretching vergleichen.</td><td><a href="#reverse">07–10 · Verwandeln</a></td></tr>
    <tr><td>45–55 Min.</td><td>Einen Raum und einen Parameterverlauf gestalten.</td><td><a href="#space">14 · Raum</a> / <a href="#automation">17 · Automation</a></td></tr>
    <tr><td>55–80 Min.</td><td>Eigenständige Kompositionszeit. Selektiv wiederholen, rendern und neu schneiden.</td><td><a href="#structure">19 · Form</a> / <a href="#resample">18 · Resampling</a></td></tr>
    <tr><td>80–90 Min.</td><td>Exportkontrolle und kurze Hörbeispiele; vollständige gemeinsame Präsentation gegebenenfalls in der Folgestunde.</td><td><a href="#export">20 · Export</a></td></tr>
    </tbody></table></div>
    <p>Die Minuten pro Einzelschritt sind Arbeitsimpulse, keine feste Stundenlänge. In 60 Minuten: nur Grundoperationen, eine Verwandlung, Form und Export wählen. Für 120 Minuten oder eine zweite Einheit: Warp, Filter, Dynamik, Effektketten und Sends vertiefen. Die gesamte Sammlung muss nicht in einer Stunde abgearbeitet werden.</p>
    <div class="course-steps"><section class="course-card"><span class="eyebrow">01 / Gemeinsam</span><h3>Hören & benennen</h3><p>Eine kurze Demonstration erklärt die Veränderung. Die Hörfrage ist für alle dieselbe.</p></section><section class="course-card"><span class="eyebrow">02 / Individuell</span><h3>Selbst ausprobieren</h3><p>DAW wählen, Schritte ausführen, Variante sichern. Schnellere Lernende nutzen die Vertiefungsaufgabe.</p></section><section class="course-card"><span class="eyebrow">03 / Gemeinsam</span><h3>Vergleichen & wählen</h3><p>Zwei Ergebnisse anhören. Was hat sich verändert? Welche Variante soll im Stück eine Rolle spielen?</p></section></div>
    <h3>Drei Verfahren — drei verschiedene Fragen</h3><div class="table-wrap"><table><thead><tr><th>Verfahren</th><th>Tonhöhe</th><th>Dauer</th><th>Vergleichsversuch</th></tr></thead><tbody><tr><td><a href="#pitch">Pitch-Shift</a></td><td>ändert sich</td><td>bleibt etwa gleich</td><td>−12 Halbtöne; weiterhin 3 Sekunden</td></tr><tr><td><a href="#speed">Repitch / Varispeed</a></td><td>ändert sich gekoppelt</td><td>ändert sich gekoppelt</td><td>½ Geschwindigkeit: 6 Sekunden, −12 Halbtöne</td></tr><tr><td><a href="#stretch">Time-Stretch</a></td><td>bleibt etwa gleich</td><td>ändert sich</td><td>4-fache Dauer: 12 Sekunden</td></tr></tbody></table></div>
    <div class="callout"><h3>Zum gemeinsamen Hören</h3><ul><li>Welche Eigenschaft des Ausgangsklangs bleibt erkennbar?</li><li>Wo gibt es einen klaren Kontrast — und wie wird er vorbereitet?</li><li>Was trägt Wiederholung zur Form bei?</li><li>Welche Pause oder Reduktion macht das Stück stärker?</li><li>Ist der Schluss eine Entscheidung oder nur das Ende der Datei?</li></ul></div><a class="button-primary" href="#setup">Mit Schritt 01 beginnen <span>→</span></a></section>'''


def build():
    course=json.loads((ROOT/'data/operations.json').read_text())
    ops=course['operations']
    daws=[json.loads((ROOT/f'data/{did}.json').read_text()) for did in DAW_IDS]
    ids={op['id'] for op in ops}
    assert len(ids)==20
    for daw in daws:
        assert set(daw['operations'])==ids, f"Missing/extra operations: {daw['id']}"
        sources={s['id'] for s in daw['sources']}
        for op in daw['operations'].values():
            assert op['steps'] and op['term'] and op['sources']
            assert set(op['sources'])<=sources
        for im in daw.get('images',[]):
            if im.get('local'): assert (ROOT/im['local']).is_file(),im['local']
    nav=''
    for phase in course['phases']:
        nav+=f'<div class="nav-group"><h3>{e(phase["name"])}</h3>'
        for i,op in enumerate(ops):
            if op['phase']!=phase['id']:continue
            keywords=' '.join([op['title'],op['short'],op['concept']]+[d['operations'][op['id']]['term'] for d in daws])
            nav+=f'<a class="operation-link" href="#{op["id"]}" data-search="{e(keywords)}"><span class="number">{i+1:02d}</span><span>{e(op["short"])}</span>{"<span class=\"level-dot\" title=\"Vertiefung\"></span>" if op["level"]=="Vertiefung" else ""}</a>'
        nav+='</div>'
    buttons=''.join(f'<button class="daw-button" data-daw="{d["id"]}" aria-pressed="{str(d["id"]=="ableton").lower()}">{e(SHORT[d["id"]])}</button>' for d in daws)
    glossary='<section class="page-view" id="woerterbuch" hidden><span class="eyebrow">Die gleiche Operation, andere Namen</span><h2>Das DAW-Wörterbuch.</h2><p>Jede Zelle öffnet die passende Anleitung. Die englischen Bezeichnungen entsprechen den dokumentierten Oberflächen; deutsche Menüs können anders heißen. Ein ähnlicher Name garantiert nicht dieselbe Funktion.</p><div class="table-wrap"><table class="glossary"><thead><tr><th>Operation</th>'+''.join('<th>'+e(d['name'])+'</th>' for d in daws)+'</tr></thead><tbody>'
    for i,op in enumerate(ops):
        glossary+=f'<tr><td>{i+1:02d} · {e(op["short"])}</td>'+''.join(f'<td><a href="?daw={d["id"]}#{op["id"]}">{e(d["operations"][op["id"]]["term"])}</a></td>' for d in daws)+'</tr>'
    glossary+='</tbody></table></div><h3>Grundbegriffe</h3><div class="table-wrap"><table><thead><tr><th>Gemeint ist …</th>'+''.join('<th>'+e(d['name'])+'</th>' for d in daws)+'</tr></thead><tbody>'
    for key,title in [('region','Audiobaustein'),('timeline','Zeitleiste'),('mixer','Mischpult'),('stretch','Zeitbearbeitung'),('render','Audio berechnen')]:
        glossary+='<tr><td>'+title+'</td>'+''.join('<td>'+e(d['terms'][key])+'</td>' for d in daws)+'</tr>'
    glossary+='</tbody></table></div></section>'
    sources='<section class="page-view" id="quellen" hidden><span class="eyebrow">Nachlesen & weiterlernen · Stand 21.10.2026</span><h2>Handbücher & Bildquellen.</h2><p>Die Anleitungen wurden anhand der offiziellen Dokumentation recherchiert. Version, Edition, Sprache und eigene Tastaturbelegungen können einzelne Wege verändern. Die Menü- und Werkzeugnamen helfen deshalb auch dann, wenn ein Shortcut anders belegt ist.</p><p>Die Schritte wurden nicht in allen fünf Desktop-Programmen praktisch getestet. Wähle bei Abweichungen die verlinkte Anleitung für deine installierte Version. Die eigenen Grafiken erklären das Prinzip; aufklappbare Herstellerabbildungen zeigen echte Oberflächen.</p>'
    for daw in daws:
        sources+=f'<section class="source-daw"><span class="eyebrow">{e(daw["platform"])}</span><h3>{e(daw["name"])}</h3><p class="source-intro">{e(daw["version"])}<br>{e(daw["intro"])}</p><ul>'
        for s in daw['sources']:
            sources+=f'<li>{link(s["url"],s["title"]+" ↗")}<small>Abruf: {e(s.get("accessed","2026-10-21"))}</small></li>'
        sources+='</ul>'
        if daw.get('images'):
            sources+='<h4>Abbildungen</h4><ul>'
            for im in daw['images']:
                sources+=f'<li>{link(im["sourceUrl"],im["title"])}<small>{e(im["credit"])}</small></li>'
            sources+='</ul>'
        sources+='</section>'
    sources+='<div class="callout copyright"><h3>Credits</h3><p>Konzept und Lehre: Adrián Artacho · MUK / Elektronische Musik. Die Herstellerabbildungen stammen aus den jeweils verlinkten Handbüchern; die Rechte bleiben bei Ableton, Apple, Steinberg, Image-Line bzw. Avid. Sie dienen hier der Erläuterung der jeweiligen Bedienung. Marken und Produktnamen gehören ihren jeweiligen Inhabern.</p><p>Das dreisekündige Beispiel wurde eigens synthetisiert. Du darfst es für diese Übung und eigene Musik frei verwenden. Alle Prinzipdarstellungen sind eigens für diese Anleitung erstellt.</p></div></section>'
    mobile='<option value="">Schritt wählen …</option>'+''.join(f'<option value="{op["id"]}">{i+1:02d} · {e(op["short"])}</option>' for i,op in enumerate(ops))+'<option value="unterricht">Unterrichtsplan</option><option value="woerterbuch">DAW-Wörterbuch</option><option value="quellen">Quellen & Versionen</option>'
    style_revision=hashlib.sha256((ROOT/'assets/style.css').read_bytes()).hexdigest()[:12]
    app_revision=hashlib.sha256((ROOT/'assets/app.js').read_bytes()).hexdigest()[:12]
    html=f'''<!doctype html>
<html lang="de" class="no-js"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DAW Basics — 3 Sekunden → 3 Minuten · MUK</title><meta name="description" content="Eine gemeinsame Kompositionsübung für Ableton Live, Logic Pro, Cubase, FL Studio und Pro Tools. 20 Operationen, konkrete Anleitungen und offizielle Bildquellen. MUK / Elektronische Musik · Adrián Artacho."><meta name="theme-color" content="#f6f5f1"><meta property="og:title" content="3 Sekunden → 3 Minuten · DAW Basics"><meta property="og:description" content="Ein Klang. Fünf DAWs. Schritt für Schritt zum eigenen Stück."><meta property="og:type" content="website"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css?v={style_revision}"><script src="assets/app.js?v={app_revision}" defer></script></head>
<body><a class="skip" href="#workspace">Zur Anleitung springen</a><noscript><p class="nojs">JavaScript ist deaktiviert. Alle Operationen und DAW-Anleitungen werden untereinander angezeigt.</p></noscript>
<header class="topbar"><div class="wrap"><a class="identity" href="#" aria-label="DAW Basics — Start"><span class="muk">MUK</span><span class="course"><strong>Elektronische Musik</strong>DAW Basics · Adrián Artacho</span></a><nav class="topnav" aria-label="Weitere Inhalte"><a class="desktop-link" href="#unterricht">Unterrichtsplan</a><a class="desktop-link" href="#woerterbuch">Wörterbuch</a><a class="desktop-link" href="#quellen">Quellen</a><button id="print-guide" type="button">Anleitung drucken ↗</button></nav></div></header>
<main class="wrap"><section class="hero" aria-labelledby="site-title"><div><span class="eyebrow">Eine Kompositionswerkstatt für fünf DAWs</span><h1 id="site-title">3 Sekunden.<br><span>3 Minuten.</span></h1><p class="lead">Ein kurzer Klang ist der Anfang. Schneide, schichte und verwandle ihn — bis daraus dein eigenes Stück wird.</p><a class="button-primary" href="#setup">Mit Schritt 01 beginnen <span>→</span></a><div class="hero-meta"><span>20 OPERATIONEN</span><span>5 DAWs</span><span>DEIN TEMPO</span></div></div><div class="sound-card"><span class="eyebrow">Vom Material zur Form</span>{hero_visual()}<div class="audio-title"><span>Dein Ausgangsmaterial</span><span>00:03</span></div><audio controls preload="metadata" aria-label="Dreisekündiges Ausgangsmaterial anhören"><source src="assets/audio/3-sekunden.wav" type="audio/wav">Dein Browser unterstützt keine Audiowiedergabe.</audio><a href="assets/audio/3-sekunden.wav" download>Beispielklang herunterladen · WAV ↙</a><p class="sample-note">Oder nimm deinen eigenen Klang. Das Beispiel enthält einen Impuls, Tonanteile und Geräusch — genug Material für viele Richtungen.</p></div></section>
<section class="chooser" aria-label="DAW auswählen"><span class="chooser-label">Wähle deine DAW</span><div class="daw-buttons" role="group" aria-label="DAW für alle Schritte">{buttons}</div><span class="note">Deine Auswahl bleibt über alle Schritte erhalten.</span></section>
<div class="workspace" id="workspace"><aside class="sidebar"><div class="sidebar-heading"><span class="eyebrow">Dein Weg durch die Übung</span><span id="progress-label">0 / 20</span></div><input class="search" id="operation-search" type="search" placeholder="Operation oder DAW-Begriff …" aria-label="Operationen durchsuchen"><nav aria-label="Operationen">{nav}</nav><p class="search-empty" id="search-empty" hidden>Keine passende Operation. Versuche „Pitch“, „Fade“ oder „Render“.</p><div class="nav-extras"><a href="#unterricht">↗ Unterrichtsplan</a><a href="#woerterbuch">↗ DAW-Wörterbuch</a><a href="#quellen">↗ Quellen & Versionen</a></div><div class="progress-line" role="progressbar" aria-label="Abgeschlossene Schritte" aria-valuemin="0" aria-valuemax="20" aria-valuenow="0"><span id="progress-fill" style="width:0%"></span></div><button class="reset-progress" id="reset-progress">Häkchen zurücksetzen</button></aside>
<div class="content"><div class="mobile-select"><label for="step-select">DEIN NÄCHSTER SCHRITT</label><select id="step-select">{mobile}</select></div><p class="print-daw" hidden></p>{''.join(operation_html(op,i,ops,daws) for i,op in enumerate(ops))}{lesson()}{glossary}{sources}</div></div></main>
<footer class="footer"><div class="wrap"><p>{link('https://muk.ac.at/','MUK — Musik und Kunst Privatuniversität der Stadt Wien')}<br>Elektronische Musik · {link('https://muk.ac.at/studienangebot/lehrende/details/adrian-artacho.html','Adrián Artacho')}</p><p>Dokumentationsstand: 21.10.2026 · Fortschritt nur in diesem Browser gespeichert.<br><a href="#quellen">Quellen & Bildnachweise</a> · {link('https://github.com/AdrianArtacho/DAW-basics','Quellcode auf GitHub ↗')}</p></div></footer><div class="status" role="status" aria-live="polite" hidden></div></body></html>'''
    (ROOT/'index.html').write_text(html,encoding='utf-8')
    print(f"Built index.html: {len(ops)} operations × {len(daws)} DAWs; {sum(len(d['sources']) for d in daws)} source entries")


if __name__=='__main__': build()
