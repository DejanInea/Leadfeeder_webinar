import bisect
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = json.loads((ROOT / 'webinar.en-orig.json3').read_text(encoding='utf-8'))
names = {'B': 'Bernardo Vestia', 'M': 'Mansi Harsh Sheth', 'S': 'Swapnil Gupta', 'U': 'Unidentified speaker (non-speech)'}
# Handoffs reviewed against caption context; names verified on the introduction slide.
turns = [(0,'B'),(284.720,'M'),(810.639,'B'),(812.800,'M'),
 (933.440,'B'),(1024.640,'M'),(1260.799,'S'),(1875.941,'U'),
 (1876.080,'S'),(1919.679,'B'),(1935.2,'S'),(2466.800,'B'),
 (2584.079,'S'),(2706.560,'B'),(2775.359,'S'),(2814.160,'B'),
 (2887.680,'S'),(2920.8,'B'),(2940.079,'M'),(2959.119,'B'),
 (2970.559,'M'),(2992.240,'B'),(3009.040,'S'),(3075.520,'B'),
 (3128.720,'S'),(3255.520,'B'),(3308.720,'S'),(3378.960,'B')]
starts = [t for t,_ in turns]
tokens = []
for e in source['events']:
    for s in e.get('segs', []):
        text = s['utf8'].replace('>>', '').strip()
        if not text:
            continue
        t = (e['tStartMs'] + s.get('tOffsetMs', 0)) / 1000
        speaker = turns[bisect.bisect_right(starts,t)-1][1]
        tokens.append((t,speaker,text))

replacements = [
 (r'\blead feeders\b', "Leadfeeder's"),
 (r'\blead feeder\b', 'Leadfeeder'), (r'\blead fielder\b', 'Leadfeeder'),
 (r'\bLeaf Field\b', 'Leadfeeder'), (r'\belite feeder\b','Leadfeeder'),
 (r'\bweb insights\b','Web Insights'), (r'\bweb visitors\b','Web Visitors'),
 (r'\bswap millil\b','Swapnil'), (r'\bswap mill\b','Swapnil'),
 (r'\bswap nail\b','Swapnil'), (r'\bSwapno\b','Swapnil'),
 (r'\bBernardu\b','Bernardo'), (r'\bBernhard\b','Bernardo'),
 (r'\bMani\b','Mansi'), (r'\bMati\b','Mansi'), (r'\bMarci\b','Mansi'),
 (r'\bchild GPT\b','ChatGPT'),
 (r'\bcharge GPT\b','ChatGPT'), (r'\bcharg cursor\b','ChatGPT, Cursor'),
 (r'\byour cloud\b','your Claude'), (r'\binto cloud\b','into Claude'),
 (r'\bintense score\b','intent score'), (r'\bintense signals\b','intent signals'),
 (r'\bIC CP\b','ICP'), (r'\bSCP\b','ICP'), (r'\bCTM\b','GTM'),
 (r'\bonetoone\b','one-to-one'),
]

def clean(text):
    text = re.sub(r'\s+', ' ', text).strip()
    for pattern,replacement in replacements:
        text = re.sub(pattern,replacement,text,flags=re.I)
    return text

paragraphs = []
pending = []
for token in tokens:
    if pending and (token[1] != pending[0][1] or
        (token[0]-pending[0][0]>=25 and re.search(r'[.!?][\]"\']?$',pending[-1][2])) or
        token[0]-pending[0][0]>=50):
        paragraphs.append((pending[0][0], pending[0][1], clean(' '.join(x[2] for x in pending))))
        pending=[]
    pending.append(token)
if pending:
    paragraphs.append((pending[0][0],pending[0][1],clean(' '.join(x[2] for x in pending))))

def stamp(t):
    n=int(t)
    return f'{n//3600:02d}:{n//60%60:02d}:{n%60:02d}'

