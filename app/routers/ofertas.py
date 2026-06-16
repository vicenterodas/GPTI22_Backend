import uuid
from flask import Blueprint, request, jsonify
from app.db import get_db_connection

ofertas_bp = Blueprint("ofertas", __name__, url_prefix="/ofertas")


@ofertas_bp.route("", methods=["GET"])
def get_ofertas():
    try:
        area = request.args.get("area")
        modalidad = request.args.get("modalidad")
        ubicacion = request.args.get("ubicacion")
        nivel = request.args.get("nivel")
        empresa = request.args.get("empresa")
        activa = request.args.get("activa")

        query = "SELECT * FROM ofertas WHERE 1=1"
        params = []

        if area:
            query += " AND area LIKE ?"
            params.append(f"%{area}%")

        if modalidad:
            query += " AND modalidad LIKE ?"
            params.append(f"%{modalidad}%")

        if ubicacion:
            query += " AND ubicacion LIKE ?"
            params.append(f"%{ubicacion}%")

        if nivel:
            query += " AND nivel LIKE ?"
            params.append(f"%{nivel}%")

        if empresa:
            query += " AND empresa LIKE ?"
            params.append(f"%{empresa}%")

        if activa is not None:
            query += " AND activa = ?"
            params.append(int(activa))

        conn = get_db_connection()
        rows = conn.execute(query, params).fetchall()
        conn.close()

        return jsonify([dict(r) for r in rows]), 200

    except Exception as e:
        return jsonify({
            "error": "Error al obtener ofertas",
            "details": str(e)
        }), 500


@ofertas_bp.route("", methods=["POST"])
def create_oferta():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Body JSON requerido"
            }), 400

        required_fields = ["titulo", "empresa", "link"]

        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({
                "error": "Faltan campos obligatorios",
                "missing": missing
            }), 400

        id_oferta = str(uuid.uuid4())

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO ofertas (
                id,
                titulo, empresa, descripcion, ubicacion,
                modalidad, area, nivel,
                fecha_publicacion, fecha_expiracion,
                link, salario, duracion,
                activa
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_oferta,
            data.get("titulo"),
            data.get("empresa"),
            data.get("descripcion"),
            data.get("ubicacion"),
            data.get("modalidad"),
            data.get("area"),
            data.get("nivel"),
            data.get("fecha_publicacion"),
            data.get("fecha_expiracion"),
            data.get("link"),
            data.get("salario"),
            data.get("duracion"),
            1
        ))

        conn.commit()
        conn.close()

        return jsonify({"message": "Oferta creada correctamente"}), 201

    except Exception as e:
        return jsonify({
            "error": "Error al crear oferta",
            "details": str(e)
        }), 500