import random
import requests

# URL untuk mendapatkan proxy gratis
PROXY_URL = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=ipport&format=text&timeout=20000"

# Fungsi untuk mendapatkan proxy dari URL
def get_proxies():
    try:
        response = requests.get(PROXY_URL)
        if response.status_code == 200:
            proxies = response.text.split('\n')
            return [proxy.strip() for proxy in proxies if proxy.strip()]
        else:
            return []
    except Exception as e:
        return []

proxies = get_proxies()  # Memanggil fungsi untuk mendapatkan daftar proxy

# Accounts will be checked in the order they are listed
AccountList = [
    {
        "account_name": "Account 1",  # A custom name for the account (not important, just for logs)
        "Authorization": "Bearer 172156699925197JJk1mkT2Ugjnc23fcYGOQ3IE9sMhJGzLQQ8Dh0aHMkr2YbOOBEJUxaL0T9nqrU1956471752",  # To get the token, refer to the README.md file
        "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Refer to the README.md file to obtain a user agent
        "Proxy": {"http": random.choice(proxies)} if proxies else {},  # Use a random proxy from the list
        "config": {
            "auto_tap": True,  # Enable auto tap by setting it to True, or set it to False to disable
            "auto_finish_mini_game": True,  # Enable auto finish mini game by setting it to True, or set it to False to disable
            "auto_free_tap_boost": True,  # Enable auto free tap boost by setting it to True, or set it to False to disable
            "auto_get_daily_cipher": True,  # Enable auto get daily cipher by setting it to True, or set it to False to disable
            "auto_get_daily_task": True,  # Enable auto get daily task by setting it to True, or set it to False to disable
            "auto_upgrade": False,  # Enable auto upgrade by setting it to True, or set it to False to disable
            "auto_upgrade_start": 2000000,  # Start buying upgrades when the balance is greater than this amount
            "auto_upgrade_min": 100000,  # Stop buying upgrades when the balance is less than this amount
            "wait_for_best_card": False,  # Recommended to keep it True for high level accounts
            "auto_get_task": True,  # Enable auto get (Youtube/Twitter and ...) task to True, or set it to False to disable
        },
        "telegram_chat_id": "1956471752",  # String - you can get it from https://t.me/chatIDrobot
    },
    # Add more accounts if you want to use multiple accounts
    {
        "account_name": "Account 2",  # A custom name for the account (not important, just for logs)
        "Authorization": "Bearer 1721542631603Jr4RbQe9F60ENgf3CvoF14QJ8bszUUCGBEeCSssFwSN58dlns6tjGXAl2T8RmRtr5776809976",  # To get the token, refer to the README.md file
        "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Refer to the README.md file to obtain a user agent
         "Proxy": {"http": random.choice(proxies)} if proxies else {},  # Use a random proxy from the list
        "config": {
            "auto_tap": True,  # Enable auto tap by setting it to True, or set it to False to disable
            "auto_finish_mini_game": True,  # Enable auto finish mini game by setting it to True, or set it to False to disable
            "auto_free_tap_boost": True,  # Enable auto free tap boost by setting it to True, or set it to False to disable
            "auto_get_daily_cipher": True,  # Enable auto get daily cipher by setting it to True, or set it to False to disable
            "auto_get_daily_task": True,  # Enable auto get daily task by setting it to True, or set it to False to disable
            "auto_upgrade": False,  # Enable auto upgrade by setting it to True, or set it to False to disable
            "auto_upgrade_start": 2000000,  # Start buying upgrades when the balance is greater than this amount
            "auto_upgrade_min": 100000,  # Stop buying upgrades when the balance is less than this amount
            "wait_for_best_card": False,  # Recommended to keep it True for high level accounts
            "auto_get_task": True,  # Enable auto get (Youtube/Twitter and ...) task to True, or set it to False to disable
        },
        "telegram_chat_id": "1956471752",  # String - you can get it from https://t.me/chatIDrobot
    },
    # Add more accounts if you want to use multiple accounts
    {
        "account_name": "Account 3",  # A custom name for the account (not important, just for logs)
        "Authorization": "Bearer 1721543853584jmw1WWeb4uKXGqQ10elHLULh3m7O1EdYNp2II4Kdr1RoOEcO7NDFqdRCRV7HDyTZ6562518291",  # To get the token, refer to the README.md file
        "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Refer to the README.md file to obtain a user agent
        "Proxy": {"http": random.choice(proxies)} if proxies else {},  # Use a random proxy from the list
        "config": {
            "auto_tap": True,  # Enable auto tap by setting it to True, or set it to False to disable
            "auto_finish_mini_game": True,  # Enable auto finish mini game by setting it to True, or set it to False to disable
            "auto_free_tap_boost": True,  # Enable auto free tap boost by setting it to True, or set it to False to disable
            "auto_get_daily_cipher": True,  # Enable auto get daily cipher by setting it to True, or set it to False to disable
            "auto_get_daily_task": True,  # Enable auto get daily task by setting it to True, or set it to False to disable
            "auto_upgrade": True,  # Enable auto upgrade by setting it to True, or set it to False to disable
            "auto_upgrade_start": 2000000,  # Start buying upgrades when the balance is greater than this amount
            "auto_upgrade_min": 100000,  # Stop buying upgrades when the balance is less than this amount
            "wait_for_best_card": True,  # Recommended to keep it True for high level accounts
            "auto_get_task": True,  # Enable auto get (Youtube/Twitter and ...) task to True, or set it to False to disable
        },
        "telegram_chat_id": "1956471752",  # String - you can get it from https://t.me/chatIDrobot
    },
    # Add more accounts if you want to use multiple accounts
    {
        "account_name": "Account 4",  # A custom name for the account (not important, just for logs)
        "Authorization": "Bearer 1721567261957TIyQgWOKIODrDruXvfH23Quyro2xcq56YdYm4PBHJEEr05zpOHguWafb8QZMv4ya5214630123",  # To get the token, refer to the README.md file
        "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Refer to the README.md file to obtain a user agent
        "Proxy": {"http": random.choice(proxies)} if proxies else {},  # Use a random proxy from the list
        "config": {
            "auto_tap": True,  # Enable auto tap by setting it to True, or set it to False to disable
            "auto_finish_mini_game": True,  # Enable auto finish mini game by setting it to True, or set it to False to disable
            "auto_free_tap_boost": True,  # Enable auto free tap boost by setting it to True, or set it to False to disable
            "auto_get_daily_cipher": True,  # Enable auto get daily cipher by setting it to True, or set it to False to disable
            "auto_get_daily_task": True,  # Enable auto get daily task by setting it to True, or set it to False to disable
            "auto_upgrade": True,  # Enable auto upgrade by setting it to True, or set it to False to disable
            "auto_upgrade_start": 2000000,  # Start buying upgrades when the balance is greater than this amount
            "auto_upgrade_min": 100000,  # Stop buying upgrades when the balance is less than this amount
            "wait_for_best_card": True,  # Recommended to keep it True for high level accounts
            "auto_get_task": True,  # Enable auto get (Youtube/Twitter and ...) task to True, or set it to False to disable
        },
        "telegram_chat_id": "1956471752",  # String - you can get it from https://t.me/chatIDrobot
    },
    # Add more accounts if you want to use multiple accounts
    {
        "account_name": "Account 5",  # A custom name for the account (not important, just for logs)
        "Authorization": "Bearer 1721567313321hy0ZpdkRmnB7KEzWLxs6EDczrG3zX7S5GPWxorK0ZbQxydJVfvot9Sk2gcnGMn5b6018362074",  # To get the token, refer to the README.md file
        "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Refer to the README.md file to obtain a user agent
        "Proxy": {"http": random.choice(proxies)} if proxies else {},  # Use a random proxy from the list
        "config": {
            "auto_tap": True,  # Enable auto tap by setting it to True, or set it to False to disable
            "auto_finish_mini_game": True,  # Enable auto finish mini game by setting it to True, or set it to False to disable
            "auto_free_tap_boost": True,  # Enable auto free tap boost by setting it to True, or set it to False to disable
            "auto_get_daily_cipher": True,  # Enable auto get daily cipher by setting it to True, or set it to False to disable
            "auto_get_daily_task": True,  # Enable auto get daily task by setting it to True, or set it to False to disable
            "auto_upgrade": True,  # Enable auto upgrade by setting it to True, or set it to False to disable
            "auto_upgrade_start": 2000000,  # Start buying upgrades when the balance is greater than this amount
            "auto_upgrade_min": 100000,  # Stop buying upgrades when the balance is less than this amount
            "wait_for_best_card": True,  # Recommended to keep it True for high level accounts
            "auto_get_task": True,  # Enable auto get (Youtube/Twitter and ...) task to True, or set it to False to disable
        },
        "telegram_chat_id": "1956471752",  # String - you can get it from https://t.me/chatIDrobot
    },
    {
        "account_name": "Account 6",  # A custom name for the account (not important, just for logs)
        "Authorization": "Bearer 1721572874040KMPYRuKzyAuuutn3IQdxXcyFzq4iyKDTx5Bph4M735rNretqFuHWPfIHNGbDfkeQ6287112847",  # To get the token, refer to the README.md file
        "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Refer to the README.md file to obtain a user agent
        "Proxy": {"http": random.choice(proxies)} if proxies else {},  # Use a random proxy from the list
        "config": {
            "auto_tap": True,  # Enable auto tap by setting it to True, or set it to False to disable
            "auto_finish_mini_game": True,  # Enable auto finish mini game by setting it to True, or set it to False to disable
            "auto_free_tap_boost": True,  # Enable auto free tap boost by setting it to True, or set it to False to disable
            "auto_get_daily_cipher": True,  # Enable auto get daily cipher by setting it to True, or set it to False to disable
            "auto_get_daily_task": True,  # Enable auto get daily task by setting it to True, or set it to False to disable
            "auto_upgrade": True,  # Enable auto upgrade by setting it to True, or set it to False to disable
            "auto_upgrade_start": 2000000,  # Start buying upgrades when the balance is greater than this amount
            "auto_upgrade_min": 100000,  # Stop buying upgrades when the balance is less than this amount
            "wait_for_best_card": True,  # Recommended to keep it True for high level accounts
            "auto_get_task": True,  # Enable auto get (Youtube/Twitter and ...) task to True, or set it to False to disable
        },
        "telegram_chat_id": "1956471752",  # String - you can get it from https://t.me/chatIDrobot
    },
    {
        "account_name": "Account 7",  # A custom name for the account (not important, just for logs)
        "Authorization": "Bearer 1721572973564eJBRVhZwXc4UdFfktVBOhi23BfZPeJrtJCKF42cwZTCjkBDZ00gPHVWFKQZnoA1w6332828005",  # To get the token, refer to the README.md file
        "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Refer to the README.md file to obtain a user agent
        "Proxy": {"http": random.choice(proxies)} if proxies else {},  # Use a random proxy from the list
        "config": {
            "auto_tap": True,  # Enable auto tap by setting it to True, or set it to False to disable
            "auto_finish_mini_game": True,  # Enable auto finish mini game by setting it to True, or set it to False to disable
            "auto_free_tap_boost": True,  # Enable auto free tap boost by setting it to True, or set it to False to disable
            "auto_get_daily_cipher": True,  # Enable auto get daily cipher by setting it to True, or set it to False to disable
            "auto_get_daily_task": True,  # Enable auto get daily task by setting it to True, or set it to False to disable
            "auto_upgrade": True,  # Enable auto upgrade by setting it to True, or set it to False to disable
            "auto_upgrade_start": 2000000,  # Start buying upgrades when the balance is greater than this amount
            "auto_upgrade_min": 100000,  # Stop buying upgrades when the balance is less than this amount
            "wait_for_best_card": True,  # Recommended to keep it True for high level accounts
            "auto_get_task": True,  # Enable auto get (Youtube/Twitter and ...) task to True, or set it to False to disable
        },
        "telegram_chat_id": "1956471752",  # String - you can get it from https://t.me/chatIDrobot
    },
    {
        "account_name": "Account 8",  # A custom name for the account (not important, just for logs)
        "Authorization": "Bearer 1721573021500rh3A71U4NAoNPODNko0hmGja84jQgyiLONKhKFY4LbRXNrhko5sbHRMaQ9VlVwxA5978317114",  # To get the token, refer to the README.md file
        "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Refer to the README.md file to obtain a user agent
        "Proxy": {"http": random.choice(proxies)} if proxies else {},  # Use a random proxy from the list
        "config": {
            "auto_tap": True,  # Enable auto tap by setting it to True, or set it to False to disable
            "auto_finish_mini_game": True,  # Enable auto finish mini game by setting it to True, or set it to False to disable
            "auto_free_tap_boost": True,  # Enable auto free tap boost by setting it to True, or set it to False to disable
            "auto_get_daily_cipher": True,  # Enable auto get daily cipher by setting it to True, or set it to False to disable
            "auto_get_daily_task": True,  # Enable auto get daily task by setting it to True, or set it to False to disable
        },
        "telegram_chat_id": "1956471752",  # String - you can get it from https://t.me/chatIDrobot
    },
    {
        "account_name": "Account 9",  # A custom name for the account (not important, just for logs)
        "Authorization": "Bearer 172157306841438lfGoqSRFVWwVXxqCK390XK0u2HISPvOqdnP0gnEquGbyASBq21CHxsY5bhQ5Vu1595360744",  # To get the token, refer to the README.md file
        "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Refer to the README.md file to obtain a user agent
        "Proxy": {"http": random.choice(proxies)} if proxies else {},  # Use a random proxy from the list
        "config": {
            "auto_tap": True,  # Enable auto tap by setting it to True, or set it to False to disable
            "auto_finish_mini_game": True,  # Enable auto finish mini game by setting it to True, or set it to False to disable
            "auto_free_tap_boost": True,  # Enable auto free tap boost by setting it to True, or set it to False to disable
            "auto_get_daily_cipher": True,  # Enable auto get daily cipher by setting it to True, or set it to False to disable
            "auto_get_daily_task": True,  # Enable auto get daily task by setting it to True, or set it to False to disable
        },
        "telegram_chat_id": "1956471752",  # String - you can get it from https://t.me/chatIDrobot
    },
    {
        "account_name": "Account 10",  # A custom name for the account (not important, just for logs)
        "Authorization": "Bearer 1721573133710B7X3phA7r8xGE9Uj2XFvG6FPRW46Eo4E94tuJV79UzI8iKypP6h9yWPZXTMVocRP5149521220",  # To get the token, refer to the README.md file
        "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Refer to the README.md file to obtain a user agent
        "Proxy": {"http": random.choice(proxies)} if proxies else {},  # Use a random proxy from the list
        "config": {
            "auto_tap": True,  # Enable auto tap by setting it to True, or set it to False to disable
            "auto_finish_mini_game": True,  # Enable auto finish mini game by setting it to True, or set it to False to disable
            "auto_free_tap_boost": True,  # Enable auto free tap boost by setting it to True, or set it to False to disable
            "auto_get_daily_cipher": True,  # Enable auto get daily cipher by setting it to True, or set it to False to disable
        },
        "telegram_chat_id": "1956471752",  # String - you can get it from https://t.me/chatIDrobot
    },
    {
        "account_name": "Account 11",  # A custom name for the account (not important, just for logs)
        "Authorization": "Bearer 1721573191627tGvmEzwcgmDBtI0SiRoUuGDmhQaOkzCxOAgKMha1g4iGU7Or54RED1Hyxyg6ffne5474552805",  # To get the token, refer to the README.md file
        "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Refer to the README.md file to obtain a user agent
        "Proxy": {"http": random.choice(proxies)} if proxies else {},  # Use a random proxy from the list
        "config": {
            "auto_tap": True,  # Enable auto tap by setting it to True, or set it to False to disable
            "auto_finish_mini_game": True,  # Enable auto finish mini game by setting it to True, or set it to False to disable
            "auto_free_tap_boost": True,  # Enable auto free tap boost by setting it to True, or set it to False to disable
            "auto_get_daily_cipher": True,  # Enable auto get daily cipher by setting it to True, or set it to False to disable
        },
        "telegram_chat_id": "1956471752",  # String - you can get it from https://t.me/chatIDrobot
    },
    {
        "account_name": "Account 12",  # A custom name for the account (not important, just for logs)
        "Authorization": "Bearer 1721573235725NY0wdjs40CDJGtEiCW5M8twnPYM0DCDA7IX0x3u6qOZhxab6SztN2Z4QBlPXENKy7463987005",  # To get the token, refer to the README.md file
        "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Refer to the README.md file to obtain a user agent
        "Proxy": {"http": random.choice(proxies)} if proxies else {},  # Use a random proxy from the list
        "config": {
            "auto_tap": True,  # Enable auto tap by setting it to True, or set it to False to disable
            "auto_finish_mini_game": True,  # Enable auto finish mini game by setting it to True, or set it to False to disable
            "auto_free_tap_boost": True,  # Enable auto free tap boost by setting it to True, or set it to False to disable
            "auto_get_daily_cipher": True,  # Enable auto get daily cipher by setting it to True, or set it to False to disable
        },
        "telegram_chat_id": "1956471752",  # String - you can get it from https://t.me/chatIDrobot
    }
]