import xml.etree.ElementTree as ET
import math
import json

inFileName = 'c:\\temp\\good.gpx'
outFileName = 'c:\\temp\\gps.gpx'
pointFileName = 'c:\\temp\\points.json'

drawMesh = True

step = 1.0

ET.register_namespace('', "http://www.topografix.com/GPX/1/0")
tree = ET.parse(inFileName)
root = tree.getroot()


def ReadData():
    with open(pointFileName) as dataFile:
        data = json.load(dataFile)

    for track in data['tracks']:
        print('track :' + str(track))

    return data['tracks']


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


# Returns track segment.
def AddTrack(rootElement, trackName):
    track = ET.Element("{http://www.topografix.com/GPX/1/0}trk")
    name = ET.Element("{http://www.topografix.com/GPX/1/0}name")
    name.text = trackName

    trkseg = ET.Element("{http://www.topografix.com/GPX/1/0}trkseg")
    track.append(name)
    track.append(trkseg)

    rootElement.append(track)
    return trkseg


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


def DrawTrack(rootElement, trackData):
    points = trackData['points']
    track = AddTrack(rootElement, trackData['name'])

    if len(points) != 0:
        startPoint = points[0]

        if len(points) == 1:
            AddPoint(track, startPoint['lon'], startPoint['lan'])

        elif len(points) > 1:
            for endPoint in points[1:]:
                DrawSegment(track, startPoint, endPoint)
                startPoint = endPoint



def DrawMesh(rootElement, trackData):
    points = trackData['points']
    track = AddTrack(rootElement, trackData['name'])

    if len(points) != 0:
        startPoint = points[0]

        if len(points) == 1:
            AddPoint(track, startPoint['lon'], startPoint['lan'])

        elif len(points) > 1:
            for i in range(0, len(points)):
                startPoint = points[i]
                for j in range(i + 1, len(points)):
                    endPoint = points[j]
                    DrawSegment(track, startPoint, endPoint)


tracks = ReadData()

for gpx in root.iter('{http://www.topografix.com/GPX/1/0}gpx'):
    # Removes existing tracks.
    for trk in gpx.findall('{http://www.topografix.com/GPX/1/0}trk'):
        gpx.remove(trk)

    for track in tracks:
        if drawMesh:
            DrawMesh(gpx, track)
        else:
            DrawTrack(gpx, track)

    # Only one gpx in the file.
    break

for trk in root.iter('{http://www.topografix.com/GPX/1/0}trk'):
    print('trk: ' + str(trk))

tree.write(outFileName)
