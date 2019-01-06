import time
from pprint import pprint
from urllib.parse import urlencode
from requests import get, post, delete
from jwt import encode

ACCESS_KEY = ""
SECRET_KEY = ""

##############################################################

def get_account():
    # check available for all accounts
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
    # orderable information
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
    # order
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

def order_list(state="wait", page=1):
    # order details(list)
    query = {
        "state": state,
        "page": page
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
    url = "https://api.upbit.com/v1/orders?" + query_encoded
    resp = get(url, headers=headers)
    resp_data = resp.json()
    return resp_data

def order_cancle(uuid):
    # order cancellation
    query = {
        "uuid": uuid
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
    url = "https://api.upbit.com/v1/order?" + query_encoded
    resp = delete(url, headers=headers)
    resp_data = resp.json()
    return resp_data    

def ticker(markets):
    # ticker
    url = "https://api.upbit.com/v1/ticker?markets=" + markets
    resp = get(url)
    resp_data = resp.json()
    return resp_data

def extension_list(before_list, unit):
    ex_list = []
    for i in before_list:
        for _ in range(0, int(unit)):
            ex_list.append(i)
    return ex_list

def candle_minute(market, to="", count=1, unit=1):
    # candle information for minute
    # unit == string type
    param = {"market": market, "to": to, "count": count}
    url = "https://api.upbit.com/v1/candles/minutes/" + unit + "?" + urlencode(param)
    resp = get(url)
    resp_data = resp.json()
    trade_price_list = []
    for i in range(0, count):
        trade_price_list.append(resp_data[i]["trade_price"])
    return extension_list(trade_price_list, unit)

def candle_day(market, to="", count=1):
    # candle information for day
    param = {"market": market, "to": to, "count": count}
    url = "https://api.upbit.com/v1/candles/days?" + urlencode(param)
    resp = get(url)
    resp_data = resp.json()
    return resp_data


def make_EMA(param_list):
    ema = .0
    copy_list = param_list
    copy_list.reverse()
    ema_list = []
    for i in range(0, 200):
        if i == 0:
            ema = copy_list[i]
        else:
            k = float(2/(i+2))
            ema = (copy_list[i]*k) + (ema*(1-k))
        ema_list.append(ema)
    ema_list.reverse()
    return ema_list

def make_MACD(medium_ema, long_ema):
    MACD = []
    for i in range(0, 200):
        MACD.append(medium_ema[i] - long_ema[i])
    return MACD

def make_Oscillator(macd, signal):
    Oscillator = []
    for i in range(0, 200):
        Oscillator.append(macd[i] - signal[i])
    return Oscillator

##############################################################

def main():
    # 지수이동평균: (c*k)+(xp*(1-k))
    # c = 종가, k = 2/(n+1), n = n일, xp = 전일지수이평

    # 확장된 list들
    medium_list = candle_minute("KRW-BTC", count=40, unit="5")
    long_list = candle_minute("KRW-BTC", count=20, unit="10")

    medium_ema = make_EMA(medium_list)
    long_ema = make_EMA(long_list)
    
    #########################################
    #평가 기준
    #########################################

    MACD = make_MACD(medium_ema, long_ema)

    Signal = make_EMA(MACD)

    Oscillator = make_Oscillator(MACD, Signal)

    ##########################################
    #매매 판단
    ##########################################

    # 0. MACD와 시그널의 골든 크로스 -> 매수사인 +1
    #    MACD와 시그널의 데드 크로스 -> 매도사인 -1
    # 1. MACD와 시그널이 골든 크로스 후 2개의 선이 제로선을 웃돈다 -애매
    #    MACD와 시그널이 데드 크로스 후 2개의 선이 제로선을 밑돈다 -애매
    # 2. MACD의 상승 == 가격의 상승 경향 +1
    #    MACD의 하락 == 가격의 하락 경향 -1
    # 3. MACD의 0(제로)는 MACD와 시그널의 크로스를 의미한다.
    # 4. MACD의 천장 - 상승 추세에서 가격이 상승, 상향 힘을 약화 == MACD는 천장을 친다. -1
    #    MACD의 바닥 - 하향 추세에서 가격이 하락, 하향 힘을 약화 == MACD는 바닥을 친다. +1
    # 5. 가격이 상승하고 있는데 MACD가 하강을 시작하면 천장이 가까운 것으로 추정된다.
    #    가격이 하락하고 있는데 MACD가 상승을 시작하면 바닥이 가까운 것으로 추정된다.
    # 6. 감소하고 있던 오실레이터가 증가로 전환 +1
    #    증가하고 있던 오실레이터가 감소로 전환 -1

    ###########################################
    
    print("turn on the trader!")
    sell_count = 0

    while True:
        print("판단 근거 확인")

        print("0.MACD의 상승 및 하락 확인")
        if MACD[0] > MACD[1]:
            sell_count += 1
            print("MACD의 상승 추세")
        elif MACD[0] < MACD[1]:
            sell_count -= 1
            print("MACD의 하락 추세")
        print("sell_count: " + sell_count)

        print("1.골든 크로스 및 데드 크로스 확인")
        # 진성 및 가성 판단할 필요가 있음
        # 진성 golden&death cross graph 개형 확인
        # fake cross에 유의하여 수수료 낭비하지 않기
        for i in range(0, 200):
            if MACD[i+1] < MACD[i]:
                if MACD[i+1] - Signal[i+1] < 0 and MACD[i] - Signal[i] > 0:
                    print("Golden Cross Occurred!")
                    sell_count += 1
                    break
            elif MACD[i+1] > MACD[i]:
                if MACD[i+i] - Signal[i+1] > 0 and MACD[i] - Signal[i] < 0:
                    print("Death Cross Occurred!")
                    sell_count -= 1
                    break
            else pass

        print("2.MACD의 천장 및 바닥 확인")
        # TODO

        print("3.Oscillator 상승 및 하락 확인")
        for i in range(0, 200):
            if Oscillator[i+2] > Oscillator[i+1]:
                if Oscillator[i+1] < Oscillator[i]:
                    print("Positive Oscillator!")
                    sell_count += 1
                    break
            elif Oscillator[i+2] < Oscillator[i+1]:
                if Oscillator[i+1] > Oscillator[i]:
                    print("Negative Oscillator!")
                    sell_count -= 1
                    break
            else break


        # 최종 매매 판단
        if sell_count > 0:
            # 매수
            # TODO

        elif sell_count < 0:
            # 매도
            # TODO



        # 시세 계속 확인(MACD, 단순 시세, 시그널 등)

    # 각각 요인들을 확인하고 sell_count를 조정
    # sell_count가 양수일 경우 -> 매수
    # sell_count가 음수일 경우 -> 매도
    # 초기 프로토 타입은 BTC로만 작동


##############################################################

if __name__ == '__main__':
    main()