#!/usr/bin/env python3
"""
NewebPay 藍新金流 Python 完整範例

依照 taiwan-payment-skill 最高規範撰寫
支援: MPG 整合支付 (信用卡、ATM、超商代碼、LINE Pay、Apple Pay 等)

API 文件: https://www.newebpay.com
"""

import hashlib
import urllib.parse
import json
from datetime import datetime
from typing import Dict, Literal, Optional
from dataclasses import dataclass, field

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


@dataclass
class MPGOrderData:
    """NewebPay MPG 付款訂單資料"""
    merchant_order_no: str
    amt: int
    item_desc: str
    email: str
    return_url: str
    notify_url: Optional[str] = None
    client_back_url: Optional[str] = None
    enable_credit: bool = True
    enable_vacc: bool = False
    enable_cvs: bool = False
    enable_barcode: bool = False
    enable_linepay: bool = False
    enable_applepay: bool = False
    login_type: int = 0
    order_comment: Optional[str] = None
    trade_limit: int = 900
    exp_date: Optional[str] = None


@dataclass
class MPGOrderResponse:
    """NewebPay MPG 付款訂單回應"""
    success: bool
    merchant_order_no: str
    form_action: str = ''
    trade_info: str = ''
    trade_sha: str = ''
    merchant_id: str = ''
    version: str = ''
    error_message: str = ''
    raw: Dict[str, str] = field(default_factory=dict)


@dataclass
class MPGCallbackData:
    """NewebPay MPG 付款回傳資料"""
    status: str
    message: str
    merchant_order_no: str
    amt: int
    trade_no: str
    merchant_id: str
    payment_type: str
    pay_time: str
    ip: str
    esc_row_bank_acount: Optional[str] = None
    code_no: Optional[str] = None
    barcode_1: Optional[str] = None
    barcode_2: Optional[str] = None
    barcode_3: Optional[str] = None
    expire_date: Optional[str] = None
    raw: Dict = field(default_factory=dict)


