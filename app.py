from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from google import genai
import psycopg2
import psycopg2.extras
import traceback
import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "techstore-secret-2026")

# =====================================================
# CONFIGURACIÓN GEMINI
# =====================================================

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

# =====================================================
# CONFIGURACIÓN CLOUDINARY
# =====================================================

cloudinary.config(
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key    = os.environ.get("CLOUDINARY_API_KEY"),
    api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
    secure     = True
)

CLOUDINARY_UPLOAD_PRESET = os.environ.get("CLOUDINARY_UPLOAD_PRESET", "techstore_admin")

# =====================================================
# CONFIGURACIÓN POSTGRESQL
# =====================================================

DATABASE_URL = os.environ.get("DATABASE_URL")


# =====================================================
# HELPERS DB
# =====================================================

def consultar_db(sql, params=None):
    conn = cur = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        return cur.fetchall()
    except Exception as e:
        print(f"\n[ERROR DB SELECT] {e}")
        return None
    finally:
        if cur:  cur.close()
        if conn: conn.close()


def ejecutar_db(sql, params=None):
    conn = cur = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        conn.commit()
        try:
            return cur.fetchone()
        except Exception:
            return True
    except Exception as e:
        print(f"\n[ERROR DB WRITE] {e}")
        if conn: conn.rollback()
        return None
    finally:
        if cur:  cur.close()
        if conn: conn.close()


# =====================================================
# DECORADORES DE ROLES
# =====================================================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("usuario_id"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("usuario_id"):
            return redirect(url_for("login"))
        if session.get("rol") != "admin":
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


# =====================================================
# PÁGINAS PÚBLICAS
# =====================================================

@app.route("/")
def index():
    return render_template("index.html")


# =====================================================
# AUTH — LOGIN
# =====================================================

@app.route("/login")
def login():
    if session.get("usuario_id"):
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    try:
        data   = request.get_json()
        correo = data.get("correo", "").strip().lower()
        pin    = data.get("pin", "").strip()

        if not correo or not pin:
            return jsonify({"error": "Correo y PIN son obligatorios"}), 400

        if len(pin) != 4 or not pin.isdigit():
            return jsonify({"error": "El PIN debe tener 4 dígitos"}), 400

        usuario = ejecutar_db(
            "SELECT id_usr, nombre, correo, rol FROM usuarios WHERE correo = %s AND pin = %s",
            (correo, pin)
        )

        if not usuario:
            return jsonify({"error": "Correo o PIN incorrectos"}), 401

        session["usuario_id"] = usuario["id_usr"]
        session["nombre"]     = usuario["nombre"]
        session["correo"]     = usuario["correo"]
        session["rol"]        = usuario["rol"]

        return jsonify({
            "ok":     True,
            "nombre": usuario["nombre"],
            "rol":    usuario["rol"]
        })

    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Error interno"}), 500


# =====================================================
# AUTH — REGISTRO
# =====================================================

@app.route("/registro")
def registro():
    if session.get("usuario_id"):
        return redirect(url_for("index"))
    return render_template("registro.html")


@app.route("/api/registro", methods=["POST"])
def api_registro():
    try:
        data   = request.get_json()
        nombre = data.get("nombre", "").strip()
        correo = data.get("correo", "").strip().lower()
        pin    = data.get("pin", "").strip()

        if not nombre or not correo or not pin:
            return jsonify({"error": "Todos los campos son obligatorios"}), 400

        if len(pin) != 4 or not pin.isdigit():
            return jsonify({"error": "El PIN debe tener exactamente 4 dígitos"}), 400

        if "@" not in correo or "." not in correo:
            return jsonify({"error": "Correo inválido"}), 400

        # Verificar si ya existe
        existe = consultar_db(
            "SELECT id_usr FROM usuarios WHERE correo = %s",
            (correo,)
        )

        if existe:
            return jsonify({"error": "Ese correo ya está registrado"}), 409

        nuevo = ejecutar_db(
            "INSERT INTO usuarios (nombre, correo, pin, rol) VALUES (%s, %s, %s, 'cliente') RETURNING id_usr, nombre, rol",
            (nombre, correo, pin)
        )

        if nuevo:
            session["usuario_id"] = nuevo["id_usr"]
            session["nombre"]     = nuevo["nombre"]
            session["correo"]     = correo
            session["rol"]        = "cliente"

            return jsonify({"ok": True, "nombre": nuevo["nombre"], "rol": "cliente"}), 201
        else:
            return jsonify({"error": "Error al crear la cuenta"}), 500

    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Error interno"}), 500


