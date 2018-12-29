import time
from pprint import pprint
from urllib.parse import urlencode
from requests import get, post
from jwt import encode

ACCESS_KEY = "E10F3xqOUGAYxxFmExfGBo2xxx5Q1IsrpHqDszgx"
SECRET_KEY = "1DjcP3cRxk7J4ymY4xkDxcnt9R1hXRT68FHDv3x3"

# Start with "_" is private function normally
# Implicit promise of no use in external modules

####################################################

def get_account():
    # 전체 계좌 조회
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

def orderable_info(market):
    # 주문 가능 정보
    query = {
        "market": market
    }

    query_encoded = urlencode(query)

    payload = {
        "access_key": ACCESS_KEY,
        "nonce": int(time.time() * 1000),
        "query": query_encoded
    }

    token = encode(payload, SECRET_KEY).decode()

    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = "https://api.upbit.com/v1/orders/chance?" + query_encoded
    resp = get(url, headers=headers)
    resp_data = resp.json()
    return resp_data

def order(market, side, volume, price, ord_type):
    # 주문
    query = {
        "market": market,
        "side": side,
        "volume": volume,
        "price": price,
        "ord_type": ord_type
    }

    query_encoded = urlencode(query)

    payload = {
        "access_key": ACCESS_KEY,
        "nonce": int(time.time() * 1000),
        "query": query_encoded
    }

    token = encode(payload, SECRET_KEY).decode()

    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = "https://api.upbit.com/v1/orders"
    resp = post(url, headers=headers, json=query)
    resp_data = resp.json()
    return resp_data    

####################################################    

def main():
    resp_data = order("KRW-BTC", "bid", "0.00027979", "4289000", "limit")
    pprint(resp_data)

if __name__ == '__main__':
    main()