import xml.etree.ElementTree as ET
import math
import json

inFileName = 'e:\\temp\\good.gpx'
outFileName = 'e:\\temp\\gps.gpx'
pointFileName = 'e:\\temp\\points.json'

drawMesh = True

step = 1.0  # Degrees.

ET.register_namespace('', "http://www.topografix.com/GPX/1/0")
tree = ET.parse(inFileName)
root = tree.getroot()

def CrossProduct(a, b):
    x = a[1] * b[2] - a[2] * b[1]
    y = a[2] * b[0] - a[0] * b[2]
    z = a[0] * b[1] - a[1] * b[0]
    return x, y, z


def DegToRad(angle):
    return angle * math.pi / 180.0


def RadToDeg(angle):
    return angle * 180.0 / math.pi


#  Radius is given as 1.
def SphericalToCartesian(lon, lat):
    z = math.sin(DegToRad(lat))
    x = math.cos(DegToRad(lat)) * math.cos(DegToRad(lon))
    y = math.cos(DegToRad(lat)) * math.sin(DegToRad(lon))
    return x, y, z


def CartesianInnerProduct(v1, v2):
    #print('v1 = ' + str(v1[0]) + ', ' + str(v1[1]) + ', ' + str(v1[2]))
    #print('v2 = ' + str(v2[0]) + ', ' + str(v2[1]) + ', ' + str(v2[2]))
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]


def SpericalToVector(lon, lat):
    x, y, z = SphericalToCartesian(lon, lat)
    v = [x, y, z]
    return v


def Sign(value):
    return -1 if value < 0 else 1


def CartesianToSpherical(v):
    x = v[0]
    y = v[1]
    z = v[2]
    lat = math.acos(math.sqrt(x * x + y * y) / math.sqrt(x * x + y * y + z * z)) * Sign(z)
    lon = math.acos(x / math.sqrt(x * x + y * y)) * Sign(y)
    return RadToDeg(lon), RadToDeg(lat)


def NormalizeVector(v):
    norma = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if norma != 0.0:
        return [v[0] / norma, v[1] / norma, v[2] / norma]
    else:
        return v


def RotateAround(axis, vector, angle):
    # Clockwise direction.
    phi = (-1) * DegToRad(angle)
    matrix = {}
    axis = NormalizeVector(axis)
    l = axis[0]
    m = axis[1]
    n = axis[2]
    matrix[0, 0] = l * l + math.cos(phi) * (1 - l * l)
    matrix[0, 1] = l * (1 - math.cos(phi)) * m + n * math.sin(phi)
    matrix[0, 2] = l * (1 - math.cos(phi)) * n - m * math.sin(phi)
    matrix[1, 0] = l * (1 - math.cos(phi)) * m - n * math.sin(phi)
    matrix[1, 1] = m * m + math.cos(phi) * (1 - m * m)
    matrix[1, 2] = m * (1 - math.cos(phi)) * n + l * math.sin(phi)
    matrix[2, 0] = l * (1 - math.cos(phi)) * n + m * math.sin(phi)
    matrix[2, 1] = m * (1 - math.cos(phi)) * n - l * math.sin(phi)
    matrix[2, 2] = n * n + math.cos(phi) * (1 - n * n)
    vector1 = [0, 0, 0]
    vector1[0] = matrix[0, 0] * vector[0] + matrix[0, 1] * vector[1] + matrix[0, 2] * vector[2]
    vector1[1] = matrix[1, 0] * vector[0] + matrix[1, 1] * vector[1] + matrix[1, 2] * vector[2]
    vector1[2] = matrix[2, 0] * vector[0] + matrix[2, 1] * vector[1] + matrix[2, 2] * vector[2]
    return vector1


def PointToVector(p):
    return SpericalToVector(p['lon'], p['lat'])


def AngleBetwee2Points(p1, p2):
    cos = CartesianInnerProduct(PointToVector(p1), PointToVector(p2))
    #print('cos = ' + str(cos))
    return math.acos(cos)


def RotateStartVector(startLon, startLat, endLon, endLat):
    x1 = SpericalToVector(startLon, startLat)
    y1 = SpericalToVector(endLon, endLat)
    # Rotation axis.
    z1 = CrossProduct(x1, y1)
    x2 = RotateAround(z1, x1, step)
    z2 = CrossProduct(x2, y1)
    lon, lat = CartesianToSpherical(x2)
    return CartesianInnerProduct(z2, z1), lon, lat


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

def AddStep(track, lon, lat, endLon, endLat, n):
    #print('#' + str(n) + ', lon = ' + str(lon) + ', lat = ' + str(lat))
    AddPoint(track, lon, lat)
    return RotateStartVector(lon, lat, endLon, endLat)


def DrawSegment(track, startPoint, endPoint):
    # Current values of latitude and longitude.
    lon = startPoint['lon']
    lat = startPoint['lat']

    n = 0
    # Start point.
    innerProduct, lon, lat = AddStep(track, lon, lat, endPoint['lon'], endPoint['lat'], n)
    n += 1

    while innerProduct > 0:
        innerProduct, lon, lat = AddStep(track, lon, lat, endPoint['lon'], endPoint['lat'], n)
        n += 1

    # End point.
    AddStep(track, endPoint['lon'], endPoint['lat'], endPoint['lon'], endPoint['lat'], n)


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


def DrawMeshByNeighbors(rootElement, trackData):
    points = trackData['points']
    track = AddTrack(rootElement, trackData['name'])

    if len(points) != 0:
        startPoint = points[0]

        if len(points) == 1:
            AddPoint(track, startPoint['lon'], startPoint['lan'])

        elif len(points) > 1:
            n = 0
            for i in range(0, len(points)):
                startPoint = points[i]
                minAngle = None
                for j in range(0, len(points)):
                    if j != i:
                        endPoint = points[j]
                        angle = AngleBetwee2Points(startPoint, endPoint)
                        if minAngle == None or angle < minAngle:
                            minAngle = angle

                print('min angle between points: ' + str(RadToDeg(minAngle)))
                for j in range(i + 1, len(points)):
                    endPoint = points[j]
                    angle = AngleBetwee2Points(startPoint, endPoint)
                    if RadToDeg(math.fabs(angle - minAngle)) < step:
                        print('segment # ' + str(n))
                        n += 1
                        DrawSegment(track, startPoint, endPoint)


tracks = ReadData()

for gpx in root.iter('{http://www.topografix.com/GPX/1/0}gpx'):
    # Removes existing tracks.
    for trk in gpx.findall('{http://www.topografix.com/GPX/1/0}trk'):
        gpx.remove(trk)

    for track in tracks:
        if drawMesh:
            #DrawMesh(gpx, track)
            DrawMeshByNeighbors(gpx, track)
        else:
            DrawTrack(gpx, track)

    # Only one gpx in the file.
    break

tree.write(outFileName)
