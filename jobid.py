import requests
import json
import math

domain_url = "https://sjobs.brassring.com/TgNewUI/Search/Ajax/ProcessSortAndShowMoreJobs"
cookies = {
    'CoreID6': '19502957485815011231250&ci=51290000|25121_5051',
    'tg_session_25121_5051': '^rTyCC9j2EL4sl_slp_rhc_Bb2JDXUY_slp_rhc_Tyqm9fANqrbCF8rfYeyGtLV6FO6iB73AlIccU4fxzJOYjWa8_slp_rhc_kUKhl7kYdENvDMxgMptQrdzMQ1bngCU6erM=',
    'tg_session': '^rTyCC9j2EL4sl_slp_rhc_Bb2JDXUY_slp_rhc_Tyqm9fANqrbCF8rfYeyGtLV6FO6iB73AlIccU4fxzJOYjWa8_slp_rhc_kUKhl7kYdENvDMxgMptQrdzMQ1bngCU6erM=',
    'tg_rft': '^aK3hB3UzVAplgXSlcp4EnjRSbZH+FUrHTDOG+zlmyUOyZwQSN6m2M5wHf5NFTB7494Ama+wI+uj5OurRN/5JZvggRYxNAv9bnl20/oIJQvA=',
    'tg_rft_mvc': 'ELvmKaSEs9tHMR4LfHwLGcf-vdcYGsboUBCE257e1G_JA2xmrBrjEjCu5pxQv-IrGVOLQYWgS4h00zR3Kz2EjERfwpIegXHT9PlBWk_bK7kNUK9GSG1dJIeDvrq6UXwUVvFW2Hw_thfenkAec8VN6Q2',
    'cmTPSet': 'Y',
    'CoreM_State': '39~-1~-1~-1~-1~3~3~5~3~3~7~7~|~~|~~|~~|~||||||~|~~|~~|~~|~~|~~|~~|~~|~',
    'CoreM_State_Content': '6~|~0F4743437AF83043~4ED11A15A8465729~C7F791148061836A~1B4F26D1A3375B95~F7E816A8F261C218~CF0BC188EF1159D7~|~0~1~2~3~4~5',
    '51290000|25121_5051_clogin': 'l=1502539901&v=1&e=1502542336910',
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

default_page_number = "1"

data = '{"partnerId":"25121","siteId":"5051","keyword":"","location":"",\
		"keywordCustomSolrFields":"AutoReq,JobTitle,FORMTEXT9","locationCustomSolrFields":"FORMTEXT2,FORMTEXT4,\
		Location","Latitude":0,"Longitude":0,"facetfilterfields":{"Facet":[]},"powersearchoptions":\
		{"PowerSearchOption":[{"VerityZone":"FORMTEXT9","Type":"single-select","OptionCodes":[]},\
		{"VerityZone":"FORMTEXT1","Type":"radio","OptionCodes":[]},\
		{"VerityZone":"FORMTEXT2","Type":"single-select","OptionCodes":[]},\
		{"VerityZone":"FORMTEXT3","Type":"single-select","OptionCodes":[]},\
		{"VerityZone":"FORMTEXT4","Type":"single-select","OptionCodes":[]},\
		{"VerityZone":"Department","Type":"select","OptionCodes":[]},\
		{"VerityZone":"LastUpdated","Type":"date","Value":null},\
		{"VerityZone":"languagelist","Type":"multi-select","OptionCodes":["11111111"]}]},\
		"SortType":"score","pageNumber":%s,"encryptedSessionValue":"^rTyCC9j2EL4sl_slp_rhc_Bb2JDXUY_slp_rhc_Tyqm9fANqrbCF8rfYeyGtLV6FO6iB73AlIccU4fxzJOYjWa8_slp_rhc_kUKhl7kYdENvDMxgMptQrdzMQ1bngCU6erM="}'

data_page_one = data%default_page_number

response = requests.post(domain_url, headers=headers, cookies=cookies, data=data_page_one)
resonse_content = json.loads(response.content.decode('utf8'))
#job_id = resonse_content["Jobs"]["Job"][0]["Questions"][0]["Value"]
number_of_jobs = resonse_content["JobsCount"]
number_of_pages = math.ceil(number_of_jobs / 50 )

def find_job_ids(cookies=cookies, headers=headers, data=data, pages=number_of_pages, url=domain_url):
	id_list = []
	for page in range(1,5):
		print(page)
		data_with_page_number =data%page
		response = requests.post(domain_url, headers=headers, cookies=cookies, data=data_with_page_number)
		resonse_content = json.loads(response.content.decode('utf8'))
		jobs = resonse_content["Jobs"]["Job"]
		job_ids = [job["Questions"][0]["Value"] for job in jobs]
		id_list.extend(job_ids)

	return id_list
		

