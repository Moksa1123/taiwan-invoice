#!/usr/bin/env python3
"""
台灣金流 API 連線測試腳本

支援平台: ECPay, NewebPay, PayUNi

用法:
    python test_payment.py                    # 測試 ECPay 連線
    python test_payment.py --platform newebpay # 測試 NewebPay 連線
    python test_payment.py --platform payuni   # 測試 PayUNi 連線
    python test_payment.py --list             # 列出支援平台
    python test_payment.py --create           # 建立測試訂單
    python test_payment.py --query ORDER123   # 查詢訂單
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

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


# 平台設定
PLATFORMS = {
    'ecpay': {
        'name': '綠界科技 ECPay',
        'merchant_id': '3002607',
        'hash_key': 'pwFHCqoQZGmho4w6',
        'hash_iv': 'EkRm7iFT261dpevs',
        'api_url': 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5',
        'query_url': 'https://payment-stage.ecpay.com.tw/Cashier/QueryTradeInfo/V5',
        'test_url': 'https://payment-stage.ecpay.com.tw/',
        'auth_method': 'SHA256',
        'test_card': '4311-9522-2222-2222',
    },
    'newebpay': {
        'name': '藍新金流 NewebPay',
        'merchant_id': '請至後台申請',
        'hash_key': '請至後台申請',
        'hash_iv': '請至後台申請',
        'api_url': 'https://ccore.newebpay.com/MPG/mpg_gateway',
        'query_url': 'https://ccore.newebpay.com/API/QueryTradeInfo',
        'test_url': 'https://ccore.newebpay.com/',
        'auth_method': 'AES-256-CBC',
        'test_card': '4000-2211-1111-1111',
    },
    'payuni': {
        'name': '統一金流 PAYUNi',
        'merchant_id': '請至後台申請',
        'hash_key': '請至後台申請',
        'hash_iv': '請至後台申請',
        'api_url': 'https://sandbox-api.payuni.com.tw/api/upp',
        'query_url': 'https://sandbox-api.payuni.com.tw/api/trade_query',
        'test_url': 'https://sandbox-api.payuni.com.tw/',
        'auth_method': 'AES-256-GCM',
        'test_card': '4000-2211-1111-1111',
    },
}


def generate_ecpay_mac(params: dict, hash_key: str, hash_iv: str) -> str:
    """ECPay CheckMacValue (SHA256)"""
    sorted_params = sorted(params.items())
    param_str = '&'.join(f'{k}={v}' for k, v in sorted_params)
    raw = f'HashKey={hash_key}&{param_str}&HashIV={hash_iv}'
    encoded = urllib.parse.quote_plus(raw).lower()
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest().upper()


def generate_newebpay_trade_info(params: dict, hash_key: str, hash_iv: str) -> str:
    """NewebPay TradeInfo (AES-256-CBC)"""
    if not HAS_CRYPTO:
        return "需要 pycryptodome 套件"
    query_string = urllib.parse.urlencode(params)
    cipher = AES.new(hash_key.encode('utf-8'), AES.MODE_CBC, hash_iv.encode('utf-8'))
    padded = pad(query_string.encode('utf-8'), AES.block_size)
    encrypted = cipher.encrypt(padded)
    return encrypted.hex()


def generate_newebpay_sha(trade_info: str, hash_key: str, hash_iv: str) -> str:
    """NewebPay TradeSha (SHA256)"""
    raw = f'HashKey={hash_key}&{trade_info}&HashIV={hash_iv}'
    return hashlib.sha256(raw.encode('utf-8')).hexdigest().upper()


def generate_payuni_encrypt(params: dict, hash_key: str, hash_iv: str) -> str:
    """PayUNi EncryptInfo (AES-256-GCM)"""
    if not HAS_CRYPTO:
        return "需要 pycryptodome 套件"
    query_string = urllib.parse.urlencode(params)
    cipher = AES.new(hash_key.encode('utf-8'), AES.MODE_GCM, nonce=hash_iv.encode('utf-8'))
    encrypted, tag = cipher.encrypt_and_digest(query_string.encode('utf-8'))
    return (encrypted + tag).hex()


def generate_payuni_hash(encrypt_info: str, hash_key: str, hash_iv: str) -> str:
    """PayUNi HashInfo (SHA256)"""
    raw = encrypt_info + hash_key + hash_iv
    return hashlib.sha256(raw.encode('utf-8')).hexdigest().upper()


def test_connection(platform: str):
    """測試 API 連線"""
    config = PLATFORMS.get(platform)
    if not config:
        print(f'錯誤: 不支援的平台 "{platform}"')
        print(f'支援的平台: {", ".join(PLATFORMS.keys())}')
        sys.exit(1)

    print('=' * 60)
    print(f'{config["name"]} API 連線測試')
    print('=' * 60)
    print()

    # 測試環境資訊
    print('[測試環境]')
    print(f'  平台: {config["name"]}')
    print(f'  商店代號: {config["merchant_id"]}')
    print(f'  加密方式: {config["auth_method"]}')
    print(f'  測試網址: {config["test_url"]}')
    print()

    # 測試加密計算
    print('[加密計算測試]')
    if platform == 'ecpay':
        test_params = {
            'MerchantID': config['merchant_id'],
            'MerchantTradeNo': 'TEST123456',
            'TotalAmount': 100,
        }
        mac = generate_ecpay_mac(test_params, config['hash_key'], config['hash_iv'])
        print(f'  CheckMacValue: {mac}')
        print(f'  長度: {len(mac)} (應為 64)')
        print(f'  格式: {"正確" if len(mac) == 64 else "錯誤"}')

    elif platform == 'newebpay':
        if HAS_CRYPTO and config['hash_key'] != '請至後台申請':
            test_params = {
                'MerchantID': config['merchant_id'],
                'MerchantOrderNo': 'TEST123456',
                'Amt': 100,
            }
            trade_info = generate_newebpay_trade_info(test_params, config['hash_key'], config['hash_iv'])
            trade_sha = generate_newebpay_sha(trade_info, config['hash_key'], config['hash_iv'])
            print(f'  TradeInfo: {trade_info[:50]}...')
            print(f'  TradeSha: {trade_sha}')
        else:
            print('  (需要設定 hash_key/hash_iv 及 pycryptodome 套件)')

    elif platform == 'payuni':
        if HAS_CRYPTO and config['hash_key'] != '請至後台申請':
            test_params = {
                'MerID': config['merchant_id'],
                'MerTradeNo': 'TEST123456',
                'TradeAmt': 100,
            }
            encrypt_info = generate_payuni_encrypt(test_params, config['hash_key'], config['hash_iv'])
            hash_info = generate_payuni_hash(encrypt_info, config['hash_key'], config['hash_iv'])
            print(f'  EncryptInfo: {encrypt_info[:50]}...')
            print(f'  HashInfo: {hash_info}')
        else:
            print('  (需要設定 hash_key/hash_iv 及 pycryptodome 套件)')
    print()

    # 測試網路連線
    if HAS_REQUESTS:
        print('[網路連線測試]')
        try:
            response = requests.head(config['test_url'], timeout=5)
            print(f'  狀態碼: {response.status_code}')
            print(f'  連線: {"成功" if response.status_code < 500 else "失敗"}')
        except requests.RequestException as e:
            print(f'  連線失敗: {e}')
    else:
        print('[網路連線測試]')
        print('  (需要 requests 套件: pip install requests)')
    print()

    # 顯示測試信用卡
    print('[測試信用卡]')
    print(f'  卡號: {config["test_card"]}')
    print('  有效期: 任意未過期日期')
    print('  CVV: 任意三碼')
    print()

    print('=' * 60)
    print('測試完成')
    print('=' * 60)


def create_test_order(platform: str):
    """建立測試訂單"""
    config = PLATFORMS.get(platform)
    if not config:
        print(f'錯誤: 不支援的平台 "{platform}"')
        sys.exit(1)

    if config['merchant_id'] == '請至後台申請':
        print(f'錯誤: 請先設定 {config["name"]} 的測試帳號')
        print('請編輯此腳本，填入您的測試商店資訊')
        sys.exit(1)

    order_id = f'TEST{int(time.time())}'
    trade_date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    print('=' * 60)
    print(f'建立 {config["name"]} 測試訂單')
    print('=' * 60)
    print()
    print(f'訂單編號: {order_id}')
    print(f'交易時間: {trade_date}')
    print(f'金額: 100 TWD')
    print()

    if platform == 'ecpay':
        params = {
            'MerchantID': config['merchant_id'],
            'MerchantTradeNo': order_id,
            'MerchantTradeDate': trade_date,
            'PaymentType': 'aio',
            'TotalAmount': 100,
            'TradeDesc': urllib.parse.quote('測試訂單'),
            'ItemName': '測試商品 x 1',
            'ReturnURL': 'https://example.com/callback',
            'ChoosePayment': 'Credit',
            'EncryptType': 1,
        }
        params['CheckMacValue'] = generate_ecpay_mac(params, config['hash_key'], config['hash_iv'])

        html = f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>ECPay 測試</title></head>
<body>
<h1>ECPay 測試訂單 {order_id}</h1>
<form method="post" action="{config['api_url']}">
'''
        for k, v in params.items():
            html += f'<input type="hidden" name="{k}" value="{v}">\n'
        html += '<button type="submit">前往付款</button>\n</form>\n</body></html>'

        filename = f'ecpay_test_{order_id}.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f'已產生測試頁面: {filename}')
        print('請在瀏覽器中開啟此檔案進行付款測試')
        print()
        print(f'測試信用卡: {config["test_card"]}')

    else:
        print(f'{platform} 的測試訂單建立功能需要 pycryptodome 套件')
        print('請執行: pip install pycryptodome')


def query_order(platform: str, order_id: str):
    """查詢訂單狀態"""
    if not HAS_REQUESTS:
        print('錯誤: 需要 requests 套件')
        sys.exit(1)

    config = PLATFORMS.get(platform)
    if not config:
        print(f'錯誤: 不支援的平台 "{platform}"')
        sys.exit(1)

    print('=' * 60)
    print(f'查詢 {config["name"]} 訂單: {order_id}')
    print('=' * 60)
    print()

    if platform == 'ecpay':
        params = {
            'MerchantID': config['merchant_id'],
            'MerchantTradeNo': order_id,
            'TimeStamp': int(time.time()),
        }
        params['CheckMacValue'] = generate_ecpay_mac(params, config['hash_key'], config['hash_iv'])

        try:
            response = requests.post(config['query_url'], data=params, timeout=10)
            print(f'HTTP 狀態碼: {response.status_code}')
            print('回應內容:')
            print(response.text)
        except requests.RequestException as e:
            print(f'查詢失敗: {e}')
    else:
        print(f'{platform} 的查詢功能需要額外設定')


def list_platforms():
    """列出支援的平台"""
    print('=' * 60)
    print('支援的金流平台')
    print('=' * 60)
    print()
    for key, config in PLATFORMS.items():
        print(f'  {key:12} - {config["name"]}')
        print(f'                 加密: {config["auth_method"]}')
        print(f'                 測試: {config["test_url"]}')
        print()


def main():
    parser = argparse.ArgumentParser(
        description='台灣金流 API 測試工具 (支援 ECPay/NewebPay/PayUNi)'
    )
    parser.add_argument(
        '--platform', '-p',
        type=str,
        default='ecpay',
        help='金流平台 (ecpay/newebpay/payuni)'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出支援的平台'
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

    if args.list:
        list_platforms()
    elif args.create:
        create_test_order(args.platform)
    elif args.query:
        query_order(args.platform, args.query)
    else:
        test_connection(args.platform)


if __name__ == '__main__':
    main()
