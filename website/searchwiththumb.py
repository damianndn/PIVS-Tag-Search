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
    curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
    curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
    
    # Disable TLS verification
    curl.setopt(pycurl.SSL_VERIFYPEER, False)
    curl.setopt(pycurl.SSL_VERIFYHOST, False)
    
    curl.perform()
    curl.close()
    body = buffer.getvalue().decode('utf-8')
    buffer.close()
    return body

def searchwiththumb():
    url = "https://192.168.10.202/pivision/services/repository"
    user = "administrator"
    pw = "77@NguyenQuyDuc"

    res =  json.loads(perform_ntlm_authenticated_request(url,user,pw))
    return res



def getThumbById(Id,jsonObject):
    return next((obj for obj in jsonObject if obj['Id']==Id),None)


