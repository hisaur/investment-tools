/**
 * Google Apps Script: Portfolio Ingestion & Export Suite
 * -------------------------------------------------------
 * Verified against official Trading 212 Public API (v0) specification.
 *
 * AUTHENTICATION:
 * Trading 212 uses HTTP Basic Authentication:
 * Authorization: Basic Base64(API_KEY_ID:SECRET_KEY)
 * Credentials are stored securely in private UserProperties (never in cells).
 *
 * ENDPOINTS & SCHEMA (Trading 212 v0):
 * - Orders History: GET https://live.trading212.com/api/v0/equity/history/orders?limit=50
 * - Account Info:   GET https://live.trading212.com/api/v0/equity/account/info
 * - Item structure:
 *     item.order: { id, ticker, status, type, side, filledValue, createdAt }
 *     item.fill:  { quantity, price, filledAt, walletImpact: { taxes } }
 *
 * ACTIONS:
 * 1. syncTrading212Orders() : Broker API -> Google Sheet ledger
 * 2. autoExportToCSV()      : Google Sheet ledger -> Drive CSV (runs on edit)
 * Both actions are completely decoupled and do NOT call each other.
 */

const T212_LIVE_BASE_URL = "https://live.trading212.com/api/v0";
const T212_DEMO_BASE_URL = "https://demo.trading212.com/api/v0";

/**
 * Creates custom menu in Google Sheets UI when spreadsheet opens.
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("📊 Ghostfolio Sync")
    .addItem("📥 Sync Trading 212 Trades", "syncTrading212Orders")
    .addItem("📤 Export Sheet to Drive CSV", "autoExportToCSV")
    .addSeparator()
    .addItem("⚙️ Set Trading 212 API Credentials", "setTrading212ApiKey")
    .addItem("🔄 Toggle Demo / Live Mode", "toggleTrading212Environment")
    .addToUi();
}

function getUiSafely() {
  try { return SpreadsheetApp.getUi(); } catch (e) { return null; }
}

/**
 * Robust URL constructor that prevents double /api/v0 prefixing
 * and enforces strict HTTPS.
 */
