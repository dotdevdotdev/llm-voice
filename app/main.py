from fastapi import FastAPI, Request, Form
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import aiohttp
from app.llm_voice import get_llm_response, text_to_speech, Config

app = FastAPI()
templates = Jinja2Templates(directory="templates")
config = Config()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate")
async def generate_audio(prompt: str = Form(...)):
    async with aiohttp.ClientSession() as session:
        llm_response = await get_llm_response(prompt)
        if llm_response:
            return StreamingResponse(
                text_to_speech(llm_response, session), media_type="audio/mpeg"
            )
        else:
            return {"error": "Failed to get LLM response"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
