import xml.etree.ElementTree as ET
import math
import json

inFileName = 'e:\\temp\\good.gpx'
outFileName = 'e:\\temp\\gps.gpx'
pointFileName = 'e:\\temp\\points.json'

startPoint = dict(lat=26.57, lon=67.2)
endPoint = dict(lat=26.57, lon=139.2)

step = 1.0

ET.register_namespace('', "http://www.topografix.com/GPX/1/0")
tree = ET.parse(inFileName)
root = tree.getroot()


def ReadPoints():
    return json.loads(pointFileName).points


def AddPoint(track, lon, lat):
    point = ET.Element("{http://www.topografix.com/GPX/1/0}trkpt", dict(lon=str(lon),
                                                                        lat=str(lat)))
    track.append(point)

    time = ET.Element("{http://www.topografix.com/GPX/1/0}time")
    time.text = '2011-09-22T18:57:01Z'
    point.append(time)

    fix = ET.Element("{http://www.topografix.com/GPX/1/0}fix")
    fix.text = '2d'
    point.append(fix)

    sat = ET.Element("{http://www.topografix.com/GPX/1/0}sat")
    sat.text = '6'
    point.append(sat)


def DrawSegment(track, startPoint, endPoint):
    deltaLon = endPoint['lon'] - startPoint['lon']
    deltaLat = endPoint['lat'] - startPoint['lat']
    angleLen = math.sqrt(deltaLon * deltaLon + deltaLat * deltaLat)
    stepLon = deltaLon * step / angleLen
    stepLat = deltaLat * step / angleLen

    # Current values of latitude and longitude.
    lon = startPoint['lon']
    lat = startPoint['lat']

    def AddStep(lon, lat):
        AddPoint(track, lon, lat)
        lon += stepLon
        lat += stepLat
        deltaLat1 = lat - startPoint['lat']
        deltaLon1 = lon - startPoint['lon']
        return math.sqrt(deltaLon1 * deltaLon1 + deltaLat1 * deltaLat1), lon, lat

    len, lon, lat = AddStep(lon, lat)

    while len <= angleLen:
        len, lon, lat = AddStep(lon, lat)


points = ReadPoints()
print(str(points))

for trk in root.iter('{http://www.topografix.com/GPX/1/0}trkseg'):
    # Удал. т. раобтает только для дочерних.
    for point in trk.findall('{http://www.topografix.com/GPX/1/0}trkpt'):
        trk.remove(point)
    DrawSegment(trk, startPoint, endPoint)

for trk in root.iter('{http://www.topografix.com/GPX/1/0}trkpt'):
    print(trk.attrib)

tree.write(outFileName)
