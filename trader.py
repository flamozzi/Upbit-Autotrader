import time
from pprint import pprint

from requests import get
from jwt import encode

ACCESS_KEY = ""
SECRET_KEY = ""

# Start with "_" is private function normally
# Implicit promise of no use in external modules

def get_account():
        payload = {
                "access_key": ACCESS_KEY,
                "nonce": int(time.time() * 1000)
        }

        token = encode(payload, SECRET_KEY).decode()
        # Python3 are encoded with utf-8 basically

        headers = {
                "Authorization": f"Bearer {token}"
        }
        url = "https://api.upbit.com/v1/accounts"
        resp = get(url, headers=headers)
        resp_data = resp.json()
        return resp_data

def main():
        resp_data = get_account()
        pprint(resp_data)

if __name__ == '__main__':
        main()