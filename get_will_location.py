import json
import boto3

client = boto3.client('s3')

resp = client.get_object(Bucket="pike-owntracks",Key="latest/latest.json")

owntracks = json.loads(resp['Body'].read())

lat = owntracks['lat']
lon = owntracks['lon']
regions = owntracks['inregions']

return({
    "latitude": lat,
    "longitude",lon,
    "regions": regions
})
