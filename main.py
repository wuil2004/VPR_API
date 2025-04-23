from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from vrp_solver import resolver_vrp

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def form_post(
    request: Request,
    origen: str = Form(...),
    max_paquetes: int = Form(...),
    max_distancia: float = Form(...),
    max_gasolina: float = Form(...)
):
    rutas = resolver_vrp(origen, max_paquetes, max_distancia, max_gasolina)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "rutas": rutas,
        "origen": origen
    })