import bcrypt
from core import banco

def autenticar(email, senha_digitada):
    conn = banco.conectar(); c = conn.cursor()
    c.execute("SELECT id, nome, senha, perfil, email FROM usuarios WHERE email = ?", (email,))
    user = c.fetchone(); conn.close()
    if not user:
        return None
    try:
        ok = bcrypt.checkpw(senha_digitada.encode(), user["senha"].encode())
    except:
        return None
    if ok:
        return {"id": user["id"], "nome": user["nome"], "perfil": user["perfil"], "email": user["email"]}
    return None

def cadastrar_usuario(nome, email, senha, perfil):
    conn = banco.conectar(); c = conn.cursor()
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    c.execute("INSERT INTO usuarios (nome,email,senha,perfil) VALUES (?,?,?,?)",
              (nome, email, senha_hash, perfil))
    conn.commit(); conn.close()
