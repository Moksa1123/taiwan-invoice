# PayUni Logistics API Reference

統一金流 (PAYUNi) 物流 API 完整參考文件。

---

## 目錄

1. [API 端點總覽](#api-端點總覽)
2. [測試環境](#測試環境)
3. [加密機制](#加密機制)
4. [物流類型](#物流類型)
5. [7-11 超商取貨](#7-11-超商取貨)
6. [黑貓宅配](#黑貓宅配)
7. [物流狀態通知](#物流狀態通知)
8. [物流狀態查詢](#物流狀態查詢)
9. [錯誤碼對照表](#錯誤碼對照表)
10. [常見問題排解](#常見問題排解)

---

## API 端點總覽

### 基礎 API 路徑

| 環境 | 基礎路徑 |
|------|----------|
| **測試環境** | `https://sandbox-api.payuni.com.tw/api/` |
| **正式環境** | `https://api.payuni.com.tw/api/` |

### 物流相關端點

| 功能 | 端點路徑 | 說明 |
|------|----------|------|
| 建立物流訂單 | `/logistics/create` | 建立物流託運單 |
| 物流狀態查詢 | `/logistics/query` | 查詢物流狀態 |
| 取消物流訂單 | `/logistics/cancel` | 取消物流訂單 |

---

## 測試環境

### 測試帳號

測試帳號請至 PayUni 後台申請：

```
後台網址: https://www.payuni.com.tw/
路徑: 會員 > 商店清單 > 指定商店名稱 > 串接設定
```

取得以下資訊：
- **商店代號 (MerID)**
- **Hash Key**
- **Hash IV**

### 測試環境端點

```
https://sandbox-api.payuni.com.tw/api/{endpoint}
```

### 注意事項

1. 物流幕後 API 需向 PayUni 申請開通
2. 建議使用固定 IP 主機，避免 IP 變動造成功能失效
3. 非即時付款 (超商代碼、虛擬帳號) 需等付款完成才會建立物流單

---

## 加密機制

PayUni 採用 **AES-256-GCM** 加密與 **SHA256 HMAC** 驗證。

### 加密流程

1. **準備參數** - 組合所有請求參數
2. **URL Encode** - 將參數轉為 Query String
3. **AES-256-GCM 加密** - 使用 Hash Key 和 Hash IV 加密
4. **產生 HashInfo** - 使用 SHA256 計算驗證碼
5. **發送請求** - 將加密資料 POST 至 API

### PHP 加密範例

```php
<?php

class PayuniEncryption
{
    private string $merKey;
    private string $merIV;

    public function __construct(string $merKey, string $merIV)
    {
        $this->merKey = $merKey;
        $this->merIV = $merIV;
    }

    /**
     * AES-256-GCM 加密
     */
    public function encrypt(array $params): string
    {
        // 1. 組合 Query String
        $queryString = http_build_query($params);

        // 2. AES-256-GCM 加密
        $tag = '';
        $encrypted = openssl_encrypt(
            $queryString,
            'aes-256-gcm',
            $this->merKey,
            OPENSSL_RAW_DATA,
            $this->merIV,
            $tag,
            '',
            16
        );

        // 3. 組合加密結果 (加密資料 + tag)
        $encryptInfo = bin2hex($encrypted . $tag);

        return $encryptInfo;
    }

    /**
     * AES-256-GCM 解密
     */
    public function decrypt(string $encryptInfo): array
    {
        // 1. Hex 轉 Binary
        $data = hex2bin($encryptInfo);

        // 2. 分離加密資料和 tag
        $encrypted = substr($data, 0, -16);
        $tag = substr($data, -16);

        // 3. AES-256-GCM 解密
        $decrypted = openssl_decrypt(
            $encrypted,
            'aes-256-gcm',
            $this->merKey,
            OPENSSL_RAW_DATA,
            $this->merIV,
            $tag
        );

        // 4. 解析 Query String
        parse_str($decrypted, $result);

        return $result;
    }

    /**
     * 產生 HashInfo (SHA256)
     */
    public function hashInfo(string $encryptInfo): string
    {
        $raw = $encryptInfo . $this->merKey . $this->merIV;
        return strtoupper(hash('sha256', $raw));
    }
}
```

### Python 加密範例

```python
"""PayUni AES-256-GCM 加密"""

from Crypto.Cipher import AES
from urllib.parse import urlencode, parse_qs
import hashlib


class PayuniEncryption:
    def __init__(self, mer_key: str, mer_iv: str):
        self.mer_key = mer_key.encode('utf-8')
        self.mer_iv = mer_iv.encode('utf-8')

    def encrypt(self, params: dict) -> str:
        """AES-256-GCM 加密"""
        # 1. 組合 Query String
        query_string = urlencode(params)

        # 2. AES-256-GCM 加密
        cipher = AES.new(self.mer_key, AES.MODE_GCM, nonce=self.mer_iv)
        encrypted, tag = cipher.encrypt_and_digest(query_string.encode('utf-8'))

        # 3. 組合加密結果
        encrypt_info = (encrypted + tag).hex()

        return encrypt_info

    def decrypt(self, encrypt_info: str) -> dict:
        """AES-256-GCM 解密"""
        # 1. Hex 轉 Binary
        data = bytes.fromhex(encrypt_info)

        # 2. 分離加密資料和 tag
        encrypted = data[:-16]
        tag = data[-16:]

        # 3. AES-256-GCM 解密
        cipher = AES.new(self.mer_key, AES.MODE_GCM, nonce=self.mer_iv)
        decrypted = cipher.decrypt_and_verify(encrypted, tag)

        # 4. 解析 Query String
        result = dict(parse_qs(decrypted.decode('utf-8')))
        return {k: v[0] for k, v in result.items()}

    def hash_info(self, encrypt_info: str) -> str:
        """產生 HashInfo (SHA256)"""
        raw = encrypt_info + self.mer_key.decode() + self.mer_iv.decode()
        return hashlib.sha256(raw.encode('utf-8')).hexdigest().upper()
```

---

## 物流類型

### 支援的物流服務

| 物流類型 | 代碼 | 溫層 | 說明 |
|----------|------|------|------|
| 7-11 店到店 (C2C) | `PAYUNi_Logistic_711` | 常溫 | 消費者自行寄件 |
| 7-11 店到店冷凍 | `PAYUNi_Logistic_711_Freeze` | 冷凍 | 冷凍店到店 |
| 7-11 大宗寄倉 (B2C) | `PAYUNi_Logistic_711_B2C` | 常溫 | 商家寄倉 |
| 黑貓宅配常溫 | `PAYUNi_Logistic_Tcat` | 常溫 | 宅配到府 |
| 黑貓宅配冷凍 | `PAYUNi_Logistic_Tcat_Freeze` | 冷凍 | 冷凍宅配 |
| 黑貓宅配冷藏 | `PAYUNi_Logistic_Tcat_Cold` | 冷藏 | 冷藏宅配 |

### GoodsType 溫層代碼

| 代碼 | 溫層 | 適用物流 |
|------|------|----------|
| `1` | 常溫 | 全部 |
| `2` | 冷凍 | 7-11 冷凍、黑貓冷凍 |
| `3` | 冷藏 | 僅黑貓宅配 |

### 撥款時間

| 物流類型 | 撥款時間 |
|----------|----------|
| 超商取貨 | 取貨日 + 7 天 |
| 黑貓宅配 | 取貨日 + 15 天 |

---

## 7-11 超商取貨

### 建立物流訂單

#### 端點

```
POST /api/logistics/create
```

#### EncryptInfo 參數

| 參數 | 類型 | 長度 | 必填 | 說明 |
|------|------|------|------|------|
| `MerID` | String | 20 | ✓ | 商店代號 |
| `MerTradeNo` | String | 50 | ✓ | 商店訂單編號 |
| `LogisticsType` | String | 50 | ✓ | 物流類型代碼 |
| `GoodsType` | Integer | - | ✓ | 溫層 `1`:常溫 `2`:冷凍 |
| `GoodsAmount` | Integer | - | ✓ | 商品金額 |
| `GoodsName` | String | 50 | ✓ | 商品名稱 |
| `SenderName` | String | 10 | ✓ | 寄件人姓名 |
| `SenderPhone` | String | 20 | ✓ | 寄件人電話 |
| `SenderStoreID` | String | 10 | 否 | 寄件門市代號 (C2C 必填) |
| `ReceiverName` | String | 10 | ✓ | 收件人姓名 |
| `ReceiverPhone` | String | 20 | ✓ | 收件人電話 |
| `ReceiverStoreID` | String | 10 | ✓ | 收件門市代號 |
| `NotifyURL` | String | 500 | ✓ | 物流狀態通知網址 |
| `Timestamp` | Integer | - | ✓ | Unix 時間戳 |

### C2C vs B2C 差異

| 項目 | C2C 店到店 | B2C 大宗寄倉 |
|------|-----------|-------------|
| 寄件方式 | 消費者自行至門市寄件 | 商家統一寄倉 |
| SenderStoreID | 必填 | 不需要 |
| 適用場景 | 個人賣家 | 企業電商 |

### 門市查詢

7-11 門市代號可透過以下方式取得：

```
7-11 電子地圖: https://emap.pcsc.com.tw/
```

### PHP 範例

```php
<?php

$encryption = new PayuniEncryption($merKey, $merIV);

$params = [
    'MerID' => 'YOUR_MER_ID',
    'MerTradeNo' => 'LOG' . time(),
    'LogisticsType' => 'PAYUNi_Logistic_711',
    'GoodsType' => 1,
    'GoodsAmount' => 500,
    'GoodsName' => '測試商品',
    'SenderName' => '寄件人',
    'SenderPhone' => '0912345678',
    'SenderStoreID' => '123456',  // C2C 必填
    'ReceiverName' => '收件人',
    'ReceiverPhone' => '0987654321',
    'ReceiverStoreID' => '654321',
    'NotifyURL' => 'https://your-site.com/payuni_shipping_711_notify',
    'Timestamp' => time(),
];

$encryptInfo = $encryption->encrypt($params);
$hashInfo = $encryption->hashInfo($encryptInfo);

$ch = curl_init();
curl_setopt_array($ch, [
    CURLOPT_URL => 'https://api.payuni.com.tw/api/logistics/create',
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => http_build_query([
        'MerID' => $params['MerID'],
        'Version' => '1.0',
        'EncryptInfo' => $encryptInfo,
        'HashInfo' => $hashInfo,
    ]),
    CURLOPT_RETURNTRANSFER => true,
]);

$response = curl_exec($ch);
curl_close($ch);

$result = json_decode($response, true);

if ($result['Status'] === 'SUCCESS') {
    $data = $encryption->decrypt($result['EncryptInfo']);
    // $data['LogisticsID'] - 物流編號
    // $data['CVSPaymentNo'] - 超商繳費代碼
    print_r($data);
}
```

### 回應參數 (解密後)

| 參數 | 說明 |
|------|------|
| `LogisticsID` | PayUni 物流編號 |
| `MerTradeNo` | 商店訂單編號 |
| `CVSPaymentNo` | 超商繳費代碼 |
| `CVSValidationNo` | 超商驗證碼 |
| `ExpireDate` | 取貨期限 |

---

## 黑貓宅配

### 建立物流訂單

#### 端點

```
POST /api/logistics/create
```

#### EncryptInfo 參數

| 參數 | 類型 | 長度 | 必填 | 說明 |
|------|------|------|------|------|
| `MerID` | String | 20 | ✓ | 商店代號 |
| `MerTradeNo` | String | 50 | ✓ | 商店訂單編號 |
| `LogisticsType` | String | 50 | ✓ | 物流類型代碼 |
| `GoodsType` | Integer | - | ✓ | 溫層 `1`:常溫 `2`:冷凍 `3`:冷藏 |
| `GoodsAmount` | Integer | - | ✓ | 商品金額 |
| `GoodsName` | String | 50 | ✓ | 商品名稱 |
| `GoodsWeight` | Integer | - | 否 | 商品重量 (g) |
| `SenderName` | String | 10 | ✓ | 寄件人姓名 |
| `SenderPhone` | String | 20 | ✓ | 寄件人電話 |
| `SenderZipCode` | String | 5 | ✓ | 寄件人郵遞區號 |
| `SenderAddress` | String | 200 | ✓ | 寄件人地址 |
| `ReceiverName` | String | 10 | ✓ | 收件人姓名 |
| `ReceiverPhone` | String | 20 | ✓ | 收件人電話 |
| `ReceiverZipCode` | String | 5 | ✓ | 收件人郵遞區號 |
| `ReceiverAddress` | String | 200 | ✓ | 收件人地址 |
| `ScheduledPickupDate` | String | 10 | 否 | 預定取貨日期 `yyyy/MM/dd` |
| `ScheduledDeliveryDate` | String | 10 | 否 | 預定配達日期 `yyyy/MM/dd` |
| `ScheduledDeliveryTime` | String | 2 | 否 | 預定配達時段 |
| `NotifyURL` | String | 500 | ✓ | 物流狀態通知網址 |
| `Timestamp` | Integer | - | ✓ | Unix 時間戳 |

### ScheduledDeliveryTime 配達時段

| 代碼 | 時段 |
|------|------|
| `01` | 13:00 前 |
| `02` | 14:00 - 18:00 |
| `03` | 不指定 |

### 尺寸與重量限制

| 溫層 | 材積 | 重量 |
|------|------|------|
| 常溫 | 150cm | 20kg |
| 冷凍/冷藏 | 120cm | 15kg |

**材積計算**: 長 + 寬 + 高 ≤ 限制

### PHP 範例

```php
<?php

$encryption = new PayuniEncryption($merKey, $merIV);

$params = [
    'MerID' => 'YOUR_MER_ID',
    'MerTradeNo' => 'LOG' . time(),
    'LogisticsType' => 'PAYUNi_Logistic_Tcat',
    'GoodsType' => 1,  // 常溫
    'GoodsAmount' => 1000,
    'GoodsName' => '測試商品',
    'GoodsWeight' => 500,  // 500g
    'SenderName' => '寄件人',
    'SenderPhone' => '0912345678',
    'SenderZipCode' => '100',
    'SenderAddress' => '台北市中正區某某路1號',
    'ReceiverName' => '收件人',
    'ReceiverPhone' => '0987654321',
    'ReceiverZipCode' => '300',
    'ReceiverAddress' => '新竹市東區某某路2號',
    'ScheduledDeliveryTime' => '02',  // 14:00-18:00
    'NotifyURL' => 'https://your-site.com/payuni_shipping_tcat_notify',
    'Timestamp' => time(),
];

$encryptInfo = $encryption->encrypt($params);
$hashInfo = $encryption->hashInfo($encryptInfo);

$ch = curl_init();
curl_setopt_array($ch, [
    CURLOPT_URL => 'https://api.payuni.com.tw/api/logistics/create',
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => http_build_query([
        'MerID' => $params['MerID'],
        'Version' => '1.0',
        'EncryptInfo' => $encryptInfo,
        'HashInfo' => $hashInfo,
    ]),
    CURLOPT_RETURNTRANSFER => true,
]);

$response = curl_exec($ch);
curl_close($ch);

$result = json_decode($response, true);

if ($result['Status'] === 'SUCCESS') {
    $data = $encryption->decrypt($result['EncryptInfo']);
    // $data['LogisticsID'] - 物流編號
    // $data['ShipmentNo'] - 託運單號
    print_r($data);
}
```

### 回應參數 (解密後)

| 參數 | 說明 |
|------|------|
| `LogisticsID` | PayUni 物流編號 |
| `MerTradeNo` | 商店訂單編號 |
| `ShipmentNo` | 黑貓託運單號 |
| `BookingNote` | 取貨編號 |

---

## 物流狀態通知

### Notify URL 設定

| 物流類型 | Notify URL 格式建議 |
|----------|---------------------|
| 超商物流 | `https://your-site.com/payuni_shipping_711_notify` |
| 黑貓宅配 | `https://your-site.com/payuni_shipping_tcat_notify` |

### 通知流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   物流商    │────▶│   PayUni    │────▶│    商店     │
│  狀態更新   │     │    處理     │     │ NotifyURL  │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                          │ POST (加密資料)
                          ▼
                    ┌─────────────┐
                    │    商店     │
                    │  解密處理   │
                    └─────────────┘
                          │
                          │ 回應 "SUCCESS"
                          ▼
                    ┌─────────────┐
                    │   PayUni    │
                    │  確認收到   │
                    └─────────────┘
```

### 通知參數

PayUni 會 POST 加密資料到 `NotifyURL`：

| 參數 | 說明 |
|------|------|
| `MerID` | 商店代號 |
| `EncryptInfo` | 加密的物流狀態 |
| `HashInfo` | SHA256 驗證碼 |

### 解密後的通知內容

| 參數 | 說明 |
|------|------|
| `MerID` | 商店代號 |
| `MerTradeNo` | 商店訂單編號 |
| `LogisticsID` | PayUni 物流編號 |
| `LogisticsType` | 物流類型 |
| `LogisticsStatus` | 物流狀態碼 |
| `LogisticsStatusMsg` | 物流狀態訊息 |
| `UpdateTime` | 狀態更新時間 |

### 處理範例

```php
<?php

// 接收通知
$encryptInfo = $_POST['EncryptInfo'] ?? '';
$hashInfo = $_POST['HashInfo'] ?? '';
$merID = $_POST['MerID'] ?? '';

// 驗證 HashInfo
$encryption = new PayuniEncryption($merKey, $merIV);
$calculatedHash = $encryption->hashInfo($encryptInfo);

if ($hashInfo !== $calculatedHash) {
    echo 'HashInfo Error';
    exit;
}

// 解密
$data = $encryption->decrypt($encryptInfo);

// 根據物流狀態更新訂單
switch ($data['LogisticsStatus']) {
    case '11':
        // 已出貨
        updateOrderLogisticsStatus($data['MerTradeNo'], 'shipped');
        break;
    case '21':
        // 已到店
        updateOrderLogisticsStatus($data['MerTradeNo'], 'arrived');
        break;
    case '22':
        // 已取貨
        updateOrderLogisticsStatus($data['MerTradeNo'], 'picked_up');
        break;
    case '31':
    case '32':
        // 退貨
        updateOrderLogisticsStatus($data['MerTradeNo'], 'returned');
        break;
}

// 回應 SUCCESS
echo 'SUCCESS';
```

---

## 物流狀態查詢

### 端點

```
POST /api/logistics/query
```

### EncryptInfo 參數

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `MerID` | String | ✓ | 商店代號 |
| `MerTradeNo` | String | ✓ | 商店訂單編號 |
| `Timestamp` | Integer | ✓ | Unix 時間戳 |

### 回應參數 (解密後)

| 參數 | 說明 |
|------|------|
| `LogisticsID` | PayUni 物流編號 |
| `MerTradeNo` | 商店訂單編號 |
| `LogisticsType` | 物流類型 |
| `LogisticsStatus` | 物流狀態碼 |
| `LogisticsStatusMsg` | 物流狀態訊息 |
| `ShipmentNo` | 託運單號 |
| `ReceiverStoreID` | 收件門市代號 (超商) |
| `UpdateTime` | 狀態更新時間 |

### 貨態即時查詢

| 物流類型 | 查詢網址 |
|----------|----------|
| 7-11 | https://eservice.7-11.com.tw/E-Tracking/search.aspx |
| 黑貓宅配 | https://www.t-cat.com.tw/inquire/trace.aspx |

---

## 錯誤碼對照表

### 物流狀態碼 (LogisticsStatus)

| 狀態碼 | 說明 |
|--------|------|
| `11` | 已出貨 |
| `21` | 已到店 (超商) / 配達中 (宅配) |
| `22` | 已取貨 / 配達完成 |
| `31` | 退貨中 |
| `32` | 退貨完成 |

### 詳細物流狀態

#### 7-11 超商

| 狀態碼 | 說明 |
|--------|------|
| `11` | 已出貨 (寄件門市已收件) |
| `21` | 已到店 (到達取件門市) |
| `22` | 已取貨 (消費者已取件) |
| `31` | 退貨中 (超過取貨期限) |
| `32` | 退貨完成 |

#### 黑貓宅配

| 狀態碼 | 說明 |
|--------|------|
| `11` | 已出貨 (黑貓已收件) |
| `21` | 配達中 |
| `22` | 配達完成 |
| `31` | 退貨中 (配達失敗) |
| `32` | 退貨完成 |

### 常見錯誤訊息

| 錯誤訊息 | 說明 | 處理方式 |
|----------|------|----------|
| `參數錯誤` | 必填參數缺失或格式錯誤 | 檢查參數格式 |
| `商店代號錯誤` | MerID 不存在 | 確認商店代號 |
| `門市代號錯誤` | StoreID 無效 | 重新查詢門市代號 |
| `物流類型錯誤` | LogisticsType 無效 | 確認物流類型代碼 |
| `HashInfo 驗證失敗` | 加密資料不正確 | 重新計算 HashInfo |
| `超過尺寸限制` | 材積/重量超過限制 | 調整商品包裝 |

---

## 常見問題排解

### 門市代號無效

**問題**: 收到 `門市代號錯誤`

**解決**:
1. 至 7-11 電子地圖重新查詢門市代號
2. 確認門市是否仍在營運
3. 確認門市是否支援店到店服務

### 物流狀態通知未收到

**問題**: 物流狀態變更但沒收到通知

**檢查項目**:
1. NotifyURL 是否為 HTTPS
2. 伺服器是否能被外網存取
3. 是否正確回應 `SUCCESS`
4. 防火牆是否阻擋 PayUni IP

### 黑貓取貨時間

**問題**: 如何安排黑貓取貨時間

**說明**:
1. 使用 `ScheduledPickupDate` 指定取貨日期
2. 黑貓會在指定日期至寄件地址取貨
3. 取貨時段通常為 9:00-18:00

### 超商取貨期限

**問題**: 超商取貨期限是多久

**說明**:
- 7-11: 7 天
- 超過期限未取件會自動退貨

---

## 官方資源

- **官方網站**: https://www.payuni.com.tw/
- **物流服務**: https://www.payuni.com.tw/shipping
- **API 文件**: https://www.payuni.com.tw/docs/web/
- **GitHub**: https://github.com/payuni
