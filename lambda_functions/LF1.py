import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging
import decimal 
import boto3

queue_url = 'https://sqs.us-east-1.amazonaws.com/529645924119/Q1.fifo'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def elicit_slot(intent_name, slots, slot_to_elicit, message):
    return {
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def close(fulfillment_state, message):
    response = {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response

def delegate(slots):
    return {
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')
        
def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def build_validation_result(is_valid, violated_slot, message_content):
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }
    
    
def sendmsgtosqs(intent_request):

    cuisine = intent_request['currentIntent']['slots']['Cuisine']
    numberofpeople = intent_request['currentIntent']['slots']['NumberOfPeople']
    phonenumber = intent_request['currentIntent']['slots']['PhoneNumber']
    email = intent_request['currentIntent']['slots']['Email']
    diningtime = intent_request['currentIntent']['slots']['DiningTime']
    diningdate = intent_request['currentIntent']['slots']['DiningDate']
    location = intent_request['currentIntent']['slots']['Location']
    name = intent_request['currentIntent']['slots']['Name']
    
    # sqs = boto3.client('sqs')
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='dining')
    
    
    
    my_json = {
        "cuisine": cuisine,
        "location":  location,
        "name": name,
        "email": email,
        "number_of_people": numberofpeople,
        "dining_time": diningtime,
        "dining_date": diningdate,
        "phonenumber": phonenumber
    }
    json_body = json.dumps(my_json)
    response = queue.send_message(MessageBody=json_body)
    
    
    # response = sqs.send_message(
    #     QueueUrl=queue_url,
    #     MessageGroupId="dining_bot",
    #     MessageDeduplicationId="dining_dupli",
    #     MessageAttributes = {
    #         'cuisine': {
    #             'DataType': 'String',
    #             'StringValue': str(cuisine)
    #         },
    #         'location': {
    #             'DataType': 'String',
    #             'StringValue': str(location)
    #         },
    #         'name': {
    #             'DataType': 'String',
    #             'StringValue': str(name)
    #         },
    #         'phone_number': {
    #             'DataType': 'String',
    #             'StringValue': str(phonenumber)
    #         },
    #         'email': {
    #             'DataType': 'String',
    #             'StringValue': str(email)
    #         },
    #         'number_of_people': {
    #             'DataType': 'String',
    #             'StringValue': str(numberofpeople)
    #         },
    #         'dining_time': {
    #             'DataType': 'String',
    #             'StringValue': str(diningtime)
    #         },
    #         'dining_date': {
    #             'DataType': 'String',
    #             'StringValue': str(diningdate)
    #         }
    #     },
    #     # MessageBody= 'User request information from Lex'
    #     MessageBody= json.dumps({
    #         "cuisine": cuisine,
    #         "location":  location,
    #         "name": name,
    #         "phone_number": phonenumber,
    #         "email": email,
    #         "number_of_people": numberofpeople,
    #         "dining_time": diningtime,
    #         "dining_date": diningdate
    #     })
    # )
    
    logger.debug('SQS response={}'.format(response))
    



def validate_make_suggestions(cuisine, numberofpeople, phonenumber, diningtime, location, email, diningdate):
    location_types = ['manhattan']
    cuisine_types = ['indian', 'chinese', 'thai', 'italian', 'mexican']
    
    # validate this cuisine is from our list of 5 cuisines
    if cuisine:
        cuisine = cuisine.lower()
        if cuisine not in cuisine_types:
            return build_validation_result(False,'Cuisine','Sorry, We do not have that cuisine. Please pick one from the following: Indian, Chinese, Thai, Italian, Mexican')
    
    # validate that location is manhattan                                   
    if location and (location.lower() not in location_types):
        return build_validation_result(False,'Location','Sorry, We do not have that location. Please pick one from the following: Manhattan')
      
    # validate that 0 < numberofpeople < 20                          
    if numberofpeople and (int(numberofpeople) <= 0 or int(numberofpeople) >= 20):
        return build_validation_result(False, 'NumberOfPeople', 'Sorry, that value is out of range. Please enter a number between 1 and 19.')

    # validate phonenumber to have 10 digits only
    if phonenumber and len(phonenumber) != 10:
        return build_validation_result(False, 'PhoneNumber', 'Sorry, that number is invalid. Please enter a 10 digit number.')

    # validate email to have "@"
    if email and ("@" not in email):
        return build_validation_result(False, 'Email', 'Sorry, that email is invalid. Please enter a valid email.')

    
    # validate Date: Day should be either current day/any day after the current day ??
    if diningdate:
        user_date = datetime.datetime.strptime(diningdate, '%Y-%m-%d').date()
        curr_date = datetime.date.today()
        
        if not isvalid_date(diningdate):
            return build_validation_result(False, 'DiningDate', 'Sorry, that date is not valid. What date works best for you?')
            

        elif user_date < curr_date:
            return build_validation_result(False, 'DiningDate', 'Sorry, date must not be in the past. Can you try a different date?')


    # validate Time
    if diningtime:
        if len(diningtime) != 5:
            return build_validation_result(False, 'DiningTime', 'Sorry, I did not recognize that. What time would you like to book your restaurant?')

        user_hour, user_minute = diningtime.split(':')
        user_hour = parse_int(user_hour)
        user_minute = parse_int(user_minute)
        
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        current_hour = parse_int(now.strftime("%H"))
        current_minute = parse_int(now.strftime("%M"))
        
        # check for nulls
        if math.isnan(user_hour) or math.isnan(user_minute):
            return build_validation_result(False, 'DiningTime', 'Sorry, I did not recognize that. What time would you like to book your restaurant?')
            
        # validate time - should be greater than the current time 
        user_date = datetime.datetime.strptime(diningdate, '%Y-%m-%d').date()
        curr_date = datetime.date.today()
        
        print("dates")
        print(user_date)
        print(curr_date)
        
        if user_date == curr_date:
            if (user_hour < current_hour):
                return build_validation_result(False, 'DiningTime', 'Sorry, that time has already passed. Can you enter a valid time please?')
            elif (user_hour == current_hour) and (user_minute <= current_minute):
                return build_validation_result(False, 'DiningTime', 'Sorry, that time has already passed. Can you enter a valid time please?')


    return build_validation_result(True, None, None)

def make_suggestions(intent_request):
    
    source = intent_request['invocationSource']
    cuisine = intent_request['currentIntent']['slots']['Cuisine']
    numberofpeople = intent_request['currentIntent']['slots']['NumberOfPeople']
    phonenumber = intent_request['currentIntent']['slots']['PhoneNumber']
    diningtime = intent_request['currentIntent']['slots']['DiningTime']
    location = intent_request['currentIntent']['slots']['Location']
    name = intent_request['currentIntent']['slots']['Name']
    diningdate = intent_request['currentIntent']['slots']['DiningDate']
    email = intent_request['currentIntent']['slots']['Email']
    
 
    if source == 'DialogCodeHook':  
        slots = intent_request['currentIntent']['slots']
        validation_result = validate_make_suggestions(cuisine, numberofpeople, phonenumber, diningtime, location, email, diningdate)
        
        # if any slot is invalid
        if not validation_result['isValid']:
            x = validation_result['isValid']
            print(str(x) + "is invalid")
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )
        
        return delegate(slots)

    sendmsgtosqs(intent_request)
    
    return close(
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'You’re all set. Expect my suggestions shortly! Have a good day.'
        }
    )

def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    
    if intent_name == 'DiningSuggestionsIntent':
        return make_suggestions(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')    

def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    
    logger.debug('event={}'.format(event))
    response = dispatch(event)
    logger.debug('response={}'.format(response))
    return response    
    