class NewebPayMPGService:
    """
    NewebPay 藍新金流 MPG 整合支付服務

    認證方式: AES-256-CBC + SHA256
    加密方式: 雙層加密 (AES 加密 + SHA256 驗證)

    支援付款方式:
    - CREDIT: 信用卡
    - VACC: ATM 轉帳
    - CVS: 超商代碼
    - BARCODE: 超商條碼
    - LINEPAY: LINE Pay
    - APPLEPAY: Apple Pay

    測試環境說明:
    - 需至藍新金流申請測試帳號
    - 測試網址: https://ccore.newebpay.com
    """

    # 測試環境
    TEST_API_URL = 'https://ccore.newebpay.com/MPG/mpg_gateway'
    TEST_QUERY_URL = 'https://ccore.newebpay.com/API/QueryTradeInfo'

    # 正式環境
    PROD_API_URL = 'https://core.newebpay.com/MPG/mpg_gateway'
    PROD_QUERY_URL = 'https://core.newebpay.com/API/QueryTradeInfo'

    def __init__(
        self,
        merchant_id: str,
        hash_key: str,
        hash_iv: str,
        is_production: bool = False
    ):
        """
        初始化 NewebPay MPG 服務

        Args:
            merchant_id: 商店代號
            hash_key: HashKey (32 字元)
            hash_iv: HashIV (16 字元)
            is_production: 是否為正式環境 (預設 False)

        Raises:
            ImportError: 缺少 pycryptodome 套件
        """
        if not HAS_CRYPTO:
            raise ImportError('需要安裝 pycryptodome: pip install pycryptodome')

        self.merchant_id = merchant_id
        self.hash_key = hash_key.encode('utf-8')
        self.hash_iv = hash_iv.encode('utf-8')
        self.api_url = self.PROD_API_URL if is_production else self.TEST_API_URL
        self.query_url = self.PROD_QUERY_URL if is_production else self.TEST_QUERY_URL

    def encrypt_trade_info(self, data: Dict[str, any]) -> str:
        """
        加密 TradeInfo (AES-256-CBC)

        Args:
            data: 交易資料字典

        Returns:
            str: AES 加密後的 hex 字串

        Example:
            >>> data = {'MerchantID': 'MS123', 'Amt': 100}
            >>> encrypted = service.encrypt_trade_info(data)
            >>> len(encrypted) > 0
            True
        """
        # 步驟 1: 轉換為查詢字串
        query_string = urllib.parse.urlencode(data)

        # 步驟 2: AES-256-CBC 加密
        cipher = AES.new(self.hash_key, AES.MODE_CBC, self.hash_iv)
        padded = pad(query_string.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded)

        # 步驟 3: 轉換為 hex
        return encrypted.hex()

    def decrypt_trade_info(self, encrypted_data: str) -> Dict[str, any]:
        """
        解密 TradeInfo (AES-256-CBC)

        Args:
            encrypted_data: AES 加密的 hex 字串

        Returns:
            Dict: 解密後的資料字典

        Raises:
            ValueError: 解密失敗
        """
        try:
            # 步驟 1: hex 轉 bytes
            encrypted_bytes = bytes.fromhex(encrypted_data)

            # 步驟 2: AES-256-CBC 解密
            decipher = AES.new(self.hash_key, AES.MODE_CBC, self.hash_iv)
            decrypted = decipher.decrypt(encrypted_bytes)
            unpadded = unpad(decrypted, AES.block_size)

            # 步驟 3: 解析查詢字串
            query_string = unpadded.decode('utf-8')
            params = urllib.parse.parse_qs(query_string)

            # 步驟 4: 轉換為單值字典
            result = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
            return result
        except Exception as e:
            raise ValueError(f'解密失敗: {str(e)}')

    def generate_trade_sha(self, trade_info: str) -> str:
        """
        產生 TradeSha (SHA256)

        Args:
            trade_info: 加密後的 TradeInfo

        Returns:
            str: SHA256 雜湊值 (大寫)

        Example:
            >>> trade_sha = service.generate_trade_sha('abcd1234')
            >>> len(trade_sha)
            64
        """
        # 組合字串: HashKey=xxx&TradeInfo=xxx&HashIV=xxx
        raw = f"HashKey={self.hash_key.decode('utf-8')}&{trade_info}&HashIV={self.hash_iv.decode('utf-8')}"

        # SHA256 雜湊並轉大寫
        return hashlib.sha256(raw.encode('utf-8')).hexdigest().upper()

    def verify_trade_sha(self, trade_info: str, trade_sha: str) -> bool:
        """
        驗證 TradeSha

        Args:
            trade_info: 加密後的 TradeInfo
            trade_sha: 接收到的 TradeSha

        Returns:
            bool: 驗證是否通過
        """
        calculated_sha = self.generate_trade_sha(trade_info)
        return calculated_sha == trade_sha.upper()

    def create_order(
        self,
        data: MPGOrderData,
    ) -> MPGOrderResponse:
        """
        建立 MPG 整合支付訂單

        Args:
            data: MPG 訂單資料 (MPGOrderData)

        Returns:
            MPGOrderResponse: MPG 訂單回應

        Raises:
            ValueError: 參數驗證失敗

        Example:
            >>> order_data = MPGOrderData(
            ...     merchant_order_no=f'MPG{int(time.time())}',
            ...     amt=2500,
            ...     item_desc='測試商品',
            ...     email='test@example.com',
            ...     return_url='https://your-site.com/callback',
            ...     enable_credit=True,
            ...     enable_vacc=True,
            ...     enable_cvs=True,
            ... )
            >>> result = service.create_order(order_data)
            >>> print(result.form_action)
        """
        # 參數驗證
        if data.amt < 1:
            raise ValueError('金額必須大於 0')
        if len(data.merchant_order_no) > 30:
            raise ValueError('訂單編號不可超過 30 字元')

        # 準備 API 參數
        trade_info_data = {
            'MerchantID': self.merchant_id,
            'RespondType': 'JSON',
            'TimeStamp': str(int(datetime.now().timestamp())),
            'Version': '2.0',
            'MerchantOrderNo': data.merchant_order_no,
            'Amt': data.amt,
            'ItemDesc': data.item_desc,
            'Email': data.email,
            'ReturnURL': data.return_url,
            'LoginType': data.login_type,
            'TradeLimit': data.trade_limit,
        }

        # 啟用付款方式
        if data.enable_credit:
            trade_info_data['CREDIT'] = 1
        if data.enable_vacc:
            trade_info_data['VACC'] = 1
        if data.enable_cvs:
            trade_info_data['CVS'] = 1
        if data.enable_barcode:
            trade_info_data['BARCODE'] = 1
        if data.enable_linepay:
            trade_info_data['LINEPAY'] = 1
        if data.enable_applepay:
            trade_info_data['APPLEPAY'] = 1

        # 可選參數
        if data.notify_url:
            trade_info_data['NotifyURL'] = data.notify_url
        if data.client_back_url:
            trade_info_data['ClientBackURL'] = data.client_back_url
        if data.order_comment:
            trade_info_data['OrderComment'] = data.order_comment
        if data.exp_date:
            trade_info_data['ExpDate'] = data.exp_date

        # 加密 TradeInfo
        trade_info = self.encrypt_trade_info(trade_info_data)

        # 產生 TradeSha
        trade_sha = self.generate_trade_sha(trade_info)

        # 回傳表單資料
        return MPGOrderResponse(
            success=True,
            merchant_order_no=data.merchant_order_no,
            form_action=self.api_url,
            trade_info=trade_info,
            trade_sha=trade_sha,
            merchant_id=self.merchant_id,
            version='2.0',
            raw={'TradeInfo': trade_info, 'TradeSha': trade_sha},
        )

    def parse_callback(self, callback_data: Dict[str, str]) -> MPGCallbackData:
        """
        解析 MPG 付款回傳資料

        Args:
            callback_data: POST 回傳的參數字典

        Returns:
            MPGCallbackData: 解析後的回傳資料

        Raises:
            ValueError: TradeSha 驗證失敗或解密失敗

        Example:
            >>> callback = request.form.to_dict()
            >>> result = service.parse_callback(callback)
            >>> if result.status == 'SUCCESS':
            ...     print(f"付款成功: {result.trade_no}")
        """
        # 驗證 TradeSha
        trade_info = callback_data.get('TradeInfo', '')
        trade_sha = callback_data.get('TradeSha', '')

        if not self.verify_trade_sha(trade_info, trade_sha):
            raise ValueError('TradeSha 驗證失敗')

        # 解密 TradeInfo
        decrypted = self.decrypt_trade_info(trade_info)

        # 解析回傳資料
        result_data = decrypted.get('Result', '')
        if isinstance(result_data, str):
            try:
                result_dict = json.loads(result_data)
            except:
                result_dict = {}
        else:
            result_dict = result_data

        return MPGCallbackData(
            status=decrypted.get('Status', ''),
            message=decrypted.get('Message', ''),
            merchant_order_no=result_dict.get('MerchantOrderNo', ''),
            amt=int(result_dict.get('Amt', 0)),
            trade_no=result_dict.get('TradeNo', ''),
            merchant_id=result_dict.get('MerchantID', ''),
            payment_type=result_dict.get('PaymentType', ''),
            pay_time=result_dict.get('PayTime', ''),
            ip=result_dict.get('IP', ''),
            esc_row_bank_acount=result_dict.get('EscrowBankAcount'),
            code_no=result_dict.get('CodeNo'),
            barcode_1=result_dict.get('Barcode_1'),
            barcode_2=result_dict.get('Barcode_2'),
            barcode_3=result_dict.get('Barcode_3'),
            expire_date=result_dict.get('ExpireDate'),
            raw=decrypted,
        )


