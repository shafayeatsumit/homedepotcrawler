import requests
import json
import math

domain_url = "https://sjobs.brassring.com/TgNewUI/Search/Ajax/ProcessSortAndShowMoreJobs"

cookies = {
    'CoreID6': '39950272970615011695518&ci=51290000|25121_5051',
    'tg_rft_mvc': 'xB3c3Gf8FbtKbpM-E_aDitJgTjJUAxHSchM7Asu8sabcPQA667aI3v4wGFsdrwlAk4eXVhYfflm69RLwGij5o3FXdQCDNAbtKLCX5kjxyb3dG7lnkoQiueWIRToRgOigLusBNZIVVkWN_R3HmuC-Yg2',
    'cmTPSet': 'Y',
    'tg_rft': '^aK3hB3UzVAplgXSlcp4EnjRSbZH+FUrHTDOG+zlmyUOyZwQSN6m2M5wHf5NFTB7494Ama+wI+uj5OurRN/5JZvggRYxNAv9bnl20/oIJQvA=',
    'tg_session_25121_5051': '^KRtWTAtRi8qx6BzFSIKwgNoHbg4OIR4vumIwPIuLn5ZoUIqSafcxhAJe8XZqB77zTC9VD9RPi8CXYtEx7vSK4kTeWHEoYv9sZS7jVS31Vmw=',
    'tg_session': '^KRtWTAtRi8qx6BzFSIKwgNoHbg4OIR4vumIwPIuLn5ZoUIqSafcxhAJe8XZqB77zTC9VD9RPi8CXYtEx7vSK4kTeWHEoYv9sZS7jVS31Vmw=',
    'CoreM_State': '31~-1~-1~-1~-1~3~3~5~3~3~7~7~|~~|~~|~~|~||||||~|~~|~~|~~|~~|~~|~~|~~|~',
    'CoreM_State_Content': '6~|~4ED11A15A8465729~0F4743437AF83043~C7F791148061836A~E4928F52FDDDEF0A~27EEC91DF80E35AD~|~0~1~2~3~4',
    '51290000|25121_5051_clogin': 'l=1503075531&v=1&e=1503078190208',
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

data = '{"partnerId":"25121","siteId":"5051","keyword":"","location":"",\
		"keywordCustomSolrFields":"AutoReq,JobTitle,FORMTEXT9",\
		"locationCustomSolrFields":"FORMTEXT2,FORMTEXT4,Location","Latitude":0,"Longitude":0,\
		"facetfilterfields":{"Facet":[]},\
		"powersearchoptions":{"PowerSearchOption":[{"VerityZone":"FORMTEXT9","Type":"single-select","OptionCodes":[]},\
		{"VerityZone":"FORMTEXT1","Type":"radio","OptionCodes":[]},{"VerityZone":"FORMTEXT2","Type":"single-select","OptionCodes":[]},\
		{"VerityZone":"FORMTEXT3","Type":"single-select","OptionCodes":[]},{"VerityZone":"FORMTEXT4","Type":"single-select","OptionCodes":[]},\
		{"VerityZone":"Department","Type":"select","OptionCodes":[]},{"VerityZone":"LastUpdated","Type":"date","Value":null},\
		{"VerityZone":"languagelist","Type":"multi-select","OptionCodes":["3084"]}]},\
		"SortType":"score","pageNumber":%s,\
		"encryptedSessionValue":"^KRtWTAtRi8qx6BzFSIKwgNoHbg4OIR4vumIwPIuLn5ZoUIqSafcxhAJe8XZqB77zTC9VD9RPi8CXYtEx7vSK4kTeWHEoYv9sZS7jVS31Vmw="}'

requests.post('https://sjobs.brassring.com/TgNewUI/Search/Ajax/ProcessSortAndShowMoreJobs', headers=headers, cookies=cookies, data=data)

data_page_one = data%1

response = requests.post(domain_url, headers=headers, cookies=cookies, data=data_page_one)
resonse_content = json.loads(response.content.decode('utf8'))
#job_id = resonse_content["Jobs"]["Job"][0]["Questions"][0]["Value"]
number_of_jobs = resonse_content["JobsCount"]
print(number_of_jobs)
number_of_pages = math.ceil(number_of_jobs / 50 )

def find_job_ids(cookies=cookies, headers=headers, data=data, pages=number_of_pages, url=domain_url):
	id_list = []
	for page in range(1,pages):
		print("page number ==>",page)
		data_with_page_number =data%page
		response = requests.post(domain_url, headers=headers, cookies=cookies, data=data_with_page_number)
		resonse_content = json.loads(response.content.decode('utf8'))
		jobs = resonse_content["Jobs"]["Job"]
		job_ids = [job["Questions"][0]["Value"] for job in jobs]
		id_list.extend(job_ids)

	return id_list
		

