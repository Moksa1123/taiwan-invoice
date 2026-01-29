# 快速參考 (Quick Reference)

> 此文件為 Claude 專用快速參考,提供金流服務商比較表、常用代碼片段、快速查找表。

## 三家服務商快速比較

| 特性 | 綠界 ECPay | 藍新 NewebPay | 統一 PAYUNi |
|------|-----------|--------------|------------|
| **加密方式** | URL Encode + SHA256 | AES-256-CBC + SHA256 雙層 | AES-256-GCM + SHA256 |
| **API 風格** | Form POST | Form POST + AES | RESTful JSON |
| **內容格式** | application/x-www-form-urlencoded | application/x-www-form-urlencoded | application/json |
| **市佔率** | 🥇 最高 | 🥈 高 | 🥉 中等 |
| **支付方式** | 11 種 | 13 種 | 8 種 |
| **文檔品質** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **測試環境** | ✅ 完整 | ✅ 完整 | ✅ 完整 |
| **最佳用途** | 高交易量電商 | 多元支付需求 | 新創 API 開發 |

## 常用代碼片段

### ECPay - 快速建立訂單

```typescript
import crypto from 'crypto'

// 1. 生成 CheckMacValue
function generateECPayCheckMac(params: Record<string, any>, hashKey: string, hashIV: string): string {
    const { CheckMacValue, ...cleanParams } = params
    const sortedKeys = Object.keys(cleanParams).sort()
    const paramString = sortedKeys.map(k => `${k}=${cleanParams[k]}`).join('&')
    const rawString = `HashKey=${hashKey}&${paramString}&HashIV=${hashIV}`
    const encoded = encodeURIComponent(rawString).toLowerCase()
    return crypto.createHash('sha256').update(encoded).digest('hex').toUpperCase()
}

// 2. 建立訂單參數
const orderParams = {
    MerchantID: '3002607',
    MerchantTradeNo: 'ORD' + Date.now(),
    MerchantTradeDate: new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14),
    PaymentType: 'aio',
    TotalAmount: 1000,
    TradeDesc: '商品描述',
    ItemName: '商品名稱',
    ReturnURL: 'https://yourdomain.com/api/payment/callback',
    ChoosePayment: 'Credit',
    EncryptType: 1
}
orderParams.CheckMacValue = generateECPayCheckMac(orderParams, hashKey, hashIV)

// 3. POST 到 https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5
```

### NewebPay - 快速建立訂單

```typescript
import crypto from 'crypto'

// 1. AES 加密
function encryptNewebPay(data: Record<string, any>, hashKey: string, hashIV: string) {
    const queryString = new URLSearchParams(data).toString()
    const cipher = crypto.createCipheriv('aes-256-cbc', hashKey, hashIV)
    cipher.setAutoPadding(true)
    let encrypted = cipher.update(queryString, 'utf8', 'hex')
    encrypted += cipher.final('hex')

    const tradeSha = crypto
        .createHash('sha256')
        .update(`HashKey=${hashKey}&${encrypted}&HashIV=${hashIV}`)
        .digest('hex')
        .toUpperCase()

    return { TradeInfo: encrypted, TradeSha: tradeSha }
}

// 2. 建立訂單參數
const orderData = {
    MerchantID: 'YOUR_MERCHANT_ID',
    RespondType: 'JSON',
    TimeStamp: Math.floor(Date.now() / 1000).toString(),
    Version: '2.0',
    MerchantOrderNo: 'ORD' + Date.now(),
    Amt: 1000,
    ItemDesc: '商品描述',
    Email: 'customer@example.com',
    NotifyURL: 'https://yourdomain.com/api/payment/callback',
    ReturnURL: 'https://yourdomain.com/payment/result'
}

const encrypted = encryptNewebPay(orderData, hashKey, hashIV)

// 3. POST 到 https://ccore.newebpay.com/MPG/mpg_gateway
// Body: MerchantID, TradeInfo, TradeSha, Version
```

### PAYUNi - 快速建立訂單

