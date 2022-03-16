import pytest
from aiohttp import web

async def test_get_post(aiohttp_server: Any) -> None:
    async def handler(request: web.Request) -> web.Response:
        data = await request.json()
        assert data["title"] == "test title"
        assert data["text"] == "test text"
        return web.json_response(
            {
                "status": "ok",
                "data": {
                    "id": 1,
                    "title": "test title",
                    "text": "test text",
                    "owner": "test_user",
                    "editor": "test_user",
                },
            }
        )

    app = web.Application()
    app.add_routes([web.post("/api", handler)])
    server = await aiohttp_server(app)