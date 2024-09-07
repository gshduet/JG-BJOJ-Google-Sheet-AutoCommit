from pydantic import BaseModel, Field


class SheetAutoCommit(BaseModel):
    user_name: str = Field(..., description="이름, 성 빼고!")
    solved_problems: str = Field(..., description="풀어낸 문제들")
    mark:str = Field(..., description="넣고 싶은 마크, 예: 왕")