```typescript
import crypto from 'crypto'

// 1. AES-GCM 加密
function encryptPAYUNi(data: Record<string, any>, hashKey: string, hashIV: string) {
    const jsonString = JSON.stringify(data)
    const cipher = crypto.createCipheriv('aes-256-gcm', hashKey, hashIV)
    let encrypted = cipher.update(jsonString, 'utf8', 'hex')
    encrypted += cipher.final('hex')
    const authTag = cipher.getAuthTag().toString('hex')
    const encryptInfo = encrypted + authTag

    const hashInfo = crypto
        .createHash('sha256')
        .update(`HashKey=${hashKey}&${encryptInfo}&HashIV=${hashIV}`)
        .digest('hex')
        .toUpperCase()

    return { EncryptInfo: encryptInfo, HashInfo: hashInfo }
}

// 2. 建立訂單參數
const orderData = {
    MerchantID: 'YOUR_MERCHANT_ID',
    MerchantTradeNo: 'ORD' + Date.now(),
    MerchantTradeDate: new Date().toISOString().slice(0, 19).replace('T', ' '),
    TotalAmount: 1000,
    TradeDesc: '商品描述',
    ItemName: '商品名稱',
    NotifyURL: 'https://yourdomain.com/api/payment/callback',
    ReturnURL: 'https://yourdomain.com/payment/result'
}

const encrypted = encryptPAYUNi(orderData, hashKey, hashIV)

// 3. POST 到 https://sandbox-api.payuni.com.tw/api/upp
// Body: MerchantID, EncryptInfo, HashInfo
```

## 付款方式對照表

| 付款方式 | ECPay | NewebPay | PAYUNi | 備註 |
|---------|-------|----------|--------|------|
| 信用卡一次付清 | `Credit` | `CREDIT` | `credit` | 最常用 |
| 信用卡分期 | `Credit` + InstallmentFlag | `CREDIT` + InstFlag | `credit` + Installment | 需最低 1000 元 |
| 信用卡定期 | `Credit` + PeriodType | `CREDIT` + PeriodType | `credit` + Period | 訂閱制 |
| ATM 虛擬帳號 | `ATM` | `VACC=1` | `atm` | 1-3 天 |
| 網路 ATM | `WebATM` | `WEBATM=1` | `webatm` | 即時 |
| 超商代碼 | `CVS` | `CVS=1` | `cvs` | 30-20,000 |
| 超商條碼 | `BARCODE` | `BARCODE=1` | `barcode` | 20-40,000 |
| Apple Pay | `ApplePay` | `APPLEPAY=1` | `applepay` | 需申請 |
| Google Pay | `GooglePay` | `GOOGLEPAY=1` | `googlepay` | 需申請 |
| LINE Pay | `LINEPAY` | `LINEPAY=1` | ❌ | NewebPay 最佳 |
| 台灣 Pay | `TWQR` | `P2G=1` | `taiwanpay` | 最高 49,999 |
| BNPL 無卡分期 | `BNPL` | ❌ | ❌ | ECPay 獨家 |
| AFTEE 先享後付 | ❌ | ❌ | `aftee` | PAYUNi 獨家 |

## 錯誤碼快速查找

### ECPay 常見錯誤

| 錯誤碼 | 說明 | 解決方案 |
|-------|------|---------|
| `10100058` | CheckMacValue 錯誤 | 檢查參數排序、URL Encode |
| `10100003` | 訂單編號重複 | 使用唯一的 MerchantTradeNo |
| `10100047` | 金額不符 | 檢查 TotalAmount 是否正整數 |
| `10100073` | 商品名稱錯誤 | ItemName 不可為空 |
| `10200095` | 付款逾時 | 重新建立訂單 |

### NewebPay 常見錯誤

| 錯誤碼 | 說明 | 解決方案 |
|-------|------|---------|
| `TRA10001` | 交易失敗 | 檢查加密參數 |
| `TRA10002` | CheckValue 錯誤 | 檢查 TradeSha 計算 |
| `TRA10003` | 訂單不存在 | 檢查 MerchantOrderNo |
| `TRA10004` | 金額錯誤 | 檢查 Amt 是否正整數 |
| `TRA10005` | 商店代號錯誤 | 檢查 MerchantID |

### PAYUNi 常見錯誤

| 錯誤碼 | 說明 | 解決方案 |
|-------|------|---------|
| `ER0001` | 參數錯誤 | 檢查必填欄位 |
| `ER0002` | 簽章錯誤 | 檢查 HashInfo 計算 |
| `ER0003` | 訂單重複 | 使用唯一訂單號 |
| `ER0004` | 金額錯誤 | 檢查 TotalAmount |
| `ER0005` | 商店不存在 | 檢查 MerchantID |

## 測試資料快速複製

### ECPay 測試環境
```
MerchantID: 3002607
HashKey: pwFHCqoQZGmho4w6
HashIV: EkRm7iFT261dpevs
測試 URL: https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5
測試卡號: 4311-9522-2222-2222
有效期: 任意未來月年 (如 12/28)
CVV: 任意 3 碼 (如 123)
```

### NewebPay 測試環境
```
測試 URL: https://ccore.newebpay.com/MPG/mpg_gateway
測試卡號: 4000-2211-1111-1111
有效期: 任意未來月年 (如 12/28)
CVV: 任意 3 碼 (如 123)
後台: https://cwww.newebpay.com/
注意: 需先申請測試帳號
```

