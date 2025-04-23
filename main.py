from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import math
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
    total = distancia(origen, coord[ruta[0]])
    for i in range(len(ruta)-1):
        total += distancia(coord[ruta[i]], coord[ruta[i+1]])
    total += distancia(coord[ruta[-1]], destino)
    return total

def consumo_gasolina(distancia):
    return distancia / 10  # 10 km por litro

def vrp_voraz_con_destino(origen, destino, max_carga, max_distancia, max_gasolina):
    s = {}
    for c1 in coord:
        for c2 in coord:
            if c1 != c2 and not (c2, c1) in s:
                d_c1_c2 = distancia(coord[c1], coord[c2])
                d_c1_origen = distancia(coord[c1], origen)
                d_c2_destino = distancia(coord[c2], destino)
                s[c1, c2] = d_c1_origen + d_c2_destino - d_c1_c2
    s = sorted(s.items(), key=itemgetter(1), reverse=True)

    rutas = []
    for k, v in s:
        rc1 = en_ruta(rutas, k[0])
        rc2 = en_ruta(rutas, k[1])

        def validar_y_agregar(nueva_ruta):
            d = distancia_ruta_con_destino(nueva_ruta, origen, destino)
            if (peso_ruta(nueva_ruta) <= max_carga and
                d <= max_distancia and
                consumo_gasolina(d) <= max_gasolina):
                return nueva_ruta
            return None

        if rc1 == None and rc2 == None:
            nueva = validar_y_agregar([k[0], k[1]])
            if nueva: rutas.append(nueva)
        elif rc1 and not rc2:
            if rc1[0] == k[0]:
                nueva = validar_y_agregar([k[1]] + rc1)
            elif rc1[-1] == k[0]:
                nueva = validar_y_agregar(rc1 + [k[1]])
            else:
                continue
            if nueva: rutas[rutas.index(rc1)] = nueva
        elif not rc1 and rc2:
            if rc2[0] == k[1]:
                nueva = validar_y_agregar([k[0]] + rc2)
            elif rc2[-1] == k[1]:
                nueva = validar_y_agregar(rc2 + [k[0]])
            else:
                continue
            if nueva: rutas[rutas.index(rc2)] = nueva
        elif rc1 != rc2:
            if rc1[-1] == k[0] and rc2[0] == k[1]:
                nueva = validar_y_agregar(rc1 + rc2)
            elif rc2[-1] == k[1] and rc1[0] == k[0]:
                nueva = validar_y_agregar(rc2 + rc1)
            else:
                continue
            if nueva:
                rutas.remove(rc1)
                rutas.remove(rc2)
                rutas.append(nueva)
    return rutas


@app.get("/", response_class=HTMLResponse)
def form(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ciudades": list(coord.keys()),
        "origen": None,
        "destino": None,
        "max_carga": None,
        "max_distancia": None,
        "max_gasolina": None
    })


@app.post("/rutas", response_class=HTMLResponse)
async def generar_rutas(
    request: Request,
    origen: str = Form(...),
    destino: str = Form(...),
    max_carga: int = Form(...),
    max_distancia: float = Form(...),
    max_gasolina: float = Form(...)
):
    almacen = coord[origen]
    ciudad_final = coord[destino]

    rutas = vrp_voraz_con_destino(almacen, ciudad_final, max_carga, max_distancia, max_gasolina)

    resultados = []
    for i, ruta in enumerate(rutas, 1):
        dist = distancia_ruta_con_destino(ruta, almacen, ciudad_final)
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
        "max_carga": max_carga,
        "max_distancia": max_distancia,
        "max_gasolina": max_gasolina
    })
