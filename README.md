# Gimkit MCP Server 🎮

專為 **Gimkit** 測驗題庫設計的 Model Context Protocol (MCP) 伺服器，支援雲端部署（如 Render.com）或本地運行，能讓 Claude Desktop、Cursor、Cline 等 AI 客戶端直接調用以生成符合 Gimkit 官方規範的匯入檔案。

## 🛠️ 提供的 MCP Tools

1. **`format_to_gimkit_csv`**：接收 JSON 格式的題目資料，自動轉換並排版為 Gimkit 官方標準的 5 欄位 CSV 內容（題目、正解、3 個誘答）。
2. **`validate_gimkit_quiz`**：防呆驗證題庫格式，檢查是否缺少題目、答案、重複選項或超過誘答數量上限。

## 🚀 部署至 Render.com（完全免費）

1. 前往 [Render.com](https://render.com/)，以 GitHub 帳號登入。
2. 點擊 **New +** ➔ 選擇 **Web Service**。
3. 連結此倉庫 `gimkit-mcp-server`。
4. 設定：
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
   - **Plan**: Free ($0)
5. 點擊 **Deploy Web Service**。

部署完成後，取得你的專屬 URL：`https://<你的服務名稱>.onrender.com/sse`。

## 💻 客戶端連線設定 (MCP Client Configuration)

### 1. Cursor / Cline
在 MCP 設定檔中加入：
```json
{
  "mcpServers": {
    "gimkit-formatter": {
      "url": "https://<你的服務名稱>.onrender.com/sse"
    }
  }
}
```

### 2. Claude Desktop (使用 mcp-remote)
```json
{
  "mcpServers": {
    "gimkit-formatter": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://<你的服務名稱>.onrender.com/sse"
      ]
    }
  }
}
```
