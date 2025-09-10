from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from typing import List, Optional, Dict, Any
import os
import uuid
import aiohttp
import asyncio
from datetime import datetime
import shutil
from pathlib import Path

from agent import Retriever, Summarizer, Explainer, Comparer, OutlineGenerator

# 数据模型定义
from pydantic import BaseModel
from typing import List, Optional


class ChatResponse(BaseModel):
    response: str
    session_id: str


class FileInfo(BaseModel):
    id: str
    filename: str
    path: str
    upload_time: datetime


app = FastAPI(title="智能科研助手API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 阿里云百炼配置
ALIYUN_BAILIAN_CONFIG = {
    "base_url": "https://dashscope.aliyuncs.com/api/v1",
    "api_key": os.getenv("DASHSCOPE_API_KEY"),
    "model": "qwen-plus",
    "enable_search": True
}

# 检查API密钥
if not ALIYUN_BAILIAN_CONFIG["api_key"]:
    raise ValueError("DASHSCOPE_API_KEY环境变量未设置")

# 存储对话历史和文件
conversation_histories = {}
uploaded_files = {}


# 初始化阿里云百炼会话
async def init_bailian_session():
    return aiohttp.ClientSession()


# 调用阿里云百炼API
async def call_bailian_api(session: aiohttp.ClientSession, messages: List[Dict[str, str]],
                           temperature: float = 0.8, max_tokens: int = 2000) -> Dict[str, Any]:
    """调用阿里云百炼的qwen-plus模型API"""
    url = f"{ALIYUN_BAILIAN_CONFIG['base_url']}/services/aigc/text-generation/generation"
    headers = {
        "Authorization": f"Bearer {ALIYUN_BAILIAN_CONFIG['api_key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": ALIYUN_BAILIAN_CONFIG["model"],
        "input": {
            "messages": messages
        },
        "parameters": {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "result_format": "message"
        }
    }

    if ALIYUN_BAILIAN_CONFIG["enable_search"]:
        payload["parameters"]["enable_search"] = True

    try:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise HTTPException(status_code=response.status, detail=f"API调用失败: {error_text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调用阿里云API时发生错误: {str(e)}")


# 处理研究任务
retriever, summarizer, explainer, comparer, outlineGenerator = Retriever(), Summarizer(), Explainer(), Comparer(), OutlineGenerator()
async def handle_research_task(session: aiohttp.ClientSession, task_type: str, user_query: str,
                               context: List[Dict[str, str]] = None, files: List[FileInfo] = None) -> str:
    """处理不同类型的研究任务"""
    if task_type == "concept_explanation":
        agent = explainer
    elif task_type == "viewpoint_comparison":
        agent = comparer
    elif task_type == "outline_generation":
        agent = outlineGenerator
    elif task_type == "literature_summary":
        agent = summarizer
    else: # 默认为信息检索
        agent = retriever

    # 历史消息
    messages = []
    if context:
        messages.extend(context)
    # 已上传文件
    file_content = ""
    if files:
        file_content = "\n".join([f"文件 '{f.filename}' 的内容已上传，可供参考。" for f in files])

    user_message = user_query
    if file_content:
        user_message = f"{user_query}\n\n相关文件信息:\n{file_content}"

    """ 以下为原代码：
    messages.append({"role": "user", "content": user_message})
    response = await call_bailian_api(session, messages)

    if "output" in response and "choices" in response["output"] and len(response["output"]["choices"]) > 0:
        return response["output"]["choices"][0]["message"]["content"]
    else:
        return "抱歉，我没有得到有效的响应。请稍后再试。
    """
    return agent.reply(user_message, messages=messages)


# 分析查询意图
def analyze_query_intent(query: str) -> str:
    query_lower = query.lower()

    if any(word in query_lower for word in ["解释", "什么是", "含义", "定义"]):
        return "concept_explanation"
    elif any(word in query_lower for word in ["对比", "比较", "区别", "差异"]):
        return "viewpoint_comparison"
    elif any(word in query_lower for word in ["大纲", "结构", "提纲", "框架"]):
        return "outline_generation"
    elif any(word in query_lower for word in ["摘要", "总结", "概括", "文献"]):
        return "literature_summary"
    else:
        return "information_retrieval"


# 保存上传的文件
async def save_uploaded_file(file: UploadFile) -> FileInfo:
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    file_path = f"uploads/{file_id}{file_extension}"

    os.makedirs("uploads", exist_ok=True)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return FileInfo(
        id=file_id,
        filename=file.filename,
        path=file_path,
        upload_time=datetime.now()
    )


# 路由处理
@app.on_event("startup")
async def startup_event():
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    app.state.http_session = await init_bailian_session()


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.http_session.close()


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """提供前端界面"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(
        message: str = Form(...),
        session_id: str = Form(...),
        files: Optional[List[UploadFile]] = File(None)
):
    """处理聊天请求"""
    try:
        if session_id not in conversation_histories:
            conversation_histories[session_id] = []

        conversation_history = conversation_histories[session_id]

        file_infos = []
        if files:
            for file in files:
                file_info = await save_uploaded_file(file)
                file_infos.append(file_info)
                if session_id not in uploaded_files:
                    uploaded_files[session_id] = []
                uploaded_files[session_id].append(file_info)

        if message.lower() in ["hi", "hello", "你好", "您好", "嗨"]:
            response_text = "你好！我是智能科研助手，可以帮助你搜索资料、解释概念、生成大纲等。请告诉我你需要什么帮助？"
        else:
            intent = analyze_query_intent(message)

            context = []
            for msg in conversation_history[-6:]:
                context.append({"role": "user", "content": msg["user"]})
                context.append({"role": "assistant", "content": msg["assistant"]})

            response_text = await handle_research_task(
                app.state.http_session,
                intent,
                message,
                context,
                uploaded_files.get(session_id, [])
            )

        conversation_histories[session_id].append({
            "user": message,
            "assistant": response_text,
            "timestamp": datetime.now().isoformat(),
            "files": [f.filename for f in file_infos]
        })

        return ChatResponse(
            response=response_text,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{session_id}")
async def get_conversation_history(session_id: str):
    if session_id in conversation_histories:
        return conversation_histories[session_id]
    else:
        return []


@app.delete("/api/history/{session_id}")
async def clear_conversation_history(session_id: str):
    if session_id in conversation_histories:
        del conversation_histories[session_id]
    if session_id in uploaded_files:
        del uploaded_files[session_id]
    return {"message": "对话历史已清除"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)