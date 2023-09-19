import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = os.environ.get("INFLUXDB_TOKEN")

org = "alteryx"
url = "http://localhost:8086"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket="spectr"

write_api = client.write_api(write_options=SYNCHRONOUS)


def write_to_influx(data):
    write_api.write(bucket=bucket, org="alteryx", record=data)

# json_body = [
#     {
#         "measurement": "brushEvents",
#         "tags": {
#             "user": "Carol",
#             "brushId": "6c89f539-71c6-490d-a28d-6c5d84c0ee2f"
#         },
#         "fields": {
#             "duration1": 127
#         }
#     },
#     {
#         "measurement": "brushEvents",
#         "tags": {
#             "user": "Carol",
#             "brushId": "6c89f539-71c6-490d-a28d-6c5d84c0ee2f"
#         },
#         "fields": {
#             "duration1": 162,
#             "duration2": 165,
#         }
#     }
# ]
# write_api.write(bucket=bucket, org="alteryx", record=json_body)


