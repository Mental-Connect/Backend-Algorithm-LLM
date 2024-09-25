import os
import sys
import asyncio
import logging
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from Algorithm.audio_text_llm.service.audio_to_text import audio_to_text_model
from Algorithm.question_answering_llm.service.chat_bot import chatbot
from Service.common.request import Request
from Service.common.response import Response
from Service.common.session_manager import *
from Service.common.subject_information import SubjectInformation
from Service.common.router_functions import *
from Service.database.mogodb import collection
from Service.logging.logging import * 

# FastAPI app
app = FastAPI()
app.mount("/demo", StaticFiles(directory="demo"), name="demo")

@app.get("/")
async def get():
    with open("demo/demo.html", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content)

@app.post("/subject-information", response_model=SubjectInformation)
async def student_info(info: SubjectInformation):
    session_manager.student_id_info = info.subject_id
    logging.info(f"Received student info: {info.subject_id}")
    session_manager.database_data_saved[session_manager.student_id_info] = {
        "Student Name": info.subject_name,
        "Student Age": info.subject_age,
        "Student Gender": info.subject_gender,
    }
    return info

@app.websocket("/audio-transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_manager.active_websockets.add(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            await session_manager.audio_queue.put(data)
    except WebSocketDisconnect:
        handle_disconnection(websocket)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        await websocket.close()


# Start audio queue processing on startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_audio_queue())

@app.post("/chatbot", response_model=Response)
async def chat_model(request: Request):
    full_transcription = session_manager.transcription_storage[TRANSCRIPTION_KEY]
    student_id = session_manager.student_id_info
    if not full_transcription:
        return {"response": "No transcription available. Please upload an audio file first."}

    response_text = chatbot(query=request.prompt, context=full_transcription)

    if student_id:
        if 'question_answers' not in session_manager.database_data_saved[student_id]:
            session_manager.database_data_saved[student_id]['question_answers'] = []
        session_manager.database_data_saved[student_id]['question_answers'].append({
            "prompt": request.prompt,
            "answer": response_text.response
        })
    else:
        logging.warning("Student ID is not initialized")
    
    
    logging.info(f"Database after chat: {session_manager.database_data_saved}")
    return Response(response=response_text.response)

@app.post("/save_session")
async def end_session():
    if session_manager.database_data_saved:
        documents = [data for data in session_manager.database_data_saved.values()]
        collection.insert_many(documents)
        session_manager.database_data_saved.clear()
        return {"status": "Session data saved and cleared"}
    else:
        return {"status": "No session data to save"}



