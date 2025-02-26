from bs4 import BeautifulSoup
import requests
import random
import json
import pprint


li_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?_l=en_US&keywords=Software%20Engineer&location=San%20Francisco%20Bay%20Area&geoId=90000084&f_TPR=r86400&start={}"
test_url = "http://lumtest.com/myip.json"
success = False


config = json.load(open("scrapper-config.json"))
proxies_list = config['proxies_list']
rand_proxy = random.choice(proxies_list)

languages = (config["Languages"])
techs = (config["Techs"])

# Free proxies is failing because I need SSL Verification
# Or the page is being populated by JavaScript?
# BrightData Proxies not working for linkedin. Maybe because of trial account.
# Okay using only an HTTP proxy works but is NOT SAFE
# https://stackoverflow.com/questions/69220126/getting-ssl-certificate-verify-failed-when-using-proxy-with-python-requests
resp = requests.get(li_url.format(25), proxies=config['proxies'], headers=config['headers'])

if(resp.status_code != 200):
    print(f"Failed with {resp.status_code}")
else:
    print(f"Success - {resp.status_code}")
    success = True
    #break

if success:
    soup = BeautifulSoup(resp.text, 'html.parser')
    jobs = soup.find_all("a", class_ = 'base-card__full-link', href=True)
    #print(soup.find('h4', class_='base-search-card__title'))
    #pprint.pprint(resp.text)
    
    #for j in jobs:
    #    print(j['href'])

target_resp = requests.get(jobs[0]['href'], proxies=config['proxies'], headers=config['headers'])

if(target_resp.status_code == 200):
    target_soup = BeautifulSoup(target_resp.text, 'html.parser')
    target_job = target_soup.find('div', class_ = 'show-more-less-html__markup')
    print(target_job.contents)

for i in languages:
    res = target_job.text.find(i)
    if (res != -1):
        print(i)

for i in techs:
    res = target_job.text.find(i)
    if (res != -1):
        print(i)