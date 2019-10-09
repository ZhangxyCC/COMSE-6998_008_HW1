import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    print(event)
    text = event["messages"]
    client = boto3.client('lex-runtime')
    response = client.post_text(
            botName='HwOne',
            botAlias='chat',
            userId="kkkmh",
            sessionAttributes={},
            requestAttributes={},
            # event.BotRequest.Message.UnstructuredMessage.Text;
            #inputText = event["BotRequest"]["Message"]["UnstructuredMessage"]["text"]
            inputText = text
        )
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json', 
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'},
        'body':response["message"]
    }
    
   
