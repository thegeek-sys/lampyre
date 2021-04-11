import requests
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

print()

def new_api():
    driver = webdriver.Firefox()
    driver.get('https://tempmail.plus/en/#!')

    driver.find_element_by_css_selector("#pre_copy").click()

    driver.get('https://lampyre.io/')
    driver.find_element_by_css_selector(".dropdown").click()
    driver.find_elements_by_css_selector(".dropdown-items li")[1].click()
    driver.find_element_by_name('login').send_keys(Keys.CONTROL, "v")
    driver.find_element_by_name('password').send_keys('11111111')
    driver.find_element_by_name('password_confirm').send_keys('11111111')
    driver.find_element_by_css_selector('button[type="submit"]').click()

    driver.get('https://tempmail.plus/en/#!')

    while True:
        try:
            driver.find_element_by_css_selector('.mail').click()
            break
        except:
            continue

    activation = driver.find_element_by_css_selector('.overflow-auto a').get_attribute('href')
    driver.get(activation)
    driver.get('https://account.lampyre.io/lighthouse/api')
    try:
        api = driver.find_element_by_css_selector('.wrapper-token .text').text
    except:
        driver.find_element_by_css_selector('input[formcontrolname="login"]').send_keys(Keys.CONTROL, "v")
        driver.find_element_by_css_selector('input[formcontrolname="password"]').send_keys('11111111')
        driver.find_element_by_css_selector('button[type="submit"]').click()
        time.sleep(4)
        driver.get('https://account.lampyre.io/lighthouse/api')
        time.sleep(1)
        api = driver.find_element_by_css_selector('.wrapper-token .text').text
    driver.quit()
    return api

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    B_CYAN = '\033[96m'
    B_GREEN = '\033[92m'
    B_WHITE = '\033[97m'
    D_GREEN = '\033[32m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print(bcolors.D_GREEN+'+----------------------------------+')
print('|                                  |')
print('|  '+bcolors.B_WHITE+bcolors.BOLD+'Lampyre query system'+bcolors.ENDC+bcolors.D_GREEN+'            |')
print('|                                  |')
print('|             '+bcolors.B_CYAN+bcolors.BOLD+'by Flavio Sperandeo'+bcolors.ENDC+bcolors.D_GREEN+'  |')
print('+----------------------------------+'+bcolors.ENDC)

if os.path.isfile('api.txt'):
    f = open('api.txt')
    apikey = f.read()
else:
    print('File "api.txt" non trovato')
    print('Crazione file e generazione chiave...')
    f = open('api.txt', 'w')
    apikey = new_api()
    f.write(apikey)
    
f.close()
print('Chiave API attuale: '+bcolors.BOLD+apikey+bcolors.ENDC)

balance = requests.get("https://api.lighthouse.lampyre.io/api/1.0/balance",
            params={"token": apikey})
while balance.status_code != 200 or balance.json()['balance'] == 0:
    print('Chiave API scaduta o non valida')
    print('Generazione nuova chiave in corso...')
    apikey = new_api()
    print('Nuova chiave: '+apikey)
    balance = requests.get("https://api.lighthouse.lampyre.io/api/1.0/balance",
            params={"token": apikey})
    if balance.status_code == 200 and balance.json()['balance'] != 0:
        os.remove("api.txt")
        f = open("api.txt","w")
        f.write(apikey)
        break

print('Photons rimasti: '+bcolors.BOLD+str(balance.json()['balance'])+bcolors.ENDC)
print('1 -> phone')
print('2 -> email')
select = input('> ')

if select == '1':
    req = input('Inserire numero di telefono: ')
    if os.path.isdir('./'+req):
        print('Cartella già esistente')
        quit()
    res = requests.get("https://account.lampyre.io/api/1.6/find/by-token",
                params={"token": apikey, "phone": req})
elif select == '2':
    req = input('Inserire email: ')
    if os.path.isdir('./'+req):
        print('Cartella già esistente')
        quit()
    res = requests.get("https://account.lampyre.io/api/1.6/find/by-token",
                params={"token": apikey, "email": req})
else:
    print('ERROR')
    quit()

path = './'+req+'/'
os.mkdir('./'+req)

request_uuid = res.json()['request_uuid']
first = True
while True:
    res = requests.get("https://account.lampyre.io/api/1.6/find/"+request_uuid+"/by-token",
        params={"token": apikey})
    data = res.json()
    if data['status'] == 2:
        print()
        print('Informazioni trovate!')
        break
    elif data['status'] == 1:
        if first:
            print('In elaborazione', end='')
            first = False
        else:
            print(end='.', flush=True)
        time.sleep(3)
    elif data['status'] == 3:
        print('ERRORE')
        quit()

res = requests.get("https://account.lampyre.io/api/1.6/find/"+request_uuid+"/by-token",
            params={"token": apikey})
data = res.json()
f = open(path+req+".json","w")
f.write(json.dumps(data, indent=4))

for source in data['result']:
    service = source['source']
    source = source['data']
    try:
        source[0]['avatar_url']
        os.mkdir(path+service)
        if type(source[0]['avatar_url']) is list:
            print('Trovate '+str(len(source[0]['avatar_url']))+' avatar in '+service)
            for avatar in source[0]['avatar_url']:
                avatar_jpg = requests.get("https://api.lighthouse.lampyre.io/api/1.0/"+avatar,
                    params={"token": apikey})
                f = open(path+service+'/'+avatar[7:]+'.jpg', 'wb')
                f.write(avatar_jpg.content)
        else:
            print('Trovato 1 avatar in '+service)
            avatar_jpg = requests.get("https://api.lighthouse.lampyre.io/api/1.0/"+source[0]['avatar_url'],
                params={"token": apikey})
            f = open(path+service+'/'+source[0]['avatar_url'][7:]+'.jpg', 'wb')
            f.write(avatar_jpg.content)
    except KeyError:
        pass

print('File creato con successo!')