# -*- coding: utf-8 -*-
import os
import sys
import json
import re
from bs4 import BeautifulSoup
import random
from textblob import TextBlob
from textblob import Word
import nltk
from nltk.corpus import stopwords
import time
import string








import requests
from flask import Flask, request

nltk.data.path.append('./nltk_data/')       #tell python where to look for nltk


app = Flask(__name__)



def pick_words(lines):
  """A function to find words with possible context in a string"""
  blob=TextBlob(lines)
  if blob.tags==[]:
	  return []
  words=[word for word in blob.tags if word[1]=='NN' or word[1]=='NNS' or word[1]=='NNP' or word=="JJ"]      #nouns and adjectives
  if words==[]:
	  words=[word for word in blob.tags if 'VB' in word[1] and word[0] not in stopwords.words('english')]       #no nouns but non-stopword verbs
  if words==[]:
	  words=blob.tags       #all words are stop words
	   	
	  
	  
  return words
	

def pick_random_word(lines): 
  """Picks a random word and finds a relevant word from its definition"""
  words=pick_words(lines)
  NNP_words=[i for i in words if i[1] in ('NNP','NNPS')]
  if NNP_words!=[]:
    random_word=random.choice(NNP_words)
    return random_word[0]
  elif words!=[]:
    random_word=random.choice(words)  
    return random_word[0]
  else:
    return 'nothing'     #no word in lines   
       
   #   word_obj=Word(random_word[0])
   #   try:
     #   noun_regex=re.compile(r'\w+\.n\.[0-9]*')
      #  noun_synsets=[synset for synset in word_obj.synsets if noun_regex.match(synset.name())]      #only the noun synsets are useful(others cause gibberish)
     #   random_synset = random.choice(noun_synsets)
    #    random_lemma = random.choice(random_synset.lemma_names())
   #     return random_lemma.replace('_',' ')
   #   except IndexError:
        
 
        
		  

def 	goodreads_get(query):
	#'<a href="/quotes/tag/love?page=99">99</a>
	quote_data=requests.get('http://www.goodreads.com/quotes/tag/{}'.format(str(query)))
	soup=BeautifulSoup(quote_data.text,'lxml')
	
	pages=soup.find_all('a',href=re.compile(r'/quotes/tag/.*page=[1-9]*'))
	
	if pages != []:
		max_page=int(pages[-2].text)
		print(max_page)
		page=random.randint(1,max_page)
		quote_data=requests.get('http://www.goodreads.com/quotes/tag/{}?page={}'.format(str(query),str(page)))
		
	
	
	quotes_set=soup.find_all('div',class_='quoteText')
	if quotes_set==[]:
	  log('got gibberish')
	  return "I don't understand"     
	#quotes=[''.join(s for s in quote if s in string.printable) for quote in quotes]
	found=False
	for i in range(1,len(quotes_set)*2):    #we don't want unicode characters - 5 chances to find a quote
	  quote=random.choice(quotes_set)
	  quote=quote.text.split('//<!')[0] #remove script
	  counter=0
	  for s in quote:
	    if s in string.printable:
	      counter+=1
	  log(counter)    
	    
	  if counter/len(quote) > 0.5:     #more than 50% of text should be printable
	    found=True                           #fast way to guarantee it contains mostly latin characters
	    quote=''.join(s for s in quote if s in string.printable)
	    break
			
	
	authors=soup.find_all('a',class_='authorOrTitle')
	authors=[author.text for author in authors]        #for later use
	if found:
	  return quote
	else:
	  return "I don't speak that many languages yet" 
	

def gnomiko_get(query):
	pass
	
	
	
	
	
	
	
	
	
	
	

	
	
  
  
  
  
  
  

def Quote_Get(query,default_query='Gibberish'):
  quote_data=requests.get('https://en.wikiquote.org/wiki/{}'.format(str(query).lower()),allow_redirects=True)          #parse brainy quote by term
  soup=BeautifulSoup(quote_data.text,'html.parser')
  
  error_text='If you have created this page in the past few minutes and it has not yet appeared'
  if error_text in soup.text:
      return Quote_Get('Confusion')
  
  search_heading=soup.find('h1',class_='firstHeading').text
  
 
  
  if search_heading=='Search Results' or error_text in search_heading:
      return Quote_Get('confusion')
      
      
  body=soup.find('div',id='mw-content-text',class_='mw-content-ltr')
  quotes=body.find_all('ul')
  previous=quotes[0]
  
  num_of_quote=random.randint(0,len(quotes)//2) #about half are duplicates
  
  for quote in quotes:
      if len(quote.find_all('li'))>2:     # gets rid of menus since quotes only contain up to 2 li
          continue
      
      
      if quote.text not in previous.text:  #duplicate uls are avoided
        if num_of_quote==0:
          return quote.text                        #erratic formatting blocks beautiful soup
        else:                                               #iterative method to keep ram to a minimum
          num_of_quote-=1
          previous=quote  
  return Quote_Get('Confusion')
                            

      
      
  
      
      
  
  
  
  
  


      
  
  
  
  
  
  
  
	  
  
  #quotes=soup.find_all('a',class_=re.compile('qt_[1-9]*'))
  #authors=soup.find_all('a',class_=re.compile('qa_[1-9]*'))  
  #full_quote="""{}                            
  #-{}"""                                            
  
  
  
  #full_quotes=[full_quote.format(quote.text,author.text) for quote,author in zip(quotes,authors)]
  
  
  
  #try:
    #quote=random.choice(full_quotes)       #choose a random quote
  #except IndexError:
    #return Quote_Get('confused')
  #return quote
  
  
  





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
    

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message
					

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    try:
                      log(message_text)
                    except UnicodeEncodeError:      #if a 
                      send_message(sender_id,'Only English please')
                      return "ok", 200
				      
						
						
						
						
                    
                    
                    try:
                        
                        
                        reply_text=goodreads_get(pick_random_word(message_text))
                        
                        
                        if reply_text!='':
                          send_message(sender_id,reply_text)
                        
                        
                    except KeyError:
                     send_message(sender_id,'I need text messages')
                    except ValueError:
                     log('Null message')
                        
					
                    
                    
						

                    

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
 
  
  
 
  
 
  
  
  

  
  
  
  


   