title='Webinar - Web Insights and AI Assistant'
note=('Full caption-based transcript of the 59:56 recording. Text is derived from the '
      'YouTube English automatic captions, with paragraph formatting and limited corrections '
      'to names and product terminology. Fillers and repetitions are retained. Speaker names '
      'are verified against the introduction slide; attribution is inferred from introductions, '
      'handoffs and conversational context, not automated voice diarization. This has not '
      'been fully checked against the audio, so caption wording and speaker attribution may '
      'contain errors. The brief throat-clearing at 31:15 cannot be confidently attributed. '
      'All nonempty caption segments are included; captions end at approximately 59:49. '
      'Statements about pricing and availability describe what was said in the recording.')
roster=['Bernardo Vestia — Director of Product Marketing (host)',
        'Mansi Harsh Sheth — VP Product', 'Swapnil Gupta — Senior Product Manager']
url='https://www.youtube.com/watch?v=lCZN1RNqrpo'
md=[f'# {title}', '', 'Full speaker-labeled transcript', '', f'Source: {url}', '',note,'', 'Speakers:', '']
md += ['- '+r for r in roster]
md += ['','---','']
txt=[title,'Full speaker-labeled transcript',f'Source: {url}','',note,'',*roster,'']
for t,s,text in paragraphs:
    md += [f'**[{stamp(t)}] {names[s]}**', '',text,'']
    txt += [f'[{stamp(t)}] {names[s]}',text,'']
stem='Webinar - Full speaker-labeled transcript'
(ROOT/(stem+'.md')).write_text('\n'.join(md),encoding='utf-8')
(ROOT/(stem+'.txt')).write_text('\n'.join(txt),encoding='utf-8')
blocks='\n'.join(f'<section><h2><a href="https://www.youtube.com/watch?v=lCZN1RNqrpo&amp;t={int(t)}s">{stamp(t)}</a> {html.escape(names[s])}</h2><p>{html.escape(text)}</p></section>' for t,s,text in paragraphs)
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Speaker-labeled transcript</title><style>
body{max-width:880px;margin:48px auto;padding:0 24px;color:#172f31;background:#fff;font:18px/1.7 system-ui,sans-serif}h1{font-size:34px;line-height:1.2}h2{font-size:16px;margin:0;color:#155e63}section{margin:30px 0}p{margin:8px 0}a{color:#155e63}aside{font-size:14px;line-height:1.6;padding:20px;background:#f0f5f4;border-radius:8px}header{border-bottom:2px solid #cbdad7;padding-bottom:24px}.subtitle{font-size:20px;color:#526a6c}@media print{body{font-size:11pt;margin:0;max-width:none}h2{break-after:avoid;font-size:10pt}p{orphans:3;widows:3}section{margin:16px 0}aside{font-size:9pt}a{text-decoration:none}}
</style><header><h1>'''+html.escape(title)+'</h1><p class="subtitle">Full speaker-labeled transcript · 59:56</p><ul>'+''.join('<li>'+html.escape(r)+'</li>' for r in roster)+'</ul><aside>'+html.escape(note)+'</aside><p><a href="'+url+'">Source video</a> · Click timestamps to open the corresponding moment.</p></header><main>'+blocks+'</main></html>'
(ROOT/(stem+'.html')).write_text(page,encoding='utf-8')
assert len(tokens)==sum(bool(s['utf8'].replace('>>','').strip()) for e in source['events'] for s in e.get('segs',[]))
assert tokens==sorted(tokens,key=lambda x:x[0]),'Nonchronological caption tokens'
audit={'source_segments_preserved':len(tokens),'paragraphs':len(paragraphs),
       'word_count':sum(len(p[2].split()) for p in paragraphs),'first_timestamp':stamp(tokens[0][0]),
       'last_timestamp':stamp(tokens[-1][0]),'speaker_turns':[(stamp(t),names[s]) for t,s in turns]}
(ROOT/'transcript-validation.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps(audit,indent=2))
