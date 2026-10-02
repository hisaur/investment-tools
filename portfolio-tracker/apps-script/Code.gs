/**
 * Google Apps Script: Multi-Broker Google Sheet to Drive CSV Ingestion
 * with Dynamic Trading 212 API Sync
 * 
 * Target File: portfolio_docker_sync.csv (stored in Google Drive root)
 */

const SYNC_FILE_NAME = "portfolio_docker_sync.csv";
const T212_LIVE_BASE_URL = "https://live.trading212.com/api/v0";
const T212_DEMO_BASE_URL = "https://demo.trading212.com/api/v0";

/**
 * Creates custom menu in Google Sheets UI when spreadsheet opens.
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("📊 Ghostfolio Sync")
    .addItem("📥 Sync Trading 212 Trades (Dynamic)", "syncTrading212Orders")
    .addSeparator()
    .addItem("📤 Export Now to Drive CSV", "autoExportToCSV")
    .addSeparator()
    .addItem("⚙️ Set Trading 212 API Key", "setTrading212ApiKey")
    .addItem("🔄 Toggle Demo / Live Mode", "toggleTrading212Environment")
    .addToUi();
}

/**
 * Safely gets UI (returns null if running headlessly via automated trigger).
 */
function getUiSafely() {
  try {
    return SpreadsheetApp.getUi();
  } catch (e) {
    return null;
  }
}

/**
 * Prompts the user to enter their Trading 212 API Key.
 * Stored securely in UserProperties (never in cells or code).
 */
function setTrading212ApiKey() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.prompt(
    "Trading 212 API Configuration",
    "Enter your Trading 212 API Key (ensure 'History' permissions are checked in T212 settings):",
    ui.ButtonSet.OK_CANCEL
  );

  if (response.getSelectedButton() === ui.Button.OK) {
    const key = response.getResponseText().trim();
    if (key) {
      PropertiesService.getUserProperties().setProperty("T212_API_KEY", key);
      ui.alert("✅ Trading 212 API Key stored securely in Google User Properties!");
    } else {
      ui.alert("⚠️ API key cannot be empty.");
    }
  }
}

/**
 * Toggles between Live and Demo (Practice) Trading 212 environments.
 */
function toggleTrading212Environment() {
  const props = PropertiesService.getUserProperties();
  const current = props.getProperty("T212_ENV") || "live";
  const next = current === "live" ? "demo" : "live";
  props.setProperty("T212_ENV", next);
  SpreadsheetApp.getUi().alert(`Trading 212 environment is now set to: ${next.toUpperCase()}`);
}

/**
 * Fetches recent filled orders from Trading 212 API and appends new trades into the sheet.
 * Only rows with Broker == 'Trading212' are synced; all other brokers are untouched.
 * Automatically triggers autoExportToCSV() after appending new trades.
 */
function syncTrading212Orders() {
  const ui = getUiSafely();
  const props = PropertiesService.getUserProperties();
  let apiKey = props.getProperty("T212_API_KEY");

  if (!apiKey) {
    if (ui) {
      const promptResp = ui.prompt(
        "Trading 212 API Key Required",
        "No API Key found. Please enter your Trading 212 API Key:",
        ui.ButtonSet.OK_CANCEL
      );
      if (promptResp.getSelectedButton() !== ui.Button.OK) return;
      apiKey = promptResp.getResponseText().trim();
      if (!apiKey) {
        ui.alert("Sync aborted: No API Key provided.");
        return;
      }
      props.setProperty("T212_API_KEY", apiKey);
    } else {
      Logger.log("Trading 212 sync aborted: No API key found in UserProperties.");
      return;
    }
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
          "Authorization": apiKey,
          "User-Agent": "Antigravity-PortfolioTracker/1.0"
        },
        muteHttpExceptions: true
      });

      const statusCode = response.getResponseCode();
      if (statusCode === 401 || statusCode === 403) {
        throw new Error(`Authentication failed (HTTP ${statusCode}). Verify that your API key is correct and has 'History' permissions enabled.`);
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
        if (orderId && existingOrderIds.has(orderId)) {
          continue;
        }

        const status = (order.status || "").toUpperCase();
        if (status !== "FILLED" && status !== "EXECUTED" && !order.dateExecuted) {
          continue;
        }

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
        if (existingSignatures.has(signature)) {
          continue;
        }

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

      if (allInPageAlreadyKnown && items.length > 0) {
        break;
      }

      nextPath = payload.nextPagePath || null;
    }

    // 4. Append new trades to the sheet
    if (newTrades.length > 0) {
      newTrades.sort((a, b) => (a[colIndex.date] > b[colIndex.date] ? 1 : -1));

      const startRow = sheet.getLastRow() + 1;
      const range = sheet.getRange(startRow, 1, newTrades.length, headers.length);
      range.setValues(newTrades);

      Logger.log(`Successfully added ${newTrades.length} new Trading 212 trades.`);

      // 5. Auto-export to Drive CSV using your existing function!
      autoExportToCSV();

      const msg = `Added ${newTrades.length} new trades from Trading 212.\nExported latest portfolio_docker_sync.csv to Google Drive.`;
      Logger.log(msg);
      if (ui) {
        ui.alert(`✅ Sync Complete!\n\n${msg}`);
      }
    } else {
      Logger.log("Up to date: No new Trading 212 trades found.");
      if (ui) {
        ui.alert("ℹ️ Up to date: No new Trading 212 trades found.");
      }
    }

  } catch (err) {
    Logger.log(`Trading 212 Sync Error: ${err.message}`);
    if (ui) {
      ui.alert(`❌ Trading 212 Sync Error:\n\n${err.message}`);
    }
  }
}

/**
 * Exports the active sheet data to portfolio_docker_sync.csv in Google Drive root.
 */
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

// Backward compatibility alias
function exportToDriveCSV() {
  autoExportToCSV();
}
