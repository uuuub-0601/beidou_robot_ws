#!/usr/bin/env python3
"""Rasterize elderly_final.sdf axis-aligned box collisions into a ROS map."""
from pathlib import Path
import math
import xml.etree.ElementTree as ET

WORLD = Path(__file__).resolve().parents[1]
SDF = WORLD / "src/beidou_gazebo/worlds/elderly_final.sdf"
OUT = WORLD / "maps"
RESOLUTION = 0.05
XMIN, XMAX = -10.0, 10.0
YMIN, YMAX = -8.0, 8.0
WIDTH = round((XMAX-XMIN)/RESOLUTION)
HEIGHT = round((YMAX-YMIN)/RESOLUTION)
OCCUPIED_MODELS = {"wall_left", "wall_right", "wall_back", "wall_front", "final_flowerbed", "final_bench_west", "final_bench_east", "final_table", "final_partition"}

def pose_values(text):
    vals=[float(v) for v in (text or "0 0 0 0 0 0").split()]
    return (vals+[0.0]*6)[:6]

def mark(grid, cx, cy, sx, sy):
    # Axis-aligned boxes in elderly_final.sdf; use conservative ceil bounds.
    x0=max(0, math.floor(((cx-sx/2)-XMIN)/RESOLUTION))
    x1=min(WIDTH-1, math.ceil(((cx+sx/2)-XMIN)/RESOLUTION)-1)
    y0=max(0, math.floor(((cy-sy/2)-YMIN)/RESOLUTION))
    y1=min(HEIGHT-1, math.ceil(((cy+sy/2)-YMIN)/RESOLUTION)-1)
    for iy in range(y0,y1+1):
        for ix in range(x0,x1+1): grid[iy][ix]=0

root=ET.parse(SDF).getroot()
grid=[[254]*WIDTH for _ in range(HEIGHT)]
found=[]
for model in root.findall(".//model"):
    name=model.get("name")
    if name not in OCCUPIED_MODELS: continue
    mp=model.find("pose"); mx,my,*_=pose_values(mp.text if mp is not None else None)
    collision=model.find("link/collision")
    box=collision.find(".//box/size") if collision is not None else None
    if box is None: raise RuntimeError(f"{name} has no box collision")
    sx,sy,*_=pose_values(box.text)
    mark(grid,mx,my,sx,sy); found.append((name,mx,my,sx,sy))
missing=OCCUPIED_MODELS-{n for n,*_ in found}
if missing: raise RuntimeError(f"Missing models: {sorted(missing)}")
OUT.mkdir(exist_ok=True)
pgm=OUT/"elderly_final.pgm"
with pgm.open("wb") as f:
    f.write(f"P5\n{WIDTH} {HEIGHT}\n255\n".encode())
    for row in reversed(grid): f.write(bytes(row))
yaml=OUT/"elderly_final.yaml"
yaml.write_text("image: elderly_final.pgm\nmode: trinary\nresolution: 0.05\norigin: [-10.0, -8.0, 0.0]\nnegate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196\n")
print(f"generated {pgm} and {yaml}: {WIDTH}x{HEIGHT}, origin=({XMIN},{YMIN})")
for item in found: print("  ", item)
