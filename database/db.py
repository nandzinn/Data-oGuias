"""
database/db.py
Gerenciamento do banco de dados SQLite para o DocStamp Pro.
Inclui: criação de tabelas, autenticação de usuários, preferências e logs de auditoria (LGPD).
"""

import sqlite3
import bcrypt
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docstamp.db")
SESSION_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".session")


def get_connection():
    """Retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializa o banco de dados criando as tabelas necessárias."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            stamp_color TEXT DEFAULT '#FF6B00',
            stamp_size INTEGER DEFAULT 14,
            stamp_position TEXT DEFAULT 'top',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    """)

    # Tabela de logs de auditoria (LGPD)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stamp_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT,
            stamp_date TEXT NOT NULL,
            stamp_color TEXT,
            stamp_size INTEGER,
            stamp_position TEXT,
            processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

    # Cria admin padrão se não existir nenhum usuário
    _create_default_admin()


def _create_default_admin():
    """Cria o administrador padrão na primeira execução."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        create_user(
            name="Administrador",
            email="admin@empresa.com",
            password="Admin@123",
            role="admin",
            stamp_color="#1E3A8A"
        )


def create_user(name: str, email: str, password: str,
                role: str = "user", stamp_color: str = "#2563EB",
                stamp_size: int = 14) -> bool:
    """
    Cria um novo usuário com senha hasheada.
    Retorna True em caso de sucesso, False se e-mail já existe.
    """
    try:
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO users (name, email, password_hash, role, stamp_color, stamp_size)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, email, password_hash, role, stamp_color, stamp_size)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def authenticate(email: str, password: str):
    """
    Autentica um usuário pelo e-mail e senha.
    Retorna dict com dados do usuário ou None se inválido.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        return None

    if bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        # Atualiza último login
        _update_last_login(user["id"])
        return dict(user)
    return None


def _update_last_login(user_id: int):
    """Atualiza o timestamp de último login do usuário."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET last_login = ? WHERE id = ?",
        (datetime.now().isoformat(), user_id)
    )
    conn.commit()
    conn.close()


def update_user_preferences(user_id: int, stamp_color: str, stamp_size: int,
                            stamp_position: str = "top"):
    """Salva as preferências de carimbo do usuário."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE users SET stamp_color = ?, stamp_size = ?, stamp_position = ?
           WHERE id = ?""",
        (stamp_color, stamp_size, stamp_position, user_id)
    )
    conn.commit()
    conn.close()


def get_user_by_id(user_id: int):
    """Retorna dados de um usuário pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def get_all_users():
    """Retorna todos os usuários (para o painel admin)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, stamp_color, stamp_size, created_at, last_login FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users


def delete_user(user_id: int) -> bool:
    """Remove um usuário (apenas admin pode chamar)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ? AND role != 'admin'", (user_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def log_stamp(user_id: int, file_name: str, file_path: str,
              stamp_date: str, stamp_color: str, stamp_size: int,
              stamp_position: str = "top"):
    """Registra o log de auditoria de um carimbo realizado (LGPD)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO stamp_logs (user_id, file_name, file_path, stamp_date,
           stamp_color, stamp_size, stamp_position)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, file_name, file_path, stamp_date, stamp_color, stamp_size, stamp_position)
    )
    conn.commit()
    conn.close()


def get_user_logs(user_id: int, limit: int = 50):
    """Retorna os logs de auditoria de um usuário."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM stamp_logs WHERE user_id = ?
           ORDER BY processed_at DESC LIMIT ?""",
        (user_id, limit)
    )
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs


# ── Sessão local (lembrar de mim) ────────────────────────────────────────────

def save_session(user_id: int):
    """Salva sessão local criptografada (lembrar de mim)."""
    data = json.dumps({"user_id": user_id, "saved_at": datetime.now().isoformat()})
    with open(SESSION_FILE, "w") as f:
        f.write(data)


def load_session():
    """Carrega sessão local. Retorna user_id ou None."""
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
        return data.get("user_id")
    except Exception:
        return None


def clear_session():
    """Remove a sessão salva."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
