from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import JSONResponse


def custom_openapi(
        app: FastAPI,
        title: str,
        version: str,
        description: str,
        public_schemas: list = None
):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=title,
        version=version,
        description=description,
        routes=app.routes,
    )

    # Filter paths
    public_paths = {}
    for path, path_item in openapi_schema["paths"].items():
        for method, method_info in path_item.items():
            if "tags" in method_info and "public" in method_info["tags"]:

                if path not in public_paths:
                    public_paths[path] = {}

                public_paths[path][method] = method_info

                if "responses" in method_info:
                    method_info["responses"].pop("422", None)

    openapi_schema["paths"] = public_paths

    if public_schemas is not None:
        filtered_schemas = {
            k: v for k, v in
            openapi_schema.get("components", {}).get("schemas", {}).items() if
            k in public_schemas
        }

        if "components" not in openapi_schema:
            openapi_schema["components"] = {}

        openapi_schema["components"]["schemas"] = filtered_schemas

    else:
        if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
            del openapi_schema["components"]["schemas"]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def setup_public_docs(
        app: FastAPI,
        title: str,
        version: str,
        description: str,
        public_schemas: list = None
):
    app.openapi = lambda: custom_openapi(app, title, version, description, public_schemas)

    @app.get("/public-docs", include_in_schema=False)
    async def get_documentation():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=f"{title} - Public API Docs"
        )

    @app.get("/openapi.json", include_in_schema=False)
    async def get_openapi_json():
        return JSONResponse(
            custom_openapi(app, title, version, description, public_schemas)
        )
