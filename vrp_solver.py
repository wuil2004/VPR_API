from typing import List, Tuple
import networkx as nx

def resolver_vrp(origen: str, max_paquetes: int, max_distancia: float, max_gasolina: float) -> List[List[str]]:
    ciudades = ["EDO.MEX", "QRO", "CDMX", "SLP", "MTY", "PUE", "GDL", "MICH", "SON"]
    paquetes = {
        "EDO.MEX": 12,
        "QRO": 8,
        "CDMX": 4,
        "SLP": 15,
        "MTY": 20,
        "PUE": 6,
        "GDL": 10,
        "MICH": 5,
        "SON": 25
    }

    distancias = {
        ("CDMX", "EDO.MEX"): 47,
        ("CDMX", "QRO"): 211,
        ("CDMX", "SLP"): 412,
        ("CDMX", "MTY"): 913,
        ("CDMX", "PUE"): 131,
        ("CDMX", "GDL"): 535,
        ("CDMX", "MICH"): 303,
        ("CDMX", "SON"): 1820,
        ("QRO", "EDO.MEX"): 179,
        ("QRO", "SLP"): 246,
        ("SLP", "MTY"): 496,
        ("GDL", "MTY"): 935,
        ("GDL", "SON"): 1483,
        ("MICH", "SON"): 1601,
    }

    for (c1, c2), d in list(distancias.items()):
        distancias[(c2, c1)] = d

    G = nx.Graph()
    for (c1, c2), d in distancias.items():
        G.add_edge(c1, c2, weight=d)

    pendientes = [(c, paquetes[c]) for c in ciudades if c != origen]
    rutas = []

    while pendientes:
        ruta = [origen]
        carga = 0
        distancia = 0
        gasolina = max_gasolina
        disponibles = pendientes.copy()

        while disponibles:
            actuales = [(ciudad, paquetes, nx.dijkstra_path(G, ruta[-1], ciudad), nx.dijkstra_path_length(G, ruta[-1], ciudad))
                        for ciudad, paquetes in disponibles]

            actuales = [x for x in actuales if carga + x[1] <= max_paquetes and distancia + x[3] <= max_distancia and gasolina - (x[3] / 10) >= 0]

            if not actuales:
                break

            actuales.sort(key=lambda x: x[3])
            ciudad, carga_ciudad, camino, dist = actuales[0]
            ruta.extend(camino[1:])
            carga += carga_ciudad
            distancia += dist
            gasolina -= dist / 10
            pendientes = [x for x in pendientes if x[0] != ciudad]
            disponibles = [x for x in disponibles if x[0] != ciudad]

        rutas.append(ruta)

    return rutas