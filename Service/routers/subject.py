from fastapi import APIRouter
from Service.common.http.subject_information_request import SubjectInformationRequest
from Service.common.audio_receive_queue import audio_receive_queue
from Service.common.data.student_info import StudentInfo
import logging

student_information = StudentInfo()
router = APIRouter()

@router.post("/subject-information", response_model=SubjectInformationRequest)
async def student_info(info: SubjectInformationRequest):
    student_information.student_id_info = info.subject_id
    logging.info(f"Received student info: {info.subject_id}")
    student_information.database_data_saved[student_information.student_id_info] = {
        "Student Name": info.subject_name,
        "Student Age": info.subject_age,
        "Student Gender": info.subject_gender,
    }
    return info
