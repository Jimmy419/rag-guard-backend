import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from mcp_client import get_agent
import asyncio

app = FastAPI()

# 获取当前文件的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "1"

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
