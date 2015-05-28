import os
import sys
import time
from urllib import FancyURLopener
import urllib2
import simplejson

# useful search info here:
# https://developers.google.com/image-search/v1/jsondevguide

# Define search term
searchTerm = "cute"

# Replace spaces ' ' in search term for '%20' in order to comply with request
searchTerm = searchTerm.replace(' ','%20')


# Start FancyURLopener with defined version
class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
myopener = MyOpener()

# Set count to 0
count= 0

for i in range(0,1):
    # Notice that the start changes for each iteration in order to request a new set of images for each loop
    url = ('https://ajax.googleapis.com/ajax/services/search/images?' + 'v=1.0&q='+searchTerm+'&start='+str(i*4)+'&userip=MyIP'+'&imgtype=lineart')
    print url
    request = urllib2.Request(url, None, {'Referer': 'testing'})
    response = urllib2.urlopen(request)
    
    # Get results using JSON
    results = simplejson.load(response)
    data = results['responseData']
    dataInfo = data['results']
    
    # Iterate for each result and get unescaped url
    for myUrl in dataInfo:
        count = count + 1
        print myUrl['unescapedUrl']
        ending = myUrl['url'].split('.')[-1]
        
        myopener.retrieve(myUrl['unescapedUrl'],str(count)+"." + ending)
    
    # Sleep for one second to prevent IP blocking from Google
    time.sleep(1)