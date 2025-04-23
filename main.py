from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
import math
from operator import itemgetter

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Datos base
ciudades_coord = {
    'EDO.MEX': (19.2938258568844, -99.65366252023884),
    'QRO': (20.593537489366717, -100.39004057702225),
    'CDMX': (19.432854452264177, -99.13330004822943),
    'SLP': (22.151725492903953, -100.97657666103268),
    'MTY': (25.673156272083876, -100.2974200019319),
    'PUE': (19.063532268065185, -98.30729139446866),
    'GDL': (20.67714565083998, -103.34696388920293),
    'MICH': (19.702614895389996, -101.19228631929688),
    'SON': (29.075273188617818, -110.95962477655333)
}
ciudades_pedidos = {
    'EDO.MEX': 10,
    'QRO': 13,
    'CDMX': 7,
    'SLP': 11,
    'MTY': 15,
    'PUE': 8,
    'GDL': 6,
    'MICH': 7,
    'SON': 8
}

# Lógica de rutas
def distancia(coord1, coord2):
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

def en_ruta(rutas, c):
    for r in rutas:
        if c in r:
            return r
    return None

def peso_ruta(ruta, pedidos):
    return sum(pedidos[c] for c in ruta)

def distancia_ruta(ruta, almacen, coord):
    total = distancia(almacen, coord[ruta[0]])
    for i in range(len(ruta)-1):
        total += distancia(coord[ruta[i]], coord[ruta[i+1]])
    total += distancia(coord[ruta[-1]], almacen)
    return total

def consumo_gasolina(distancia):
    return distancia / 10

def vrp_voraz(almacen, coord, pedidos, max_carga, max_distancia, max_gasolina):
    s = {}
    for c1 in coord:
        for c2 in coord:
            if c1 != c2 and (c2, c1) not in s:
                d_c1_c2 = distancia(coord[c1], coord[c2])
                d_c1_almacen = distancia(coord[c1], almacen)
                d_c2_almacen = distancia(coord[c2], almacen)
                s[(c1, c2)] = d_c1_almacen + d_c2_almacen - d_c1_c2

    s = sorted(s.items(), key=itemgetter(1), reverse=True)

    rutas = []
    for (c1, c2), _ in s:
        rc1 = en_ruta(rutas, c1)
        rc2 = en_ruta(rutas, c2)

        def check(nueva_ruta):
            peso = peso_ruta(nueva_ruta, pedidos)
            dist = distancia_ruta(nueva_ruta, almacen, coord)
            gas = consumo_gasolina(dist)
            return peso <= max_carga and dist <= max_distancia and gas <= max_gasolina

        if rc1 is None and rc2 is None:
            nueva = [c1, c2]
            if check(nueva):
                rutas.append(nueva)
        elif rc1 and rc2 is None:
            if rc1[0] == c1:
                nueva = [c2] + rc1
            elif rc1[-1] == c1:
                nueva = rc1 + [c2]
            else:
                continue
            if check(nueva):
                rutas[rutas.index(rc1)] = nueva
        elif rc1 is None and rc2:
            if rc2[0] == c2:
                nueva = [c1] + rc2
            elif rc2[-1] == c2:
                nueva = rc2 + [c1]
            else:
                continue
            if check(nueva):
                rutas[rutas.index(rc2)] = nueva
        elif rc1 != rc2:
            if rc1[0] == c1 and rc2[-1] == c2:
                nueva = rc2 + rc1
            elif rc1[-1] == c1 and rc2[0] == c2:
                nueva = rc1 + rc2
            else:
                continue
            if check(nueva):
                rutas.remove(rc1)
                rutas.remove(rc2)
                rutas.append(nueva)

    return rutas

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ciudades": list(ciudades_coord.keys()),
        "resultados": None,
        "origen": "",
        "destinos": [],
        "max_carga": 0,
        "max_distancia": 0,
        "max_gasolina": 0
    })

@app.post("/rutas", response_class=HTMLResponse)
async def generar_rutas(
    request: Request,
    origen: str = Form(...),
    destinos: List[str] = Form(...),
    max_carga: int = Form(...),
    max_distancia: float = Form(...),
    max_gasolina: float = Form(...)
):
    almacen = ciudades_coord[origen]
    ciudades_seleccionadas = [origen] + destinos
    coord_filtrado = {k: v for k, v in ciudades_coord.items() if k in ciudades_seleccionadas}
    pedidos_filtrados = {k: v for k, v in ciudades_pedidos.items() if k in ciudades_seleccionadas}

    rutas = vrp_voraz(almacen, coord_filtrado, pedidos_filtrados, max_carga, max_distancia, max_gasolina)

    resultados = []
    if rutas:
        for i, ruta in enumerate(rutas, 1):
            dist = distancia_ruta(ruta, almacen, coord_filtrado)
            gas = consumo_gasolina(dist)
            resultados.append({
                "id": i,
                "ruta": ruta,
                "peso": peso_ruta(ruta, pedidos_filtrados),
                "distancia": f"{dist:.2f}",
                "gasolina": f"{gas:.2f}"
            })
    else:
        resultados = "No se encontraron rutas que cumplieran con los requisitos."

    return templates.TemplateResponse("index.html", {
        "request": request,
        "ciudades": list(ciudades_coord.keys()),
        "resultados": resultados,
        "origen": origen,
        "destinos": destinos,
        "max_carga": max_carga,
        "max_distancia": max_distancia,
        "max_gasolina": max_gasolina
    })
