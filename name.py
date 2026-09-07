import os
import random
import time
from concurrent.futures import ThreadPoolExecutor

BOLD = '\033[1m'
R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
D = '\033[0m'
C = '\033[96m'

def logo():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'{BOLD}{C}')
    print(" ╔═══════════════════════════════════════╗")
    print(" ║       _____ __      ___              ║")
    print(" ║      / __(_) /__   / _ \\__ ____ _  ___ ║")
    print(" ║     / _// / / -_) / // / // / ' \\/ _ \\ ║")
    print(" ║    /_/ /_/_/\\__/ /____/\\_,_/_/_/_/ .__/║")
    print(" ║                                 /_/    ║")
    print(" ║                                       ║")
    print(" ║         User Generator V-2.0          ║")
    print(" ╚═══════════════════════════════════════╝")
    print(f'{D}')

def username_gen(names, start, end):
    usernames = []
    for name in names.split(','):
        name = name.strip()
        for num in range(start, end + 1):
            username = f'{name.lower()}{num} | {name.capitalize()}'
            usernames.append(username)
    return usernames

def save_usernames(usernames):
    with open('.uids.txt', 'w') as file:
        for username in usernames:
            file.write(username + '\n')

def generate_usernames():
    logo()
    print(f'{BOLD}{Y} ENTER NAME (Eg: Rakib){D}\n')
    names = input(f'{BOLD}{G} ENTER NAME : {D}')
    print('')
    start = int(input(f'{BOLD}{Y} START (Eg : 1 ) : '))
    end = int(input(f'{BOLD}{Y} END (Eg : 1000 ) : '))
    
    usernames = username_gen(names, start, end)
    save_usernames(usernames)
    
    print('')
    print(f'{BOLD}{G} ═══════════════════════════════════════{D}')
    print(f'{BOLD}{G} TOTAL {Y}{len(usernames)}{G} USERNAMES GENERATED{D}')
    print(f'{BOLD}{G} SAVED TO: .uids.txt{D}')
    print(f'{BOLD}{G} ═══════════════════════════════════════{D}\n')
    
    print(f'{BOLD}{C} PREVIEW (First 10):{D}')
    for i, username in enumerate(usernames[:10], 1):
        print(f'{G} {i}. {username}{D}')
    if len(usernames) > 10:
        print(f'{Y} ... and {len(usernames) - 10} more{D}')
    print('')

def main():
    generate_usernames()

if __name__ == '__main__':
    main()