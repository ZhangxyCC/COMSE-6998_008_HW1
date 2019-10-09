import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging
import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger()
logger.setLevel(logging.ERROR)
sqs = boto3.resource('sqs')

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message, response_card):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message,
            #'responseCard': response_card
        }
    }
    
def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }



def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response

def validate_cuisine(cuisine):
    cuisine_types = ['chinese','pizza','japanese','mexican','italian']
    if(cuisine):
        return cuisine.lower() in cuisine_types

def validate_location(location):
    return location.lower() == "manhattan"


def validate_appointment(res_info):
    cuisine = res_info["Cuisine"]
    location = res_info["Location"]
    if cuisine is not None and not validate_cuisine(cuisine):
        return build_validation_result(False,'Cuisine','We do not provide support for {} cuisine yet.'.format(cuisine))
    if location is not None and not validate_location(location):
        return build_validation_result(False,'Location','We only have restaurant in Manhattan now')
    return {'isValid': True}
    
    

def build_validation_result(is_valid, violated_slot, message_content):
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def make_appointment(intent_request):
    res_info = {
        "Location" : intent_request['currentIntent']['slots']['Location'],
        "time" : intent_request['currentIntent']['slots']['Time'],
        "NumberofPeople" : intent_request['currentIntent']['slots']['NumberofPeople'],
        "Cuisine" : intent_request['currentIntent']['slots']['Cuisine'],
        "PhoneNumber" : intent_request['currentIntent']['slots']['PhoneNumber']
        }
    print(res_info)
    source = intent_request['invocationSource']
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    slots = intent_request['currentIntent']['slots']
    
    if intent_request['invocationSource'] == 'DialogCodeHook':
        result = validate_appointment(res_info)
        if result['isValid'] != True:
            slots[result['violatedSlot']] = None
            elicit_slot(session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message'])
            print("Invalid response:",response)
            return response
            
        print("after invalid return 1")
        
        response = {
                'sessionAttributes' : intent_request['sessionAttributes'],
                'dialogAction' : {
                        'type' : 'Delegate',
                        'slots' : slots
                }
        }
        return response
    sqs_client = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/234570711936/sqs'
    # original  = res_info["PhoneNumber"]
    # res_info["PhoneNumber"] = "+1" + original
    print("message to sent")
    print(res_info)
    try:
        msg = sqs_client.send_message(QueueUrl=queue_url,
                                      MessageBody=json.dumps(res_info))
        print(msg)
    except ClientError as e:
        logging.error(e)
        return None
    # response = queue.send_message(MessageBody=json.dumps(res_info))
    # print(response)

    return close(
        output_session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': "You're all set. Expect my recommendations shortly! Have a good day."
        }
    )

def thankyou(intent_request):
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    return close(
        output_session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': "You are welcome."
        }
    )
    
def greeting(intent_request):
    response = {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": "Hi there, how can I help?"
            }
        }
    }
    return response
    


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    if intent_name == 'DiningSuggestionsIntent':
        return make_appointment(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thankyou(intent_request)
    elif intent_name == 'GreetingIntent':
        return greeting(intent_request)
    
    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    print(event)
    print(context)
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)