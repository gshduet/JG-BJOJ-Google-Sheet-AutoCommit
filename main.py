import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import apis
from docs import setup_public_docs

load_dotenv()
ENV = os.environ.get('SERVICE_ENV')
PORT = 8001 if ENV == 'dev' else 80
app = FastAPI(docs_url=None, redoc_url=None)


origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

init_schemas = ['HTTPValidationError', 'ValidationError']
input_schemas = [
    'SheetAutoCommit',
]

setup_public_docs(
    app,
    title='Jungle GoogleSheet AutoCommit API',
    version='1.0.0',
    description='백준을 풀고 마이페이지의 맞은 문제를 샥! 긁어서 입력하면 스프레드 시트에 자동으로 커밋해드립니다!',
    public_schemas=init_schemas + input_schemas
)

@app.get('/health')
def heathcheck():
    return 200

app.include_router(apis.google_router)

if __name__ == '__main__':
    uvicorn_config = {
        'app': 'main:app',
        'host': '0.0.0.0',
        'port': PORT,
        'reload': ENV == 'dev',
        'log_level': 'info'
    }
    uvicorn.run(**uvicorn_config)
