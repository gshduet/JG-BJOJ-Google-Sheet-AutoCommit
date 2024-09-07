import time

import gspread
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from google.auth.exceptions import TransportError

from schemas import SheetAutoCommit
from config import get_settings


config = get_settings()
google_router = APIRouter(prefix='/api/google')


def exponential_backoff(func):
    def wrapper(*args, **kwargs):
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except (gspread.exceptions.APIError, TransportError) as e:
                if attempt == max_attempts - 1:
                    raise
                wait_time = 2 ** attempt
                print(f"API error, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    return wrapper

@google_router.post(
    '/commit',
    description='정보 입력 API',
    tags=['public']
)
async def docs_contacn(request: SheetAutoCommit):
    json_file_path = config.json_file_path
    spreadsheet_url = config.spreadsheet_url
    user_name: str = request.user_name
    solved_problems: list = request.solved_problems.split()
    mark: str = request.mark

    gc = gspread.service_account(json_file_path)
    doc = gc.open_by_url(spreadsheet_url)
    worksheet = doc.worksheet("시트1")

    @exponential_backoff
    def get_all_values():
        return worksheet.get_all_values()

    @exponential_backoff
    def batch_update(updates):
        worksheet.batch_update(updates)

    # 전체 워크시트 데이터를 한 번에 가져오기
    data = get_all_values()

    # 1. 사용자 이름 찾기
    user_column = None
    for col, cell in enumerate(data[1], start=1):  # 2번째 행 (인덱스 1)
        if cell == user_name:
            user_column = col
            break

    if user_column is None:
        return JSONResponse(status_code=404, content={"message": "User not found"})

    # 2 & 3. 문제 번호 찾고 마크 표시하기
    updates = []
    for row, row_data in enumerate(data[2:], start=3):  # 3번째 행부터 시작
        problem_number = row_data[1]  # B열 (인덱스 1)
        if problem_number in solved_problems:
            updates.append({
                'range': f'{chr(64 + user_column)}{row}',
                'values': [[mark]]
            })

    if updates:
        batch_update(updates)

    return JSONResponse(
        status_code=200,
        content={
            "message": "Update completed",
            "problems_marked": len(updates)
        }
    )