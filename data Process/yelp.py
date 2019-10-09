import requests
import json
import time

#get data from yelp api and store in json file

MY_API_KEY = ""
headers = {"Authorization": "Bearer {api_key}".format(api_key=MY_API_KEY)}
url = "https://api.yelp.com/v3/businesses/search"

parameters = {
    "term": 'restaurants',
    "location": 'manhattan',
    "categories":'korean',
    "limit":50,
    "offset":0
}

categories=['pizza','chinese','mexican','italian','japanese']
infos=[]

for cate in categories:
	parameters['offset']=0
	parameters['categories']=cate
	while parameters['offset']+parameters['limit']<1001:
		response = requests.get(url, headers=headers, params=parameters)
	
		for r in response_info:
			rest_info={}
			rest_info['id']=r['id']
			del r['id']
			rest_info["name"] = r["name"]
			info = {}
			info["rating"] = r["rating"] if r["rating"] else None
			info["location"] = r["location"]["display_address"]
			info["zip_code"] = r["location"]["zip_code"] if r["location"]["zip_code"] else None
			info['categories']=cate
			info["review_count"] = r["review_count"]
			info["coordinates"] = r["coordinates"]
			rest_info['insertedAtTimestamp']=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
			rest_info['info']=info
			infos.append(rest_info)
		
		parameters['offset']+=50
		
# print(len(infos))

with open('restaurant.json','w') as f:
	f.write(json.dumps(infos,indent=2)) 