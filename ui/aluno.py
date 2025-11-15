import ttkbootstrap as ttk
from core import banco

def abrir(parent, user):
    janela = ttk.Toplevel(parent)
    janela.title(f"Aluno — {user['nome']}")
    janela.geometry("640x360")
    frm = ttk.Frame(janela, padding=12); frm.pack(fill='both', expand=True)
    ttk.Label(frm, text=f"Aluno: {user['nome']}", font=("Inter",14,"bold")).pack(anchor='w')
    lbl = ttk.Label(frm, text="", font=("Inter",12))
    lbl.pack(anchor='w', pady=10)

    def carregar():
        conn = banco.conectar(); c = conn.cursor()
        c.execute("SELECT id FROM alunos WHERE nome=?", (user["nome"],))
        row = c.fetchone()
        if not row:
            lbl.config(text="Aluno não encontrado."); return
        aluno_id = row["id"]
        c.execute("""
            SELECT n.nota, u.nome
            FROM notas n
            JOIN usuarios u ON u.id = n.professor_id
            WHERE n.aluno_id=?
        """, (aluno_id,))
        notas = c.fetchall(); conn.close()
        if not notas:
            lbl.config(text="Nenhuma nota lançada."); return
        texto = "Suas notas:\\n"
        for n in notas:
            texto += f"Professor {n[1]} — Nota: {n[0]}\\n"
        lbl.config(text=texto)

    ttk.Button(frm, text="Carregar Nota", bootstyle="primary", command=carregar).pack(pady=8)
