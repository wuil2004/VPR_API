from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import math
from typing import Optional
from operator import itemgetter

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Coordenadas y pedidos fijos
coord = {
    'EDO.MEX': (19.2938, -99.6536),
    'QRO': (20.5935, -100.3900),
    'CDMX': (19.4328, -99.1333),
    'SLP': (22.1517, -100.9765),
    'MTY': (25.6731, -100.2974),
    'PUE': (19.0635, -98.3072),
    'GDL': (20.6771, -103.3469),
    'MICH': (19.7026, -101.1922),
    'SON': (29.0752, -110.9596)
}
pedidos = {
    'EDO.MEX': 10, 'QRO': 13, 'CDMX': 7, 'SLP': 11,
    'MTY': 15, 'PUE': 8, 'GDL': 6, 'MICH': 7, 'SON': 8
}

def distancia(coord1, coord2):
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

def en_ruta(rutas, c):
    for r in rutas:
        if c in r:
            return r
    return None

def peso_ruta(ruta):
    return sum(pedidos[c] for c in ruta)

def distancia_ruta_con_destino(ruta, origen, destino):
    total = distancia(origen, coord[ruta[0]])  # origen debe ser un nombre de ciudad
    for i in range(len(ruta) - 1):
        total += distancia(coord[ruta[i]], coord[ruta[i + 1]])
    total += distancia(coord[ruta[-1]], destino)  # destino debe ser un nombre de ciudad
    return total

def consumo_gasolina(distancia):
    return distancia / 10  # 10 km por litro

def vrp_voraz_con_destino(origen, intermedias, destino, max_carga, max_distancia, max_gasolina):
    ciudades_ruta = [origen] + intermedias + [destino]
    rutas = []

    for i in range(len(ciudades_ruta) - 1):
        ruta = [ciudades_ruta[i], ciudades_ruta[i + 1]]
        dist = distancia_ruta_con_destino(ruta, coord[origen], coord[destino])
        if dist <= max_distancia:
            rutas.append(ruta)

    return rutas

@app.get("/", response_class=HTMLResponse)
def form(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ciudades": list(coord.keys())
    })

@app.post("/rutas", response_class=HTMLResponse)
async def generar_rutas(
    request: Request,
    origen: str = Form(...),
    intermedias: Optional[list[str]] = Form([], alias="intermedias"),  # Asignamos valor predeterminado con Optional
    destino: str = Form(...),
    max_carga: int = Form(...),
    max_distancia: float = Form(...),
    max_gasolina: float = Form(...)
):
    print(f"Origen: {origen}, Intermedias: {intermedias}, Destino: {destino}")
    
    rutas = vrp_voraz_con_destino(origen, intermedias, destino, max_carga, max_distancia, max_gasolina)

    resultados = []
    for i, ruta in enumerate(rutas, 1):
        dist = distancia_ruta_con_destino(ruta, coord[origen], coord[destino])
        gas = consumo_gasolina(dist)
        resultados.append({
            "id": i,
            "ruta": ruta,
            "peso": peso_ruta(ruta),
            "distancia": f"{dist:.2f}",
            "gasolina": f"{gas:.2f}"
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "ciudades": list(coord.keys()),
        "resultados": resultados,
        "origen": origen,
        "destino": destino,
        "intermedias": intermedias,
        "max_carga": max_carga,
        "max_distancia": max_distancia,
        "max_gasolina": max_gasolina
    })
