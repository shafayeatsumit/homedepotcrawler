import requests
import json
from jobid import find_job_ids 
import re
from datetime import datetime,timedelta
import csv
import codecs
from geopy import geocoders
from db_insert import insert_jobs
import psycopg2
import re
import time 
from db_update import update_jobs


domain_url = "https://sjobs.brassring.com/TgNewUI/Search/Ajax/JobDetails"
#result = re.search(r'[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]',location.address)

cookies = {
    'CoreID6': '19502957485815011231250&ci=51290000|25121_5051',
    'tg_session_25121_5051': '^l2OoFdgFD0vVhfx0PvjJfY3TVeXISl5FrRUl_slp_rhc_ZYJMvHtKJdtusuqPNQLQLsAAfX1JNzWlOt9H4cHo5rcp5ckUUvjXA1mgoQRK4kAgO_slp_rhc_88HY=',
    'tg_session': '^l2OoFdgFD0vVhfx0PvjJfY3TVeXISl5FrRUl_slp_rhc_ZYJMvHtKJdtusuqPNQLQLsAAfX1JNzWlOt9H4cHo5rcp5ckUUvjXA1mgoQRK4kAgO_slp_rhc_88HY=',
    'tg_rft_mvc': 'AYU7NujyPLGRtombdvGhU2iQqEiZngMC8rn9byLwSqMROOSvpJW_A0NGXsPIa2o0KI0zLhAsCvGkmsdkAgRCB5aJlkju0B53Pm8Bdsg7i_JDQqAXoGJ-snaAj3IfzCMCfKT4wtmii7zuT1pRYMHD-w2',
    'cmTPSet': 'Y',
    'tg_rft': '^aK3hB3UzVAplgXSlcp4EnjRSbZH+FUrHTDOG+zlmyUOyZwQSN6m2M5wHf5NFTB7494Ama+wI+uj5OurRN/5JZvggRYxNAv9bnl20/oIJQvA=',
    'CoreM_State': '39~-1~-1~-1~-1~3~3~5~3~3~7~7~|~~|~~|~~|~||||||~|~~|~~|~~|~~|~~|~~|~~|~',
    'CoreM_State_Content': '6~|~4ED11A15A8465729~0F4743437AF83043~C7F791148061836A~1B4F26D1A3375B95~F7E816A8F261C218~CF0BC188EF1159D7~|~0~1~2~3~4~5',
    '51290000|25121_5051_clogin': 'l=1502179687&v=1&e=1502182296884',
}

headers = {
    'Origin': 'https://sjobs.brassring.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://sjobs.brassring.com/TGnewUI/Search/Home/Home?partnerid=25121&siteid=5051',
    'Connection': 'keep-alive',
}

data = '{"partnerId":"25121","siteId":"5051","jobid":"%s","configMode":"","jobSiteId":"5051"}'
#data = '{"partnerId":"25121","siteId":"5051","jobid":"%s","configMode":"","jobSiteId":"5060"}'

def province_initial(province_name):
    provinces = {
        "Alberta" : "1",
        "Manitoba" : "3",
        "British Columbia" : "2",
        "New Brunswick" : "4",
        "Newfoundland" : "5",
        "Nova Scotia" : "7",
        "Northwest Territories" : "6",
        "Nunavut" : "8",
        "Ontario" : "9",
        "Prince Edward Island" : "13",
        "Quebec" : "10",
        "Québec" : "10",
        "Saskatchewan" : "11",
        "Yukon"  : "12"
    }
    return provinces[province_name.strip()]    


def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def string_to_datetime(date): 
    try:
        result = datetime.strptime(date, '%m/%d/%Y')
    except Exception as e:
        result = datetime.now() + timedelta(days=60)
    return result

def get_lat_lon(address):
    g = geocoders.GoogleV3(api_key='AIzaSyCZsl42Ue3KaTlNjrhk3WJG1475pugV42g')
    location = None
    location = g.geocode("home depot Canada {0}".format(address), timeout=20)
    if location:
        lat, lon = location.latitude, location.longitude
        postal_code_regex = re.search(r'[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d',location.address)
        if postal_code_regex:
            postal_code = postal_code_regex.group(0)
        else:
            postal_code = None    
        return lat,lon,postal_code

    else:
        return None, None, None  
def parser(resonse_content, job):
    root_url = 'https://sjobs.brassring.com/TGnewUI/Search/Home/Home?partnerid=25121&siteid=5051#jobDetails='
    conn = psycopg2.connect("dbname='jobdb' user='jobmin' password='f1d3r!@#' host='www.jobminister.ca'")
    result = {}
    try:
        job_detail = resonse_content['JobDetailQuestions']
        result["job_description"] = job_detail[7]['AnswerValue']
        result["job_title"] = cleanhtml(job_detail[9]['AnswerValue'])
        result["job_type"] = job_detail[10]['AnswerValue']
        result["province"] = province_initial(job_detail[11]['AnswerValue']) if (job_detail[11]["QuestionName"]=='Province') else "N/A"
        result["raw_address"] = job_detail[8]['AnswerValue']
        result["address"] = re.sub(r'\d+[- ]?',"",job_detail[8]['AnswerValue'])
        result["last_apply_date"] = string_to_datetime(job_detail[12]['AnswerValue']) if (job_detail[12]["QuestionName"] == 'Last Date to Apply') else datetime.now() + timedelta(days=30)
        result["department_name"] = job_detail[6]['AnswerValue']
        result["last_updated"] = string_to_datetime(job_detail[5]['AnswerValue'])
        lat , lon, postal_code = get_lat_lon(result["raw_address"])
        result["lat"] = lat
        result["lon"] = lon
        result["postal_code"] = postal_code
        result["web_link"] = root_url + job
        print("raw address", result["raw_address"])

        #update_jobs(result,conn)
        insert_jobs(result,conn)            
    except Exception as e:
        print("exception",e) 
           
def get_job_detail(jobs, cookies=cookies, headers=headers, data=data, url=domain_url ):

    for job in jobs:
        print("job Id",job)
        
        data_with_job_id = data%str(job)
        try:
            response = requests.post(url, headers=headers, cookies=cookies, data=data_with_job_id, timeout=15)
            resonse_content = json.loads(response.content.decode('utf8'))
            content_value = resonse_content["ServiceResponse"]["Jobdetails"]
        except Exception as e:
            print("exception timeout ",e)
            
        if content_value == None :
            try:
                response = requests.post(url, headers=headers, cookies=cookies, data = '{"partnerId":"25121","siteId":"5051","jobid":"%s","configMode":"","jobSiteId":"5060"}'%job, timeout=15)
                resonse_content = json.loads(response.content.decode('utf8'))
                content_value = resonse_content["ServiceResponse"]["Jobdetails"]
            except Exception as e:
                print ("connection time out exception",e)
        
        if content_value :
            parser(content_value, job)
        else: 
            print("Null")

job_id_list = find_job_ids()

get_job_detail(job_id_list)



