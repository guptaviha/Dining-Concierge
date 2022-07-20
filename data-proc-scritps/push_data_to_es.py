import boto3
import csv
import requests
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
import pandas as pd

base_path = "/Users/aatman/nyu/Sem2/CC/assignment1/data/"

region = "us-east-1"
service = "es"
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = "https://search-yelp-restaurant-data-idw5yplh7blonn57r3fi3prbv4.us-east-1.es.amazonaws.com"
index = "cuisine-index"
type = "_doc"
url = host + "/" + index + "/" + type + "/"

headers = { "Content-Type": "application/json" }

search = OpenSearch(
	hosts = [{"host": host, "port": 443}],
	http_auth = awsauth,
	use_ssl = True,
	verify_certs = True,
	connection_class = RequestsHttpConnection
)


def handler(event, context):
	count = 0
	for record in event['Records']:
		# Get the primary key for use as the OpenSearch ID
		id = record['dynamodb']['Keys']['id']['S']

		if record['eventName'] == 'REMOVE':
			r = requests.delete(url + id, auth=awsauth)
		else:
			document = record['dynamodb']['NewImage']
			r = requests.put(url + id, auth=awsauth, json=document, headers=headers)
		count += 1
	return str(count) + ' records processed.'


def main():
	file_path = "/Users/aatman/nyu/Sem2/CC/assignment1/results.csv"
	csv = pd.read_csv(file_path)
	print(csv)



if __name__ == "__main__":
	main()