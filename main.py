import xml.etree.ElementTree as ET

inFileName = 'c:\\temp\\good.gpx'
outFileName = 'c:\\temp\\gps.gpx'

startLat = 0.0
startLon = 0.0

stepLat = 1.0
stepLon = 1.0

ET.register_namespace('', "http://www.topografix.com/GPX/1/0")
tree = ET.parse(inFileName)
root = tree.getroot()

print(root.tag)

for trk in root.iter('{http://www.topografix.com/GPX/1/0}trkseg'):
    # Удал. т. раобтает только для дочерних.
    for point in trk.findall('{http://www.topografix.com/GPX/1/0}trkpt'):
        trk.remove(point)

    for i in range(0, 10):
        point = ET.Element("{http://www.topografix.com/GPX/1/0}trkpt", dict(lon=str(startLon + stepLon * i),
                                                                            lat=str(startLat + stepLat * i)))
        trk.append(point)

        time = ET.Element("{http://www.topografix.com/GPX/1/0}time")
        time.text = '2011-09-22T18:57:01Z'
        point.append(time)

        fix = ET.Element("{http://www.topografix.com/GPX/1/0}fix")
        fix.text = '2d'
        point.append(fix)

        sat = ET.Element("{http://www.topografix.com/GPX/1/0}sat")
        sat.text = '6'
        point.append(sat)

for trk in root.iter('{http://www.topografix.com/GPX/1/0}trkpt'):
    print(trk.attrib)

tree.write(outFileName)
