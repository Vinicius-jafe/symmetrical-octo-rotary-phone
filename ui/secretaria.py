import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog
from core import banco, auth

def abrir(parent, user):
    janela = ttk.Toplevel(parent)
    janela.title(f"Secretaria — {user['nome']}")
    janela.geometry("1000x600")

    # layout: sidebar fixa + content
    sidebar = ttk.Frame(janela, width=220, padding=8)
    sidebar.pack(side='left', fill='y')

    content = ttk.Frame(janela, padding=12)
    content.pack(side='right', expand=True, fill='both')

    ttk.Label(sidebar, text="Menu", font=("Inter", 12, "bold")).pack(anchor='nw', pady=(6, 10))
    ttk.Button(sidebar, text="Professores", bootstyle="light", command=lambda: show_prof()).pack(fill='x', pady=4)
    ttk.Button(sidebar, text="Alunos", bootstyle="light", command=lambda: show_alunos()).pack(fill='x', pady=4)

    # botão sair
    def sair():
        janela.destroy()
        parent.deiconify()

    ttk.Button(sidebar, text="Sair", bootstyle="danger", command=sair).pack(
        side='bottom', fill='x', padx=8, pady=10
    )

    # tabela professores
    tree_prof = ttk.Treeview(content, columns=("id", "nome", "email"), show="headings", height=10)
    tree_prof.heading("id", text="ID")
    tree_prof.heading("nome", text="Nome")
    tree_prof.heading("email", text="Email")
    tree_prof.pack(fill='both', expand=True, pady=6)

    # tabela alunos
    tree_aluno = ttk.Treeview(content, columns=("id", "nome", "matricula"), show="headings", height=10)
    tree_aluno.heading("id", text="ID")
    tree_aluno.heading("nome", text="Nome")
    tree_aluno.heading("matricula", text="Matrícula")

    def carregar_professores():
        for i in tree_prof.get_children(): tree_prof.delete(i)
        conn = banco.conectar(); c = conn.cursor()
        c.execute("SELECT id,nome,email FROM usuarios WHERE perfil='professor'")
        for r in c.fetchall():
            tree_prof.insert("", "end", values=(r["id"], r["nome"], r["email"]))
        conn.close()

    def carregar_alunos():
        for i in tree_aluno.get_children(): tree_aluno.delete(i)
        conn = banco.conectar(); c = conn.cursor()
        c.execute("SELECT id,nome,matricula FROM alunos")
        for r in c.fetchall():
            tree_aluno.insert("", "end", values=(r["id"], r["nome"], r["matricula"]))
        conn.close()

    def show_prof():
        tree_aluno.pack_forget()
        tree_prof.pack(fill='both', expand=True)

    def show_alunos():
        tree_prof.pack_forget()
        tree_aluno.pack(fill='both', expand=True)

    # -------- Adicionar Professor --------
    def add_prof():
        nome = simpledialog.askstring("Nome","Nome:", parent=janela)
        email = simpledialog.askstring("Email","Email:", parent=janela)
        senha = simpledialog.askstring("Senha","Senha:", parent=janela)
        if not nome or not email or not senha: return

        auth.cadastrar_usuario(nome, email, senha, "professor")
        carregar_professores()
        messagebox.showinfo("OK","Professor cadastrado")

    # -------- Excluir Professor --------
    def del_prof():
        sel = tree_prof.selection()
        if not sel: return
        idp = tree_prof.item(sel[0])["values"][0]
        if messagebox.askyesno("Excluir","Deseja excluir?"):
            conn = banco.conectar(); c = conn.cursor()
            c.execute("DELETE FROM usuarios WHERE id=?", (idp,))
            conn.commit(); conn.close()
            carregar_professores()

    # -------- Adicionar Aluno --------
    def add_aluno():
        nome = simpledialog.askstring("Nome","Nome do aluno:", parent=janela)
        matricula = simpledialog.askstring("Matrícula","Matrícula:", parent=janela)
        email = simpledialog.askstring("Email","Email do aluno:", parent=janela)
        senha = simpledialog.askstring("Senha","Senha:", parent=janela)

        if not nome or not email or not senha:
            return

        try:
            auth.cadastrar_usuario(nome, email, senha, "aluno")
        except:
            messagebox.showerror("Erro","Email já está em uso.")
            return

        conn = banco.conectar(); c = conn.cursor()
        c.execute("INSERT INTO alunos (nome, matricula) VALUES (?, ?)", (nome, matricula))
        conn.commit(); conn.close()

        carregar_alunos()
        messagebox.showinfo("OK","Aluno cadastrado!")

    # -------- Excluir Aluno --------
    def del_aluno():
        sel = tree_aluno.selection()
        if not sel: return
        ida = tree_aluno.item(sel[0])["values"][0]
        if messagebox.askyesno("Excluir","Deseja excluir?"):
            conn = banco.conectar(); c = conn.cursor()
            c.execute("DELETE FROM alunos WHERE id=?", (ida,))
            conn.commit(); conn.close()
            carregar_alunos()

    # -------- Ver Dados do Aluno --------
    def ver_dados_aluno():
        sel = tree_aluno.selection()
        if not sel:
            messagebox.showwarning("Aviso","Selecione um aluno.")
            return

        aluno_id = tree_aluno.item(sel[0])["values"][0]

        conn = banco.conectar()
        c = conn.cursor()

        c.execute("SELECT nome, matricula FROM alunos WHERE id=?", (aluno_id,))
        aluno = c.fetchone()

        c.execute("SELECT email FROM usuarios WHERE nome=?", (aluno["nome"],))
        u = c.fetchone()

        c.execute("""
            SELECT n.nota, p.nome 
            FROM notas n
            LEFT JOIN usuarios p ON n.professor_id = p.id
            WHERE n.aluno_id=?
        """, (aluno_id,))
        notas = c.fetchall()

        conn.close()

        texto = f"Nome: {aluno['nome']}\nMatrícula: {aluno['matricula']}\nEmail: {u['email'] if u else '—'}\n\nNotas:\n"

        if notas:
            for n in notas:
                texto += f"• {n['nota']} (Professor: {n['nome']})\n"
        else:
            texto += "Nenhuma nota cadastrada."

        messagebox.showinfo("Dados do Aluno", texto)

    # TOOLBAR
    toolbar = ttk.Frame(content)
    toolbar.pack(fill='x')

    ttk.Button(toolbar, text="Adicionar Prof", bootstyle="primary", command=add_prof).pack(side='left', padx=6, pady=6)
    ttk.Button(toolbar, text="Excluir Prof", bootstyle="danger", command=del_prof).pack(side='left', padx=6)

    ttk.Button(toolbar, text="Adicionar Aluno", bootstyle="primary", command=add_aluno).pack(side='left', padx=6)
    ttk.Button(toolbar, text="Excluir Aluno", bootstyle="danger", command=del_aluno).pack(side='left', padx=6)

    ttk.Button(toolbar, text="Ver Dados Aluno", bootstyle="info", command=ver_dados_aluno).pack(side='left', padx=6)

    carregar_professores()
    carregar_alunos()