### PAYUNi 測試環境
```
測試 URL: https://sandbox-api.payuni.com.tw/api/upp
後台: https://sandbox.payuni.com.tw/
注意: 需先申請測試帳號
```

## 欄位對照表

| 用途 | ECPay | NewebPay | PAYUNi |
|-----|-------|----------|--------|
| 商店代號 | `MerchantID` | `MerchantID` | `MerchantID` |
| 訂單編號 | `MerchantTradeNo` | `MerchantOrderNo` | `MerchantTradeNo` |
| 訂單日期 | `MerchantTradeDate` | `TimeStamp` | `MerchantTradeDate` |
| 訂單金額 | `TotalAmount` | `Amt` | `TotalAmount` |
| 商品名稱 | `ItemName` | `ItemDesc` | `ItemName` |
| 商品描述 | `TradeDesc` | `ItemDesc` | `TradeDesc` |
| 付款通知 URL | `ReturnURL` | `NotifyURL` | `NotifyURL` |
| 完成導向 URL | `OrderResultURL` | `ReturnURL` | `ReturnURL` |
| 付款方式 | `ChoosePayment` | 多個開關 | `PaymentType` |
| 簽章 | `CheckMacValue` | `TradeSha` | `HashInfo` |
| 加密資料 | - | `TradeInfo` | `EncryptInfo` |

## 回呼驗證範例

### ECPay 回呼驗證
```typescript
export async function POST(request: Request) {
    const formData = await request.formData()
    const params = Object.fromEntries(formData)

    // 驗證簽章
    const receivedMac = params.CheckMacValue
    const calculatedMac = generateECPayCheckMac(params, hashKey, hashIV)

    if (receivedMac !== calculatedMac) {
        return new Response('0|CheckMacValue Error')
    }

    // 更新訂單
    // ...

    return new Response('1|OK')
}
```

### NewebPay 回呼驗證
```typescript
export async function POST(request: Request) {
    const formData = await request.formData()
    const tradeInfo = formData.get('TradeInfo') as string
    const tradeSha = formData.get('TradeSha') as string

    // 驗證 TradeSha
    const calculatedSha = crypto
        .createHash('sha256')
        .update(`HashKey=${hashKey}&${tradeInfo}&HashIV=${hashIV}`)
        .digest('hex')
        .toUpperCase()

    if (tradeSha !== calculatedSha) {
        return Response.json({ Status: 'ERROR', Message: 'CheckValue Error' })
    }

    // 解密 TradeInfo
    const decrypted = decryptNewebPay(tradeInfo, hashKey, hashIV)

    // 更新訂單
    // ...

    return Response.json({ Status: 'SUCCESS' })
}
```

### PAYUNi 回呼驗證
```typescript
export async function POST(request: Request) {
    const body = await request.json()
    const { EncryptInfo, HashInfo } = body

    // 驗證 HashInfo
    const calculatedHash = crypto
        .createHash('sha256')
        .update(`HashKey=${hashKey}&${EncryptInfo}&HashIV=${hashIV}`)
        .digest('hex')
        .toUpperCase()

    if (HashInfo !== calculatedHash) {
        return Response.json({ Status: 'ERROR', Message: 'Hash Error' })
    }

    // 解密 EncryptInfo
    const decrypted = decryptPAYUNi(EncryptInfo, hashKey, hashIV)

    // 更新訂單
    // ...

    return Response.json({ Status: 'SUCCESS' })
}
```

## 智能工具快速使用

```bash
# 搜索錯誤碼
python scripts/search.py "10100058" --domain error

# 推薦服務商
python scripts/recommend.py "電商 高交易量"

# 測試連線
python scripts/test_payment.py ecpay
```

## 前端表單提交範例

```typescript
// 通用表單提交函數
function submitPaymentForm(action: string, params: Record<string, string>) {
    const form = document.createElement('form')
    form.method = 'POST'
    form.action = action
    form.target = '_self'

    Object.entries(params).forEach(([key, value]) => {
        const input = document.createElement('input')
        input.type = 'hidden'
        input.name = key
        input.value = value
        form.appendChild(input)
    })

    document.body.appendChild(form)
    form.submit()
}

// ECPay 使用
submitPaymentForm('https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5', orderParams)

// NewebPay 使用
submitPaymentForm('https://ccore.newebpay.com/MPG/mpg_gateway', {
    MerchantID: merchantID,
    TradeInfo: encrypted.TradeInfo,
    TradeSha: encrypted.TradeSha,
    Version: '2.0'
})

// PAYUNi 使用 (JSON POST，不用表單)
fetch('https://sandbox-api.payuni.com.tw/api/upp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        MerchantID: merchantID,
        EncryptInfo: encrypted.EncryptInfo,
        HashInfo: encrypted.HashInfo
    })
})
```

---

最後更新:2026/01/29
