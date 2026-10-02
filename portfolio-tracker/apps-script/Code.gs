/**
 * Google Apps Script: Portfolio Ingestion & Export Suite
 * -------------------------------------------------------
 * Two independent actions in a single file:
 * 1. syncTrading212Orders() : Broker -> Google Sheet (Does NOT call export)
 * 2. autoExportToCSV()      : Google Sheet -> Drive CSV (Does NOT call broker sync)
 *
 * AUTHENTICATION:
 * Trading 212 uses HTTP Basic Authentication: Base64(API_KEY_ID:SECRET_KEY).
 * Credentials are stored safely in Google UserProperties (never in sheet cells).
 */

const T212_LIVE_BASE_URL = "https://live.trading212.com/api/v0";
const T212_DEMO_BASE_URL = "https://demo.trading212.com/api/v0";

/**
 * Custom menu to trigger either action or configure settings independently
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
 * Prompts user to enter both API Key ID and Secret Key,
 * saving them securely into private UserProperties.
 */
function setTrading212ApiKey() {
  const ui = SpreadsheetApp.getUi();
  const props = PropertiesService.getUserProperties();

  const idResp = ui.prompt(
    "Trading 212 Setup (Step 1 of 2)",
    "Enter your Trading 212 API Key ID (or paste 'KEY_ID:SECRET' here):",
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
      "Trading 212 Setup (Step 2 of 2)",
      "Enter your Trading 212 Secret Key (shown once upon creation):",
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

// ============================================================================
// ACTION 1: BROKER SYNC (Trading 212 -> Google Sheet)
// Completely independent: does NOT call autoExportToCSV
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
      const url = nextPath.startsWith("http") ? nextPath : `${baseUrl}${nextPath}`;
      const response = UrlFetchApp.fetch(url, {
        method: "GET",
        headers: {
          "Authorization": authHeader,
          "User-Agent": "Antigravity-PortfolioTracker/1.0"
        },
        muteHttpExceptions: true
      });

      const statusCode = response.getResponseCode();
      if (statusCode === 401 || statusCode === 403) {
        throw new Error(`Authentication failed (HTTP ${statusCode}). Verify that your API Key ID and Secret Key are correct and have 'History' permissions enabled.`);
      } else if (statusCode === 429) {
        throw new Error("Rate limit exceeded from Trading 212. Please wait a minute and retry.");
      } else if (statusCode !== 200) {
        throw new Error(`Trading 212 API error (HTTP ${statusCode}): ${response.getContentText()}`);
      }

      const payload = JSON.parse(response.getContentText());
      const items = payload.items || [];
      if (items.length === 0) break;

      let allInPageAlreadyKnown = true;

      for (const order of items) {
        const orderId = String(order.id || "").trim();
        if (orderId && existingOrderIds.has(orderId)) continue;

        const status = (order.status || "").toUpperCase();
        if (status !== "FILLED" && status !== "EXECUTED" && !order.dateExecuted) continue;

        const filledQty = parseFloat(order.filledQuantity || order.orderedQuantity || 0);
        if (isNaN(filledQty) || filledQty === 0) continue;

        const isBuy = filledQty > 0;
        const absQty = Math.abs(filledQty);
        const fillPrice = parseFloat(order.fillPrice || (order.filledValue ? order.filledValue / absQty : 0));

        const execDateRaw = order.dateExecuted || order.dateCreated;
        const execDate = execDateRaw ? Utilities.formatDate(new Date(execDateRaw), "UTC", "yyyy-MM-dd") : Utilities.formatDate(new Date(), "UTC", "yyyy-MM-dd");

        const rawTicker = String(order.ticker || "");
        const cleanSymbol = rawTicker.replace(/_[A-Z]{2}_EQ$/i, "").toUpperCase();

        const signature = `${execDate}_${cleanSymbol}_${isBuy ? "BUY" : "SELL"}_${absQty}`;
        if (existingSignatures.has(signature)) continue;

        const currency = (order.currencyCode || order.currency || "USD").toUpperCase();
        let fee = 0.0;
        if (Array.isArray(order.taxes)) {
          fee = order.taxes.reduce((sum, t) => sum + (parseFloat(t.fillCost) || 0.0), 0.0);
        }

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

      if (allInPageAlreadyKnown && items.length > 0) break;
      nextPath = payload.nextPagePath || null;
    }

    // 4. Append new trades to the sheet
    if (newTrades.length > 0) {
      newTrades.sort((a, b) => (a[colIndex.date] > b[colIndex.date] ? 1 : -1));

      const startRow = sheet.getLastRow() + 1;
      const range = sheet.getRange(startRow, 1, newTrades.length, headers.length);
      range.setValues(newTrades);

      const msg = `Added ${newTrades.length} new trades from Trading 212 into your sheet.`;
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
