#import necessary libraries
import asyncio
import aiohttp
import pycurl
import json
import time
from io import BytesIO
import re
import pprint
from .models import data_sources
from . import db
from sqlalchemy.inspection import inspect
import ast
from concurrent.futures import ThreadPoolExecutor
import pyodbc


def perform_ntlm_authenticated_request(url, username, password):
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.USERPWD, f"{username}:{password}")
    curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_NTLM)
    curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
    
    # Disable TLS verification
    curl.setopt(pycurl.SSL_VERIFYPEER, False)
    curl.setopt(pycurl.SSL_VERIFYHOST, False)
    
    curl.perform()
    curl.close()
    body = buffer.getvalue().decode('utf-8')
    buffer.close()
    return body

def findFolders(listFolder,out):
    #out = []
    #print("def was call for listFolder ID = " + str(listFolder))
    out.append(listFolder)
    username = "administrator"
    password = "77@NguyenQuyDuc"
    #for i in range(len(listFolder)):
    url = "https://192.168.10.202/pivision/utility/api/v1/folders?folderid="+str(listFolder)
    childfolder_json = json.loads(perform_ntlm_authenticated_request(url,username,password))
    for Id in range(len(childfolder_json["Items"])):
        #print("loop in "+str(Id))
        #out.append(childfolder_json["Items"][Id]["Id"])
        #print(childfolder_json["Items"][Id]["Id"])
        if childfolder_json["Items"][Id]["HasChildren"] == True:
            findFolders(childfolder_json["Items"][Id]["Id"],out)
    #print("done loop in")
    return None

def findDislays(folderId,display_id):
    username = "administrator"
    password = "77@NguyenQuyDuc"
    for Id in folderId:
        url = f"https://192.168.10.202/pivision/utility/api/v1/displays?folderid={Id}"
        display_json = json.loads(perform_ntlm_authenticated_request(url,username,password))
        for k in range(len(display_json["Items"])):
            display_id.append(display_json["Items"][k]["Id"])
    return None

def search_wildcards(inputDict, keywords):
    keywords = '*'+keywords+'*'
    regexPattern = re.compile(keywords.replace('*', '.*'),re.IGNORECASE)
    print(regexPattern)
    res = dict(filter(lambda item: regexPattern.match(item[0]), inputDict.items()))
    return res

def get_data(url,username,password):
    temp_source = []
    display_dict = {}
    display_json = json.loads(perform_ntlm_authenticated_request(url,username,password))
    for symbol in range(len(display_json["Display"]["Symbols"])):
        if "DataSources" in display_json["Display"]["Symbols"][symbol]:
            temp_source.append(display_json["Display"]["Symbols"][symbol]["DataSources"])
        display_dict[str(display_json["Display"]["Id"])+'/'+display_json["Display"]["Name"]] = temp_source
    
    return display_dict

def mergeDictionary(originList):
    mergedDict = dict()
    for member in originList:
        for display_name, data_sources in member.items():
            if display_name not in mergedDict:
                mergedDict[display_name] = data_sources
            else:
                mergedDict[display_name].extend(data_sources)
    return mergedDict

def dictInversion(originDict):
    inversedDict = {}
    for k, v in originDict.items():
        if v != []:
            for x in v:
                if isinstance(x, list):
                    for item in x:
                        inversedDict.setdefault(item, set()).add(k)
                else:
                    inversedDict.setdefault(x, set()).add(k)
    return inversedDict 

# Function to safely convert string to list using ast.literal_eval
def convert_to_list(value):
    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        # If the value cannot be converted, return it as is
        return value

def convert_to_set(value):
    try:
        return {ast.literal_eval(value)}
    except (SyntaxError, ValueError):
        # If the value cannot be converted, return it as is
        return {value}

async def memify():
    start_time = time.time()
    listFolder = ""
    out = []
    username="administrator"
    password="77@NguyenQuyDuc"
    findFolders(listFolder,out)
    #print("Exec time lasted %s seconds" %(time.time()-start_time))

    display_id = []
    allFolders = out
    findDislays(allFolders,display_id)
    display_id.sort()
    #print("Exec time lasted %s seconds" %(time.time()-start_time))
    
    
    urls = [f"https://192.168.10.202/pivision/utility/api/v1/displays/{graphic}/export" for graphic in display_id]
    
    
    #start_time = time.time()
    dis_to_data_list = []

    with ThreadPoolExecutor() as executor:
       for res in executor.map(get_data,urls,[username]*len(urls),[password]*len(urls)):
            dis_to_data_list.append(res)

    #print(len(dis_to_data_list))
    #print("The act of querying all urls is %s seconds" %{time.time()-start_time})

    merged_dict = mergeDictionary(dis_to_data_list)
    inverse = dictInversion(merged_dict)
    print("The dictionary has " + str(len(inverse)) + " entries.")


    if data_sources.query.count() != 0:
        # Clear existing data from the table
        db.session.query(data_sources).delete()

    sources_to_add = [data_sources(name=key,display=str(value)) for key, value in inverse.items()]

    #add all new data sources
    db.session.add_all(sources_to_add)
    db.session.commit()

    


    return str(len(inverse))

