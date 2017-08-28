import requests
import json
from jobid import find_job_ids 
import re
from datetime import datetime,timedelta
import csv
import codecs
from geopy import geocoders

domain_url = "https://sjobs.brassring.com/TgNewUI/Search/Ajax/JobDetails"



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
        result = datetime.now()
    return result

def get_lat_lon(city, province):
    g = geocoders.GoogleV3(api_key='AIzaSyCZsl42Ue3KaTlNjrhk3WJG1475pugV42g')
    location = None
    location = g.geocode("{0} {1} Canada".format(city, province), timeout=10)
    if location:
        print("Location is:", location.latitude, location.longitude)
        lat, lon = location.latitude, location.longitude
        return lat,lon
    else:
        return None, None  
    
def get_job_detail(job_id, cookies=cookies, headers=headers, data=data, url=domain_url ):
    result = {}
    data_with_job_id = data%str(job_id)
    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data_with_job_id, timeout=15)
        resonse_content = json.loads(response.content.decode('utf8'))
        content_value = resonse_content["ServiceResponse"]["Jobdetails"]
    
    except Exception as e:
        print("exception ",e)

    if content_value == None :
        try:
            response = requests.post(url, headers=headers, cookies=cookies, data = '{"partnerId":"25121","siteId":"5051","jobid":"%s","configMode":"","jobSiteId":"5060"}'%job_id, timeout=15)
            resonse_content = json.loads(response.content.decode('utf8'))
            content_value = resonse_content["ServiceResponse"]["Jobdetails"]
        except Exception as e:
            print ("connection time out exception",e)

    if content_value:
        print("inside value")
        job_detail = resonse_content["ServiceResponse"]["Jobdetails"]['JobDetailQuestions']
        result["job_description"] = job_detail[7]['AnswerValue']
        result["title"] = cleanhtml(job_detail[9]['AnswerValue'])
        result["job_type"] = job_detail[10]['AnswerValue']
        result["province"] = province_initial(job_detail[11]['AnswerValue']) if (len(job_detail)>=12) else "N/A"
        result["address"] = job_detail[8]['AnswerValue']
        result["last_apply_date"] = string_to_datetime(job_detail[12]['AnswerValue']) if (len(job_detail)>=13) else datetime.now() + timedelta(days=30)
        result["department_name"] = job_detail[6]['AnswerValue']
        result["last_updated"] = string_to_datetime(job_detail[5]['AnswerValue'])
        print (result["province"])
        #print (result["job_description"])
        

get_job_detail("1189138")



