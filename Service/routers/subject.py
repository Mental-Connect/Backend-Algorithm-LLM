from fastapi import APIRouter
from Service.common.subject_information import SubjectInformation
from Service.common.session_manager import session_manager
import logging

router = APIRouter()

@router.post("/subject-information", response_model=SubjectInformation)
async def student_info(info: SubjectInformation):
    session_manager.student_id_info = info.subject_id
    logging.info(f"Received student info: {info.subject_id}")
    session_manager.database_data_saved[session_manager.student_id_info] = {
        "Student Name": info.subject_name,
        "Student Age": info.subject_age,
        "Student Gender": info.subject_gender,
    }
    return info
