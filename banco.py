import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "notas.db")

def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        perfil TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS alunos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        matricula TEXT UNIQUE
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aluno_id INTEGER NOT NULL,
        professor_id INTEGER NOT NULL,
        nota REAL,
        FOREIGN KEY(aluno_id) REFERENCES alunos(id),
        FOREIGN KEY(professor_id) REFERENCES usuarios(id)
    )""")

    conn.commit()
    conn.close()


def seed_defaults():
    import bcrypt
    conn = conectar()
    c = conn.cursor()

    def exists_email(email):
        c.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        return c.fetchone() is not None

    # secretaria
    if not exists_email("secretaria@escola.com"):
        senha = bcrypt.hashpw("secretaria123".encode(), bcrypt.gensalt()).decode()
        c.execute("INSERT INTO usuarios (nome,email,senha,perfil) VALUES (?,?,?,?)",
                  ("Secretaria", "secretaria@escola.com", senha, "secretaria"))

    # professor
    if not exists_email("professor@escola.com"):
        senha = bcrypt.hashpw("professor123".encode(), bcrypt.gensalt()).decode()
        c.execute("INSERT INTO usuarios (nome,email,senha,perfil) VALUES (?,?,?,?)",
                  ("Professor Exemplo", "professor@escola.com", senha, "professor"))

    # aluno + nota inicial
    c.execute("SELECT id FROM alunos WHERE matricula = 'MAT001'")
    if not c.fetchone():
        c.execute("INSERT INTO alunos (nome,matricula) VALUES (?,?)",
                  ("Aluno Exemplo", "MAT001"))
        aluno_id = c.lastrowid

        if not exists_email("aluno@escola.com"):
            senha = bcrypt.hashpw("aluno123".encode(), bcrypt.gensalt()).decode()
            c.execute("INSERT INTO usuarios (nome,email,senha,perfil) VALUES (?,?,?,?)",
                      ("Aluno Exemplo", "aluno@escola.com", senha, "aluno"))

        c.execute("SELECT id FROM usuarios WHERE email = 'professor@escola.com'")
        prof = c.fetchone()
        if prof:
            pid = prof["id"]
            c.execute("INSERT INTO notas (aluno_id, professor_id, nota) VALUES (?,?,?)",
                      (aluno_id, pid, 7.5))

    conn.commit()
    conn.close()
