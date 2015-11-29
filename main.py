import xml.etree.ElementTree as ET
import math
import json

inFileName = 'e:\\temp\\good.gpx'
outFileName = 'e:\\temp\\gps.gpx'
pointFileName = 'e:\\temp\\points.json'

drawMesh = True

step = 1.0

ET.register_namespace('', "http://www.topografix.com/GPX/1/0")
tree = ET.parse(inFileName)
root = tree.getroot()

def DegToRad(angle):
    return angle * math.pi / 180.0


#  Radius is given as 1.
def SphericalToCartesian(lon, lat):
    z = math.sin(DegToRad(lat))
    x = math.cos(DegToRad(lat)) * math.cos(DegToRad(lon))
    y = math.cos(DegToRad(lat)) * math.sin(DegToRad(lon))
    return x, y, z


def CartesianInnerProduct(v1, v2):
    print('v1 = ' + str(v1[0]) + ', ' + str(v1[1]) + ', ' + str(v1[2]))
    print('v2 = ' + str(v2[0]) + ', ' + str(v2[1]) + ', ' + str(v2[2]))
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]


def SpericalToVector(lon, lat):
    x, y, z = SphericalToCartesian(lon, lat)
    v = []
    v.append(x)
    v.append(y)
    v.append(z)
    return v


def PointToVector(p):
    return SpericalToVector(p['lon'], p['lat'])


def AngleBetwee2Points(p1, p2):
    cos = CartesianInnerProduct(PointToVector(p1), PointToVector(p2))
    print('cos = ' + str(cos))
    return math.acos(cos)


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

    angle = AngleBetwee2Points(startPoint, endPoint)
    print('angle ' + str(angle * 180 / math.pi))

    def AddStep(lon, lat):
        x, y, z = SphericalToCartesian(lon, lat)
        print('x, y, z = ', str(x), ', ', str(y), ', ', str(z))

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

tree.write(outFileName)
