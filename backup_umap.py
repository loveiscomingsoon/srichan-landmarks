#!/usr/bin/env python3
"""Archive the public uMap without cookies or edit credentials."""
import json
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE = 'https://umap.openstreetmap.fr/map/1471827/download/'
ROOT = Path(__file__).resolve().parent

def main():
    request = Request(SOURCE, headers={'User-Agent': 'SrichanLandmarksBackup/1.0', 'Accept': 'application/json'})
    with urlopen(request, timeout=60) as response:
        if 'html' in response.headers.get('Content-Type', ''):
            raise ValueError('Expected JSON, received HTML')
        data = json.load(response)
    if data.get('type') != 'umap' or not isinstance(data.get('layers'), list):
        raise ValueError('Unexpected uMap backup structure')
    # Keep public map data and settings; exclude administrative metadata.
    clean = {key: data[key] for key in ('type', 'geometry', 'properties', 'layers') if key in data}
    features = []
    for layer in clean['layers']:
        if layer.get('type') != 'FeatureCollection' or not isinstance(layer.get('features'), list):
            raise ValueError('Invalid layer')
        features.extend(layer['features'])
    if not any(f.get('geometry', {}).get('type') == 'Polygon' for f in features):
        raise ValueError('Missing survey zones; refusing to replace the last backup')
    for name, value in [('umap-backup.umap', clean), ('srichan-survey.geojson', {'type': 'FeatureCollection', 'features': features})]:
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'
        temp = ROOT / (name + '.tmp')
        temp.write_text(payload, encoding='utf-8')
        temp.replace(ROOT / name)
    print(f'Backed up {len(features)} public features')

if __name__ == '__main__':
    main()
