# ECPay Logistics API Reference

綠界科技 (ECPay) 物流 API 完整參考文件。

---

## 目錄

1. [API 端點總覽](#api-端點總覽)
2. [測試環境](#測試環境)
3. [物流類型](#物流類型)
4. [CheckMacValue 計算](#checkmacvalue-計算)
5. [建立物流訂單](#建立物流訂單)
6. [超商電子地圖](#超商電子地圖)
7. [列印託運單](#列印託運單)
8. [物流狀態查詢](#物流狀態查詢)
9. [物流狀態通知](#物流狀態通知)
10. [錯誤碼對照表](#錯誤碼對照表)

---

## API 端點總覽

### 基礎 API 路徑

| 環境 | 基礎路徑 |
|------|----------|
| **測試環境** | `https://logistics-stage.ecpay.com.tw` |
| **正式環境** | `https://logistics.ecpay.com.tw` |

### 物流相關端點

| 功能 | 測試環境 | 正式環境 |
|------|----------|----------|
| 建立物流訂單 | `/Express/Create` | `/Express/Create` |
| 超商電子地圖 | `/Express/map` | `/Express/map` |
| 列印託運單 | `/helper/printTradeDocument` | `/helper/printTradeDocument` |
| 查詢訂單 | `/Helper/QueryLogisticsTradeInfo/V2` | `/Helper/QueryLogisticsTradeInfo/V2` |

---

## 測試環境

### 測試帳號

```
測試網址: https://logistics-stage.ecpay.com.tw
商店代號: 2000132
HashKey:  5294y06JbISpM5x9
HashIV:   v77hoKGq4kWxNNIS
```

### 測試用超商門市

| 超商 | 測試門市代號 |
|------|-------------|
| 7-11 | `131386` |
| 全家 | `006598` |
| 萊爾富 | `2001` |
| OK | `1328` |

---

## 物流類型

### 超商取貨類型

| 類型 | 代碼 | 說明 |
|------|------|------|
| 7-11 超商取貨 | `UNIMART` | 統一超商 B2C |
| 7-11 交貨便 | `UNIMARTC2C` | C2C 店到店 |
| 全家超商取貨 | `FAMI` | 全家便利商店 B2C |
| 全家店到店 | `FAMIC2C` | C2C 店到店 |
| 萊爾富超商取貨 | `HILIFE` | 萊爾富 B2C |
| 萊爾富店到店 | `HILIFEC2C` | C2C 店到店 |
| OK 超商取貨 | `OKMART` | OK 便利商店 B2C |
| OK 店到店 | `OKMARTC2C` | C2C 店到店 |

### 宅配類型

| 類型 | 代碼 | 說明 |
|------|------|------|
| 黑貓宅急便 | `TCAT` | 宅配到府 |
| 宅配通 | `ECAN` | 常溫宅配 |

### LogisticsType 對照

| 值 | 說明 |
|------|------|
| `CVS` | 超商取貨 |
| `Home` | 宅配 |

---

## CheckMacValue 計算

### 計算步驟

1. 將參數依照 Key 排序 (A-Z, 不分大小寫)
2. 組合成 `key=value&key=value` 格式
3. 前後加上 `HashKey={HashKey}&` 和 `&HashIV={HashIV}`
4. URL Encode (RFC 1866)
5. 轉小寫
6. 計算 MD5
7. 轉大寫

### PHP 範例

```php
<?php

function generateCheckMacValue(array $params, string $hashKey, string $hashIV): string
{
    // 1. 排序參數 (不分大小寫)
    uksort($params, 'strcasecmp');

    // 2. 組合字串
    $paramStr = urldecode(http_build_query($params));

    // 3. 加上 HashKey 和 HashIV
    $raw = "HashKey={$hashKey}&{$paramStr}&HashIV={$hashIV}";

    // 4. URL Encode
    $encoded = urlencode($raw);

    // 5. 轉小寫
    $lower = strtolower($encoded);

    // 6. MD5
    $md5 = md5($lower);

    // 7. 轉大寫
    return strtoupper($md5);
}
```

### Python 範例

```python
import hashlib
import urllib.parse

def generate_check_mac_value(params: dict, hash_key: str, hash_iv: str) -> str:
    # 1. 排序參數
    sorted_params = sorted(params.items(), key=lambda x: x[0].lower())

    # 2. 組合字串
    param_str = '&'.join(f'{k}={v}' for k, v in sorted_params)

    # 3. 加上 HashKey 和 HashIV
    raw = f'HashKey={hash_key}&{param_str}&HashIV={hash_iv}'

    # 4. URL Encode
    encoded = urllib.parse.quote_plus(raw)

    # 5. 轉小寫
    lower = encoded.lower()

    # 6. MD5
    md5 = hashlib.md5(lower.encode('utf-8')).hexdigest()

    # 7. 轉大寫
    return md5.upper()
```

---

## 建立物流訂單

### 端點

```
POST /Express/Create
```

### 通用參數

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `MerchantID` | String(10) | ✓ | 商店代號 |
| `MerchantTradeNo` | String(20) | ✓ | 訂單編號 (唯一) |
| `MerchantTradeDate` | String(20) | ✓ | 訂單日期 `yyyy/MM/dd HH:mm:ss` |
| `LogisticsType` | String(20) | ✓ | 物流類型 `CVS`/`Home` |
| `LogisticsSubType` | String(20) | ✓ | 物流子類型 |
| `GoodsAmount` | Integer | ✓ | 商品金額 |
| `GoodsName` | String(50) | ✓ | 商品名稱 |
| `SenderName` | String(10) | ✓ | 寄件人姓名 |
| `SenderPhone` | String(20) | ✓ | 寄件人電話 |
| `SenderCellPhone` | String(20) | 否 | 寄件人手機 |
| `ReceiverName` | String(10) | ✓ | 收件人姓名 |
| `ReceiverPhone` | String(20) | ✓ | 收件人電話 |
| `ReceiverCellPhone` | String(20) | 否 | 收件人手機 |
| `ServerReplyURL` | String(200) | ✓ | 物流狀態通知網址 |
| `CheckMacValue` | String | ✓ | 檢查碼 |

### 超商取貨專用參數

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `ReceiverStoreID` | String(6) | ✓ | 收件門市代號 |
| `ReturnStoreID` | String(6) | 否 | 退貨門市代號 |
| `IsCollection` | String(1) | 否 | 是否代收貨款 `Y`/`N` |
| `CollectionAmount` | Integer | 否 | 代收金額 |

### 宅配專用參數

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `SenderZipCode` | String(5) | ✓ | 寄件人郵遞區號 |
| `SenderAddress` | String(200) | ✓ | 寄件人地址 |
| `ReceiverZipCode` | String(5) | ✓ | 收件人郵遞區號 |
| `ReceiverAddress` | String(200) | ✓ | 收件人地址 |
| `Temperature` | String(4) | 否 | 溫層 `0001`常溫 `0002`冷藏 `0003`冷凍 |
| `Distance` | String(2) | 否 | 距離 `00`同縣市 `01`外縣市 `02`離島 |
| `Specification` | String(4) | 否 | 規格 (見下表) |
| `ScheduledDeliveryTime` | String(1) | 否 | 預定送達時段 |
| `ScheduledDeliveryDate` | String(10) | 否 | 預定送達日期 |

### Specification 規格代碼

| 代碼 | 尺寸 |
|------|------|
| `0001` | 60cm |
| `0002` | 90cm |
| `0003` | 120cm |
| `0004` | 150cm |

### ScheduledDeliveryTime 時段代碼

| 代碼 | 時段 |
|------|------|
| `1` | 13:00 前 |
| `2` | 14:00-18:00 |
| `3` | 不限時 |
| `4` | 任何時間 (黑貓夜配) |

### PHP 範例 - 超商取貨

```php
<?php

$params = [
    'MerchantID' => '2000132',
    'MerchantTradeNo' => 'LOG' . time(),
    'MerchantTradeDate' => date('Y/m/d H:i:s'),
    'LogisticsType' => 'CVS',
    'LogisticsSubType' => 'UNIMART',
    'GoodsAmount' => 500,
    'GoodsName' => '測試商品',
    'SenderName' => '寄件人',
    'SenderPhone' => '0912345678',
    'ReceiverName' => '收件人',
    'ReceiverPhone' => '0987654321',
    'ReceiverStoreID' => '131386',
    'ServerReplyURL' => 'https://your-site.com/logistics_notify',
    'IsCollection' => 'N',
];

$params['CheckMacValue'] = generateCheckMacValue($params, $hashKey, $hashIV);

$ch = curl_init();
curl_setopt_array($ch, [
    CURLOPT_URL => 'https://logistics-stage.ecpay.com.tw/Express/Create',
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => http_build_query($params),
    CURLOPT_RETURNTRANSFER => true,
]);

$response = curl_exec($ch);
curl_close($ch);

// 解析回應 (格式: 1|OK|MerchantID=xxx|...)
```

### 回應格式

成功回應:
```
1|OK|MerchantID=2000132|MerchantTradeNo=LOG1234567890|RtnCode=300|RtnMsg=交易成功|AllPayLogisticsID=1234567890|CVSPaymentNo=AB12345|CVSValidationNo=1234|LogisticsType=CVS|LogisticsSubType=UNIMART|GoodsAmount=500|UpdateStatusDate=2024/01/15 10:30:00|ReceiverName=收件人|ReceiverPhone=0987654321|ReceiverStoreID=131386|BookingNote=|CheckMacValue=ABC123...
```

失敗回應:
```
0|ErrorCode|ErrorMessage
```

---

## 超商電子地圖

### 端點

```
POST /Express/map
```

### 參數

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `MerchantID` | String(10) | ✓ | 商店代號 |
| `LogisticsType` | String(20) | ✓ | 固定 `CVS` |
| `LogisticsSubType` | String(20) | ✓ | 超商類型 |
| `IsCollection` | String(1) | ✓ | 是否代收 `Y`/`N` |
| `ServerReplyURL` | String(200) | ✓ | 選擇門市後的回傳網址 |
| `ExtraData` | String(200) | 否 | 額外資料 (會原樣回傳) |

### 流程

1. 建立表單 POST 至電子地圖端點
2. 使用者在地圖選擇門市
3. ECPay POST 門市資料至 `ServerReplyURL`

### 回傳參數

| 參數 | 說明 |
|------|------|
| `CVSStoreID` | 門市代號 |
| `CVSStoreName` | 門市名稱 |
| `CVSAddress` | 門市地址 |
| `CVSTelephone` | 門市電話 |
| `ExtraData` | 額外資料 |

### PHP 範例

```php
<?php
// 產生電子地圖表單
$html = <<<HTML
<form id="map-form" method="post" action="https://logistics-stage.ecpay.com.tw/Express/map" target="map-iframe">
    <input type="hidden" name="MerchantID" value="2000132">
    <input type="hidden" name="LogisticsType" value="CVS">
    <input type="hidden" name="LogisticsSubType" value="UNIMART">
    <input type="hidden" name="IsCollection" value="N">
    <input type="hidden" name="ServerReplyURL" value="https://your-site.com/map_callback">
    <input type="hidden" name="ExtraData" value="order_123">
</form>
<iframe name="map-iframe" width="100%" height="600"></iframe>
<script>document.getElementById('map-form').submit();</script>
HTML;
```

---

## 列印託運單

### 端點

```
POST /helper/printTradeDocument
```

### 參數

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `MerchantID` | String(10) | ✓ | 商店代號 |
| `AllPayLogisticsID` | String(20) | ✓ | ECPay 物流編號 |
| `CheckMacValue` | String | ✓ | 檢查碼 |

### 回應

成功時會回傳 PDF 檔案內容。

---

## 物流狀態查詢

### 端點

```
POST /Helper/QueryLogisticsTradeInfo/V2
```

### 參數

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `MerchantID` | String(10) | ✓ | 商店代號 |
| `AllPayLogisticsID` | String(20) | ✓ | ECPay 物流編號 |
| `CheckMacValue` | String | ✓ | 檢查碼 |

### 回應參數

| 參數 | 說明 |
|------|------|
| `MerchantID` | 商店代號 |
| `MerchantTradeNo` | 訂單編號 |
| `AllPayLogisticsID` | ECPay 物流編號 |
| `LogisticsType` | 物流類型 |
| `LogisticsSubType` | 物流子類型 |
| `LogisticsStatus` | 物流狀態碼 |
| `GoodsAmount` | 商品金額 |
| `UpdateStatusDate` | 狀態更新時間 |
| `ReceiverName` | 收件人姓名 |
| `ReceiverPhone` | 收件人電話 |
| `ReceiverStoreID` | 收件門市代號 |
| `TradeDate` | 交易時間 |

---

## 物流狀態通知

### 通知流程

ECPay 會在物流狀態變更時 POST 資料至 `ServerReplyURL`。

### 通知參數

| 參數 | 說明 |
|------|------|
| `MerchantID` | 商店代號 |
| `MerchantTradeNo` | 訂單編號 |
| `AllPayLogisticsID` | ECPay 物流編號 |
| `LogisticsType` | 物流類型 |
| `LogisticsSubType` | 物流子類型 |
| `LogisticsStatus` | 物流狀態碼 |
| `GoodsAmount` | 商品金額 |
| `UpdateStatusDate` | 狀態更新時間 |
| `ReceiverName` | 收件人姓名 |
| `ReceiverPhone` | 收件人電話 |
| `ReceiverStoreID` | 收件門市代號 |
| `CheckMacValue` | 檢查碼 |

### 處理範例

```php
<?php

// 接收通知
$postData = $_POST;

// 取出 CheckMacValue
$receivedMac = $postData['CheckMacValue'];
unset($postData['CheckMacValue']);

// 重新計算 CheckMacValue
$calculatedMac = generateCheckMacValue($postData, $hashKey, $hashIV);

// 驗證
if ($receivedMac !== $calculatedMac) {
    echo '0|CheckMacValue Error';
    exit;
}

// 根據物流狀態更新訂單
$logisticsStatus = $postData['LogisticsStatus'];

switch ($logisticsStatus) {
    case '300':
        // 訂單建立成功
        updateOrderStatus($postData['MerchantTradeNo'], 'created');
        break;
    case '2030':
        // 已交寄
        updateOrderStatus($postData['MerchantTradeNo'], 'shipped');
        break;
    case '2063':
        // 配達完成
        updateOrderStatus($postData['MerchantTradeNo'], 'delivered');
        break;
    case '2067':
        // 消費者取貨完成
        updateOrderStatus($postData['MerchantTradeNo'], 'picked_up');
        break;
    case '2073':
        // 退貨中
        updateOrderStatus($postData['MerchantTradeNo'], 'returning');
        break;
    case '2074':
        // 退貨完成
        updateOrderStatus($postData['MerchantTradeNo'], 'returned');
        break;
}

// 回應 OK
echo '1|OK';
```

---

## 錯誤碼對照表

### 物流狀態碼

| 狀態碼 | 說明 |
|--------|------|
| `300` | 訂單建立成功 |
| `2030` | 已交寄 |
| `2063` | 配達完成 |
| `2067` | 消費者取貨完成 |
| `2073` | 退貨中 |
| `2074` | 退貨完成 |

### 超商取貨詳細狀態

| 狀態碼 | 說明 |
|--------|------|
| `300` | 訂單建立成功 |
| `310` | 已產生托運單 |
| `2030` | 已交寄 |
| `2063` | 到達門市 |
| `2067` | 消費者取貨完成 |
| `2068` | 消費者取貨失敗 |
| `2073` | 退貨中 |
| `2074` | 退貨完成 |

### 宅配詳細狀態

| 狀態碼 | 說明 |
|--------|------|
| `300` | 訂單建立成功 |
| `310` | 已產生托運單 |
| `2030` | 已交寄 |
| `2063` | 配達完成 |
| `2072` | 配達失敗 |
| `2073` | 退貨中 |
| `2074` | 退貨完成 |

### 常見錯誤訊息

| 錯誤碼 | 說明 | 處理方式 |
|--------|------|----------|
| `10500001` | MerchantID 為必填 | 檢查參數 |
| `10500002` | MerchantTradeNo 為必填 | 檢查參數 |
| `10500003` | CheckMacValue 錯誤 | 重新計算 CheckMacValue |
| `10500008` | LogisticsSubType 錯誤 | 確認物流類型代碼 |
| `10500019` | ReceiverStoreID 錯誤 | 重新查詢門市代號 |

---

## 官方資源

- **官方網站**: https://www.ecpay.com.tw/
- **物流 API 文件**: https://developers.ecpay.com.tw/?p=7421
- **技術客服**: techsupport@ecpay.com.tw
