import boto3
import json
import os
import random
import urllib3


num_restaurants_to_send = 3

mail = boto3.client('ses')
sqs = boto3.resource('sqs')
dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('yelp-restaurants-v2')
users = dynamodb.Table('users')
queue = sqs.get_queue_by_name(QueueName='dining')

http = urllib3.PoolManager()


def save_recommendations(name, recommendations):
    print('--dining-- Saving recommendations')
    recs = ''
    for rec in recommendations:
        recs += rec[0] + ' at ' + rec[1] + '\n'
    users.put_item(
       Item={
            'name': name,
            'recommendations': recs
        }
    )
    return


def send_email_via_ses(name, email, restaurants):
    print('--dining-- Sending Email')
    if len(email) == 0:
        email='vg2237@nyu.edu'
    recs = 'Hi, ' + name + '!\nBased on your choices we suggest these restaurants:\n'
    for rec in restaurants:
        recs += rec[0] + ' at ' + rec[1] + '\n'
    recs += "Bon Appetit!\n"
    response = mail.send_email(
        Source='am11444@nyu.edu',
        Destination={'ToAddresses': [email]},
        Message={
            'Subject': {
                'Data': 'Dining Concierge - Restaurant Suggestions - LF2'
            },
            'Body': {
                'Text': {
                    'Data': recs
                }
            }
        }
    )
    return


def get_restaurant_ids_from_es(cuisine):
    url = "https://search-yelp-restaurant-data-idw5yplh7blonn57r3fi3prbv4.us-east-1.es.amazonaws.com/restaurants/_search?q=" + cuisine + "&pretty"
    response = http.request('GET', url, headers = {'Authorization': 'Basic eWVscDpZZWxwQDEyMw=='})
    resp = json.loads(response.data.decode('utf-8'))
    ids = []
    # print('hello:', resp)
    for hit in resp['hits']['hits']:
        ids.append(hit['_id'])
    return ids
    

def get_restaurant_details_from_dynamo(id):
    response = table.get_item(Key={'id': str(id)})
    item = response['Item']
    return [item['name'], item['address']]
    

def process_message(msg):
    cuisine = msg['cuisine']
    name = msg['name']
    email = msg['email']
    print('--dining-- Making ES call')
    ids = get_restaurant_ids_from_es(cuisine)
    
    email_ids = random.sample(ids, num_restaurants_to_send)
    for id_ in email_ids:
        ids.remove(id_)
    restaurants = []
    print('--dining-- Getting restaurant details from DynamoDB')
    for id in email_ids:
        restaurants.append(get_restaurant_details_from_dynamo(id))
    send_email_via_ses(name, email, restaurants)
    
    recommendations = []
    email_ids = random.sample(ids, num_restaurants_to_send)
    for id in email_ids:
        recommendations.append(get_restaurant_details_from_dynamo(id))
    save_recommendations(name, recommendations)
    return


def lambda_handler(event, context):
    # my_json = {
    # "cuisine": 'indian',
    # "location":  'manhattan',
    # "name": 'aatman',
    # "email": 'am11444@nyu.edu',
    # "number_of_people": 3,
    # "dining_time": '7PM',
    # "dining_date": '2022/12/31'
    # }
    # process_message(my_json)
    for message in queue.receive_messages():
        my_json = json.loads(message.body)
        process_message(my_json)
        message.delete()
    return