"""Build the standalone two-tab webinar document from the editable transcript."""
import html
import json
import base64
import re
from pathlib import Path

root = Path(__file__).resolve().parent
text = (root / 'Webinar - Full speaker-labeled transcript.txt').read_text(encoding='utf-8')
matches = list(re.finditer(r'^\[(\d{2}):(\d{2}):(\d{2})\] (.+)$', text, re.M))
rows = []
sl = json.loads((root / 'transcript.sl.json').read_text(encoding='utf-8'))
assert set(sl) == {str(i) for i in range(len(matches))}, 'Missing Slovenian passages'
sl_txt = ['Web Insights in pomočnik z umetno inteligenco', 'Celoten prepis z označenimi govorci — slovenski prevod', '',
          'Vir: https://www.youtube.com/watch?v=lCZN1RNqrpo', '',
          'Prevod angleškega prepisa iz samodejnih podnapisov, ne nov prepis zvoka. Za berljivost so mašila in ponovitve zglajeni. Vsi odlomki so vključeni; nejasnosti in uredniška pojasnila so označeni v oglatih oklepajih. Prevod ni v celoti preverjen glede na zvok.', '']
sl_md = ['# Web Insights in pomočnik z umetno inteligenco', '', *sl_txt[1:], '']
for i, m in enumerate(matches):
    seconds = int(m[1])*3600 + int(m[2])*60 + int(m[3])
    body = text[m.end():matches[i+1].start() if i+1 < len(matches) else len(text)].strip()
    name = m[4]
    initial = {'Bernardo Vestia':'BV','Mansi Harsh Sheth':'MS','Swapnil Gupta':'SG'}.get(name,'?')
    sl_name = 'Neznani govorec (negovorni zvok)' if initial=='?' else name
    heading = f'[{m[1]}:{m[2]}:{m[3]}] {sl_name}'
    sl_txt += [heading, sl[str(i)], '']
    sl_md += [f'**{heading}**', '', sl[str(i)], '']
    rows.append(f'<article class="utterance" id="t-{seconds}" data-speaker="{html.escape(name)}" tabindex="-1"><div class="utterance-meta"><span class="avatar {initial}">{initial}</span><strong>{html.escape(name)}</strong><a class="time" href="https://www.youtube.com/watch?v=lCZN1RNqrpo&amp;t={seconds}s" target="_blank" rel="noopener" aria-label="Open video at {m[1]}:{m[2]}:{m[3]}">{m[1]}:{m[2]}:{m[3]} ↗</a></div><p>{html.escape(body)}</p></article>')
template = (root / 'webinar-page.template.html').read_text(encoding='utf-8')
page = template.replace('<!-- TRANSCRIPT -->','\n'.join(rows)).replace('{{COUNT}}',str(len(rows)))
payload = {'transcript': [sl[str(i)] for i in range(len(matches))], 'report': (root/'report.sl.html').read_text(encoding='utf-8')}
page = page.replace('<!-- TRANSLATIONS -->', json.dumps(payload,ensure_ascii=False).replace('<','\\u003c'))
font_css=[]
for weight,label in [(300,'Light'),(400,'Regular'),(700,'Bold')]:
    for subset,unicode_range in [('Latin','U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'),('LatinExt','U+0100-02AF,U+0304,U+0308,U+0329,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF')]:
        encoded=base64.b64encode((root/'assets'/'fonts'/f'Roboto{label}{subset}.woff2').read_bytes()).decode('ascii')
        font_css.append(f'@font-face{{font-family:Roboto;font-style:normal;font-weight:{weight};font-display:swap;src:url(data:font/woff2;base64,{encoded}) format("woff2");unicode-range:{unicode_range}}}')
theme='\n'.join(font_css)+'\n'+(root/'inea-theme.css').read_text(encoding='utf-8')
page=page.replace('<script type="application/json" id="translations">','<style id="inea-theme">'+theme+'</style>\n<script type="application/json" id="translations">')
out = root / 'Webinar - Full speaker-labeled transcript.html'
out.write_text(page,encoding='utf-8')
(root/'Webinar - Full speaker-labeled transcript.sl.txt').write_text('\n'.join(sl_txt),encoding='utf-8')
(root/'Webinar - Full speaker-labeled transcript.sl.md').write_text('\n'.join(sl_md),encoding='utf-8')
print(f'Built {out.name}: {len(rows)} transcript paragraphs, {len(page):,} characters.')
