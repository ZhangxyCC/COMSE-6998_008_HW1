import boto3
import json
import time
import decimal
from requests_aws4auth import AWS4Auth
import requests
import random
import os
from botocore.exceptions import ClientError



def elasticSearch(category):
    host = 'https://search-hw1domaintest-3pqh5dd4bviby77nxe55uvwgvq.us-east-1.es.amazonaws.com' # The domain with https:// and trailing slash. For example, https://my-test-domain.us-east-1.es.amazonaws.com/
    path = '/restaurant' # the Elasticsearch API endpoint
    region = 'us-east-1' # For example, us-west-1
    service = 'es'
    access_key = os.environ['access_key']
    secret_key = os.environ['secret_key']
    awsauth = AWS4Auth(access_key, secret_key, region, service)
    
    url = host + path
    search='/_search?q='+ category
    r = requests.get(url+search, auth=awsauth) # requests.get, post, and delete have similar syntax
    
    index=random.randint(0, 9)
    print(json.dumps(json.loads(r.text), indent=2))
    hits=json.loads(r.text)['hits']['hits'][index]
    
    return hits["_id"]
    
    
def getFromDynamo(id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('yelp-restaurants')
    response = table.get_item(
        Key = {
            'id': id
        }
    )
    item = response['Item']
    return item
            


def lambda_handler(event, context):
    print(event)
    print(context)
    
    body = event['Records'][0]['body']
    #print(body)
    slots = json.loads(body)
    
    #print(type(body))
    
    
   
    #slots = event['Records'][0]['body']
    print(slots)
    category = slots['Cuisine']
    print(category)
    sns = boto3.client('sns')
   
   
    
    if category is not None:
        id = elasticSearch(category)
        item = getFromDynamo(id)
        
        #print(item)
        # {'info': {'rating': Decimal('4'), 'coordinates': {'latitude': Decimal('40.747844'), 'longitude': Decimal('-73.983901')}, 'review_count': Decimal('707'), 'location': ['14 E 34th St', 'New York, NY 10016'], 'categories': 'chinese', 'zip_code': '10016'}, 'id': 'kwqOmEwWJ0D9PyCdFGE3-g', 'name': 'Xian Famous Foods', 'insertedAtTimestamp': '2019-09-30 19:10:25'}
        sns = boto3.client('sns')
        phoneNumber = slots['PhoneNumber']
        numOfPeople = slots['NumberofPeople']
        time = slots['time']
        # 'Sushi Nakazawa, located at 23 Commerce St, 2. Jin Ramen, located at 3183 Broadway, 3. Nikko, located at 1280 Amsterdam Ave. Enjoy your meal!”
        print(phoneNumber)
        message = "Hello! Here are my {} restaurant suggestions for {} people, for today at {}: {}, locates at {}. Enjoy your meal!".format(category, numOfPeople, time,item['name'], item['info']['location'][0])
        #message = "This is test message"
        print(message)
        # response = sns.publish(
        #     Message = message,    
        #     PhoneNumber = phoneNumber
        # )
        send_email(slots,message)
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
def send_email(slots,message):
    SENDER = "xz2878@columbia.edu"

    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = slots["PhoneNumber"]
    
    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "ConfigSet"
    
    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"
    
    # The subject line for the email.
    SUBJECT = slots['Cuisine'] + " restaurant recommendation"
    
    BODY_TEXT = (message
            )
                
    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>"""+message+"""
    </body>
    </html>
    """            
    
    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    client = boto3.client('ses',region_name=AWS_REGION)
    
    # Try to send the email.
    try:
        response = client.verify_email_identity(
        EmailAddress = RECIPIENT
        )
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
