from flask import Flask, request, jsonify, render_template
from vrp import calcular_rutas  # asegúrate de que tu lógica está aquí

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/calcular", methods=["POST"])
def api_calcular():
    data = request.get_json()

    coord = data["coord"]
    pedidos = data["pedidos"]
    almacen = tuple(data["almacen"])
    max_carga = data["max_carga"]
    max_litros = data["max_litros"]
    max_distancia = data["max_distancia"]
    litros_por_km = data["litros_por_km"]

    rutas = calcular_rutas(coord, pedidos, almacen, max_carga, max_litros, max_distancia, litros_por_km)

    return jsonify({"rutas": rutas})

if __name__ == "__main__":
    app.run(debug=True)