# =====================================================
# AUTH — LOGOUT
# =====================================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =====================================================
# AUTH — ESTADO DE SESIÓN (para el frontend)
# =====================================================

@app.route("/api/sesion")
def api_sesion():
    if session.get("usuario_id"):
        return jsonify({
            "logueado": True,
            "nombre":   session.get("nombre"),
            "rol":      session.get("rol")
        })
    return jsonify({"logueado": False})


# =====================================================
# PÁGINA ADMIN (protegida)
# =====================================================

@app.route("/admin")
@admin_required
def admin():
    return render_template("admin.html")


# =====================================================
# API PRODUCTOS PÚBLICA
# =====================================================

@app.route("/api/productos", methods=["GET"])
def get_productos():
    productos = consultar_db("""
        SELECT id_pro, nom_pro, pre_pro, stk_pro, ventas,
               categoria, img_url, oferta, pre_oferta
        FROM productos
        ORDER BY ventas DESC
    """)
    return jsonify(productos if productos else [])


# =====================================================
# API ADMIN — CRUD PRODUCTOS
# =====================================================

@app.route("/api/admin/productos", methods=["GET"])
@admin_required
def admin_get_productos():
    productos = consultar_db("""
        SELECT id_pro, nom_pro, pre_pro, stk_pro, ventas,
               categoria, img_url, oferta, pre_oferta
        FROM productos
        ORDER BY id_pro ASC
    """)
    return jsonify(productos if productos else [])


@app.route("/api/admin/productos", methods=["POST"])
@admin_required
def admin_crear_producto():
    try:
        data      = request.get_json()
        nom_pro   = data.get("nom_pro", "").strip()
        pre_pro   = float(data.get("pre_pro", 0))
        stk_pro   = int(data.get("stk_pro", 0))
        ventas    = int(data.get("ventas", 0))
        categoria = data.get("categoria", "General").strip()
        img_url   = data.get("img_url", "").strip()
        oferta    = bool(data.get("oferta", False))
        pre_oferta = data.get("pre_oferta")
        pre_oferta = float(pre_oferta) if pre_oferta else None

        if not nom_pro:
            return jsonify({"error": "El nombre es obligatorio"}), 400

        nuevo = ejecutar_db("""
            INSERT INTO productos (nom_pro, pre_pro, stk_pro, ventas, categoria, img_url, oferta, pre_oferta)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_pro, nom_pro, pre_pro, stk_pro, ventas, categoria, img_url, oferta, pre_oferta
        """, (nom_pro, pre_pro, stk_pro, ventas, categoria, img_url, oferta, pre_oferta))

        if nuevo:
            return jsonify({"ok": True, "producto": dict(nuevo)}), 201
        return jsonify({"error": "Error al crear"}), 500

    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Error interno"}), 500


@app.route("/api/admin/productos/<int:id_pro>", methods=["PUT"])
@admin_required
def admin_editar_producto(id_pro):
    try:
        data      = request.get_json()
        nom_pro   = data.get("nom_pro", "").strip()
        pre_pro   = float(data.get("pre_pro", 0))
        stk_pro   = int(data.get("stk_pro", 0))
        ventas    = int(data.get("ventas", 0))
        categoria = data.get("categoria", "General").strip()
        img_url   = data.get("img_url", "").strip()
        oferta    = bool(data.get("oferta", False))
        pre_oferta = data.get("pre_oferta")
        pre_oferta = float(pre_oferta) if pre_oferta else None

        if not nom_pro:
            return jsonify({"error": "El nombre es obligatorio"}), 400

        actualizado = ejecutar_db("""
            UPDATE productos
            SET nom_pro=%s, pre_pro=%s, stk_pro=%s, ventas=%s,
                categoria=%s, img_url=%s, oferta=%s, pre_oferta=%s
            WHERE id_pro=%s
            RETURNING id_pro, nom_pro, pre_pro, stk_pro, ventas, categoria, img_url, oferta, pre_oferta
        """, (nom_pro, pre_pro, stk_pro, ventas, categoria, img_url, oferta, pre_oferta, id_pro))

        if actualizado:
            return jsonify({"ok": True, "producto": dict(actualizado)})
        return jsonify({"error": "Producto no encontrado"}), 404

    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Error interno"}), 500


