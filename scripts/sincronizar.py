import json
import pathlib
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

RSS = 'https://www.ivoox.com/podcast-predicaciones-tbb-progreso-adoracion_fg_f11561816_filtro_1.xml'
DEST = pathlib.Path('data/predicaciones.json')
req = urllib.request.Request(RSS, headers={'User-Agent':'Mozilla/5.0 TBB-Predicaciones/1.0'})
with urllib.request.urlopen(req, timeout=35) as response:
    xml = response.read()
root = ET.fromstring(xml)
items = []
for node in root.findall('./channel/item')[:30]:
    def value(tag):
        return (node.findtext(tag) or '').strip()
    enclosure = node.find('enclosure')
    audio = enclosure.get('url', '') if enclosure is not None else ''
    link = value('link')
    if not link and not audio:
        continue
    pub = value('pubDate')
    try:
        pub = parsedate_to_datetime(pub).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError, IndexError):
        pub = ''
    items.append({'title':value('title') or 'Predicación', 'pubDate':pub, 'link':link, 'enclosure':{'link':audio}})
if not items:
    raise RuntimeError('RSS sin episodios válidos; no se reemplaza el respaldo')
DEST.parent.mkdir(parents=True, exist_ok=True)
DEST.write_text(json.dumps({'status':'ok','items':items}, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Sincronizados {len(items)} episodios')
