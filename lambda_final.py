import boto3
import json
import logging
import os
import urllib
#from base64 import b64decode
#from urlparse import parse_qs

#ENCRYPTED_EXPECTED_TOKEN = os.environ['kmsEncryptedToken']
#kms = boto3.client('kms')
#expected_token = kms.decrypt(CiphertextBlob=b64decode(ENCRYPTED_EXPECTED_TOKEN))['Plaintext']

##Bot User OAuth Access token
expected_token = 'xoxb-BOT TOKEN'  #slsapp

#table_name = os.environ['TABLE_NAME']
region_name = os.getenv('REGION_NAME', 'ap-northeast-1')
#dynamodb = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')
#log_table = dynamodb.Table('slacklog')
msg_table = dynamodb.Table('slackmsg')
init_table =dynamodb.Table('slacklogs')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json'
        },
    }

#message making
def lambda_handler(event, context):
    #return respond(None,event) # event : slack request data(header, body..)
    print("lambda_handler : event")

    #/init, /save 메소드 구현
    #if event['httpMethod'] == 'POST':
    print("############# TEST POST #############") # get일떄

    body = str(event['body']) #string
    item = body.split("&") #list
    item_dict = dict(x.split('=') for x in item)

    #event로 들어온 body 데이터
    print(body)

    #POST data parsing
    token = item_dict['token']
    team_id = item_dict['team_id']
    team_domain = item_dict['team_domain']
    channel_id = item_dict['channel_id']
    channel_name = item_dict['channel_name']
    user_id = item_dict['user_id']
    user_name = item_dict['user_name']
    command = item_dict['command']
    text = item_dict['text']
    #response_url
    #trigger_id

    print("input cmd")
    print(command)

    #/init cmd : post 방식
    if command == '%2Fsls_init':
         slack_message = { 'text': "put event init data! "}
         dbmsg = slack_message['text']

         print("#######input dynamodb slackinit " +command)

         #user id : PK
         items = {'slack_token' : token,
                  'team_domain' : team_domain,
                  'channel_id': channel_id,
                  'channel_name' : channel_name,
                  'user_id' : user_id,
                  'username' : user_name,
                  'command' : command,
                  'msg' : dbmsg
                  }

         slackinit_db = init_table.put_item(Item = items)
         print(slackinit_db)
         return respond(None,slack_message)


    #/save cmd
    if command == '%2Fsls_save':
         slack_message = { 'text': "update message! " }
         dbmsg = slack_message['text']

         print("#######update dynamodb slackinit" +command + user_id)
         #log_table.put_item(TableName='slacklog', Item={'username':{'S':user_name},'msg':{'S':dbmsg},'cmd':{'S':command},'op':{'S':text}})

         #items = {'username' : user_name, 'msg' : dbmsg , 'cmd' : command , 'op' : text}
         #slacklog_db = log_table.update_item(Item = items)
         #print(slacklog_db)

         #완료: msg, command update
         slackupdate_db = init_table.update_item(
            Key={
                'user_id' : user_id
            },
            UpdateExpression = "SET msg = :val1, command = :val2",
            ExpressionAttributeValues={
                ':val1' : dbmsg,
                ':val2' : command
            }
         )
         print(slackupdate_db)
         return respond(None,slack_message)

    #/echo md
    if command == '%2Fsls_echo':
        slack_message = { 'text': "eho message! "+text}
        return respond(None,slack_message)

    if command == '%2Fsls_bot':
        #해결 : DB get
        print("#######get dynamodb ")
        dbresult = msg_table.get_item( Key = {'operation': command } )
        #print(result["Item"]["operation"])
        print(dbresult["Item"]["return_msg"])

        #update message
        #slack_message =dbresult["Item"]["return_msg"] # formant : "message"
        slack_message = { 'text' : dbresult["Item"]["return_msg"] }
        return respond(None,slack_message)
