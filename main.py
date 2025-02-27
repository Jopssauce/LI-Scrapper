from bs4 import BeautifulSoup
import requests
import random
import json
import pandas as pd


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

langs_num = {}
techs_num = {}
job_datas = []

#Init dictionaries
for i in config['Languages']:
    langs_num[i] = 0

for i in config['Techs']:
    techs_num[i] = 0

count = 0
for j in jobs:
    target_resp = requests.get(j['href'], proxies=config['proxies'], headers=config['headers'])

    if(target_resp.status_code == 200):
        target_soup = BeautifulSoup(target_resp.text, 'html.parser')
        target_job = target_soup.find('div', class_ = 'show-more-less-html__markup')

        job_data = {
            'description': '',
            'title': target_soup.find('h1', class_= 'top-card-layout__title').text.strip(),
            'company': target_soup.find('a', class_='topcard__org-name-link').text.strip(),
            'location': target_soup.find('span', class_='topcard__flavor topcard__flavor--bullet').text.strip(),
            'pay': p.text.strip() if (p := target_soup.find('div', class_='salary compensation__salary')) else '',
            'level': target_soup.find('span', class_= 'description__job-criteria-text description__job-criteria-text--criteria').text.strip(),
            'langs': [],
            'techs': [],
        }

        for i in languages:
            res = target_job.text.lower().find(i.lower())
            if (res != -1):
                job_data['langs'].append(i)
                langs_num[i] += 1

        for i in techs:
            res = target_job.text.lower().find(i.lower())
            if (res != -1):
                job_data['techs'].append(i)
                techs_num[i] += 1

        count+=1
        print(f'{count}/{len(jobs)}')
        job_datas.append(job_data)


        lang_df = pd.DataFrame.from_dict(langs_num, orient="index")
        techs_df = pd.DataFrame.from_dict(techs_num, orient="index")

        job_datas_json = json.dumps(job_datas)

        with open('job_datas.json', 'w') as file:
            file.write(str(job_datas_json))
            #json.dumps(job_datas_json, file, indent=4)

        lang_df.to_csv('langs.csv')
        techs_df.to_csv('techs.csv')