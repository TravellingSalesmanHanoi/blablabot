import os
import sys
import json
import re
from bs4 import BeautifulSoup
import random

import requests
from flask import Flask, request

app = Flask(__name__)


def Quote_Get(query):
  quote_data=requests.get('https://www.brainyquote.com/search_results.html?q={}'.format(str(query).lower()))          #parse brainy quote by term
  soup=BeautifulSoup(quote_data.text,'html.parser')
  
  notFound=soup.find_all('h2')
  for entry in notFound:
	  if 'Your search for' in entry.text:
		  return Quote_Get('gibberish')
  
  
  
  
  max_pages=soup.find_all('a',href=re.compile('/search_results'))
  if max_pages!=[]:
      navigation_text=[int(i.text) for i in max_pages if i.text.isdigit()] #find how many pages there are by using the navigation panel
      max_page=max(navigation_text)
      quote_data=requests.get('https://www.brainyquote.com/search_results.html?q={}&&pg={}'.format(str(query).lower() \
      ,str(random.randint(1,max_page-1))))       #choose a random page
      soup=BeautifulSoup(quote_data.text,'html.parser') 
 
  
	  
  
  quotes=soup.find_all('a',class_=re.compile('qt_[1-9]*'))
  authors=soup.find_all('a',class_=re.compile('qa_[1-9]*'))  
  full_quote="""{}                            #format of the quote
  -{}"""                                            
  
  
  
  full_quotes=[full_quote.format(quote.text,author.text) for quote,author in zip(quotes,authors)]
  
  
	  
  quote=random.choice(full_quotes)       #choose a random quote
  return quote
  
  
  





@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message
					

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    try:
                        message_text = messaging_event["message"]["text"]  # the message's text
                        words=message_text.split(' ')
                        
                    except KeyError:
                      send_message(sender_id,'Sorry I can only talk and read in text')
					
                    
                    
						

                    send_message(sender_id,Quote_Get(str(entry)))

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print(str(message))
    sys.stdout.flush()


if __name__ == '__main__':
    #sapp.run(debug=True)
    Quote_Get('dddd')
   
