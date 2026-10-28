
from flask import Flask, jsonify, request
import os
import psycopg2

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "festdb"),
        user=os.getenv("DB_USER", "festuser"),
        password=os.getenv("DB_PASSWORD"),
    )

def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS registrations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(255) NOT NULL
                )
            """)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "registration_number": os.getenv("REGNO", "not-provided")
    })

@app.route("/api/registrations", methods=["POST"])
def create_registration():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO registrations (name, email) VALUES (%s, %s) RETURNING id",
                (name, email)
            )
            registration_id = cur.fetchone()[0]

    return jsonify({
        "message": "Registration saved",
        "id": registration_id,
        "name": name,
        "email": email
    }), 201

@app.route("/api/registrations", methods=["GET"])
def get_registrations():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email FROM registrations ORDER BY id")
            rows = cur.fetchall()

    return jsonify([
        {"id": row[0], "name": row[1], "email": row[2]}
        for row in rows
    ])

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
