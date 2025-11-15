import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog
from core import banco

def abrir(parent, user):
    janela = ttk.Toplevel(parent)
    janela.title(f"Professor — {user['nome']}")
    janela.geometry("920x560")

    sidebar = ttk.Frame(janela, width=220, padding=8)
    sidebar.pack(side='left', fill='y')

    content = ttk.Frame(janela, padding=12)
    content.pack(side='right', expand=True, fill='both')

    ttk.Label(sidebar, text=f"Olá, {user['nome']}", font=("Inter",11,"bold")).pack(anchor='nw', pady=(6,10))
    ttk.Button(sidebar, text="Lançar Notas", bootstyle="light").pack(fill='x', pady=4)

    # ============ BOTÃO SAIR ============
    def sair():
        janela.destroy()
        parent.deiconify()

    ttk.Button(sidebar, text="Sair", bootstyle="danger", command=sair).pack(
        side='bottom', fill='x', padx=8, pady=10
    )

    # ============ TREEVIEW ============
    tree = ttk.Treeview(
        content,
        columns=("aluno_id","aluno_nome","matricula","nota_id","nota"),
        show="headings",
        height=14
    )

    tree.heading("aluno_id", text="ID")
    tree.heading("aluno_nome", text="Aluno")
    tree.heading("matricula", text="Matrícula")
    tree.heading("nota_id", text="ID Nota")
    tree.heading("nota", text="Nota")
    tree.pack(fill='both', expand=True, pady=8)

    # ============ CARREGAR ============
    def carregar():
        for i in tree.get_children():
            tree.delete(i)

        conn = banco.conectar()
        c = conn.cursor()

        c.execute("""
            SELECT a.id, a.nome, a.matricula, n.id, n.nota
            FROM alunos a
            LEFT JOIN notas n ON n.aluno_id=a.id AND n.professor_id=?
        """, (user["id"],))

        for r in c.fetchall():
            tree.insert("", "end", values=(r[0],r[1],r[2],r[3],r[4]))

        conn.close()

    # ============ LANÇAR NOTA ============
    def lancar():
        sel = tree.selection()
        if not sel: return

        row = tree.item(sel[0])["values"]
        aluno_id = row[0]
        atual = row[4]

        entrada = simpledialog.askstring(
            "Nota",
            f"Nota de 0 a 10 para {row[1]}:",
            initialvalue=str(atual) if atual not in (None,"") else ""
        )

        if entrada is None:
            return

        try:
            nota = float(entrada)
        except:
            messagebox.showerror("Erro", "Nota inválida")
            return

        conn = banco.conectar()
        c = conn.cursor()

        c.execute(
            "SELECT id FROM notas WHERE aluno_id=? AND professor_id=?",
            (aluno_id, user["id"])
        )

        r = c.fetchone()

        if r:
            c.execute("UPDATE notas SET nota=? WHERE id=?", (nota, r["id"]))
        else:
            c.execute(
                "INSERT INTO notas (aluno_id, professor_id, nota) VALUES (?,?,?)",
                (aluno_id, user["id"], nota)
            )

        conn.commit()
        conn.close()
        carregar()

    # ============ VER DADOS DO ALUNO ============
    def ver_dados():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um aluno.")
            return

        row = tree.item(sel[0])["values"]
        aluno_id = row[0]

        conn = banco.conectar()
        c = conn.cursor()

        # aluno
        c.execute("SELECT nome, matricula FROM alunos WHERE id=?", (aluno_id,))
        aluno = c.fetchone()

        # email
        c.execute("SELECT email FROM usuarios WHERE nome=?", (aluno["nome"],))
        u = c.fetchone()

        # notas
        c.execute("""
            SELECT n.nota, p.nome
            FROM notas n
            LEFT JOIN usuarios p ON p.id = n.professor_id
            WHERE n.aluno_id=?
        """, (aluno_id,))
        notas = c.fetchall()

        conn.close()

        texto = (
            f"Nome: {aluno['nome']}\n"
            f"Matrícula: {aluno['matricula']}\n"
            f"Email: {u['email'] if u else '—'}\n\nNotas:\n"
        )

        if notas:
            for n in notas:
                texto += f"• {n['nota']} (Professor: {n['nome']})\n"
        else:
            texto += "Nenhuma nota cadastrada."

        messagebox.showinfo("Dados do Aluno", texto)

    # ============ TOOLBAR ============
    toolbar = ttk.Frame(content)
    toolbar.pack(fill='x')

    ttk.Button(toolbar, text="Lançar / Editar Nota", bootstyle="primary", command=lancar).pack(side='left', padx=6)
    ttk.Button(toolbar, text="Atualizar", bootstyle="secondary", command=carregar).pack(side='left', padx=6)
    ttk.Button(toolbar, text="Ver Dados do Aluno", bootstyle="info", command=ver_dados).pack(side='left', padx=6)

    carregar()
