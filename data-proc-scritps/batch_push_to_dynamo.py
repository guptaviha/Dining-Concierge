import boto3
from decimal import Decimal
import json
import os
import time


base_path = '/Users/aatman/nyu/Sem2/CC/assignment1/data/'
cuisines = ['chinese', 'indian', 'italian', 'mexican', 'thai']
restaurant_attributes = ['id', 'name', 'location', 'review_count', 'rating', 'price', 'cuisine', 'insertedAtTimestamp']
# locations = ['brooklyn', 'manhattan', 'queens']


def format_data(data, cuisine):
	dynamo_data = dict()
	keys = data.keys()
	if 'id' in keys:
		dynamo_data['id'] = data['id']
	if 'name' in keys:
		dynamo_data['name'] = data['name']
	if 'location' in keys:
		dynamo_data['location'] = data['location']
	if 'review_count' in keys:
		dynamo_data['review_count'] = data['review_count']
	if 'rating' in keys:
		dynamo_data['rating'] = Decimal(data['rating'])
	if 'price' in keys:
		dynamo_data['price'] = data['price']
	dynamo_data['cuisine'] = cuisine
	dynamo_data['insertedAtTimestamp'] = int(time.time())
	return dynamo_data


def push_data(data):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('yelp-restaurants')
	with table.batch_writer() as batch:
		for i in range(len(data)):
			batch.put_item(Item=data[i])
	return


def write_errors_to_file(errors, base_path):
	with open(base_path + '/errors.txt', 'w') as f:
		for error in errors:
			f.write(error + '\n')
	return


def main():
	errors = []
	batch_data = []
	count = 0
	for cuisine in cuisines:
		file_path = base_path + '/manhattan/' + cuisine + '/'
		for filename in os.listdir(file_path):
			f = open(file_path + filename)
			data = json.load(f)
			f.close()
			data = format_data(data, cuisine)
			batch_data.append(data)
			if len(batch_data) == 20:
				push_data(batch_data)
				print("sleeping...")
				time.sleep(120)
				count += 1
				batch_data = []
				if count % 100 == 0:
					print("count:", count)
		
	print("data pushed", count, "times")
	write_errors_to_file(errors, base_path)
	return


if __name__ == "__main__":
	main()
		