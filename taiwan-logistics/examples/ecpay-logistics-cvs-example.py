#!/usr/bin/env python3
"""
ECPay 超商取貨範例
示範如何使用 ECPay 物流 API 建立、查詢、列印超商取貨訂單
"""

import hashlib
import urllib.parse
from datetime import datetime


class ECPayLogistics:
    """ECPay 物流 API 封裝"""

    def __init__(self, merchant_id, hash_key, hash_iv, test_mode=True):
        self.merchant_id = merchant_id
        self.hash_key = hash_key
        self.hash_iv = hash_iv
        self.api_url = "https://logistics-stage.ecpay.com.tw" if test_mode else "https://logistics.ecpay.com.tw"

    def create_check_mac_value(self, params):
        """生成 CheckMacValue"""
        # 1. 參數排序
        sorted_params = sorted(params.items())

        # 2. 串接字串
        param_str = "&".join([f"{k}={v}" for k, v in sorted_params])

        # 3. 加上 HashKey 和 HashIV
        raw_str = f"HashKey={self.hash_key}&{param_str}&HashIV={self.hash_iv}"

        # 4. URL Encode
        encoded_str = urllib.parse.quote(raw_str, safe="")

        # 5. 轉小寫
        encoded_str = encoded_str.lower()

        # 6. SHA256 加密
        hash_value = hashlib.sha256(encoded_str.encode('utf-8')).hexdigest()

        # 7. 轉大寫
        return hash_value.upper()

    def create_cvs_order(self, order_id, goods_name, goods_amount, receiver_name,
                        receiver_phone, receiver_store_id, logistics_sub_type="UNIMARTC2C"):
        """建立超商取貨訂單"""
        params = {
            "MerchantID": self.merchant_id,
            "MerchantTradeNo": order_id,
            "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "LogisticsType": "CVS",
            "LogisticsSubType": logistics_sub_type,  # UNIMARTC2C, FAMIC2C, HILIFEC2C
            "GoodsAmount": goods_amount,
            "GoodsName": goods_name,
            "SenderName": "測試商家",
            "SenderPhone": "0212345678",
            "SenderCellPhone": "0912345678",
            "ReceiverName": receiver_name,
            "ReceiverCellPhone": receiver_phone,
            "ReceiverStoreID": receiver_store_id,
            "ServerReplyURL": "https://yourdomain.com/logistics/callback",
            "IsCollection": "N",  # 是否代收貨款
            "Temperature": "0001",  # 常溫
            "Distance": "00",  # 距離
            "Specification": "0001",  # 60cm
        }

        # 生成 CheckMacValue
        params["CheckMacValue"] = self.create_check_mac_value(params)

        return params

    def query_order(self, logistics_id):
        """查詢物流訂單"""
        params = {
            "MerchantID": self.merchant_id,
            "AllPayLogisticsID": logistics_id,
            "TimeStamp": str(int(datetime.now().timestamp())),
        }

        params["CheckMacValue"] = self.create_check_mac_value(params)

        return params

    def print_order(self, logistics_id):
        """列印託運單"""
        params = {
            "MerchantID": self.merchant_id,
            "AllPayLogisticsID": logistics_id,
        }

        params["CheckMacValue"] = self.create_check_mac_value(params)

        return params


def example_create_order():
    """範例1: 建立超商取貨訂單"""
    print("\n=== 範例1: 建立超商取貨訂單 ===\n")

    # 初始化 ECPay
    ecpay = ECPayLogistics(
        merchant_id="2000132",  # 測試商店代號
        hash_key="5294y06JbISpM5x9",  # 測試 HashKey
        hash_iv="v77hoKGq4kWxNNIS",  # 測試 HashIV
        test_mode=True
    )

    # 建立訂單
    order_id = f"ORDER{int(datetime.now().timestamp())}"
    params = ecpay.create_cvs_order(
        order_id=order_id,
        goods_name="測試商品",
        goods_amount=100,
        receiver_name="王小明",
        receiver_phone="0912345678",
        receiver_store_id="991182",  # 7-11 門市代號
        logistics_sub_type="UNIMARTC2C"  # 7-11 店到店
    )

    print("訂單參數:")
    for key, value in params.items():
        print(f"  {key}: {value}")


def example_query_order():
    """範例2: 查詢物流訂單"""
    print("\n=== 範例2: 查詢物流訂單 ===\n")

    ecpay = ECPayLogistics(
        merchant_id="2000132",
        hash_key="5294y06JbISpM5x9",
        hash_iv="v77hoKGq4kWxNNIS",
        test_mode=True
    )

    # 查詢訂單 (使用物流交易編號)
    logistics_id = "10001234567"  # 綠界物流交易編號
    params = ecpay.query_order(logistics_id)

    print("查詢參數:")
    for key, value in params.items():
        print(f"  {key}: {value}")


def example_print_order():
    """範例3: 列印託運單"""
    print("\n=== 範例3: 列印託運單 ===\n")

    ecpay = ECPayLogistics(
        merchant_id="2000132",
        hash_key="5294y06JbISpM5x9",
        hash_iv="v77hoKGq4kWxNNIS",
        test_mode=True
    )

    # 列印託運單
    logistics_id = "10001234567"
    params = ecpay.print_order(logistics_id)

    print("列印參數:")
    for key, value in params.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    print("ECPay 物流 API 範例")
    print("=" * 50)

    example_create_order()
    example_query_order()
    example_print_order()

    print("\n" + "=" * 50)
    print("範例執行完成")
