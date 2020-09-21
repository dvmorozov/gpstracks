### Welcome to Gpstracks

This command-line utility allows generating tracks on the surface of Earth by means a few reference points. Generated tracks can be viewed by means, for example, Google Earth. The utility generates intermediate coordinates using given points as vertexes. By such way you can outline some region or draw lines on the surface of Earth. Tracks are stored in standard format and you can use any software capable to read these data.

### Example Track

As an example I built boundaries of Bermuda Triangle and uploaded them to Google Earth.

[Bermuda Triangle](images/bermuda-triangle.png)

Here are [Bermuda Triangle coordinates](data/bermuda-triangle.json) and resulting [GPS track](data/output.gpx).

### Usage

The utility consumes set of vertexes of the track as JSON-file. Longitude and latitude must be assigned in range from -180 to 180 degrees. Negative values correspond to western longitudes and southern latitudes.

[JSON example](data/bermuda-triangle.json)

The utility requires template file to get track file in standard form.

[Template example](data/template.gpx)

Usage _gpstracks --tf=<template file name> --pf=<point file name> --of=<output file name> --step=<angle step in degrees>_.

[Download executable](data/gpstracks.zip)

### Find me on

[LinkedIn](https://www.linkedin.com/in/dmitry-morozov-79490a59/)

[Facebook](https://www.facebook.com/dmitry.v.morozov)


