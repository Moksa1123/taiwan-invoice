#!/usr/bin/env python3
"""
ECPay Logistics API 連線測試腳本

用法:
    python test_logistics.py              # 測試連線
    python test_logistics.py --create     # 建立測試訂單
    python test_logistics.py --query ORDER123  # 查詢訂單
"""

import hashlib
import urllib.parse
import time
import sys
import argparse
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ECPay 測試環境設定
TEST_CONFIG = {
    'merchant_id': '2000132',
    'hash_key': '5294y06JbISpM5x9',
    'hash_iv': 'v77hoKGq4kWxNNIS',
    'create_url': 'https://logistics-stage.ecpay.com.tw/Express/Create',
    'query_url': 'https://logistics-stage.ecpay.com.tw/Helper/QueryLogisticsTradeInfo/V2',
}


def generate_check_mac_value(params: dict, hash_key: str, hash_iv: str) -> str:
    """計算 CheckMacValue (MD5)"""
    sorted_params = sorted(params.items())
    param_str = '&'.join(f'{k}={v}' for k, v in sorted_params)
    raw = f'HashKey={hash_key}&{param_str}&HashIV={hash_iv}'
    encoded = urllib.parse.quote_plus(raw).lower()
    return hashlib.md5(encoded.encode('utf-8')).hexdigest().upper()


def test_connection():
    """測試 ECPay Logistics API 連線"""
    print('=' * 60)
    print('ECPay Logistics API 連線測試')
    print('=' * 60)
    print()

    # 測試環境資訊
    print('[測試環境]')
    print(f'  商店代號: {TEST_CONFIG["merchant_id"]}')
    print(f'  HashKey:  {TEST_CONFIG["hash_key"]}')
    print(f'  HashIV:   {TEST_CONFIG["hash_iv"]}')
    print()

    # 測試 CheckMacValue 計算
    print('[CheckMacValue 計算測試]')
    test_params = {
        'MerchantID': TEST_CONFIG['merchant_id'],
        'MerchantTradeNo': 'TEST123456',
        'LogisticsType': 'CVS',
    }

    mac = generate_check_mac_value(
        test_params,
        TEST_CONFIG['hash_key'],
        TEST_CONFIG['hash_iv']
    )
    print(f'  測試參數: {test_params}')
    print(f'  CheckMacValue: {mac}')
    print(f'  長度: {len(mac)} (應為 32, MD5)')
    print(f'  格式: {"正確" if len(mac) == 32 and mac.isupper() else "錯誤"}')
    print()

    # 測試網路連線
    if HAS_REQUESTS:
        print('[網路連線測試]')
        try:
            response = requests.head(
                'https://logistics-stage.ecpay.com.tw/',
                timeout=5
            )
            print(f'  狀態碼: {response.status_code}')
            print(f'  連線: {"成功" if response.status_code < 500 else "失敗"}')
        except requests.RequestException as e:
            print(f'  連線失敗: {e}')
    else:
        print('[網路連線測試]')
        print('  (需要 requests 套件: pip install requests)')
    print()

    print('=' * 60)
    print('測試完成')
    print('=' * 60)


def create_test_order():
    """建立測試物流訂單"""
    if not HAS_REQUESTS:
        print('錯誤: 需要 requests 套件')
        print('請執行: pip install requests')
        sys.exit(1)

    order_id = f'TEST{int(time.time())}'
    trade_date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    params = {
        'MerchantID': TEST_CONFIG['merchant_id'],
        'MerchantTradeNo': order_id,
        'MerchantTradeDate': trade_date,
        'LogisticsType': 'CVS',
        'LogisticsSubType': 'UNIMART',
        'GoodsAmount': 500,
        'GoodsName': '測試商品',
        'SenderName': '測試寄件人',
        'SenderPhone': '0912345678',
        'ReceiverName': '測試收件人',
        'ReceiverPhone': '0987654321',
        'ReceiverStoreID': '131386',  # 7-11 測試門市
        'IsCollection': 'N',
        'ServerReplyURL': 'https://example.com/callback',
    }

    params['CheckMacValue'] = generate_check_mac_value(
        params,
        TEST_CONFIG['hash_key'],
        TEST_CONFIG['hash_iv']
    )

    print('=' * 60)
    print('建立測試物流訂單')
    print('=' * 60)
    print()
    print(f'訂單編號: {order_id}')
    print(f'物流類型: 超商取貨 (7-11)')
    print(f'收件門市: 131386')
    print()

    try:
        response = requests.post(
            TEST_CONFIG['create_url'],
            data=params,
            timeout=30
        )

        print('回應:')
        result = {}
        for item in response.text.split('&'):
            if '=' in item:
                key, value = item.split('=', 1)
                result[key] = urllib.parse.unquote(value)
                print(f'  {key}: {result[key]}')

        if result.get('RtnCode') == '300':
            print()
            print('訂單建立成功!')
        else:
            print()
            print(f'訂單建立失敗: {result.get("RtnMsg", "未知錯誤")}')

    except requests.RequestException as e:
        print(f'請求失敗: {e}')


def query_order(order_id: str):
    """查詢物流訂單狀態"""
    if not HAS_REQUESTS:
        print('錯誤: 需要 requests 套件')
        print('請執行: pip install requests')
        sys.exit(1)

    params = {
        'MerchantID': TEST_CONFIG['merchant_id'],
        'AllPayLogisticsID': '',
        'MerchantTradeNo': order_id,
        'TimeStamp': int(time.time()),
    }

    params['CheckMacValue'] = generate_check_mac_value(
        params,
        TEST_CONFIG['hash_key'],
        TEST_CONFIG['hash_iv']
    )

    print('=' * 60)
    print(f'查詢訂單: {order_id}')
    print('=' * 60)
    print()

    try:
        response = requests.post(
            TEST_CONFIG['query_url'],
            data=params,
            timeout=10
        )

        print('回應:')
        for item in response.text.split('&'):
            if '=' in item:
                key, value = item.split('=', 1)
                print(f'  {key}: {urllib.parse.unquote(value)}')

    except requests.RequestException as e:
        print(f'查詢失敗: {e}')


def main():
    parser = argparse.ArgumentParser(
        description='ECPay Logistics API 測試工具'
    )
    parser.add_argument(
        '--create',
        action='store_true',
        help='建立測試訂單'
    )
    parser.add_argument(
        '--query',
        type=str,
        metavar='ORDER_ID',
        help='查詢訂單狀態'
    )

    args = parser.parse_args()

    if args.create:
        create_test_order()
    elif args.query:
        query_order(args.query)
    else:
        test_connection()


if __name__ == '__main__':
    main()
