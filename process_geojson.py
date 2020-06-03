import json
import random
from typing import List, NewType
import datetime

"""
The script used to modify standard GeoJSON to a special format to be visualized 
in a Travel layer in Kepler.GL 
Find docs here: https://docs.kepler.gl/docs/user-guides/c-types-of-layers/k-trip
Check format below:

{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "vendor":  "A"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [-74.20986, 40.81773, 0, 1564184363],
          [-74.20987, 40.81765, 0, 1564184396],
          [-74.20998, 40.81746, 0, 1564184409]
        ]
      }
    }
  ]
}
""" 

# Raw geojson files and target files.
GEOJSON_FILE = "route_lines.json"
PROCESSED_GEOJSON = "route_lines_processed.json"

# Define the flight departure timeframe  
start_time = datetime.datetime(2019, 6, 4, 7, 0, 0)
end_time = datetime.datetime(2019, 6, 4, 23, 0, 0)
Timestamp = NewType('Timestamp', datetime.datetime)

def generateTimestampSeries(nr_points: int) -> List[Timestamp]:
    """Genreate a series of timestamps with 3 minutes step starting from a random timestamp for every route."""
    random_nr = random.normalvariate(mu=0.5, sigma=0.1)
    dep_time = (start_time + random_nr * (end_time - start_time))
    timestamp_series = []
    for i in range(nr_points):
        ts = (dep_time + datetime.timedelta(minutes=3*i)).timestamp()
        timestamp_series.append(int(ts))
    return timestamp_series

def geneAltitudeSeries(nr_points: int) -> List[int]:
    """Generate a series of altitude for every route as required by the Kepler.gl framework for Trip layer.
    By default, set as 0. 
    """
    return [0] * nr_points

def main():
    with open(GEOJSON_FILE) as f:
        data = json.load(f) 

    for i, route in enumerate(data['features']):
        nr_points = len(route['geometry']['coordinates'])
        timestamp_series = generateTimestampSeries(nr_points)
        altitude_series = geneAltitudeSeries(nr_points)
        altitude_timestamp_series = list(zip(altitude_series, timestamp_series))

        for j, point in enumerate(route['geometry']['coordinates']):
            altitude_timestamp_pair = list(altitude_timestamp_series[j])
            point.extend(altitude_timestamp_pair)
            data['features'][i]['geometry']['coordinates'][j] = point
        # A workaround: Kepler.gl has a bug of processing linestrings formed by less than 4 vertices.
        if nr_points <=3:
            data['features'][i]['geometry']['coordinates'].extend([point]*2)

    with open(PROCESSED_GEOJSON, 'w+') as f:
        json.dump(data, f, default=str)

if __name__ == "__main__":
    main()
