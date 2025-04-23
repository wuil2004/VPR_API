from math import sqrt
from operator import itemgetter

def distancia(coord1, coord2):
    return sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

def en_ruta(rutas, cliente):
    for ruta in rutas:
        if cliente in ruta:
            return ruta
    return None

def calcular_rutas(coord, pedidos, almacen, max_carga, max_litros, max_distancia, litros_por_km):
    def peso_ruta(ruta):
        return sum(pedidos[cliente] for cliente in ruta)

    def distancia_ruta(ruta):
        if not ruta:
            return 0
        total = distancia(almacen, coord[ruta[0]])
        for i in range(len(ruta) - 1):
            total += distancia(coord[ruta[i]], coord[ruta[i + 1]])
        total += distancia(coord[ruta[-1]], almacen)
        return total

    def combustible_ruta(ruta):
        return distancia_ruta(ruta) * litros_por_km

    def restricciones_ok(ruta):
        return (
            peso_ruta(ruta) <= max_carga and
            distancia_ruta(ruta) <= max_distancia and
            combustible_ruta(ruta) <= max_litros
        )

    s = {}
    for c1 in coord:
        for c2 in coord:
            if c1 != c2 and (c2, c1) not in s:
                ahorro = distancia(almacen, coord[c1]) + distancia(almacen, coord[c2]) - distancia(coord[c1], coord[c2])
                s[(c1, c2)] = ahorro

    s = sorted(s.items(), key=itemgetter(1), reverse=True)

    rutas = []
    for (c1, c2), ahorro in s:
        rc1 = en_ruta(rutas, c1)
        rc2 = en_ruta(rutas, c2)

        if rc1 is None and rc2 is None:
            nueva = [c1, c2]
            if restricciones_ok(nueva):
                rutas.append(nueva)
        elif rc1 is not None and rc2 is None:
            if peso_ruta(rc1) + pedidos[c2] <= max_carga:
                if rc1[0] == c1:
                    nueva = [c2] + rc1
                elif rc1[-1] == c1:
                    nueva = rc1 + [c2]
                else:
                    continue
                if restricciones_ok(nueva):
                    rutas.remove(rc1)
                    rutas.append(nueva)
        elif rc1 is None and rc2 is not None:
            if peso_ruta(rc2) + pedidos[c1] <= max_carga:
                if rc2[0] == c2:
                    nueva = [c1] + rc2
                elif rc2[-1] == c2:
                    nueva = rc2 + [c1]
                else:
                    continue
                if restricciones_ok(nueva):
                    rutas.remove(rc2)
                    rutas.append(nueva)
        elif rc1 is not None and rc2 is not None and rc1 != rc2:
            if peso_ruta(rc1 + rc2) <= max_carga:
                if rc1[-1] == c1 and rc2[0] == c2:
                    nueva = rc1 + rc2
                elif rc2[-1] == c2 and rc1[0] == c1:
                    nueva = rc2 + rc1
                else:
                    continue
                if restricciones_ok(nueva):
                    rutas.remove(rc1)
                    rutas.remove(rc2)
                    rutas.append(nueva)

    # Devolver las rutas con info extra para el frontend
    resultado = []
    for ruta in rutas:
        resultado.append({
            "ruta": ruta,
            "distancia": distancia_ruta(ruta),
            "combustible": combustible_ruta(ruta)
        })

    return resultado
