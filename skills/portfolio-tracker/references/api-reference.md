# Ghostfolio API & Data Schema Reference

## Core Endpoints

Base URL (default local): `http://localhost:3333`

### 1. Healthcheck
- **Method**: `GET`
- **Path**: `/api/v1/health`
- **Auth**: None
- **Response**: `200 OK`
- **Use**: Verification of container readiness.

### 2. User Auto-Provisioning (Ephemeral Mode)
- **Method**: `POST`
- **Path**: `/api/v1/user`
- **Headers**: `Content-Type: application/json`
- **Body**: `{"languageCode": "en"}`
- **Response**: `{"accessToken": "<SECURITY_TOKEN>", ...}`
- **Use**: Generates the initial user account in an empty database.

### 3. Anonymous Token Exchange
- **Method**: `POST`
- **Path**: `/api/v1/auth/anonymous`
- **Headers**: `Content-Type: application/json`
- **Body**: `{"accessToken": "<SECURITY_TOKEN>"}`
- **Response**: `{"authToken": "<JWT_BEARER_TOKEN>"}`
- **Use**: Exchanges the security token for an API Bearer token.

### 4. Account Discovery
- **Method**: `GET`
- **Path**: `/api/v1/account`
- **Headers**: `Authorization: Bearer <JWT_BEARER_TOKEN>`
- **Response**: `{"accounts": [{"id": "<ACCOUNT_ID>", "name": "Default", ...}]}`

### 5. Portfolio Import
- **Method**: `POST`
- **Path**: `/api/v1/import`
- **Headers**: `Authorization: Bearer <JWT_BEARER_TOKEN>`, `Content-Type: application/json`
- **Body**:
  ```json
  {
    "activities": [
      {
        "accountId": "<ACCOUNT_ID>",
        "currency": "USD",
        "dataSource": "YAHOO",
        "date": "2026-10-01T00:00:00.000Z",
        "fee": 0,
        "quantity": 10,
        "symbol": "AAPL",
        "type": "BUY",
        "unitPrice": 150
      }
    ]
  }
  ```

---

## Synced CSV Schema (Source of Truth)

Local mount path: `G:\My Drive\portfolio_docker_sync.csv`

| Column | Type | Example | Notes |
| :--- | :--- | :--- | :--- |
| `Date` | String | `Thu Oct 01 2026 00:00:00 GMT+1000` | Normalized to ISO 8601 UTC by `sync.py` |
| `Type` | String | `BUY` or `SELL` | Transaction type |
| `Symbol` | String | `AAPL`, `MSFT`, `VIE.PA` | Ticker symbol |
| `Quantity` | Float | `10` | Number of units |
| `UnitPrice` | Float | `150.00` | Execution price |
| `Currency` | String | `USD`, `EUR`, `AUD` | Transaction currency |
| `Fee` | Float | `0.00` | Commission/brokerage fee |
