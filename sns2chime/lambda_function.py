# -*- coding: utf-8 -*-


import requests, json

def do_webhook(url, msg, page_all=False, page_present=False):
    print('start webhook')
    msg = '{}\n'.format(msg)
    if page_all: msg = '{} @All  '.format(msg)
    if page_present: msg = '{} @Present  '.format(msg)
        
    # msg = '{} @All   @Present'.format(msg)
    r = requests.post(url=url, json={'Content': msg})
    print(r)
    
def is_json(s):
    try:
        json_object = json.loads(s)
    except ValueError:
        return False
    if s[0]=='{' and s[-1]=='}':
        return True
    else:
        return False

def lambda_handler(event, context):
    chime_webhook_domain = 'https://hooks.chime.aws'
    page_all = False
    page_present = False
    
    resp = { 
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'ok'
        }
        
    print(json.dumps(event))
    qs = event['queryStringParameters']
    if 'page_all' in qs:
        page_all = True
    if 'page_present' in qs:
        page_present = True
        
    print(json.dumps(qs))
    if 'body' in event and type(event['body'])==str and is_json(event['body']):
        body_json = json.loads(event['body'])
        if 'Type' in body_json and body_json['Type'] == 'SubscriptionConfirmation' and 'SubscribeURL' in body_json:
            print('[info] got SubscribeURL, sending confirmation signal...')
            r = requests.get(url=body_json['SubscribeURL'])
            print(r)
            resp['body'] = "subscribed"
            return resp
        if 'Message' in body_json and is_json(body_json['Message']):
            body_json['Message'] = json.loads(body_json['Message'])
    elif 'text' in qs and len(qs['text'])>0:
        pass
    else:
        resp['body'] = "invalid http body"
        return resp
            
    qs_flat = '&'.join('{}={}'.format(x,y) for (x,y) in qs.items())   
    webhook_url = '{}/incomingwebhooks/{}?{}'.format(chime_webhook_domain, event['pathParameters']['proxy'], qs_flat)
    print('webhook_url=%s' % webhook_url)
    ''' overwrite the message if 'text' in the query string '''
    if 'text' in qs and len(qs['text'])>0:
        if is_json(qs['text']):
            try:
                body_json = json.loads(qs['text'])
                msg2send = json.dumps(body_json, indent=4, separators=(',', ': '))
            except yaml.parser.ParserError:
                #body_json = qs['text']
                msg2send = qs['text']
        else:
            msg2send = qs['text']
    else:
        msg2send = json.dumps(body_json, indent=4, separators=(',', ': '))
    
    do_webhook(webhook_url, msg2send, page_all, page_present )
        
    return resp
