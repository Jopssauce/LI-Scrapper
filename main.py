from bs4 import BeautifulSoup
import requests
import random
import json
import pprint


li_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?_l=en_US&keywords=Software%20Engineer&location=San%20Francisco%20Bay%20Area&geoId=90000084&f_TPR=r86400&start={}"
target_url='https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Python%20%28Programming%20Language%29&location=Las%20Vegas%2C%20Nevada%2C%20United%20States&geoId=100293800&currentJobId=3415227738&start={}'
test_url = "http://lumtest.com/myip.json"
success = False


config = json.load(open("scrapper-config.json"))
proxies_list = config['proxies_list']
#for _ in proxies_list: 
rand_proxy = random.choice(proxies_list)

# Free proxies is failing because I need SSL Verification
# Or the page is being populated by JavaScript?
# BrightData Proxies not working for linkedin. Maybe because of trial account.
# Okay using only an HTTP proxy works
# https://stackoverflow.com/questions/69220126/getting-ssl-certificate-verify-failed-when-using-proxy-with-python-requests
resp = requests.get(li_url.format(25), proxies=config['proxies'], headers=config['headers'])

if(resp.status_code != 200):
    print(f"Failed with {resp.status_code} {rand_proxy}")
else:
    print(f"Success - {rand_proxy} - {resp.status_code}")
    success = True
    #break

if success:
    soup = BeautifulSoup(resp.raw, 'html.parser')
    #print(soup.find('h4', class_='base-search-card__title'))
    #pprint.pprint(resp.text)
    print(resp.text)