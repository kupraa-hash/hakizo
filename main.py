import datetime
import requests
import json
import time
import logging
import asyncio
import random
import base64
from colorlog import ColoredFormatter
from utilities import (
    SortUpgrades,
    number_to_string,
    DailyCipherDecode,
    TextToMorseCode,
)
from accountlist import AccountList  # Impor AccountList dari accountlist.py

AccountsRecheckTime = 300
MaxRandomDelay = 120

# URL to get free proxies
PROXY_URL = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=ipport&format=text&timeout=20000"

# Logging configuration
LOG_LEVEL = logging.DEBUG
LOGFORMAT = "%(log_color)s[Master HamsterKombat Bot]%(reset)s[%(log_color)s%(levelname)s%(reset)s] %(log_color)s%(message)s%(reset)s"
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger("pythonConfig")
log.setLevel(LOG_LEVEL)
log.addHandler(stream)
# End of configuration
# ---------------------------------------------#

# Function to get proxies from the URL
def get_proxies():
    try:
        response = requests.get(PROXY_URL)
        if response.status_code == 200:
            proxies = response.text.split('\n')
            return [proxy.strip() for proxy in proxies if proxy.strip()]
        else:
            log.error(f"Failed to get proxies. Status code: {response.status_code}")
            return []
    except Exception as e:
        log.error(f"Error getting proxies: {e}")
        return []


proxies = get_proxies()

# Log informasi proxy
if proxies:
    log.info(f"Proxy berhasil dimuat sebanyak {len(proxies)}")
else:
    log.warning("Tidak ada proxy yang dimuat")

telegramBotLogging = {
    "is_active": True,  # Set it to True if you want to use it, and make sure to fill out the below fields
    "bot_token": "7120913121:AAGVcSIuDz6OONf4p2pGIGmFmz-jeDu87i0",  # HTTP API access token from https://t.me/BotFather ~ Start your bot after creating it
    # Configure the what you want to receive logs from the bot
    "messages": {
        "general_info": True,  # General information
        "account_info": True,  # Account information
        "http_errors": True,  # HTTP errors
        "other_errors": True,  # Other errors
        "daily_cipher": True,  # Daily cipher
        "daily_task": True,  # Daily task
        "upgrades": True,  # Upgrades
    },
}

# ---------------------------------------------#

