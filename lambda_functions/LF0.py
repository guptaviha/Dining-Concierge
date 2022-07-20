import json
import random
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    
    logger.debug('input from client={}'.format(event))
    

    client_input = event['messages'][0]['unstructured']['text']
    
    logger.debug('client input={}'.format(client_input))
    

    client = boto3.client('lex-runtime')

    lex_response = client.post_text(
        botName='DiningConcierge',
        botAlias='DiningConciergeAlias',
        userId="001",
        sessionAttributes={},
        requestAttributes={},
        inputText= client_input
    )
    
    
    logger.debug('lex response={}'.format(lex_response))
    
    lex_output = lex_response["message"]
    
    logger.debug('lex output={}'.format(lex_output))
        
    return {
        'headers': {
            'Access-Control-Allow-Headers' : 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },           
        'statusCode': 200,
        'messages':[{
            "type":'unstructured',
            "unstructured":{
                    # 'text': "I’m still under development, Viha. Please come back later."
                    'text': lex_output
                }
            }]
        }
