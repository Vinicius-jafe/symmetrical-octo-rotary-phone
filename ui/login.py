import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from core import auth
from ui import secretaria, professor, aluno

def start_app():
    root = ttk.Window("Sistema de Notas — Login", themename="flatly", size=(520,360))
    root.title("Sistema de Notas — Pernambuco (Estilo C)")
    # centraliza (funciona em muitos sistemas)
    try:
        root.eval('tk::PlaceWindow . center')
    except: pass

    frm = ttk.Frame(root, padding=18)
    frm.pack(expand=True, fill='both')

    # header minimalista
    header = ttk.Frame(frm)
    header.pack(pady=(0,10))
    ttk.Label(header, text="Sistema de Notas", font=("Inter", 18, "bold")).pack()
    ttk.Label(header, text="Acesso seguro — interface minimalista", font=("Inter", 10)).pack()

    # card centralizado
    card = ttk.Frame(frm, padding=12, relief="raised", bootstyle="light")
    card.pack(pady=8)

    ttk.Label(card, text="Email").grid(row=0,column=0,sticky="w")
    entrada_email = ttk.Entry(card, width=36)
    entrada_email.grid(row=0,column=1,padx=8,pady=6)

    ttk.Label(card, text="Senha").grid(row=1,column=0,sticky="w")
    entrada_senha = ttk.Entry(card, width=36, show="*")
    entrada_senha.grid(row=1,column=1,padx=8,pady=6)

    def do_login():
        email = entrada_email.get().strip(); senha = entrada_senha.get().strip()
        if not email or not senha:
            messagebox.showwarning("Atenção","Preencha email e senha.")
            return
        user = auth.autenticar(email, senha)
        if not user:
            messagebox.showerror("Erro","Usuário ou senha inválidos.")
            return
        root.withdraw()
        if user["perfil"] == "secretaria":
            secretaria.abrir(root, user)
        elif user["perfil"] == "professor":
            professor.abrir(root, user)
        else:
            aluno.abrir(root, user)

    btn = ttk.Button(card, text="Entrar", bootstyle="primary", width=28, command=do_login)
    btn.grid(row=2, column=0, columnspan=2, pady=12)

    # prefill para testes
    entrada_email.insert(0, "secretaria@escola.com")
    entrada_senha.insert(0, "secretaria123")
    root.mainloop()
