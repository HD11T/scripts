from flask import Flask, request
import asyncio
import json
import requests
from datetime import datetime
app = Flask(__name__)
class ZaloAPI:
    def __init__(self, api_domain, api_type, api_version):
        self.authDomain = api_domain
        self.apiType = api_type
        self.apiVersion = api_version

    async def get_login_info(self, imei, cookie, language="vi", local_ip="", screen_size=None, info="", source_install=None, additional_params=None, is_new=0):
        url = f"{self.authDomain}/api/login/getLoginInfo"
        params = {
            'imei': imei,
            'computer_name': "web",
            'language': language,
            'ts': int(datetime.utcnow().timestamp() * 1000)
        }
        
        HEADERS = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "sec-ch-ua": "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Linux\"",
            "origin": "https://chat.zalo.me",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://chat.zalo.me/",
            "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        }

        phanhoiapi = requests.get(url, headers=HEADERS, params=params, cookies=cookie).json()
        return phanhoiapi

async def main(imei, cookie):
    api = ZaloAPI("https://wpa.chat.zalo.me", "30", "637")
    phanhoiapi = await api.get_login_info(imei, cookie)
    
    if phanhoiapi['error_code'] == 0:
        zpw_enk = phanhoiapi['data']['zpw_enk']
        phone = phanhoiapi['data']['phone_number']
        semid_2 = phanhoiapi['data']['send2me_id']
        
        data = {
            'error_code': 0,
            'data': {
                'secret_key': zpw_enk,
                'send2me_id': semid_2,
                'phone_number': phone
            }
        }
        return data
    else:
        data = {
            'error_code': phanhoiapi['error_code'],
            'error_message': phanhoiapi['error_message']
        }
        return data

@app.route('/hytermix/zalo/login', methods=['GET'])
def get_cookie():
    tatcacookies = request.headers.get('Cookie')
    cookie_dict = {}

    if tatcacookies:
        cookies = tatcacookies.split("; ")
        for cookie in cookies:
            key, value = cookie.split("=", 1)
            cookie_dict[key] = value

    imei = request.args.get('imei')
    if imei is None or not cookie_dict:
        return {
            'error_code': 403,
            'error_message': "Login Failed. No Cookies and IMEI provided!"
        }
    data = asyncio.run(main(imei, cookie_dict))
    if data.get('error_code') in [0, 99]:
        phone = data.get('phone_number') or data['data'].get('phone_number')
    return data
@app.route('/', methods=['GET'])      
def help():
    return {'help': "Url Link Api Login Zalo: /hytermix/zalo/login"}

@app.route('/hytermix', methods=['GET'])      
def helpp():
    return {'help': "Url Link Api Login Zalo: /hytermix/zalo/login"}
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)