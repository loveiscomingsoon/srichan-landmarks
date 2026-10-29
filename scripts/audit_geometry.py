"""Reproducible topology and landmark/footprint checks. Never snaps landmark coordinates.
Run with shapely and pyproj installed. Metrics are proximity tests, not surveyed accuracy.
"""
import sys,json,math,xml.etree.ElementTree as ET
from pathlib import Path
from shapely.geometry import shape,Point,Polygon
from shapely import transform as transform_coords
def transform(project,g): return transform_coords(g,project,interleaved=False)
from shapely.strtree import STRtree
from shapely.validation import explain_validity
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[1]
project=Transformer.from_crs('EPSG:4326','EPSG:32648',always_xy=True).transform

def run():
 buildings=json.loads((ROOT/'3d/data/buildings.geojson').read_text())
 landmarks=json.loads((ROOT/'3d/data/landmarks.geojson').read_text())
 records=[];geoms=[]
 for f in buildings['features']:
  g=shape(f['geometry']);m=transform(project,g);p=f['properties'];geoms.append(m)
  records.append({'osm_id':p['osm_id'],'source_id':p.get('source_id',p['osm_id']),'source_dataset':p.get('source_dataset','OpenStreetMap'),'source_confidence':p.get('source_confidence'),'source_image_date':p.get('source_image_date'),'name':p['name'],'valid':g.is_valid,'validity':explain_validity(g),'area_m2':round(m.area,1),'height_method':p['height_method'],'height_m':p['height'] if p['height_method']!='default' else None,'source_url':p.get('source_url') or f"https://www.openstreetmap.org/way/{p['osm_id']}", 'survey_verified':False})
 rows=[]
 for f in landmarks['features']:
  p=f['properties'];point=transform(project,shape(f['geometry']));idx=sorted(range(len(geoms)),key=lambda i:point.distance(geoms[i]))[:3]
  candidates=[dict(records[i],distance_to_footprint_m=round(point.distance(geoms[i]),2),point_inside_footprint=geoms[i].covers(point)) for i in idx]
  rows.append({'number':p['image_number'],'name':p['name'],'coordinates':f['geometry']['coordinates'],'role':p.get('location_role','place_reference'),'google_name':p.get('google_maps_name',''),'candidates':candidates,'building_identity_verified':False,'entrance_verified':False,'height_verified':False,'camera_bearing_verified':False,'qc_status':'ต้องยืนยันอาคารและทางเข้า' if p.get('location_role')!='photo_viewpoint' else 'จุดมุมภาพโดยประมาณ ไม่ผูกอาคารอัตโนมัติ'})
 overlaps=[]
 tree=STRtree(geoms)
 for i,a in enumerate(geoms):
  for j in tree.query(a,predicate='intersects'):
   j=int(j)
   if j>=i:continue
   area=a.intersection(geoms[j]).area
   if area>1:overlaps.append({'source_ids':[records[i]['source_id'],records[j]['source_id']],'intersection_m2':round(area,2)})
 report={'date':'2026-10-29','crs_coordinates':'EPSG:4326 longitude,latitude','crs_measurement':'EPSG:32648 UTM zone 48N metres','method':'point-in-polygon; shortest distance to footprint; polygon validity; overlap screening','accuracy_certification':False,'independent_ground_checkpoints':0,'rmse_m':None,'source_coverage':'OSM + Overture release 2026-10-21.0; OSM precedence for overlaps; no automatic marker snapping','note':'ระยะถึงขอบอาคารไม่ใช่ค่าความคลาดเคลื่อนพิกัด และอาคารใกล้ที่สุดอาจไม่ใช่อาคารเดียวกับสถานที่','buildings':records,'landmarks':rows,'overlaps':overlaps,'invalid_count':sum(not r['valid'] for r in records),'height_unknown_count':sum(r['height_method']=='default' for r in records)}
 out=ROOT/'data/audits/2026-10-29-geometry-qc.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 for r in rows:
  c=r['candidates'][0];print(r['number'],r['name'],c['name'],c['osm_id'],c['distance_to_footprint_m'],'inside',c['point_inside_footprint'])
 print('invalid',report['invalid_count'],'overlaps',len(overlaps),'height unknown',report['height_unknown_count'])
if __name__=='__main__':run()
