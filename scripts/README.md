# ขั้นตอนตรวจ GIS ศรีจันทร์

เครื่องมือ: Python, Shapely 2.2.0, pyproj 3.8.0, OvertureMaps 1.0.2 ดู requirements-gis.txt

1. เก็บ baseline OSM ใน data/audits/2026-10-29-buildings-before.geojson และเทียบกับ OSM API ล่าสุด ไม่แก้ข้อมูลต้นทางใน OSM อัตโนมัติ
2. ดาวน์โหลด Overture เฉพาะพื้นที่: `overturemaps download --bbox=102.828,16.426,102.842,16.435 -f geojson --type=building -o overture.geojson` (รอบนี้ release 2026-10-21.0)
3. `python scripts/merge_open_buildings.py overture.geojson`: คง OSM เดิมและตัดรายการซ้ำตาม OSM way id หรือขอบ Overture ที่มีพื้นที่ทับ OSM เกิน 10% ของพื้นที่ตัวเอง ไม่ย้ายหมุด
4. `python scripts/audit_geometry.py`: พิกัด EPSG:4326 lon/lat; วัดเมตร/ตร.ม.ใน EPSG:32648 UTM 48N; ตรวจรูปทรง การทับ >1 ตร.ม. และระยะหมุดถึงขอบอาคารใกล้สุด 3 รายการ
5. `python scripts/build_quality_page.py`: สร้าง quality/index.html, CSV สำรวจ, KML และ 3d/data/qc.json; ขอบที่ทับกันติด flag ให้ตรวจต่อ ไม่อ้างว่าเป็นอาคารผิดหรือแก้ด้วยการลบเอง
6. ตรวจ XML ของ KML, จำนวน/พิกัดหมุด, null ความสูงที่ไม่ทราบ, QR hash และทดสอบหน้าเว็บจริงก่อนเผยแพร่

`height=null` + `height_method=default` หมายถึงไม่ทราบความสูง; แสดงแปลนที่พื้นเริ่มต้น การเลื่อนความสูงใน UI เป็น simulation เท่านั้น ส่วน building:levels × 3 เมตรยังเป็นการประมาณ

ข้อจำกัด: การทดสอบนี้เป็น desk QA/QC ไม่ใช่การรังวัดหรือการรับรองตาม ASPRS ไม่มี independent checkpoints จึงไม่คำนวณ RMSE ความคลาดเคลื่อนจริง การอยู่ใน/ใกล้ขอบอาคารไม่ใช่หลักฐานว่าเป็นสถานที่เดียวกันหรือทางเข้าที่ใช้งานจริง ภาพประกอบ AI ห้ามใช้เป็นหลักฐานวัดขนาดหรือพิกัด
