from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
import urllib.parse
import datetime
import os
from string import punctuation
from urllib3.util import Retry
from requests import Session
from requests.adapters import HTTPAdapter


job_keyword = urllib.parse.quote_plus(input('Job: '))
location_keyword = urllib.parse.quote_plus(input('Location: '))
level = int(input('Seniority Level: ') or 0)  # 0 - Any 1 - Intern 2 - Entry 3 - Associate 4 - Mid-Senior
tpr = input('Time Period: ') or '86400' 
pages = int(input('Pages to scrape: ') or 40) 
# f_TPR=r604800 = this week
# f_TPR=r86400 = 24 hrs ago
# f_TPR=r259200 = 3 days ago
# f_TPR=seconds
li_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?_l=en_US&keywords={}&location={}&f_E={}&f_TPR={}&start={}"
test_url = "http://lumtest.com/myip.json"

#TO-DO remove keywords from config
config = json.load(open("scrapper-config.json"))
proxies_list = json.load(open("proxies-config.json"))
past_time = datetime.datetime.now()

def get_jobs(pageNum):
    s = Session()
    retries = Retry(
        total=3,
        backoff_factor=0.1,
        status_forcelist=[502, 503, 504],
        allowed_methods={'POST'},
    )
    s.mount('https://', HTTPAdapter(max_retries=retries))

    url_string = li_url.format(job_keyword, location_keyword, level, 'r' + tpr, pageNum * 25)
    print(url_string)
    resp = s.get(url_string, proxies=proxies_list['proxies'], headers=config['headers'])
    soup = None
    if(resp.status_code != 200):
        print(f"Failed with {resp.status_code}")
    else:
        soup = BeautifulSoup(resp.text, 'html.parser')

    if soup is None:
        print(f"Failed to Parse {resp.status_code}")
        return []

    s.close()    
    return soup.find_all("div", class_ = 'base-card')

#Init dictionaries
langs_num = {}
techs_num = {}
job_datas = []

lang_casefolded = []
tech_casefolded = []

for l in config["Languages"]:
    lang_casefolded.append(l.casefold())
for t in config["Techs"]:
    tech_casefolded.append(t.casefold())

languages = set(lang_casefolded)
techs = set(tech_casefolded)

for i in config['Languages']:
    langs_num[i.casefold()] = 0

for i in config['Techs']:
    techs_num[i.casefold()] = 0

punc = punctuation.replace('#','').replace('+','').replace('.','').replace('-','')

def get_job_data(j):
    s = Session()
    retries = Retry(
        total=3,
        backoff_factor=0.1,
        status_forcelist=[502, 503, 504],
        allowed_methods={'POST'},
    )
    s.mount('https://', HTTPAdapter(max_retries=retries))

    # Find the link to job page
    ref = j.find('a', class_ = 'base-card__full-link', href=True) 
    target_resp = s.get(ref['href'], proxies=proxies_list['proxies'], headers=config['headers'])

    if(target_resp.status_code == 200):
        target_soup = BeautifulSoup(target_resp.text, 'html.parser')
        target_job = target_soup.find('div', class_ = 'show-more-less-html__markup')
    #TO-DO add date and time of job posted, black list certain companies like Dice, Jobs via Dice
        job_data = {
            #'description': str(target_job).strip(),
            'title': target_soup.find('h1', class_= 'top-card-layout__title').text.strip(),
            'company': target_soup.find('a', class_='topcard__org-name-link').text.strip(),
            'location': target_soup.find('span', class_='topcard__flavor topcard__flavor--bullet').text.strip(),
            # Removed applications because the guest and actual version are not the same. This just causes confusion.
            #'applicants': p.text.strip() if (p := target_soup.find('span', class_='num-applicants__caption')) else '',
            'date': target_soup.find('span', class_='posted-time-ago__text').text.strip(),
            'pay': p.text.strip() if (p := target_soup.find('div', class_='salary compensation__salary')) else '',
            'level': target_soup.find('span', class_= 'description__job-criteria-text description__job-criteria-text--criteria').text.strip(),
            'benefits': p.text.strip() if (p := j.find('span', class_ = 'job-posting-benefits__text')) else '' ,
            'link': ref['href'],
            'langs': [],
            'techs': [],
        }

        target_desc = target_job.text.translate(str.maketrans(punc, ' '*len(punc))).casefold().split()

        #TO-DO solve cases likes Postgres and Postgresql, maybe regex?, or a dictionary {alternate name: real name}
        for i in target_desc:
            if i in languages and i not in job_data['langs']:
                job_data['langs'].append(i)
                langs_num[i] += 1

            if i in techs and i not in job_data['techs']:
                job_data['techs'].append(i)
                techs_num[i] += 1
        s.close()
        return job_data

#TO-DO ignore dup jobs save unique jobs in a database, get total number of jobs and scrape all of them
total_count = 0

for x in range(pages):
    jobs = get_jobs(x)
    count = 0
    total_count += len(jobs)
    print(f'Page {x+1} has {len(jobs)} Jobs')
    for j in jobs:
        job_data = get_job_data(j)            
        count+=1
        #print(f'{count}/{len(jobs)}')
        job_datas.append(job_data)
print(f"{total_count} Jobs scraped for {job_keyword} at {location_keyword}")

#TO-DO arrange data in a table left column is category, top row is the date
lang_df = pd.DataFrame.from_dict(langs_num, orient='index', columns=['Date'])
techs_df = pd.DataFrame.from_dict(techs_num, orient='index', columns=['Date'])

job_datas_json = json.dumps(job_datas)

directory = f"_data/{urllib.parse.unquote_plus(job_keyword)}_{urllib.parse.unquote_plus(location_keyword)}_{datetime.datetime.now().strftime('%x').replace('/', '-')}_{datetime.datetime.now().strftime('%X').replace(':', '-')}"
if os.path.isdir(directory) == False:
    os.makedirs(directory)

with open(f'{directory}/job_datas.json', 'w') as file:
    file.write(str(job_datas_json))

lang_df.to_csv(f'{directory}/langs.csv')
techs_df.to_csv(f'{directory}/techs.csv')

cur_time = datetime.datetime.now() - past_time
print(cur_time)