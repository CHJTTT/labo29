from flask import Flask, render_template, request, jsonify
from google import genai
import psycopg2
import psycopg2.extras
import traceback
import os

app = Flask(__name__)

# =====================================================
# CONFIGURACIÓN GEMINI
# =====================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# =====================================================
# CONFIGURACIÓN POSTGRESQL (NEON)
# =====================================================

DATABASE_URL = os.environ.get("DATABASE_URL")


# =====================================================
# FUNCIÓN CONSULTAR DB
# =====================================================

def consultar_db(sql):

    conn = None
    cur = None

    try:
        conn = psycopg2.connect(DATABASE_URL)

        cur = conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )

        cur.execute(sql)

        resultado = cur.fetchall()

        return resultado

    except Exception as e:

        print("\n[ERROR DB]")
        print(sql)
        print(e)

        return None

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


# =====================================================
# PÁGINA PRINCIPAL
# =====================================================

@app.route("/")
def index():
    return render_template("index.html")


# =====================================================
# API PRODUCTOS
# =====================================================

@app.route("/api/productos", methods=["GET"])
def get_productos():

    productos = consultar_db("""
        SELECT
            nom_pro,
            pre_pro,
            stk_pro,
            ventas,
            categoria,
            img_url
        FROM productos
        ORDER BY ventas DESC
    """)

    return jsonify(productos if productos else [])


# =====================================================
# CHAT
# =====================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "respuesta": "No se recibió información."
            })

        pregunta = data.get("pregunta", "").strip()

        if not pregunta:
            return jsonify({
                "respuesta": "Por favor escribe una pregunta."
            })

        print("\n==============================")
        print("NUEVA PREGUNTA")
        print("==============================")
        print(pregunta)

        esquema = (
            "Tabla productos con columnas: "
            "id_pro, nom_pro, pre_pro, stk_pro, ventas, categoria, img_url."
        )

        datos = None

        # ==========================================
        # FASE 1 - CLASIFICACIÓN
        # ==========================================

        try:

            clasificador_prompt = f"""
Analiza el siguiente mensaje:

{pregunta}

Si es un saludo o conversación normal responde únicamente:

CHAT

Si necesita información de la tabla productos:

{esquema}

Responde únicamente una consulta SQL SELECT válida.

No agregues explicaciones.
No uses markdown.
No uses ```sql.
"""

            res_sql = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=clasificador_prompt
            )

            respuesta_sql = res_sql.text.strip()

            print("\n[CLASIFICACIÓN]")
            print(respuesta_sql)

            sql_limpio = (
                respuesta_sql
                .replace("```sql", "")
                .replace("```", "")
                .replace("`", "")
                .strip()
            )

            sql_limpio = sql_limpio.split(";")[0]

            if (
                "SELECT" in sql_limpio.upper()
                and "FROM" in sql_limpio.upper()
            ):

                print("\n[SQL DETECTADO]")
                print(sql_limpio)

                datos = consultar_db(sql_limpio + ";")

                if datos:
                    print(f"[OK] {len(datos)} filas")
                else:
                    print("[OK] Sin resultados")

            else:

                print("[MODO CHAT]")

        except Exception as e:

            print("\n[ERROR FASE 1]")
            traceback.print_exc()

        # ==========================================
        # FASE 2 - RESPUESTA HUMANA
        # ==========================================

        try:

            prompt_humano = f"""
Eres Tech Assistant de TechStore.

Pregunta del usuario:
{pregunta}

Datos encontrados:
{datos if datos else 'No se requirieron datos'}

Reglas:

1. Responde de forma natural.
2. Sé amable.
3. Usa los datos si son relevantes.
4. Nunca menciones SQL.
5. Nunca menciones tablas.
6. Nunca menciones bases de datos.
7. Responde en español.
"""

            res_final = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_humano
            )

            respuesta = res_final.text.strip()

            print("\n[RESPUESTA]")
            print(respuesta)

            return jsonify({
                "respuesta": respuesta
            })

        except Exception:

            traceback.print_exc()

            return jsonify({
                "respuesta": "Ocurrió un problema al generar la respuesta."
            })

    except Exception:

        traceback.print_exc()

        return jsonify({
            "respuesta": "Error interno del servidor."
        }), 500


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )