import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from dotenv import load_dotenv

from database import (
    criar_usuario, buscar_usuario_por_email, criar_voluntario, 
    atualizar_voluntario, listar_voluntarios, criar_demanda, 
    listar_demandas, buscar_demanda_por_id
)
from security import hash_password, verify_password
from matching import get_matches_for_demand

load_dotenv()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voluntários do Bem – GUI Simples")
        self.geometry("800x600")
        self.usuario_atual = None

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self.tab_login = ttk.Frame(nb)
        self.tab_vol = ttk.Frame(nb)
        self.tab_dem = ttk.Frame(nb)
        self.tab_match = ttk.Frame(nb)

        nb.add(self.tab_login, text="Login / Registro")
        nb.add(self.tab_vol, text="Voluntários")
        nb.add(self.tab_dem, text="Demandas")
        nb.add(self.tab_match, text="Matching")

        self.build_login_tab()
        self.build_vol_tab()
        self.build_dem_tab()
        self.build_match_tab()

    def build_login_tab(self):
        f = self.tab_login
        for w in f.winfo_children():
            w.destroy()

        ttk.Label(f, text="Email:").grid(row=0, column=0, padx=5, pady=5)
        self.email_entry = ttk.Entry(f, width=40)
        self.email_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(f, text="Senha:").grid(row=1, column=0, padx=5, pady=5)
        self.senha_entry = ttk.Entry(f, show="*", width=40)
        self.senha_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(f, text="Login", command=self.login).grid(row=2, column=1, sticky="e", padx=5, pady=5)
        ttk.Separator(f, orient="horizontal").grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)

        ttk.Label(f, text="Registro (Voluntário):").grid(row=4, column=0, columnspan=2, sticky="w", padx=5)
        
        ttk.Label(f, text="Nome:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        self.reg_nome = ttk.Entry(f, width=40)
        self.reg_nome.grid(row=5, column=1, padx=5)

        ttk.Label(f, text="Telefone:").grid(row=6, column=0, sticky="w", padx=5, pady=2)
        self.reg_telefone = ttk.Entry(f, width=40)
        self.reg_telefone.grid(row=6, column=1, padx=5)

        ttk.Label(f, text="Email:").grid(row=7, column=0, sticky="w", padx=5, pady=2)
        self.reg_email = ttk.Entry(f, width=40)
        self.reg_email.grid(row=7, column=1, padx=5)

        ttk.Label(f, text="Senha:").grid(row=8, column=0, sticky="w", padx=5, pady=2)
        self.reg_senha = ttk.Entry(f, show="*", width=40)
        self.reg_senha.grid(row=8, column=1, padx=5)

        ttk.Label(f, text="Habilidades (vírgula sep.):").grid(row=9, column=0, sticky="w", padx=5, pady=2)
        self.reg_hab = ttk.Entry(f, width=40)
        self.reg_hab.grid(row=9, column=1, padx=5)

        ttk.Button(f, text="Registrar", command=self.registrar).grid(row=11, column=1, sticky="e", padx=5, pady=8)

    def login(self):
        email = self.email_entry.get().strip()
        senha = self.senha_entry.get().strip()
        if not email or not senha:
            messagebox.showerror("Erro", "Preencha email e senha")
            return
        user = buscar_usuario_por_email(email)
        if not user or not verify_password(user['senha_hash'], senha):
            messagebox.showerror("Erro", "Credenciais inválidas")
            return
        self.usuario_atual = user
        messagebox.showinfo("OK", f"Logado como {user['nome']} ({user['papel']})")
        self.atualizar_listas()

    def registrar(self):
        nome = self.reg_nome.get().strip()
        telefone = self.reg_telefone.get().strip()
        email = self.reg_email.get().strip()
        senha = self.reg_senha.get().strip()
        hab = self.reg_hab.get().strip()
        if not nome or not email or not senha:
            messagebox.showerror("Erro", "Nome, email e senha obrigatórios")
            return
        if buscar_usuario_por_email(email):
            messagebox.showerror("Erro", "Email já cadastrado")
            return
        uid = criar_usuario(nome, telefone, email, hash_password(senha), papel="voluntario")
        criar_voluntario(uid, hab, "", "")
        messagebox.showinfo("OK", "Registrado. Faça login.")

    # --- MUDANÇA AQUI: Treeview para Voluntários ---
    def build_vol_tab(self):
        f = self.tab_vol
        for w in f.winfo_children(): 
            w.destroy()
        
        ttk.Label(f, text="Voluntários Cadastrados:").pack(anchor='w', padx=10, pady=5)
        
        # Definição das colunas
        columns = ('id', 'nome', 'habilidades')
        self.vol_tree = ttk.Treeview(f, columns=columns, show='headings', height=15)
        
        # Configuração dos cabeçalhos e largura
        self.vol_tree.heading('id', text='ID')
        self.vol_tree.column('id', width=50, anchor='center')
        
        self.vol_tree.heading('nome', text='Nome')
        self.vol_tree.column('nome', width=200, anchor='w')
        
        self.vol_tree.heading('habilidades', text='Habilidades')
        self.vol_tree.column('habilidades', width=450, anchor='w')
        
        self.vol_tree.pack(padx=10, pady=5, fill='both', expand=True)
        
        ttk.Button(f, text="Atualizar lista", command=self.atualizar_vol).pack(padx=10, pady=10)

    def atualizar_vol(self):
        # Limpa os dados antigos da tabela
        for i in self.vol_tree.get_children():
            self.vol_tree.delete(i)
        
        # Insere os novos dados
        for v in listar_voluntarios():
            self.vol_tree.insert('', 'end', values=(v['id'], v['nome'], v.get('habilidades','')))

    # --- MUDANÇA AQUI: Treeview para Demandas ---
    def build_dem_tab(self):
        f = self.tab_dem
        for w in f.winfo_children(): 
            w.destroy()
            
        ttk.Label(f, text="Demandas Disponíveis:").pack(anchor='w', padx=10, pady=5)
        
        columns = ('id', 'titulo', 'skills')
        self.dem_tree = ttk.Treeview(f, columns=columns, show='headings', height=15)
        
        self.dem_tree.heading('id', text='ID')
        self.dem_tree.column('id', width=50, anchor='center')
        
        self.dem_tree.heading('titulo', text='Título da Demanda')
        self.dem_tree.column('titulo', width=250, anchor='w')
        
        self.dem_tree.heading('skills', text='Habilidades Necessárias')
        self.dem_tree.column('skills', width=400, anchor='w')
        
        self.dem_tree.pack(padx=10, pady=5, fill='both', expand=True)
        
        btnf = ttk.Frame(f)
        btnf.pack(pady=10)
        
        ttk.Button(btnf, text="Atualizar", command=self.atualizar_dem).grid(row=0, column=0, padx=5)
        ttk.Button(btnf, text="Criar demanda", command=self.criar_demanda_dialog).grid(row=0, column=1, padx=5)

    def atualizar_dem(self):
        for i in self.dem_tree.get_children():
            self.dem_tree.delete(i)
        for d in listar_demandas():
            self.dem_tree.insert('', 'end', values=(d['id'], d['titulo'], d.get('habilidades_requeridas','')))

    def criar_demanda_dialog(self):
        if not self.usuario_atual or self.usuario_atual.get('papel') != 'admin':
            messagebox.showerror('Acesso', 'Apenas admin pode criar demandas.')
            return
        titulo = simpledialog.askstring('Título', 'Título da demanda:')
        habilidades = simpledialog.askstring('Skills', 'Habilidades (vírgula):')
        if not titulo or not habilidades: 
            return
        criar_demanda(titulo, habilidades)
        messagebox.showinfo('OK', 'Demanda criada')
        self.atualizar_dem()

    def build_match_tab(self):
        f = self.tab_match
        for w in f.winfo_children(): 
            w.destroy()
        ttk.Label(f, text='Matching').pack(anchor='w', padx=8, pady=6)
        self.match_combo = ttk.Combobox(f, state='readonly', width=80)
        self.match_combo.pack(padx=8)
        ttk.Button(f, text='Atualizar demandas', command=self.atualizar_combo).pack(padx=8, pady=6)
        ttk.Button(f, text='Gerar matches', command=self.gerar_matches).pack(padx=8, pady=6)
        self.match_text = tk.Text(f, height=15, width=95)
        self.match_text.pack(padx=8, pady=8)

    def atualizar_combo(self):
        arr = [f"{d['id']} - {d['titulo']}" for d in listar_demandas()]
        self.match_combo['values'] = arr

    def gerar_matches(self):
        sel = self.match_combo.get()
        if not sel: return
        demand_id = int(sel.split(' - ')[0])
        demanda = buscar_demanda_por_id(demand_id)
        matches = get_matches_for_demand(demanda, top_n=10)
        self.match_text.delete('1.0', tk.END)
        if not matches:
            self.match_text.insert(tk.END, 'Nenhum match encontrado.')
            return
        for m in matches:
            v = m['voluntario']
            self.match_text.insert(tk.END, f"Score: {m['score']} — {v['nome']} | skills: {v.get('habilidades','')}\n")

    def atualizar_listas(self):
        try: self.atualizar_vol()
        except: pass
        try: self.atualizar_dem()
        except: pass
        try: self.atualizar_combo()
        except: pass

if __name__ == '__main__':
    app = App()
    app.mainloop()
