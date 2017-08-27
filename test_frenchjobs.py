import requests
import json
from test_frenchjoblisting import find_job_ids 
import re
from datetime import datetime,timedelta
import csv
import codecs
from geopy import geocoders
from db_insert import insert_jobs
import psycopg2
import re

domain_url = "https://sjobs.brassring.com/TgNewUI/Search/Ajax/JobDetails"

cookies = {
    'CoreID6': '39950272970615011695518&ci=51290000|25121_5051',
    'tg_rft_mvc': 'xB3c3Gf8FbtKbpM-E_aDitJgTjJUAxHSchM7Asu8sabcPQA667aI3v4wGFsdrwlAk4eXVhYfflm69RLwGij5o3FXdQCDNAbtKLCX5kjxyb3dG7lnkoQiueWIRToRgOigLusBNZIVVkWN_R3HmuC-Yg2',
    'cmTPSet': 'Y',
    'tg_rft': '^aK3hB3UzVAplgXSlcp4EnjRSbZH+FUrHTDOG+zlmyUOyZwQSN6m2M5wHf5NFTB7494Ama+wI+uj5OurRN/5JZvggRYxNAv9bnl20/oIJQvA=',
    'tg_session_25121_5051': '^KRtWTAtRi8qx6BzFSIKwgNoHbg4OIR4vumIwPIuLn5ZoUIqSafcxhAJe8XZqB77zTC9VD9RPi8CXYtEx7vSK4kTeWHEoYv9sZS7jVS31Vmw=',
    'tg_session': '^KRtWTAtRi8qx6BzFSIKwgNoHbg4OIR4vumIwPIuLn5ZoUIqSafcxhAJe8XZqB77zTC9VD9RPi8CXYtEx7vSK4kTeWHEoYv9sZS7jVS31Vmw=',
    'CoreM_State': '31~-1~-1~-1~-1~3~3~5~3~3~7~7~|~~|~~|~~|~||||||~|~~|~~|~~|~~|~~|~~|~~|~',
    'CoreM_State_Content': '6~|~4ED11A15A8465729~0F4743437AF83043~C7F791148061836A~E4928F52FDDDEF0A~27EEC91DF80E35AD~|~0~1~2~3~4',
    '51290000|25121_5051_clogin': 'l=1503075531&v=1&e=1503078170427',
}

headers = {
    'Origin': 'https://sjobs.brassring.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://sjobs.brassring.com/TGnewUI/Search/Home/Home?partnerid=25121&siteid=5051',
    'Connection': 'keep-alive',
}

data = '{"partnerId":"25121","siteId":"5051","jobid":"1177223","configMode":"","jobSiteId":"5060"}'

#data = '{"partnerId":"25121","siteId":"5051","jobid":"%s","configMode":"","jobSiteId":"5051"}'

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
    return datetime.strptime(date, '%m/%d/%Y')

def get_lat_lon(city, province):
    g = geocoders.GoogleV3(api_key='AIzaSyCZsl42Ue3KaTlNjrhk3WJG1475pugV42g')
    location = None
    location = g.geocode("{0} {1} Canada".format(city, province), timeout=10)
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
    
def get_job_detail(jobs, cookies=cookies, headers=headers, data=data, url=domain_url ):
    root_url = 'https://sjobs.brassring.com/TGnewUI/Search/Home/Home?partnerid=25121&siteid=5051#jobDetails='
    conn = psycopg2.connect("dbname='jobdb' user='jobmin' password='f1d3r!@#' host='www.jobminister.ca'")
    for job in jobs:
        print("job Id",job)
        result = {}
        data_with_job_id = data%str(job)
        response = requests.post(url, headers=headers, cookies=cookies, data=data_with_job_id)
        resonse_content = json.loads(response.content.decode('utf8'))
        content_value = job_detail = resonse_content["ServiceResponse"]["Jobdetails"]
        if content_value != None:
            try:
                job_detail = resonse_content["ServiceResponse"]["Jobdetails"]['JobDetailQuestions']
                result["job_description"] = job_detail[7]['AnswerValue']
                result["job_title"] = cleanhtml(job_detail[9]['AnswerValue'])
                result["job_type"] = job_detail[10]['AnswerValue']
                result["province"] = province_initial(job_detail[11]['AnswerValue']) if (len(job_detail)>12) else "N/A"
                result["address"] = re.sub(r'\d+[- ]?',"",job_detail[8]['AnswerValue'])
                result["last_apply_date"] = string_to_datetime(job_detail[12]['AnswerValue']) if (len(job_detail)>12) else datetime.now() + timedelta(days=30)
                result["department_name"] = job_detail[6]['AnswerValue']
                result["last_updated"] = string_to_datetime(job_detail[5]['AnswerValue'])
                lat , lon, postal_code = get_lat_lon(result["address"],result["province"])
                result["lat"] = lat
                result["lon"] = lon
                result["postal_code"] = postal_code
                result["web_link"] = root_url + job
                print(job_detail[8]['AnswerValue'],job_detail[11]['AnswerValue'])
                print(result["lat"],result["lon"])
                print (result["postal_code"])

                #insert_jobs(result,conn)            
            except Exception as e:
                print("exception",e)

job_id_list = find_job_ids()
get_job_detail(job_id_list)