import os
import sys
import json
import re
from bs4 import BeautifulSoup
import random
from textblob import TextBlob
from textblob import Word
import nltk

import requests
from flask import Flask, request

nltk.data.path.append('./nltk_data/')       #tell python where to look for nltk

app = Flask(__name__)



def pick_words(lines):
  """A function to find words with possible context in a string"""
  blob=TextBlob(lines)
  words=[word for word in blob.tags if word[1]=='NN' or word[1]=='NNS' or word[1]=='NNP' or word=="JJ"]      #nouns and adjectives
  if words==[]:
	  return []
  return words
	

def pick_random_word(lines): 
  """Picks a random word and finds a relevant word from its definition"""
  word=pick_words(lines)
  random_word=random.choice(word)
  if random_word[1]!='NNP':   #names don't need a definition
      word_obj=Word(random_word[0])
      random_synset = random.choice(word_obj.synsets)
      random_lemma = random.choice(random_synset.lemma_names())
      return random_lemma
  else:
      return random_word[0]
  
  
  
  
  
  
  

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
  full_quote="""{}                            
  -{}"""                                            
  
  
  
  full_quotes=[full_quote.format(quote.text,author.text) for quote,author in zip(quotes,authors)]
  
  
  
  try:
    quote=random.choice(full_quotes)       #choose a random quote
  except IndexError:
    return Quote_Get('confused')
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
                        reply_text=Quote_Get(pick_random_word(message_text))
                        send_message(reply_text)
                        
                        
                    except KeyError:
                      send_message(sender_id,'I need text messages')
					
                    
                    
						

                    

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
  app.run(debug=True)
 

  
  
  
  


   