@app.route("/api/admin/productos/<int:id_pro>", methods=["DELETE"])
@admin_required
def admin_eliminar_producto(id_pro):
    try:
        eliminado = ejecutar_db(
            "DELETE FROM productos WHERE id_pro=%s RETURNING id_pro",
            (id_pro,)
        )
        if eliminado:
            return jsonify({"ok": True})
        return jsonify({"error": "Producto no encontrado"}), 404
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Error interno"}), 500


# =====================================================
# API ADMIN — SUBIR IMAGEN A CLOUDINARY
# =====================================================

@app.route("/api/admin/upload-imagen", methods=["POST"])
@admin_required
def admin_upload_imagen():
    try:
        if "imagen" not in request.files:
            return jsonify({"error": "No se recibió imagen"}), 400

        archivo = request.files["imagen"]

        if archivo.filename == "":
            return jsonify({"error": "Archivo vacío"}), 400

        tipos_ok = {"image/jpeg", "image/png", "image/webp", "image/gif"}
        if archivo.content_type not in tipos_ok:
            return jsonify({"error": "Solo JPG, PNG, WEBP o GIF"}), 400

        resultado = cloudinary.uploader.upload(
            archivo,
            folder        = "techstore",
            upload_preset = CLOUDINARY_UPLOAD_PRESET,
            resource_type = "image"
        )

        return jsonify({
            "ok":        True,
            "url":       resultado.get("secure_url"),
            "public_id": resultado.get("public_id")
        })

    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Error al subir imagen"}), 500


# =====================================================
# CHAT (IA)
# =====================================================

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data     = request.get_json()
        pregunta = (data or {}).get("pregunta", "").strip()

        if not pregunta:
            return jsonify({"respuesta": "Por favor escribe una pregunta."})

        esquema = (
            "Tabla productos con columnas: "
            "id_pro, nom_pro, pre_pro, stk_pro, ventas, categoria, img_url, "
            "oferta (boolean), pre_oferta (precio con descuento)."
        )

        datos = None

        # FASE 1 — Clasificar y generar SQL si aplica
        try:
            res_sql = client.models.generate_content(
                model    = "gemini-2.5-flash",
                contents = f"""
Analiza el siguiente mensaje:

{pregunta}

Si es un saludo o conversación normal responde únicamente: CHAT

Si necesita información de la tabla productos:
{esquema}

Responde únicamente una consulta SQL SELECT válida.
No agregues explicaciones. No uses markdown. No uses ```sql.
"""
            )

            sql_limpio = (
                res_sql.text.strip()
                .replace("```sql", "").replace("```", "").replace("`", "").strip()
                .split(";")[0]
            )

            if "SELECT" in sql_limpio.upper() and "FROM" in sql_limpio.upper():
                datos = consultar_db(sql_limpio + ";")

        except Exception:
            traceback.print_exc()

        # FASE 2 — Respuesta humana
        try:
            res_final = client.models.generate_content(
                model    = "gemini-2.5-flash",
                contents = f"""
Eres Tech Assistant de TechStore.

Pregunta del usuario: {pregunta}

Datos encontrados: {datos if datos else 'No se requirieron datos'}

Reglas:
1. Responde de forma natural y amable.
2. Usa los datos si son relevantes.
3. Nunca menciones SQL, tablas ni bases de datos.
4. Responde en español.
"""
            )
            return jsonify({"respuesta": res_final.text.strip()})

        except Exception:
            traceback.print_exc()
            return jsonify({"respuesta": "Ocurrió un problema al generar la respuesta."})

    except Exception:
        traceback.print_exc()
        return jsonify({"respuesta": "Error interno del servidor."}), 500


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)