class HamsterKombatAccount:
    def __init__(self, AccountData):
        self.account_name = AccountData["account_name"]
        self.Authorization = AccountData["Authorization"]
        self.UserAgent = AccountData["UserAgent"]
        self.Proxy = AccountData["Proxy"]
        self.config = AccountData.get("config", {})  # Ambil config, jika tidak ada, gunakan dict kosong
        self.config.setdefault("auto_get_task", False)  # Set default jika tidak ada
        self.isAndroidDevice = "Android" in self.UserAgent
        self.balanceCoins = 0
        self.availableTaps = 0
        self.maxTaps = 0
        self.ProfitPerHour = 0
        self.earnPassivePerHour = 0
        self.SpendTokens = 0
        self.account_data = None
        self.telegram_chat_id = AccountData["telegram_chat_id"]
        self.totalKeys = 0
        self.balanceKeys = 0

        # Log proxy information
        if self.Proxy:
            log.info(f"[{self.account_name}] Using proxy: {self.Proxy}")
        else:
            log.info(f"[{self.account_name}] No proxy configured")

    def SendTelegramLog(self, message, level):
        if (
            not telegramBotLogging["is_active"]
            or self.telegram_chat_id == ""
            or telegramBotLogging["bot_token"] == ""
        ):
            return

        if (
            level not in telegramBotLogging["messages"]
            or telegramBotLogging["messages"][level] is False
        ):
            return

        requests.get(
            f"https://api.telegram.org/bot{telegramBotLogging['bot_token']}/sendMessage?chat_id={self.telegram_chat_id}&text={message}"
        )

    # Send HTTP requests
    def HttpRequest(
        self,
        url,
        headers,
        method="POST",
        validStatusCodes=200,
        payload=None,
    ):
        # Default headers
        defaultHeaders = {
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Host": "api.hamsterkombatgame.io",
            "Origin": "https://hamsterkombatgame.io",
            "Referer": "https://hamsterkombatgame.io/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": self.UserAgent,
        }

        # Add default headers for Android devices to avoid detection, Not needed for iOS devices
        if self.isAndroidDevice:
            defaultHeaders["HTTP_SEC_CH_UA_PLATFORM"] = '"Android"'
            defaultHeaders["HTTP_SEC_CH_UA_MOBILE"] = "?1"
            defaultHeaders["HTTP_SEC_CH_UA"] = (
                '"Android WebView";v="125", "Chromium";v="125", "Not.A/Brand";v="24"'
            )
            defaultHeaders["HTTP_X_REQUESTED_WITH"] = "org.telegram.messenger.web"

        # Add and replace new headers to default headers
        for key, value in headers.items():
            defaultHeaders[key] = value

        try:
            log.info(f"[{self.account_name}] Sending {method} request to {url} with proxy: {self.Proxy}")
            if method == "GET":
                response = requests.get(url, headers=defaultHeaders, proxies=self.Proxy)
            elif method == "POST":
                response = requests.post(
                    url, headers=headers, data=payload, proxies=self.Proxy
                )
            elif method == "OPTIONS":
                response = requests.options(url, headers=headers, proxies=self.Proxy)
            else:
                log.error(f"[{self.account_name}] Invalid method: {method}")
                self.SendTelegramLog(
                    f"[{self.account_name}] Invalid method: {method}", "http_errors"
                )
                return False

            if response.status_code != validStatusCodes:
                log.error(
                    f"[{self.account_name}] Status code is not {validStatusCodes}"
                )
                log.error(f"[{self.account_name}] Response: {response.text}")
                self.SendTelegramLog(
                    f"[{self.account_name}] Status code is not {validStatusCodes}",
                    "http_errors",
                )
                return False

            if method == "OPTIONS":
                return True

            return response.json()
        except Exception as e:
            log.error(f"[{self.account_name}] Error: {e}")
            self.SendTelegramLog(f"[{self.account_name}] Error: {e}", "http_errors")
            return False

    # Sending sync request
    def syncRequest(self):
        url = "https://api.hamsterkombatgame.io/clicker/sync"
        headers = {
            "Access-Control-Request-Headers": self.Authorization,
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)

        headers = {
            "Authorization": self.Authorization,
        }

        # Send POST request
        return self.HttpRequest(url, headers, "POST", 200)

    # Get list of upgrades to buy
    def UpgradesForBuyRequest(self):
        url = "https://api.hamsterkombatgame.io/clicker/upgrades-for-buy"
        headers = {
            "Access-Control-Request-Headers": "authorization",
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)

        headers = {
            "Authorization": self.Authorization,
        }

        # Send POST request
        return self.HttpRequest(url, headers, "POST", 200)

    # Buy an upgrade
    def BuyUpgradeRequest(self, UpgradeId):
        url = "https://api.hamsterkombatgame.io/clicker/buy-upgrade"
        headers = {
            "Access-Control-Request-Headers": "authorization,content-type",
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)

        headers = {
            "Authorization": self.Authorization,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload = json.dumps(
            {
                "upgradeId": UpgradeId,
                "timestamp": int(datetime.datetime.now().timestamp() * 1000),
            }
        )

        # Send POST request
        return self.HttpRequest(url, headers, "POST", 200, payload)

    # Tap the hamster
    def TapRequest(self, tap_count):
        url = "https://api.hamsterkombatgame.io/clicker/tap"
        headers = {
            "Access-Control-Request-Headers": "authorization,content-type",
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)

        headers = {
            "Accept": "application/json",
            "Authorization": self.Authorization,
            "Content-Type": "application/json",
        }

        payload = json.dumps(
            {
                "timestamp": int(datetime.datetime.now().timestamp() * 1000),
                "availableTaps": 0,
                "count": int(tap_count),
            }
        )

        # Send POST request
        return self.HttpRequest(url, headers, "POST", 200, payload)

    # Get list of boosts to buy
    def BoostsToBuyListRequest(self):
        url = "https://api.hamsterkombatgame.io/clicker/boosts-for-buy"
        headers = {
            "Access-Control-Request-Headers": "authorization",
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)

        headers = {
            "Authorization": self.Authorization,
        }

        # Send POST request
        return self.HttpRequest(url, headers, "POST", 200)

    # Buy a boost
    def BuyBoostRequest(self, boost_id):
        url = "https://api.hamsterkombatgame.io/clicker/buy-boost"
        headers = {
            "Access-Control-Request-Headers": "authorization,content-type",
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)

        headers = {
            "Accept": "application/json",
            "Authorization": self.Authorization,
            "Content-Type": "application/json",
        }

        payload = json.dumps(
            {
                "boostId": boost_id,
                "timestamp": int(datetime.datetime.now().timestamp() * 1000),
            }
        )

        # Send POST request
        return self.HttpRequest(url, headers, "POST", 200, payload)

    def getAccountData(self):
        account_data = self.syncRequest()
        if account_data is None or account_data is False:
            log.error(f"[{self.account_name}] Unable to get account data.")
            self.SendTelegramLog(
                f"[{self.account_name}] Unable to get account data.", "other_errors"
            )
            return False

        if "clickerUser" not in account_data:
            log.error(f"[{self.account_name}] Invalid account data.")
            self.SendTelegramLog(
                f"[{self.account_name}] Invalid account data.", "other_errors"
            )
            return False

        if "balanceCoins" not in account_data["clickerUser"]:
            log.error(f"[{self.account_name}] Invalid balance coins.")
            self.SendTelegramLog(
                f"[{self.account_name}] Invalid balance coins.", "other_errors"
            )
            return False

        self.account_data = account_data
        self.balanceCoins = account_data["clickerUser"]["balanceCoins"]
        self.availableTaps = account_data["clickerUser"]["availableTaps"]
        self.maxTaps = account_data["clickerUser"]["maxTaps"]
        self.earnPassivePerHour = account_data["clickerUser"]["earnPassivePerHour"]
        if "balanceKeys" in account_data["clickerUser"]:
            self.balanceKeys = account_data["clickerUser"]["balanceKeys"]
        else:
            self.balanceKeys = 0

        if "totalKeys" in account_data["clickerUser"]:
            self.totalKeys = account_data["clickerUser"]["totalKeys"]
        else:
            self.totalKeys = 0

        return account_data

    def BuyFreeTapBoostIfAvailable(self):
        log.info(f"[{self.account_name}] Checking for free tap boost...")

        BoostList = self.BoostsToBuyListRequest()
        if BoostList is None:
            log.error(f"[{self.account_name}] Failed to get boosts list.")
            self.SendTelegramLog(
                f"[{self.account_name}] Failed to get boosts list.", "other_errors"
            )
            return None

        BoostForTapList = None
        for boost in BoostList["boostsForBuy"]:
            if boost["price"] == 0 and boost["id"] == "BoostFullAvailableTaps":
                BoostForTapList = boost
                break

        if (
            BoostForTapList is not None
            and "price" in BoostForTapList
            and "cooldownSeconds" in BoostForTapList
            and BoostForTapList["price"] == 0
            and BoostForTapList["cooldownSeconds"] == 0
        ):
            log.info(f"[{self.account_name}] Free boost found, attempting to buy...")
            time.sleep(5)
            self.BuyBoostRequest(BoostForTapList["id"])
            log.info(f"[{self.account_name}] Free boost bought successfully")
            return True
        else:
            log.info(f"\033[1;34m[{self.account_name}] No free boosts available\033[0m")

        return False

    def IPRequest(self):
        url = "https://api.hamsterkombatgame.io/ip"
        headers = {
            "Access-Control-Request-Headers": "authorization",
            "Access-Control-Request-Method": "GET",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 200)

        headers = {
            "Authorization": self.Authorization,
        }

        # Send GET request
        return self.HttpRequest(url, headers, "GET", 200)

    def MeTelegramRequest(self):
        url = "https://api.hamsterkombatgame.io/auth/me-telegram"
        headers = {
            "Access-Control-Request-Headers": "authorization",
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)

        headers = {
            "Authorization": self.Authorization,
        }

        # Send POST request
        return self.HttpRequest(url, headers, "POST", 200)

    def ListTasksRequest(self):
        url = "https://api.hamsterkombatgame.io/clicker/list-tasks"
        headers = {
            "Access-Control-Request-Headers": "authorization",
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)

        headers = {
            "Authorization": self.Authorization,
        }

        # Send POST request
        return self.HttpRequest(url, headers, "POST", 200)

    def GetListAirDropTasksRequest(self):
        url = "https://api.hamsterkombatgame.io/clicker/list-airdrop-tasks"
        headers = {
            "Access-Control-Request-Headers": "authorization",
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)

        headers = {
            "Authorization": self.Authorization,
        }

        # Send POST request
        return self.HttpRequest(url, headers, "POST", 200)

    def GetAccountConfigRequest(self):
        url = "https://api.hamsterkombatgame.io/clicker/config"
        headers = {
            "Access-Control-Request-Headers": "authorization",
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)

        headers = {
            "Authorization": self.Authorization,
        }

        # Send POST request
        return self.HttpRequest(url, headers, "POST", 200)

    def ClaimDailyCipherRequest(self, DailyCipher):
        url = "https://api.hamsterkombatgame.io/clicker/claim-daily-cipher"
        headers = {
            "Access-Control-Request-Headers": "authorization,content-type",
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)

        headers = {
            "Accept": "application/json",
            "Authorization": self.Authorization,
            "Content-Type": "application/json",
        }

        payload = json.dumps(
            {
                "cipher": DailyCipher,
            }
        )

        # Send POST request
        return self.HttpRequest(url, headers, "POST", 200, payload)

    def CheckTaskRequest(self, task_id):
        url = "https://api.hamsterkombatgame.io/clicker/check-task"
        headers = {
            "Access-Control-Request-Headers": "authorization,content-type",
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)  # Tambahkan url di sini

        headers = {
            "Accept": "application/json",
            "Authorization": self.Authorization,
            "Content-Type": "application/json",
        }
        payload = json.dumps(
            {
                "taskId": task_id,
            }
        )

        # Send POST request
        return self.HttpRequest(url, headers, "POST", 200, payload)

    def BuyBestCard(self):
        log.info(f"[{self.account_name}] Checking for best card...")
        time.sleep(2)
        upgradesResponse = self.UpgradesForBuyRequest()
        if upgradesResponse is None:
            log.error(f"[{self.account_name}] Failed to get upgrades list.")
            self.SendTelegramLog(
                f"[{self.account_name}] Failed to get upgrades list.", "other_errors"
            )
            return False

        upgrades = [
            item
            for item in upgradesResponse["upgradesForBuy"]
            if not item["isExpired"]
            and item["isAvailable"]
            and item["profitPerHourDelta"] > 0
        ]

        if len(upgrades) == 0:
            log.warning(f"[{self.account_name}] No upgrades available.")
            return False

        balanceCoins = int(self.balanceCoins)
        log.info(f"[{self.account_name}] Searching for the best upgrades...")

        selected_upgrades = SortUpgrades(
            upgrades, 999999999999
        )  # Set max budget to a high number
        if len(selected_upgrades) == 0:
            log.warning(f"[{self.account_name}] No upgrades available.")
            return False

        log.info(
            f"[{self.account_name}] Best upgrade is {selected_upgrades[0]['name']} with profit {selected_upgrades[0]['profitPerHourDelta']} and price {number_to_string(selected_upgrades[0]['price'])}, Level: {selected_upgrades[0]['level']}"
        )

        if balanceCoins < selected_upgrades[0]["price"]:
            log.warning(
                f"[{self.account_name}] Balance is too low to buy the best card."
            )

            self.SendTelegramLog(
                f"[{self.account_name}] Balance is too low to buy the best card, Best card: {selected_upgrades[0]['name']} with profit {selected_upgrades[0]['profitPerHourDelta']} and price {number_to_string(selected_upgrades[0]['price'])}, Level: {selected_upgrades[0]['level']}",
                "upgrades",
            )
            return False

        if (
            "cooldownSeconds" in selected_upgrades[0]
            and selected_upgrades[0]["cooldownSeconds"] > 0
        ):
            log.warning(f"[{self.account_name}] Best card is on cooldown...")
            if selected_upgrades[0]["cooldownSeconds"] > 300:
                self.SendTelegramLog(
                    f"[{self.account_name}] Best card is on cooldown for more than 5 minutes, Best card: {selected_upgrades[0]['name']} with profit {selected_upgrades[0]['profitPerHourDelta']} and price {number_to_string(selected_upgrades[0]['price'])}, Level: {selected_upgrades[0]['level']}",
                    "upgrades",
                )
                return False
            log.info(
                f"[{self.account_name}] Waiting for {selected_upgrades[0]['cooldownSeconds']} seconds, Cooldown will be completed in {selected_upgrades[0]['cooldownSeconds']} seconds..."
            )
            time.sleep(selected_upgrades[0]["cooldownSeconds"] + 1)

        log.info(f"[{self.account_name}] Attempting to buy the best card...")
        time.sleep(2)
        upgradesResponse = self.BuyUpgradeRequest(selected_upgrades[0]["id"])
        if upgradesResponse is None:
            log.error(f"[{self.account_name}] Failed to buy the best card.")
            self.SendTelegramLog(
                f"[{self.account_name}] Failed to buy the best card.", "other_errors"
            )
            return False

        log.info(f"[{self.account_name}] Best card bought successfully")
        time.sleep(3)
        balanceCoins -= selected_upgrades[0]["price"]
        self.balanceCoins = balanceCoins
        self.ProfitPerHour += selected_upgrades[0]["profitPerHourDelta"]
        self.SpendTokens += selected_upgrades[0]["price"]
        self.earnPassivePerHour += selected_upgrades[0]["profitPerHourDelta"]

        log.info(
            f"[{self.account_name}] Best card purchase completed successfully, Your profit per hour increased by {number_to_string(self.ProfitPerHour)} coins, Spend tokens: {number_to_string(self.SpendTokens)}"
        )

        self.SendTelegramLog(
            f"[{self.account_name}] Bought {selected_upgrades[0]['name']} with profit {selected_upgrades[0]['profitPerHourDelta']} and price {number_to_string(selected_upgrades[0]['price'])}, Level: {selected_upgrades[0]['level']}",
            "upgrades",
        )

        return True

    def StartMiniGame(self, AccountConfigData, AccountID):
        if "dailyKeysMiniGame" not in AccountConfigData:
            log.error(f"[{self.account_name}] Unable to get daily keys mini game.")
            self.SendTelegramLog(
                f"[{self.account_name}] Unable to get daily keys mini game.",
                "other_errors",
            )
            return

        if AccountConfigData["dailyKeysMiniGame"]["isClaimed"] == True:
            log.info(f"[{self.account_name}] Daily keys mini game already claimed.")
            return

        if AccountConfigData["dailyKeysMiniGame"]["remainSecondsToNextAttempt"] > 0:
            log.info(f"[{self.account_name}] Daily keys mini game is on cooldown...")
            return

        ## check timer.
        url = "https://api.hamsterkombatgame.io/clicker/start-keys-minigame"

        headers = {
            "Access-Control-Request-Headers": "authorization",
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)

        headers = {
            "Authorization": self.Authorization,
        }

        # Send POST request
        response = self.HttpRequest(url, headers, "POST", 200)

        if response is None:
            log.error(f"[{self.account_name}] Unable to start mini game.")
            self.SendTelegramLog(
                f"[{self.account_name}] Unable to start mini game.", "other_errors"
            )
            return

        if "dailyKeysMiniGame" not in response:
            log.error(f"[{self.account_name}] Unable to get daily keys mini game.")
            self.SendTelegramLog(
                f"[{self.account_name}] Unable to get daily keys mini game.",
                "other_errors",
            )
            return

        if response["dailyKeysMiniGame"]["isClaimed"] == True:
            log.info(f"[{self.account_name}] Daily keys mini game already claimed.")
            return

        if "remainSecondsToGuess" not in response["dailyKeysMiniGame"]:
            log.error(f"[{self.account_name}] Unable to get daily keys mini game.")
            self.SendTelegramLog(
                f"[{self.account_name}] Unable to get daily keys mini game.",
                "other_errors",
            )
            return

        waitTime = int(
            response["dailyKeysMiniGame"]["remainSecondsToGuess"]
            - random.randint(8, 15)
        )

        if waitTime < 0:
            log.error(f"[{self.account_name}] Unable to claim mini game.")
            self.SendTelegramLog(
                f"[{self.account_name}] Unable to claim mini game.", "other_errors"
            )
            return

        log.info(
            f"[{self.account_name}] Waiting for {waitTime} seconds, Mini-game will be completed in {waitTime} seconds..."
        )
        time.sleep(waitTime)

        url = "https://api.hamsterkombatgame.io/clicker/claim-daily-keys-minigame"

        headers = {
            "Access-Control-Request-Headers": "authorization,content-type",
            "Access-Control-Request-Method": "POST",
        }

        # Send OPTIONS request
        self.HttpRequest(url, headers, "OPTIONS", 204)

        headers = {
            "Accept": "application/json",
            "Authorization": self.Authorization,
            "Content-Type": "application/json",
        }

        cipher = (
            ("0" + str(waitTime) + str(random.randint(10000000000, 99999999999)))[:10]
            + "|"
            + str(AccountID)
        )
        cipher_base64 = base64.b64encode(cipher.encode()).decode()

        payload = json.dumps(
            {
                "cipher": cipher_base64,
            }
        )

        # Send POST request
        response = self.HttpRequest(url, headers, "POST", 200, payload)

        if response is None:
            log.error(f"[{self.account_name}] Unable to claim mini game.")
            self.SendTelegramLog(
                f"[{self.account_name}] Unable to claim mini game.", "other_errors"
            )
            return

        log.info(f"[{self.account_name}] Mini game claimed successfully.")

    def Start(self):
        log.info(f"[{self.account_name}] Starting account...")

        log.info(f"[{self.account_name}] Getting basic account data...")
        AccountBasicData = self.MeTelegramRequest()

        if (
            AccountBasicData is None
            or AccountBasicData is False
            or "telegramUser" not in AccountBasicData
            or "id" not in AccountBasicData["telegramUser"]
        ):
            log.error(f"[{self.account_name}] Unable to get account basic data.")
            self.SendTelegramLog(
                f"[{self.account_name}] Unable to get account basic data.",
                "other_errors",
            )
            return

        log.info(
            f"\033[1;35m[{self.account_name}] Account ID: {AccountBasicData['telegramUser']['id']}, Account detected as bot: {AccountBasicData['telegramUser']['isBot']}\033[0m"
        )
        self.SendTelegramLog(
            f"[{self.account_name}] Account ID: {AccountBasicData['telegramUser']['id']}, Account detected as bot: {AccountBasicData['telegramUser']['isBot']}",
            "account_info",
        )

        log.info(f"[{self.account_name}] Getting account config data...")
        AccountConfigData = self.GetAccountConfigRequest()
        if (
            AccountConfigData is None
            or AccountConfigData is False
            or "clickerConfig" not in AccountConfigData
        ):
            log.error(f"[{self.account_name}] Unable to get account config data.")
            self.SendTelegramLog(
                f"[{self.account_name}] Unable to get account config data.",
                "other_errors",
            )
            return

        DailyCipher = ""
        if (
            self.config["auto_get_daily_cipher"]
            and "dailyCipher" in AccountConfigData
            and "cipher" in AccountConfigData["dailyCipher"]
        ):
            log.info(f"[{self.account_name}] Decoding daily cipher...")
            DailyCipher = DailyCipherDecode(AccountConfigData["dailyCipher"]["cipher"])
            MorseCode = TextToMorseCode(DailyCipher)
            log.info(
                f"\033[1;34m[{self.account_name}] Daily cipher: {DailyCipher} and Morse code: {MorseCode}\033[0m"
            )

        log.info(f"[{self.account_name}] Getting account data...")
        getAccountDataStatus = self.getAccountData()
        if getAccountDataStatus is False:
            return

        log.info(
            f"[{self.account_name}] Account Balance Coins: {number_to_string(self.balanceCoins)}, Available Taps: {self.availableTaps}, Max Taps: {self.maxTaps}, Total Keys: {self.totalKeys}, Balance Keys: {self.balanceKeys}"
        )

        log.info(f"[{self.account_name}] Getting account upgrades...")
        upgradesResponse = self.UpgradesForBuyRequest()

        if upgradesResponse is None:
            log.error(f"[{self.account_name}] Failed to get upgrades list.")
            self.SendTelegramLog(
                f"[{self.account_name}] Failed to get upgrades list.", "other_errors"
            )
            return

        log.info(f"[{self.account_name}] Getting account tasks...")
        tasksResponse = self.ListTasksRequest()

        if tasksResponse is None:
            log.error(f"[{self.account_name}] Failed to get tasks list.")
            self.SendTelegramLog(
                f"[{self.account_name}] Failed to get tasks list.", "other_errors"
            )
            return

        log.info(f"[{self.account_name}] Getting account airdrop tasks...")
        airdropTasksResponse = self.GetListAirDropTasksRequest()

        if airdropTasksResponse is None:
            log.error(f"[{self.account_name}] Failed to get airdrop tasks list.")
            self.SendTelegramLog(
                f"[{self.account_name}] Failed to get airdrop tasks list.",
                "other_errors",
            )
            return

        log.info(f"[{self.account_name}] Getting account IP...")
        ipResponse = self.IPRequest()
        if ipResponse is None:
            log.error(f"[{self.account_name}] Failed to get IP.")
            self.SendTelegramLog(
                f"[{self.account_name}] Failed to get IP.", "other_errors"
            )
            return

        log.info(
            f"[{self.account_name}] IP: {ipResponse['ip']} Company: {ipResponse['asn_org']} Country: {ipResponse['country_code']}"
        )

        if self.config["auto_finish_mini_game"]:
            log.info(f"[{self.account_name}] Attempting to finish mini game...")
            time.sleep(1)
            self.StartMiniGame(
                AccountConfigData, AccountBasicData["telegramUser"]["id"]
            )

        # Start tapping
        if self.config["auto_tap"]:
            log.info(f"[{self.account_name}] Starting to tap...")
            time.sleep(2)
            self.TapRequest(self.availableTaps)
            log.info(f"[{self.account_name}] Tapping completed successfully.")

        if self.config["auto_get_daily_cipher"] and DailyCipher != "":
            if AccountConfigData["dailyCipher"]["isClaimed"] == True:
                log.info(
                    f"\033[1;34m[{self.account_name}] Daily cipher already claimed.\033[0m"
                )            
            else:
                                log.info(f"[{self.account_name}] Attempting to claim daily cipher...")
            time.sleep(2)
            self.ClaimDailyCipherRequest(DailyCipher)
            log.info(f"[{self.account_name}] Daily cipher claimed successfully.")
            self.SendTelegramLog(
                    f"[{self.account_name}] Daily cipher claimed successfully. Text was: {DailyCipher}, Morse code was: {TextToMorseCode(DailyCipher)}",
                    "daily_cipher",
                )

        if self.config["auto_get_daily_task"]:
            log.info(f"[{self.account_name}] Checking for daily task...")
            streak_days = None
            for task in tasksResponse["tasks"]:
                if task["id"] == "streak_days":
                    streak_days = task
                    break

            if streak_days is None:
                log.error(f"[{self.account_name}] Failed to get daily task.")
                return

            if streak_days["isCompleted"] == True:
                log.info(
                    f"\033[1;34m[{self.account_name}] Daily task already completed.\033[0m"
                )
            else:
                log.info(f"[{self.account_name}] Attempting to complete daily task...")
                day = streak_days["days"]
                rewardCoins = streak_days["rewardCoins"]
                time.sleep(2)
                self.CheckTaskRequest("streak_days")
                log.info(
                    f"[{self.account_name}] Daily task completed successfully, Day: {day}, Reward coins: {number_to_string(rewardCoins)}"
                )
                self.SendTelegramLog(
                    f"[{self.account_name}] Daily task completed successfully, Day: {day}, Reward coins: {number_to_string(rewardCoins)}",
                    "daily_task",
                )

        if self.config["auto_get_task"]:
            log.info(f"[{self.account_name}] Checking for available task...")
            selected_task = None
            for task in tasksResponse["tasks"]:
                link = task.get("link", "")
                if task["isCompleted"] == False and ("https://" in link):
                    log.info(
                        f"[{self.account_name}] Attempting to complete Youtube Or Twitter task..."
                    )
                    selected_task = task["id"]
                    rewardCoins = task["rewardCoins"]
                    time.sleep(2)
                    self.CheckTaskRequest(selected_task)
                    log.info(
                        f"[{self.account_name}] Task completed - id: {selected_task}, Reward coins: {number_to_string(rewardCoins)}"
                    )
                    self.SendTelegramLog(
                        f"[{self.account_name}] Task completed - id: {selected_task}, Reward coins: {number_to_string(rewardCoins)}",
                        "daily_task",
                    )
            if selected_task is None:
                log.info(f"\033[1;34m[{self.account_name}] Tasks already done\033[0m")

        # Start buying free tap boost
        if (
            self.config["auto_tap"]
            and self.config["auto_free_tap_boost"]
            and self.BuyFreeTapBoostIfAvailable()
        ):
            log.info(f"[{self.account_name}] Starting to tap with free boost...")
            time.sleep(2)
            self.TapRequest(self.availableTaps)
            log.info(
                f"[{self.account_name}] Tapping with free boost completed successfully."
            )

        # Start Syncing account data after tapping
        if self.config["auto_tap"]:
            self.getAccountData()
            log.info(
                f"[{self.account_name}] Account Balance Coins: {number_to_string(self.balanceCoins)}, Available Taps: {self.availableTaps}, Max Taps: {self.maxTaps}, Total Keys: {self.totalKeys}, Balance Keys: {self.balanceKeys}"
            )

        # Start buying upgrades
        if not self.config["auto_upgrade"]:
            log.error(f"[{self.account_name}] Auto upgrade is disabled.")
            return

        self.ProfitPerHour = 0
        self.SpendTokens = 0

        if self.config["wait_for_best_card"]:
            while True:
                if not self.BuyBestCard():
                    break

            self.getAccountData()
            log.info(
                f"[{self.account_name}] Final account balance: {number_to_string(self.balanceCoins)} coins, Your profit per hour is {number_to_string(self.earnPassivePerHour)} (+{number_to_string(self.ProfitPerHour)}), Spent: {number_to_string(self.SpendTokens)}"
            )
            self.SendTelegramLog(
                f"[{self.account_name}] Final account balance: {number_to_string(self.balanceCoins)} coins, Your profit per hour is {number_to_string(self.earnPassivePerHour)} (+{number_to_string(self.ProfitPerHour)}), Spent: {number_to_string(self.SpendTokens)}",
                "upgrades",
            )
            return

        if self.balanceCoins < self.config["auto_upgrade_start"]:
            log.warning(
                f"[{self.account_name}] Balance is too low to start buying upgrades."
            )
            return

        while self.balanceCoins >= self.config["auto_upgrade_min"]:
            log.info(f"[{self.account_name}] Checking for upgrades...")
            time.sleep(2)
            upgradesResponse = self.UpgradesForBuyRequest()
            if upgradesResponse is None:
                log.warning(f"[{self.account_name}] Failed to get upgrades list.")
                self.SendTelegramLog(
                    f"[{self.account_name}] Failed to get upgrades list.",
                    "other_errors",
                )
                return

            upgrades = [
                item
                for item in upgradesResponse["upgradesForBuy"]
                if not item["isExpired"]
                and item["isAvailable"]
                and item["profitPerHourDelta"] > 0
                and ("cooldownSeconds" not in item or item["cooldownSeconds"] == 0)
            ]

            if len(upgrades) == 0:
                log.warning(f"[{self.account_name}] No upgrades available.")
                return

            balanceCoins = int(self.balanceCoins)
            log.info(f"[{self.account_name}] Searching for the best upgrades...")

            selected_upgrades = SortUpgrades(upgrades, balanceCoins)
            if len(selected_upgrades) == 0:
                log.warning(f"[{self.account_name}] No upgrades available.")
                return

            log.info(
                f"[{self.account_name}] Best upgrade is {selected_upgrades[0]['name']} with profit {selected_upgrades[0]['profitPerHourDelta']} and price {number_to_string(selected_upgrades[0]['price'])}, Level: {selected_upgrades[0]['level']}"
            )

            balanceCoins -= selected_upgrades[0]["price"]

            log.info(f"[{self.account_name}] Attempting to buy an upgrade...")
            time.sleep(2)
            upgradesResponse = self.BuyUpgradeRequest(selected_upgrades[0]["id"])
            if upgradesResponse is None:
                log.error(f"[{self.account_name}] Failed to buy an upgrade.")
                return

            log.info(f"[{self.account_name}] Upgrade bought successfully")
            self.SendTelegramLog(
                f"[{self.account_name}] Bought {selected_upgrades[0]['name']} with profit {selected_upgrades[0]['profitPerHourDelta']} and price {number_to_string(selected_upgrades[0]['price'])}, Level: {selected_upgrades[0]['level']}",
                "upgrades",
            )
            time.sleep(5)
            self.balanceCoins = balanceCoins
            self.ProfitPerHour += selected_upgrades[0]["profitPerHourDelta"]
            self.SpendTokens += selected_upgrades[0]["price"]
            self.earnPassivePerHour += selected_upgrades[0]["profitPerHourDelta"]

        log.info(f"[{self.account_name}] Upgrades purchase completed successfully.")
        self.getAccountData()
        log.info(
            f"[{self.account_name}] Final account balance: {number_to_string(self.balanceCoins)} coins, Your profit per hour is {number_to_string(self.earnPassivePerHour)} (+{number_to_string(self.ProfitPerHour)}), Spent: {number_to_string(self.SpendTokens)}"
        )
        self.SendTelegramLog(
            f"[{self.account_name}] Final account balance: {number_to_string(self.balanceCoins)} coins, Your profit per hour is {number_to_string(self.earnPassivePerHour)} (+{number_to_string(self.ProfitPerHour)}), Spent: {number_to_string(self.SpendTokens)}",
            "account_info",
        )

    def claim_daily_combo(self):
        url = "https://api.hamsterkombatgame.io/clicker/claim-daily-combo"
        headers = {
            "Authorization": self.Authorization,
            "Accept": "*/*",
            "Content-Length": "0",
            "Origin": "https://hamsterkombatgame.io",
            "Referer": "https://hamsterkombatgame.io/",
            "User-Agent": self.UserAgent,
        }

        try:
            response = requests.post(url, headers=headers, proxies=self.Proxy)
            if response.status_code == 200:
                return response.json()
            else:
                log.error(f"[{self.account_name}] Gagal mengklaim daily combo. Status code: {response.status_code}")
                log.error(f"[{self.account_name}] Response: {response.text}")
                return False
        except Exception as e:
            log.error(f"[{self.account_name}] Error: {e}")
            return False


def RunAccounts():
    accounts = []
    for account in AccountList:
        accounts.append(HamsterKombatAccount(account))
        accounts[-1].SendTelegramLog(
            f"[{accounts[-1].account_name}] Hamster Kombat Auto farming bot started successfully.",
            "general_info",
        )

    while True:
        log.info("\033[1;33mStarting all accounts...\033[0m")
        for account in accounts:
            account.Start()

        if AccountsRecheckTime < 1 and MaxRandomDelay < 1:
            log.error(
                f"AccountsRecheckTime and MaxRandomDelay values are set to 0, bot will close now."
            )
            return

        if MaxRandomDelay > 0:
            randomDelay = random.randint(1, MaxRandomDelay)
            log.error(f"Sleeping for {randomDelay} seconds because of random delay...")
            time.sleep(randomDelay)

        if AccountsRecheckTime > 0:
            log.error(f"Rechecking all accounts in {AccountsRecheckTime} seconds...")
            time.sleep(AccountsRecheckTime)
# ... existing imports ...

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, CallbackQueryHandler

# Tambahkan token bot Telegram Anda
TELEGRAM_BOT_TOKEN = "7120913121:AAGVcSIuDz6OONf4p2pGIGmFmz-jeDu87i0"

# State definitions for conversation handler
ASK_DAILY_COMBO, SELECT_ACCOUNT, GET_COMBO_IDS, CONFIRM_UPGRADE, START_BOT = range(5)

# Fungsi untuk memulai bot
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Ya", callback_data='start_yes'),
            InlineKeyboardButton("Tidak", callback_data='start_no'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selamat datang!\n"
                                    "/start untuk memulai bot.\n"
                                    "/dailycombo untuk memulai combo.\n"
                                    "Apakah Anda ingin memulai bot?", reply_markup=reply_markup)

# Fungsi untuk menangani jawaban dari perintah /start
async def start_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'start_yes':
        await query.edit_message_text(text="Bot akan dimulai...")
        RunAccounts()  # Jalankan semua akun
    else:
        await query.edit_message_text("Dihentikan.\n"
                                      "/start untuk memulai bot.\n"
                                      "/dailycombo untuk memulai combo.")
        return ConversationHandler.END  # Kembali ke state awal
    
# Fungsi untuk menangani pemilihan akun
async def select_account(update: Update, context: CallbackContext) -> int:
    try:
        account_index = int(update.message.text) - 1
        if account_index < 0 or account_index >= len(AccountList):
            raise ValueError
        context.user_data['account_index'] = account_index
        await update.message.reply_text(f"Memulai akun {AccountList[account_index]['account_name']}...")

        # Panggil fungsi untuk mendapatkan combo IDs
        await update.message.reply_text("Masukkan 3 ID combo, dipisahkan dengan koma:")
        return GET_COMBO_IDS  # Kembali ke state GET_COMBO_IDS
    except ValueError:
        await update.message.reply_text("Pilihan tidak valid. Silakan masukkan nomor yang sesuai dengan daftar akun.")
        return SELECT_ACCOUNT

# Fungsi untuk memulai daily combo
async def dailycombo(update: Update, context: CallbackContext) -> int:
    context.user_data['account_index'] = 0  # Inisialisasi indeks akun
    await update.message.reply_text("Apakah Anda ingin daily combo? (y/n)")
    return ASK_DAILY_COMBO

# Fungsi untuk menangani jawaban daily combo
async def ask_daily_combo(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()
    if text == 'y':
        # Tampilkan daftar akun
        account_list_message = "Pilih akun mana?\n"
        for i, account in enumerate(AccountList):
            account_list_message += f"{i + 1}. {account['account_name']}\n"
        await update.message.reply_text(account_list_message)
        return SELECT_ACCOUNT
    
    elif text == 'n':
        await update.message.reply_text("Kembali ke menu utama.")
        await start(update, context)  # Panggil fungsi start untuk kembali ke menu sambutan
        return ConversationHandler.END  # Kembali ke state awal
    else:
        await update.message.reply_text("Silakan pilih 'y' untuk ya atau 'n' untuk tidak.")
        return ASK_DAILY_COMBO

# Tambahkan pemanggilan get_combo_ids setelah pemilihan akun
async def select_account(update: Update, context: CallbackContext) -> int:
    try:
        account_index = int(update.message.text) - 1
        if account_index < 0 or account_index >= len(AccountList):
            raise ValueError
        context.user_data['account_index'] = account_index

        # Panggil fungsi untuk mendapatkan combo IDs
        await update.message.reply_text("Masukkan 3 ID combo, dipisahkan dengan koma,\n"
                                        "\n"
                                       "1. ceo, marketing, it_team\n"
                                       "2. support_team, facebook_ads, youtube\n"
                                       "3. x, medium, instagram\n"
                                       "4. tiktok, reddit, influencers\n"
                                       "5. partnership_program, product_team, bisdev_team\n"
                                       "6. two_factor_authentication, ux_ui_team, security_team\n"
                                       "7. qa_team, antihacking_shield, risk_management_team\n"
                                       "8. security_audition, anonymous_transactions_ban, blocking_suspicious_accounts\n"
                                       "9. tokenomics_expert, consensys_explorer_pass, vc_labs\n"
                                       "10. compliance_officer, money_20_20, development_hub_mumbai\n"
                                       "11. data_center_tokyo, leaderboards, fan_tokens\n"
                                       "12. staking, btc_pairs, eth_pairs\n"
                                       "13. top_10_cmc_pairs, gamefi_tokens, defi2.0_tokens\n"
                                       "14. socialfi_tokens, meme_coins, shit_coins\n"
                                       "15. margin_trading_x10, margin_trading_x20, margin_trading_x30\n"
                                       "16. margin_trading_x50, margin_trading_x75, margin_trading_x100\n"
                                       "17. derivatives, prediction_markets, web3_integration\n"
                                       "18. dao, p2p_trading, trading_bots\n"
                                       "19. layerzero_listing, kyc, kyb\n"
                                       "20. legal_opinion, sec_transparancy, anti_money_loundering\n"
                                       "21. licence_uae, licence_europe, licence_asia\n"
                                       "22. licence_south_america, licence_australia, licence_north_america\n"
                                       "23. licence_nigeria, licence_japan, licence_ethiopia\n"
                                       "24. licence_india, licence_bangladesh, licence_indonesia\n"
                                       "25. licence_vietnam, licence_turkey, licence_philippines\n"
                                       "26. dex, oracle, vesting_smartcontracts\n"
                                       "27. launchpad, nft_marketplace, sports_integration\n"
                                       "28. sports_integration_0207, sports_integration_0507, sports_integration_0607\n"
                                       "29. sports_integration_0707, sports_integration_0807, sports_integration_0907\n"
                                       "30. sports_integration_1007, sports_integration_1407, usdt_on_ton\n"
                                       "31. blockchain_life_2024, save_hamsters_from_drowning, taker_carlson_interview\n"
                                       "32. token2049, bogdanoff, apps_center_listing\n"
                                       "33. villa_for_dev_team, long_squeeze, success_with_tucker\n"
                                       "34. forbes, two_chairs, short_squeeze\n"
                                       "35. special_hamster_conference, contract_with_football_club, dubai_office\n"
                                       "36. joe_rogan_podcast, venom_blockchain, notcoin_listing\n"
                                       "37. hamster_ai, nft_collection_launch, top10_global\n"
                                       "38. bitcoin_pizza_day, ceo_21m, hamster_daily_show\n"
                                       "39. hamster_youtube_channel, hamster_youtube_gold_button, web3_academy_launch\n"
                                       "40. lambo_for_ceo, consensys_piranja_pass, partner_announce\n"
                                       "41. football_club_winner, hamster_drop, premarket_launch\n"
                                       "42. tg_leaders, youtube_25_million, hamster_green_energy\n"
                                       "43. twitter_10_million, web3_game_con, hamster_break_records\n"
                                       "44. cx_hub_istanbul, adv_integration_0907, adv_integration_1307\n"
                                       "45. business_jet, call_btc_rise, rolex_soulmate\n"
                                       "46. appstore_launch, fight_fight, telegram_50m\n"
                                       "47. google_analytics, session_australia")
        return GET_COMBO_IDS  # Kembali ke state GET_COMBO_IDS
    except ValueError:
        await update.message.reply_text("Pilihan tidak valid. Silakan masukkan nomor yang sesuai dengan daftar akun.")
        return SELECT_ACCOUNT
    
# Fungsi untuk menangani input ID combo dari user
async def get_combo_ids(update: Update, context: CallbackContext) -> int:
    combo_ids = update.message.text.split(',')
    if len(combo_ids) != 3:
        await update.message.reply_text("Anda harus memasukkan tepat 3 ID, dipisahkan dengan koma.")
        return GET_COMBO_IDS

    combo_ids = [id.strip() for id in combo_ids]
    context.user_data['combo_ids'] = combo_ids

    account_index = context.user_data['account_index']
    account = HamsterKombatAccount(AccountList[account_index])  # Gunakan akun berdasarkan indeks

    # Ambil harga untuk setiap upgrade ID
    upgrades_response = account.UpgradesForBuyRequest()
    if not upgrades_response:
        await update.message.reply_text("Gagal mendapatkan daftar upgrade. Periksa log untuk detailnya.")
        return ConversationHandler.END

    prices = {}
    for upgrade in upgrades_response["upgradesForBuy"]:
        if upgrade["id"] in combo_ids:
            prices[upgrade["id"]] = upgrade["price"]

    if len(prices) != 3:
        await update.message.reply_text("Beberapa ID upgrade tidak ditemukan. Periksa kembali ID yang Anda masukkan.")
        return GET_COMBO_IDS

    context.user_data['prices'] = prices
    price_message = "\n".join([f"{id}: {number_to_string(price)} coins" for id, price in prices.items()])
    await update.message.reply_text(f"Harga untuk upgrade:\n{price_message}\nApakah Anda ingin lanjut buy 3 list tersebut? (y/n)")
    return CONFIRM_UPGRADE

async def confirm_upgrade(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()
    if text == 'y':
        combo_ids = context.user_data['combo_ids']
        prices = context.user_data['prices']
        account_index = context.user_data['account_index']
        account = HamsterKombatAccount(AccountList[account_index])  # Gunakan akun berdasarkan indeks

        # Panggil fungsi untuk membeli upgrade dengan ID yang diberikan
        success = True
        for upgrade_id in combo_ids:
            response = account.BuyUpgradeRequest(upgrade_id)
            if response is False or 'error_code' in response:
                success = False
                log.error(f"[{account.account_name}] Gagal membeli upgrade dengan ID: {upgrade_id}")
                log.error(f"[{account.account_name}] Response: {response}")

        if success:
            await update.message.reply_text("Upgrade berhasil dibeli.")
            log.info(f"Selesai membeli upgrade dengan ID: {', '.join(combo_ids)}")
            
            # Panggil fungsi untuk claim daily combo
            claim_response = account.claim_daily_combo()
            if claim_response:
                await update.message.reply_text("Daily combo berhasil diklaim.")
                log.info("Daily combo berhasil diklaim.")
            else:
                await update.message.reply_text("Gagal mengklaim daily combo. Periksa log untuk detailnya.")
                log.error("Gagal mengklaim daily combo.")
            
            # Beritahu jumlah koin dan lainnya
            account_data = account.getAccountData()
            if account_data:
                balance_message = (
                    f"Jumlah koin: {number_to_string(account.balanceCoins)}\n"
                    f"Available Taps: {account.availableTaps}\n"
                    f"Max Taps: {account.maxTaps}\n"
                    f"Total Keys: {account.totalKeys}\n"
                    f"Balance Keys: {account.balanceKeys}"
                )
                await update.message.reply_text(balance_message)
                
                   # Lanjutkan ke akun berikutnya
    #context.user_data['account_index'] += 1
    #if context.user_data['account_index'] < len(AccountList):
        #await update.message.reply_text("Lanjut akun lain? (y/n)")
    else:
        await update.message.reply_text("Sudah selesai. Kembali ke halaman welcome.")
        return ConversationHandler.END

    if text == 'y':
        account_list_message = "Pilih akun mana?\n"
        for i, account in enumerate(AccountList):
            account_list_message += f"{i + 1}. {account['account_name']}\n"
        await update.message.reply_text(account_list_message)
        return SELECT_ACCOUNT  # Kembali ke state SELECT_ACCOUNT untuk memilih akun baru

    elif text == 'n':
        await update.message.reply_text("Kembali ke menu utama.")
        await start(update, context)  # Panggil fungsi start untuk kembali ke menu sambutan
        return ConversationHandler.END  # Kembali ke state awal

    else:
        await update.message.reply_text("Silakan pilih 'y' untuk ya atau 'n' untuk tidak.")
        return CONFIRM_UPGRADE

# Fungsi untuk menjalankan bot Telegram
def run_telegram_bot():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Conversation handler untuk daily combo
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('dailycombo', dailycombo)],
        states={
            ASK_DAILY_COMBO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_daily_combo)],
            SELECT_ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_account)],
            GET_COMBO_IDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_combo_ids)],
            CONFIRM_UPGRADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_upgrade)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(start_callback, pattern='^start_'))

    application.run_polling()

def main():
    log.info("------------------------------------------------------------------------")
    log.info("------------------------------------------------------------------------")
    log.info("\033[1;32mWelcome to [Master Hamster Kombat] Auto farming bot...\033[0m")
    log.info("\033[1;35mVersion: 2.0\033[0m")
    log.info("\033[1;36mTo stop the bot, press Ctrl + C\033[0m")
    log.info("------------------------------------------------------------------------")
    log.info("------------------------------------------------------------------------")

    time.sleep(2)
    try:
        # Jalankan bot Telegram
        run_telegram_bot()
    except KeyboardInterrupt:
        log.error("Stopping Master Hamster Kombat Auto farming bot...")

import os
from flask import Flask


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == "__main__":
    app.run()