function buildTrading212Url(baseUrl, path) {
  if (path.startsWith("https://")) {
    return path;
  }
  if (path.startsWith("http://")) {
    return path.replace(/^http:\/\//i, "https://");
  }

  // Extract root host (e.g. https://live.trading212.com)
  const hostMatch = baseUrl.match(/^(https:\/\/[^\/]+)/i);
  const host = hostMatch ? hostMatch[1] : baseUrl.replace(/\/api\/v0\/?$/i, "");

  let cleanPath = path;
  if (!cleanPath.startsWith("/")) {
    cleanPath = "/" + cleanPath;
  }

  // Deduplicate any repeated /api/v0 (e.g. /api/v0/api/v0/...)
  cleanPath = cleanPath.replace(/^\/api\/v0\/api\/v0\//i, "/api/v0/");

  // If path already starts with /api/v0 (such as T212's nextPagePath), attach host directly
  if (cleanPath.startsWith("/api/v0/")) {
    return `${host}${cleanPath}`;
  }

  return `${host}/api/v0${cleanPath}`;
}

/**
 * Prompts user for API Key ID and Secret Key, saving to UserProperties.
 */
function setTrading212ApiKey() {
  const ui = SpreadsheetApp.getUi();
  const props = PropertiesService.getUserProperties();

  const idResp = ui.prompt(
    "Trading 212 Configuration (Step 1 of 2)",
    "Enter your Trading 212 API Key ID (or paste 'KEY_ID:SECRET'):",
    ui.ButtonSet.OK_CANCEL
  );
  if (idResp.getSelectedButton() !== ui.Button.OK) return;
  const rawInput = idResp.getResponseText().trim();
  if (!rawInput) {
    ui.alert("⚠️ API Key ID cannot be empty.");
    return;
  }

  let keyId = rawInput;
  let secretKey = "";

  if (rawInput.includes(":")) {
    const parts = rawInput.split(":");
    keyId = parts[0].trim();
    secretKey = parts.slice(1).join(":").trim();
  } else {
    const secResp = ui.prompt(
      "Trading 212 Configuration (Step 2 of 2)",
      "Enter your Trading 212 Secret Key (from Settings > API Beta):",
      ui.ButtonSet.OK_CANCEL
    );
    if (secResp.getSelectedButton() !== ui.Button.OK) return;
    secretKey = secResp.getResponseText().trim();
  }

  props.setProperty("T212_API_KEY", keyId);
  props.setProperty("T212_API_SECRET", secretKey);

  ui.alert("✅ Trading 212 credentials saved securely in UserProperties!\n(Never displayed in spreadsheet cells or shared with viewers).");
}

function toggleTrading212Environment() {
  const props = PropertiesService.getUserProperties();
  const current = props.getProperty("T212_ENV") || "live";
  const next = current === "live" ? "demo" : "live";
  props.setProperty("T212_ENV", next);
  SpreadsheetApp.getUi().alert(`Trading 212 environment is now: ${next.toUpperCase()}`);
}

/**
 * Fetches the account default currency from /equity/account/info
 */
function fetchT212AccountCurrency(baseUrl, authHeader) {
  try {
    const url = buildTrading212Url(baseUrl, "/equity/account/info");
    const resp = UrlFetchApp.fetch(url, {
      method: "GET",
      headers: {
        "Authorization": authHeader,
        "Accept": "application/json",
        "User-Agent": "Antigravity-PortfolioTracker/1.0"
      },
      muteHttpExceptions: true
    });
    if (resp.getResponseCode() === 200) {
      const data = JSON.parse(resp.getContentText());
      return (data.currencyCode || data.currency || "USD").toUpperCase();
    }
  } catch (e) {
    Logger.log("Could not fetch account info currency: " + e.message);
  }
  return "USD";
}

// ============================================================================
// ACTION 1: BROKER SYNC (Trading 212 -> Google Sheet)
// Verified against Trading 212 API v0 order history specification.
// Completely independent: does NOT call autoExportToCSV.
// ============================================================================
function syncTrading212Orders() {
  const ui = getUiSafely();
  const props = PropertiesService.getUserProperties();
  let apiKey = props.getProperty("T212_API_KEY");
  let apiSecret = props.getProperty("T212_API_SECRET") || "";

  if (!apiKey) {
    if (ui) {
      setTrading212ApiKey();
      apiKey = props.getProperty("T212_API_KEY");
      apiSecret = props.getProperty("T212_API_SECRET") || "";
      if (!apiKey) return;
    } else {
      Logger.log("Trading 212 sync aborted: No API credentials found in UserProperties.");
      return;
    }
  }

  // Construct HTTP Basic Authorization header
  let authHeader;
  if (apiSecret) {
    authHeader = "Basic " + Utilities.base64Encode(`${apiKey}:${apiSecret}`);
  } else if (apiKey.includes(":")) {
    authHeader = "Basic " + Utilities.base64Encode(apiKey);
  } else if (apiKey.startsWith("Basic ")) {
    authHeader = apiKey;
  } else {
    authHeader = apiKey;
  }

  const env = props.getProperty("T212_ENV") || "live";
  const baseUrl = env === "demo" ? T212_DEMO_BASE_URL : T212_LIVE_BASE_URL;

  // Query default account currency as fallback
  const defaultCurrency = fetchT212AccountCurrency(baseUrl, authHeader);

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheets()[0];
  const dataRange = sheet.getDataRange();
  const values = dataRange.getValues();

  // 1. Analyze existing headers and ensure Broker & OrderId columns exist
  let headers = values.length > 0 ? values[0].map(h => String(h).trim().toLowerCase()) : [];
  
  if (headers.length === 0 || (headers.length === 1 && headers[0] === "")) {
    const standardHeaders = ["Date", "Type", "Symbol", "Quantity", "UnitPrice", "Currency", "Fee", "Broker", "OrderId"];
    sheet.appendRow(standardHeaders);
    headers = standardHeaders.map(h => h.toLowerCase());
  } else {
    if (!headers.includes("broker")) {
      const nextCol = headers.length + 1;
      sheet.getRange(1, nextCol).setValue("Broker");
      headers.push("broker");
    }
    if (!headers.includes("orderid") && !headers.includes("order_id") && !headers.includes("id")) {
      const nextCol = headers.length + 1;
      sheet.getRange(1, nextCol).setValue("OrderId");
      headers.push("orderid");
    }
  }

  const colIndex = {
    date: headers.indexOf("date"),
    type: headers.indexOf("type"),
    symbol: headers.indexOf("symbol"),
    quantity: headers.indexOf("quantity"),
    unitPrice: headers.findIndex(h => h === "unitprice" || h === "unit_price" || h === "price"),
    currency: headers.indexOf("currency"),
    fee: headers.indexOf("fee"),
    broker: headers.indexOf("broker"),
    orderId: headers.findIndex(h => h === "orderid" || h === "order_id" || h === "id")
  };

  // 2. Index existing Order IDs and signatures to prevent duplicate entries
  const existingOrderIds = new Set();
  const existingSignatures = new Set();

  for (let r = 1; r < values.length; r++) {
    const row = values[r];
    if (colIndex.orderId >= 0 && row[colIndex.orderId]) {
      existingOrderIds.add(String(row[colIndex.orderId]).trim());
    }
    const dVal = row[colIndex.date] instanceof Date ? 
      Utilities.formatDate(row[colIndex.date], "UTC", "yyyy-MM-dd") : String(row[colIndex.date] || "").trim();
    const sym = String(row[colIndex.symbol] || "").trim().toUpperCase();
    const typ = String(row[colIndex.type] || "").trim().toUpperCase();
    const qty = String(row[colIndex.quantity] || "").trim();
    if (dVal && sym && qty) {
      existingSignatures.add(`${dVal}_${sym}_${typ}_${qty}`);
    }
  }

  // 3. Fetch historical orders from Trading 212 API
  let nextPath = "/equity/history/orders?limit=50";
  const newTrades = [];
  let pageCount = 0;
  const maxPages = 5;

  try {
    while (nextPath && pageCount < maxPages) {
      pageCount++;
      const url = buildTrading212Url(baseUrl, nextPath);
      Logger.log(`[T212 Sync] Fetching page ${pageCount}: ${url}`);

      const response = UrlFetchApp.fetch(url, {
        method: "GET",
        headers: {
          "Authorization": authHeader,
          "Accept": "application/json",
          "User-Agent": "Antigravity-PortfolioTracker/1.0"
        },
        muteHttpExceptions: true
      });

      const statusCode = response.getResponseCode();
      if (statusCode === 401 || statusCode === 403) {
        throw new Error(`Authentication failed (HTTP ${statusCode}) on ${url}.\nVerify that your API Key ID and Secret Key are correct and that 'History' permissions are enabled in Trading 212 settings.`);
      } else if (statusCode === 429) {
        throw new Error("Rate limit exceeded from Trading 212 (max 20 req/min for history). Please wait a moment and retry.");
      } else if (statusCode !== 200) {
        throw new Error(`Trading 212 API error (HTTP ${statusCode}) on ${url}:\n${response.getContentText()}`);
      }

      const payload = JSON.parse(response.getContentText());
      const items = payload.items || [];
      if (items.length === 0) break;

      let allInPageAlreadyKnown = true;

      for (const item of items) {
        // T212 Schema: fields can be nested under item.order and item.fill, or at top level
        const orderObj = item.order || item;
        const fillObj = item.fill || item;
        const walletObj = fillObj.walletImpact || item.walletImpact || {};

        const orderId = String(orderObj.id || item.id || "").trim();
        if (orderId && existingOrderIds.has(orderId)) {
          continue; // Already processed
        }

        // Status check: only process filled orders
        const status = String(orderObj.status || item.status || "").toUpperCase();
        if (status !== "FILLED" && status !== "EXECUTED" && status !== "PARTIALLY_FILLED" && !fillObj.filledAt && !orderObj.dateExecuted) {
          continue;
        }

        // Quantity: fill.quantity, order.filledQuantity, or fallback
        let rawQty = fillObj.quantity !== undefined ? fillObj.quantity : 
                     (orderObj.filledQuantity !== undefined ? orderObj.filledQuantity : 
                     (orderObj.orderedQuantity !== undefined ? orderObj.orderedQuantity : item.quantity));
        let numQty = parseFloat(rawQty || 0);
        if (isNaN(numQty) || numQty === 0) continue;

        // Buy vs Sell determination:
        // In T212: positive quantity is BUY, negative is SELL. Also order.side or order.type may specify BUY/SELL.
        const sideStr = String(orderObj.side || fillObj.side || orderObj.type || "").toUpperCase();
        const isSell = (numQty < 0) || sideStr === "SELL" || sideStr.includes("SELL");
        const isBuy = !isSell;
        const absQty = Math.abs(numQty);

        // Price per share
        let fillPrice = parseFloat(fillObj.price || orderObj.fillPrice || item.fillPrice || 0);
        if ((isNaN(fillPrice) || fillPrice === 0) && (orderObj.filledValue || item.filledValue) && absQty > 0) {
          fillPrice = Math.abs(parseFloat(orderObj.filledValue || item.filledValue) / absQty);
        }

        // Execution Date
        const execDateRaw = fillObj.filledAt || orderObj.dateExecuted || orderObj.createdAt || item.dateExecuted || item.dateCreated;
        let execDate = "";
        if (execDateRaw) {
          try {
            execDate = Utilities.formatDate(new Date(execDateRaw), "UTC", "yyyy-MM-dd");
          } catch (e) {
            execDate = String(execDateRaw).substring(0, 10);
          }
        } else {
          execDate = Utilities.formatDate(new Date(), "UTC", "yyyy-MM-dd");
        }

        // Clean Ticker Symbol (normalize to Yahoo Finance ticker format)
        const rawTicker = String(orderObj.ticker || item.ticker || "").toUpperCase();
        let cleanSymbol = rawTicker;
        if (cleanSymbol === "ANTM") {
          cleanSymbol = "ELV";
        } else if (cleanSymbol === "013CD_EQ" || cleanSymbol === "013C.DE" || cleanSymbol === "013C") {
          cleanSymbol = "013C.F";
        } else if (cleanSymbol === "HOP_EQ" || cleanSymbol === "HOP.PA" || cleanSymbol === "HOP") {
          cleanSymbol = "HO.PA";
        } else if (cleanSymbol === "ETH" || cleanSymbol === "ETH-USD" || cleanSymbol === "ETH/USD") {
          cleanSymbol = "ETHUSD";
        } else if (cleanSymbol === "USDE" || cleanSymbol === "USDE-USD" || cleanSymbol === "USDE/USD") {
          cleanSymbol = "USDE29470USD";
        } else if (cleanSymbol === "SUSDE" || cleanSymbol === "SUSDE-USD" || cleanSymbol === "SUSDE/USD") {
          cleanSymbol = "SUSDEUSD";
        } else if (cleanSymbol === "BTC" || cleanSymbol === "BTC-USD" || cleanSymbol === "BTC/USD") {
          cleanSymbol = "BTCUSD";
        } else if (cleanSymbol === "SOL" || cleanSymbol === "SOL-USD" || cleanSymbol === "SOL/USD") {
          cleanSymbol = "SOLUSD";
        } else if (cleanSymbol.endsWith("P_EQ")) {
          cleanSymbol = cleanSymbol.slice(0, -4) + ".PA";
        } else if (cleanSymbol.endsWith("A_EQ")) {
          cleanSymbol = cleanSymbol.slice(0, -4) + ".AS";
        } else if (cleanSymbol.endsWith("D_EQ")) {
          cleanSymbol = cleanSymbol.slice(0, -4) + ".DE";
        } else if (cleanSymbol.endsWith("L_EQ")) {
          cleanSymbol = cleanSymbol.slice(0, -4) + ".L";
        } else {
          cleanSymbol = cleanSymbol.replace(/_[A-Z]{2}_EQ$/i, "").replace(/_EQ$/i, "");
        }
        if (!cleanSymbol) continue;

        // Deduplication signature fallback
        const signature = `${execDate}_${cleanSymbol}_${isBuy ? "BUY" : "SELL"}_${absQty}`;
        if (existingSignatures.has(signature)) {
          continue;
        }

        // Currency: Determine based on instrument exchange code, never cash wallet currency (AUD)
        let currency = String(orderObj.currency || fillObj.currency || item.currencyCode || item.currency || "").toUpperCase();
        if (!currency || currency === "AUD") {
          const upperTicker = rawTicker.toUpperCase();
          if (
            upperTicker.endsWith("D_EQ") ||
            upperTicker.endsWith("A_EQ") ||
            upperTicker.endsWith("P_EQ") ||
            upperTicker === "013CD_EQ" ||
            upperTicker === "HOP_EQ" ||
            upperTicker.includes("_DE_") ||
            upperTicker.includes("_NL_") ||
            upperTicker.includes("_FR_") ||
            cleanSymbol.endsWith(".F") ||
            cleanSymbol.endsWith(".DE") ||
            cleanSymbol.endsWith(".AS") ||
            cleanSymbol.endsWith(".PA")
          ) {
            currency = "EUR";
          } else if (upperTicker.endsWith("L_EQ") || upperTicker.includes("_UK_") || cleanSymbol.endsWith(".L")) {
            currency = "GBP";
          } else {
            currency = "USD";
          }
        }

        // Fees / Taxes (Ghostfolio requires fee >= 0)
        let fee = 0.0;
        const taxes = walletObj.taxes || item.taxes;
        if (Array.isArray(taxes)) {
          fee = taxes.reduce((sum, t) => sum + Math.abs(parseFloat(t.fillCost || t.quantity || 0.0) || 0.0), 0.0);
        }
        fee = Math.abs(fee);

        // Build standard row
        const newRow = new Array(headers.length).fill("");
        newRow[colIndex.date] = execDate;
        newRow[colIndex.type] = isBuy ? "BUY" : "SELL";
        newRow[colIndex.symbol] = cleanSymbol;
        newRow[colIndex.quantity] = absQty;
        newRow[colIndex.unitPrice] = fillPrice;
        newRow[colIndex.currency] = currency;
        newRow[colIndex.fee] = fee;
        newRow[colIndex.broker] = "Trading212";
        newRow[colIndex.orderId] = orderId;

        newTrades.push(newRow);
        if (orderId) existingOrderIds.add(orderId);
        existingSignatures.add(signature);
        allInPageAlreadyKnown = false;
      }

      if (allInPageAlreadyKnown && items.length > 0) {
        break; // Reached already-synchronized history
      }

      nextPath = payload.nextPagePath || null;
    }

    // 4. Append new trades to the sheet
    if (newTrades.length > 0) {
      newTrades.sort((a, b) => (a[colIndex.date] > b[colIndex.date] ? 1 : -1));

      const startRow = sheet.getLastRow() + 1;
      const range = sheet.getRange(startRow, 1, newTrades.length, headers.length);
      range.setValues(newTrades);

      const msg = `Successfully added ${newTrades.length} new trades from Trading 212 into your sheet.`;
      Logger.log(msg);
      if (ui) ui.alert(`✅ Trading 212 Sync Complete!\n\n${msg}`);
    } else {
      Logger.log("Up to date: No new Trading 212 trades found.");
      if (ui) ui.alert("ℹ️ Up to date: No new Trading 212 trades found.");
    }

  } catch (err) {
    Logger.log(`Trading 212 Sync Error: ${err.message}`);
    if (ui) ui.alert(`❌ Trading 212 Sync Error:\n\n${err.message}`);
  }
}

// ============================================================================
// ACTION 2: CSV EXPORT (Google Sheet -> Google Drive CSV)
// Completely independent: runs on edit/trigger, does NOT call broker sync
// ============================================================================
function autoExportToCSV() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  var data = sheet.getDataRange().getValues();
  var csvContent = "";
  
  for (var i = 0; i < data.length; i++) {
    csvContent += data[i].join(",") + "\n";
  }
  
  var fileName = "portfolio_docker_sync.csv";
  var files = DriveApp.getFilesByName(fileName);
  
  if (files.hasNext()) {
    files.next().setContent(csvContent);
  } else {
    DriveApp.createFile(fileName, csvContent, MimeType.CSV);
  }
}
