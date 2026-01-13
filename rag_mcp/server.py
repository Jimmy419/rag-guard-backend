import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from mcp_client import get_agent
import asyncio

import sqlite3
import datetime

app = FastAPI()

# 获取当前文件的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DB_PATH = os.path.join(BASE_DIR, "feedback.db")

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 读取 SQL 文件（如果存在）或者直接执行 SQL 语句
    sql_path = os.path.join(BASE_DIR, "init_db.sql")
    if os.path.exists(sql_path):
        with open(sql_path, "r") as f:
            cursor.executescript(f.read())
    else:
        # Fallback SQL
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                rating INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT 1
            )
        ''')
    conn.commit()
    conn.close()

# 启动时初始化数据库
init_db()

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/admin/feedbacks", response_class=HTMLResponse)
async def get_feedbacks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    html_content = """
    <html>
        <head>
            <title>Feedback List</title>
            <style>
                body { font-family: sans-serif; padding: 20px; }
                table { border-collapse: collapse; width: 100%; max-width: 1200px; margin: 0 auto; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #007aff; color: white; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                tr:hover { background-color: #f1f1f1; }
                .star { color: #ffd700; }
                h1 { text-align: center; color: #333; }
                .answer-cell { max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
                .answer-cell:hover { white-space: normal; word-wrap: break-word; }
                .btn-resolve { 
                    background-color: #ff3b30; color: white; border: none; padding: 5px 10px; 
                    cursor: pointer; border-radius: 4px; font-size: 12px;
                }
                .btn-resolve:hover { background-color: #d63028; }
                .resolved-text { color: #28cd41; font-weight: bold; }
                .script-container { display: none; }
            </style>
            <script>
                async function markResolved(id, btn) {
                    if (!confirm('确认已更新素材并解决此问题？')) return;
                    try {
                        const response = await fetch('/mark_resolved', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ feedback_id: id })
                        });
                        const result = await response.json();
                        if (result.status === 'success') {
                            const cell = btn.parentElement;
                            cell.innerHTML = '<span class="resolved-text">已解决</span>';
                        } else {
                            alert('操作失败: ' + result.detail);
                        }
                    } catch (e) {
                        alert('网络错误');
                    }
                }
            </script>
        </head>
        <body>
            <h1>用户反馈数据</h1>
            <table>
                <thead>
                    <tr>
                        <th width="50">ID</th>
                        <th width="120">Thread ID</th>
                        <th width="200">问题</th>
                        <th>回答 (鼠标悬停查看完整)</th>
                        <th width="80">评分</th>
                        <th width="100">状态</th>
                        <th width="160">提交时间</th>
                    </tr>
                </thead>
                <tbody>
    """
    for row in rows:
        stars = "★" * row[4] + "☆" * (5 - row[4])
        # row: id, thread_id, question, answer, rating, created_at, resolved
        is_resolved = row[6]
        
        status_html = '<span class="resolved-text">已解决</span>'
        if not is_resolved and row[4] < 3:
            status_html = f'<button class="btn-resolve" onclick="markResolved({row[0]}, this)">标记已解决</button>'
        elif not is_resolved: # 理论上不应该出现 rating >=3 且 resolved=0 的情况，除非手动改库
             status_html = '<span class="resolved-text">已解决</span>'

        html_content += f"""
                <tr>
                    <td>{row[0]}</td>
                    <td>{row[1]}</td>
                    <td>{row[2]}</td>
                    <td class="answer-cell" title="{row[3].replace('"', '&quot;')}">{row[3][:100]}...</td>
                    <td><span class="star">{stars}</span> ({row[4]})</td>
                    <td>{status_html}</td>
                    <td>{row[5]}</td>
                </tr>
        """
    html_content += """
                </tbody>
            </table>
        </body>
    </html>
    """
    return html_content

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "1"

class RecordQARequest(BaseModel):
    thread_id: str
    question: str
    answer: str

class UpdateRatingRequest(BaseModel):
    feedback_id: int
    rating: int

@app.post("/record_qa")
async def record_qa(request: RecordQARequest):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # 默认评分 3 分，resolved 默认为 True (1)
        cursor.execute(
            "INSERT INTO feedback (thread_id, question, answer, rating, resolved) VALUES (?, ?, ?, ?, ?)",
            (request.thread_id, request.question, request.answer, 3, 1)
        )
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {"status": "success", "id": feedback_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update_rating")
async def update_rating(request: UpdateRatingRequest):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 如果评分 < 3，设置 resolved = 0 (False)，否则为 1 (True)
        is_resolved = 1 if request.rating >= 3 else 0
        
        cursor.execute(
            "UPDATE feedback SET rating = ?, resolved = ? WHERE id = ?",
            (request.rating, is_resolved, request.feedback_id)
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Rating updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class MarkResolvedRequest(BaseModel):
    feedback_id: int

@app.post("/mark_resolved")
async def mark_resolved(request: MarkResolvedRequest):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE feedback SET resolved = 1 WHERE id = ?",
            (request.feedback_id,)
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Marked as resolved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        agent = await get_agent()
        config = {"configurable": {"thread_id": request.thread_id}}
        
        async def generate():
            print("Start generating...")
            async for message_chunk, metadata in agent.astream(
                input={"messages": [HumanMessage(content=request.message)]},
                config=config,
                stream_mode="messages",
            ):
                # 仅处理 AI 回复的消息，跳过工具调用结果等其他消息
                if not isinstance(message_chunk, AIMessage):
                    continue

                content = message_chunk.content
                if content:
                    # print(f"Chunk received: {content[:10]}...", flush=True) # Debug log
                    if isinstance(content, str):
                        yield content
                    elif isinstance(content, list):
                        # 处理列表类型的内容（如多模态消息）
                        for item in content:
                            if isinstance(item, str):
                                yield item
                            elif isinstance(item, dict) and "text" in item:
                                yield item["text"]
                    else:
                        yield str(content)

        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
