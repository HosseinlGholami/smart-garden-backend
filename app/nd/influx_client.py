import os
from influxdb_client import InfluxDBClient, Point, WriteOptions, QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxDBHandler:
    def __init__(self, org="Robotic", bucket="TRF"):
        self.org = org
        self.token = os.getenv('INFLUXDB_TOKEN')
        self.local_ip = os.environ['LOCAL_IP']
        self.bucket = bucket
        self.url = f"http://{self.local_ip}:8086"
        
        self.write_client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.write_client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.write_client.query_api()

    def write_data(self, section, sensor_value,embedd_ts):
        try:
            # Construct InfluxDB Point
            point = Point("measurement_name") \
                .tag("section", section) \
                .field("sensor_value", sensor_value) \
                .field("embedd_ts", embedd_ts)

            # Write data point to InfluxDB
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            # print(f"Data written to InfluxDB: {point}")

        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")

        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")


    def query_data_by_place(self, place):
        try:
            query = f'from(bucket: "{self.bucket}") |> range(start: -1d) |> filter(fn: (r) => r["_measurement"] == "measurement_name" and r["place"] == "{place}")'
            tables = self.query_api.query(query=query)
            
            for table in tables:
                for record in table.records:
                    print(f"Place: {record.get_value()}")

        except Exception as e:
            print(f"Error querying data from InfluxDB: {e}")

# Example usage
# if __name__ == "__main__":

#     token = "sjjHH5h5eNvdUhqOC9M4Ze5V4eB-3XRAT7X9Pazs1QHisUU4Sbx7UhFLQEc3Lxh5glJnkJxj7tOXrKi5c_2vHw=="
#     local_ip = os.environ.get('LOCAL_IP', 'localhost')  
#     url = f"http://{local_ip}:8086"
#     org = "Robotic"
#     bucket = "nd"
#     client = InfluxDBClient(url=url, token=token, org=org)

#     # Define the time range for deletion
#     start = "2024-11-05T00:00:00Z"
#     stop = "2025-06-30T15:16:01Z"

#     # Define the predicate for filtering the data to delete (Only based on measurement)
#     predicate = '_measurement="measurement_name"'

#     # Call the delete API
#     delete_api = client.delete_api()
#     try:
#         delete_api.delete(start=start, stop=stop, predicate=predicate, bucket=bucket, org=org)
#         print("Data deletion successful!")
#     except Exception as e:
#         print(f"Error deleting data: {e}")

#     # Close the client
#     client.close()
