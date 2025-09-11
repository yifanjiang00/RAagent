from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from typing import List, Optional, Dict, Any , Union
import os
import uuid
import aiohttp
import asyncio
from datetime import datetime
import shutil
from pathlib import Path

from agent import Retriever, Summarizer, Explainer, Comparer, OutlineGenerator, IntentAnalyzer

# 数据模型定义
from pydantic import BaseModel
from typing import List, Optional
from utils.file_parser import extract_text

class ChatResponse(BaseModel):
    response: str
    session_id: str


class FileInfo(BaseModel):
    id: str
    filename: str
    path: str
    upload_time: datetime
    content: str = ""


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


# 存储对话历史和文件
conversation_histories = {}
uploaded_files = {}


# 初始化阿里云百炼会话
async def init_bailian_session():
    return aiohttp.ClientSession()


# 处理研究任务
retriever, summarizer, explainer, comparer, outlineGenerator, intent_analyzer = Retriever(), Summarizer(), Explainer(), Comparer(), OutlineGenerator(), IntentAnalyzer()
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
        # 将上下文转换为模型需要的格式
        for msg in context:
            if msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            else:
                messages.append({"role": "assistant", "content": msg["content"]})
    # 处理上传的文件内容
    file_content = ""
    if files:
        # 将所有文件内容合并
        file_contents = []
        for f in files:
            if hasattr(f, 'content'):
                file_contents.append(f"文件 '{f.filename}' 的内容:\n{f.content}")
            else:
                file_contents.append(f"文件 '{f.filename}' 的内容无法读取")
        file_content = "\n\n".join(file_contents)

    user_message = user_query
    if file_content:
        user_message = f"{user_query}\n\n相关文件信息:\n{file_content}"

    return agent.reply(user_message, messages=messages)


# 分析查询意图
def analyze_query_intent(query: str) -> str:
    return intent_analyzer.analyze(query)
'''
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
'''



# 修改save_uploaded_file函数，使其能够读取文件内容
async def save_uploaded_file(file: UploadFile) -> FileInfo:
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    file_path = f"uploads/{file_id}{file_extension}"

    os.makedirs("uploads", exist_ok=True)

    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    content = extract_text(file_path)


    return FileInfo(
        id=file_id,
        filename=file.filename,
        path=file_path,
        upload_time=datetime.now(),
        content=content  # 添加内容字段
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
        files: Union[UploadFile, List[UploadFile], None] = File(default=None),
        use_previous_files: bool = Form(False)  # 新增参数，是否使用之前上传的文件
):
    """处理聊天请求"""
    try:
        if session_id not in conversation_histories:
            conversation_histories[session_id] = []

        conversation_history = conversation_histories[session_id]

        file_infos = []
        current_files = []  # 本次请求要使用的文件

        file_list: List[UploadFile] = []
        if files:
            if isinstance(files, list):
                file_list = files
            else:
                file_list = [files]

        if file_list:
            print(f"收到 {len(file_list)} 个文件")
            for file in file_list:
                print(f"文件名: {file.filename}, 类型: {type(file)}")
                file_info = await save_uploaded_file(file)
                file_infos.append(file_info)
                # 将新上传的文件添加到会话文件列表
                if session_id not in uploaded_files:
                    uploaded_files[session_id] = []
                uploaded_files[session_id].append(file_info)
        
        # 确定要使用的文件
        if use_previous_files and session_id in uploaded_files:
            # 使用所有之前上传的文件
            current_files = uploaded_files[session_id]
        else:
            # 只使用本次上传的文件
            current_files = file_infos

        if message.lower() in ["hi", "hello", "你好", "您好", "嗨"]:
            response_text = "你好！我是智能科研助手，可以帮助你搜索资料、解释概念、生成大纲等。请告诉我你需要什么帮助？"
        else:
            intent = analyze_query_intent(message)

            context = []
            for msg in conversation_history[-6:]:  # 保留最近6轮对话作为上下文
                context.append({"role": "user", "content": msg["user"]})
                context.append({"role": "assistant", "content": msg["assistant"]})

            response_text = await handle_research_task(
                app.state.http_session,
                intent,
                message,
                context,
                current_files  # 使用确定的文件列表
            )

        conversation_histories[session_id].append({
            "user": message,
            "assistant": response_text,
            "timestamp": datetime.now().isoformat(),
            "files": [f.filename for f in file_infos]  # 只记录本次上传的文件
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