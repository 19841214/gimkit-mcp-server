import csv
import io
import json
import os
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

# Render will provide the port via PORT environment variable (default: 10000)
port = int(os.environ.get("PORT", 10000))

# Initialize FastMCP server
mcp = FastMCP("gimkit-formatter")
mcp.settings.host = "0.0.0.0"
mcp.settings.port = port

# Add healthcheck and root routes so external pingers (like Google) get 200 OK instead of 404
@mcp.custom_route("/", methods=["GET", "HEAD"])
async def root(request):
    return JSONResponse({
        "status": "ok",
        "name": "gimkit-formatter",
        "mcp_endpoint": "/sse",
        "message": "Gimkit MCP Server is running."
    })

@mcp.custom_route("/health", methods=["GET", "HEAD"])
async def health(request):
    return JSONResponse({"status": "healthy"})

@mcp.tool()
def format_to_gimkit_csv(questions_json: str) -> str:
    """
    將 JSON 格式的題目資料轉換為符合 Gimkit 官方規範的標準 CSV 內容。

    Args:
        questions_json: JSON 陣列字串。每題需包含:
            - question: 題目
            - correct_answer: 正確答案
            - incorrect_answers: 錯誤選項清單 (1~3 個)

    Returns:
        符合 Gimkit 匯入規範的 CSV 文字內容。
    """
    try:
        data = json.loads(questions_json)
        if not isinstance(data, list):
            return "錯誤：輸入的 JSON 必須是一個陣列清單。"
    except Exception as e:
        return f"JSON 解析失敗：{str(e)}"

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Gimkit 官方規範的 5 個欄位
    headers = [
        "Question",
        "Correct Answer",
        "Incorrect Answer 1",
        "Incorrect Answer 2 (Optional)",
        "Incorrect Answer 3 (Optional)"
    ]
    writer.writerow(headers)

    count = 0
    for item in data:
        q = str(item.get("question", "")).strip()
        ans = str(item.get("correct_answer", "")).strip()
        distractors = item.get("incorrect_answers", [])
        if not isinstance(distractors, list):
            distractors = [str(distractors)]
        
        distractors = [str(d).strip() for d in distractors]
        while len(distractors) < 3:
            distractors.append("")

        if q and ans:
            writer.writerow([
                q,
                ans,
                distractors[0],
                distractors[1],
                distractors[2]
            ])
            count += 1

    return output.getvalue()

@mcp.tool()
def validate_gimkit_quiz(questions_json: str) -> str:
    """
    檢查題目清單是否符合 Gimkit 規範（防呆驗證）。
    """
    try:
        data = json.loads(questions_json)
    except Exception as e:
        return f"❌ 格式錯誤：無法解析 JSON（{str(e)}）"

    issues = []
    total = len(data)

    for i, item in enumerate(data, start=1):
        q = str(item.get("question", "")).strip()
        ans = str(item.get("correct_answer", "")).strip()
        distractors = item.get("incorrect_answers", [])

        if not q:
            issues.append(f"第 {i} 題：題目內容為空。")
        if not ans:
            issues.append(f"第 {i} 題：缺少正確答案。")
        if not distractors:
            issues.append(f"第 {i} 題：至少需要提供 1 個錯誤選項。")
        elif len(distractors) > 3:
            issues.append(f"第 {i} 題：錯誤選項超過 3 個。")
        
        if ans in distractors:
            issues.append(f"第 {i} 題：正確答案「{ans}」出現在錯誤選項中！")

    if not issues:
        return f"✅ 驗證通過！共 {total} 題，全部符合 Gimkit 格式規範。"
    else:
        return f"⚠️ 發現 {len(issues)} 個問題需修正：\n" + "\n".join(f"- {issue}" for issue in issues)

if __name__ == "__main__":
    # 以 SSE (Server-Sent Events) 協定對外提供服務
    mcp.run(transport="sse")