# Usage Example
if __name__ == '__main__':
    print('=' * 60)
    print('NewebPay 藍新金流 MPG - Python 範例')
    print('=' * 60)
    print()

    # 檢查是否有 pycryptodome
    if not HAS_CRYPTO:
        print('✗ 錯誤: 需要安裝 pycryptodome 套件')
        print('  請執行: pip install pycryptodome')
        exit(1)

    # 注意: 需要替換為您的測試帳號
    print('[注意] 請先至藍新金流申請測試帳號')
    print('並將以下參數替換為您的測試環境資訊')
    print()

    # 初始化服務 (使用測試環境)
    service = NewebPayMPGService(
        merchant_id='YOUR_MERCHANT_ID',  # 請替換為您的商店代號
        hash_key='YOUR_HASH_KEY',  # 請替換為您的 HashKey (32字元)
        hash_iv='YOUR_HASH_IV',  # 請替換為您的 HashIV (16字元)
        is_production=False,
    )

    # 範例: 建立 MPG 整合支付訂單
    print('[範例] 建立 MPG 整合支付訂單')
    print('-' * 60)

    order_data = MPGOrderData(
        merchant_order_no=f'MPG{int(datetime.now().timestamp())}',
        amt=2500,
        item_desc='測試商品購買',
        email='test@example.com',
        return_url='https://your-site.com/api/payment/callback',
        notify_url='https://your-site.com/api/payment/notify',
        client_back_url='https://your-site.com/order/complete',
        enable_credit=True,  # 啟用信用卡
        enable_vacc=True,  # 啟用 ATM
        enable_cvs=True,  # 啟用超商代碼
    )

    try:
        result = service.create_order(order_data)

        if result.success:
            print(f'✓ 訂單建立成功')
            print(f'  訂單編號: {result.merchant_order_no}')
            print(f'  表單網址: {result.form_action}')
            print(f'  TradeInfo: {result.trade_info[:50]}...')
            print(f'  TradeSha: {result.trade_sha[:32]}...')
            print()
            print('請將以下參數 POST 到表單網址:')
            print(f'  MerchantID: {result.merchant_id}')
            print(f'  TradeInfo: {result.trade_info}')
            print(f'  TradeSha: {result.trade_sha}')
            print(f'  Version: {result.version}')
        else:
            print(f'✗ 訂單建立失敗: {result.error_message}')
    except Exception as e:
        print(f'✗ 發生例外: {str(e)}')

    print()
    print('=' * 60)
    print('範例執行完成')
    print('=' * 60)
