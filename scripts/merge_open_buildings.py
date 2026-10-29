import sys,json,collections
from pathlib import Path
from shapely.geometry import shape
from shapely.strtree import STRtree
r=Path(__file__).resolve().parents[1]
baseline=r/'data/audits/2026-10-29-buildings-before.geojson'
b=json.loads(baseline.read_text())
osm= [shape(f['geometry']) for f in b['features']];tree=STRtree(osm);existingids={f['properties']['osm_id'] for f in b['features']}
for f in b['features']:
 p=f['properties'];p.update(source_dataset='OpenStreetMap',source_url='https://www.openstreetmap.org/way/'+p['osm_id'],source_id='osm/way/'+p['osm_id'],survey_verified=False)
 if p['height_method']=='default':p['height']=None
raw=json.load(open(sys.argv[1]));skips=collections.Counter()
for f in raw['features']:
 pr=f['properties'];srcs=pr.get('sources') or [];src=next((s for s in srcs if s.get('property') in ['',None]),srcs[0] if srcs else {})
 record=src.get('record_id') or '';sid=record.split('@')[0]
 if sid.startswith('w') and sid[1:] in existingids:skips['same_osm_id']+=1;continue
 geom=shape(f['geometry'])
 if not geom.is_valid or geom.is_empty:skips['invalid']+=1;continue
 if geom.geom_type!='Polygon':skips['non_polygon']+=1;continue
 # Retain the directly sourced OSM polygon wherever the candidate overlaps substantially.
 if any(geom.intersection(osm[int(i)]).area/max(geom.area,1e-12)>.10 for i in tree.query(geom,predicate='intersects')):skips['osm_overlap']+=1;continue
 props={'osm_id':'','source_id':f['id'],'gers_id':f['id'],'source_dataset':src.get('dataset','Overture Maps'),'source_release':'2026-10-21.0','source_url':'https://docs.overturemaps.org/guides/buildings/','source_record':record,'source_version':src.get('version'),'source_confidence':src.get('confidence'),'source_image_date':src.get('update_time'),'license':'ODbL-1.0; Google Open Buildings attribution CC BY 4.0 where applicable','survey_verified':False,'name':(pr.get('names') or {}).get('primary') or 'ขอบอาคารจากข้อมูลเปิด — ยังไม่ยืนยันสถานที่','height':None,'height_method':'default','levels':None,'building':'yes'}
 b['features'].append({'type':'Feature','geometry':f['geometry'],'properties':props})
(r/'3d/data/buildings.geojson').write_text(json.dumps(b,ensure_ascii=False,separators=(',',':')))
m=json.loads((r/'3d/data/meta.json').read_text());m.update(buildings=len(b['features']),defaults=sum(f['properties']['height_method']=='default' for f in b['features']),overture_release='2026-10-21.0',overture_source='https://docs.overturemaps.org/getting-data/overturemaps-py/',source_counts=dict(collections.Counter(f['properties']['source_dataset'] for f in b['features'])),license='OpenStreetMap / Overture Maps ODbL; Google Open Buildings CC BY 4.0; Microsoft ML Buildings ODbL',qc='No surveyed horizontal or vertical accuracy certification; unknown height rendered flat by default')
(r/'3d/data/meta.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
print('Merged',m['buildings'],'sources',m['source_counts'],'skipped',dict(skips))
