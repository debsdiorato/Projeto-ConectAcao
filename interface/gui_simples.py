import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from dotenv import load_dotenv

from db.database import (
    criar_usuario, buscar_usuario_por_email, criar_voluntario, 
    atualizar_voluntario, listar_voluntarios, criar_demanda, 
    listar_demandas, buscar_demanda_por_id
)
from validacoes.security import hash_password, verify_password
from logica.matching import get_matches_for_demand

load_dotenv()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voluntários do Bem – GUI Simples")
        
        # Configuração inicial de geometria centralizada
        self.center_window(800, 600)
        
        self.usuario_atual = None

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)

        self.tab_login = ttk.Frame(self.nb)
        self.tab_vol = ttk.Frame(self.nb)
        self.tab_dem = ttk.Frame(self.nb)
        self.tab_match = ttk.Frame(self.nb)

        self.nb.add(self.tab_login, text="Login / Registro")
        self.nb.add(self.tab_vol, text="Voluntários")
        self.nb.add(self.tab_dem, text="Demandas")
        self.nb.add(self.tab_match, text="Matching")

        self.setup_login_ui()
        self.setup_vol_ui()
        self.setup_dem_ui()
        self.setup_match_ui()

    def center_window(self, width, height):
        """Centraliza a janela na tela do usuário"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f'{width}x{height}+{x}+{y}')

    # --- ABA LOGIN (Refatorada para Layout Centralizado) ---
    def setup_login_ui(self):
        f = self.tab_login
        
        # Container Central (Efeito de Cartão)
        card = ttk.Frame(f, padding=20, relief="groove")
        card.place(relx=0.5, rely=0.5, anchor="center") # Centraliza o card na aba

        # Título
        ttk.Label(card, text="Acesso ao Sistema", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Login Section
        ttk.Label(card, text="Email:").grid(row=1, column=0, sticky="e", padx=5)
        self.email_entry = ttk.Entry(card, width=35)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(card, text="Senha:").grid(row=2, column=0, sticky="e", padx=5)
        self.senha_entry = ttk.Entry(card, show="*", width=35)
        self.senha_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(card, text="Entrar", command=self.login).grid(row=3, column=1, sticky="e", padx=5, pady=10)

        # Separator
        ttk.Separator(card, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=15)

        # Registration Section
        ttk.Label(card, text="Novo Voluntário? Registre-se:", font=("Helvetica", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        ttk.Label(card, text="Nome:").grid(row=6, column=0, sticky="e", padx=5)
        self.reg_nome = ttk.Entry(card, width=35)
        self.reg_nome.grid(row=6, column=1, padx=5, pady=2)

        ttk.Label(card, text="Telefone:").grid(row=7, column=0, sticky="e", padx=5)
        self.reg_telefone = ttk.Entry(card, width=35)
        self.reg_telefone.grid(row=7, column=1, padx=5, pady=2)

        ttk.Label(card, text="Email:").grid(row=8, column=0, sticky="e", padx=5)
        self.reg_email = ttk.Entry(card, width=35)
        self.reg_email.grid(row=8, column=1, padx=5, pady=2)

        ttk.Label(card, text="Senha:").grid(row=9, column=0, sticky="e", padx=5)
        self.reg_senha = ttk.Entry(card, show="*", width=35)
        self.reg_senha.grid(row=9, column=1, padx=5, pady=2)

        ttk.Label(card, text="Habilidades:").grid(row=10, column=0, sticky="e", padx=5)
        self.reg_hab = ttk.Entry(card, width=35)
        self.reg_hab.grid(row=10, column=1, padx=5, pady=2)
        ttk.Label(card, text="(separe por vírgula)", font=("Arial", 8)).grid(row=11, column=1, sticky="w", padx=5)

        ttk.Button(card, text="Criar Conta", command=self.registrar).grid(row=12, column=1, sticky="e", padx=5, pady=15)

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
        messagebox.showinfo("Sucesso", f"Bem-vindo(a), {user['nome']}!\nPerfil: {user['papel']}")
        self.atualizar_listas()
        # Opcional: Mudar para a aba de voluntários ou demandas após login
        self.nb.select(self.tab_dem)

    def registrar(self):
        nome = self.reg_nome.get().strip()
        telefone = self.reg_telefone.get().strip()
        email = self.reg_email.get().strip()
        senha = self.reg_senha.get().strip()
        hab = self.reg_hab.get().strip()
        if not nome or not email or not senha:
            messagebox.showerror("Erro", "Nome, email e senha são obrigatórios")
            return
        if buscar_usuario_por_email(email):
            messagebox.showerror("Erro", "Email já cadastrado")
            return
        uid = criar_usuario(nome, telefone, email, hash_password(senha), papel="voluntario")
        criar_voluntario(uid, hab, "", "")
        messagebox.showinfo("Sucesso", "Cadastro realizado! Faça login para continuar.")

    # --- ABA VOLUNTÁRIOS ---
    def setup_vol_ui(self):
        if hasattr(self, 'vol_tree'): return
        f = self.tab_vol
        
        container = ttk.Frame(f, padding=10)
        container.pack(fill='both', expand=True)

        ttk.Label(container, text="Voluntários Cadastrados", font=("Helvetica", 12, "bold")).pack(anchor='w', pady=(0, 10))
        
        columns = ('id', 'nome', 'habilidades')
        self.vol_tree = ttk.Treeview(container, columns=columns, show='headings', height=15)
        self.vol_tree.heading('id', text='ID')
        self.vol_tree.column('id', width=50, anchor='center')
        self.vol_tree.heading('nome', text='Nome')
        self.vol_tree.column('nome', width=200, anchor='w')
        self.vol_tree.heading('habilidades', text='Habilidades')
        self.vol_tree.column('habilidades', width=450, anchor='w')
        
        # Adicionar Scrollbar
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.vol_tree.yview)
        self.vol_tree.configure(yscroll=scrollbar.set)
        
        self.vol_tree.pack(side="left", fill='both', expand=True)
        scrollbar.pack(side="right", fill="y")
        
        btn_frame = ttk.Frame(f, padding=10)
        btn_frame.pack(fill='x')
        ttk.Button(btn_frame, text="Atualizar Lista", command=self.atualizar_vol).pack(anchor='e')

    def atualizar_vol(self):
        for i in self.vol_tree.get_children():
            self.vol_tree.delete(i)
        for v in listar_voluntarios():
            self.vol_tree.insert('', 'end', values=(v['id'], v['nome'], v.get('habilidades','')))

    # --- ABA DEMANDAS ---
    def setup_dem_ui(self):
        if hasattr(self, 'dem_tree'): return
        f = self.tab_dem
        
        container = ttk.Frame(f, padding=10)
        container.pack(fill='both', expand=True)

        ttk.Label(container, text="Quadro de Demandas", font=("Helvetica", 12, "bold")).pack(anchor='w', pady=(0, 10))
        
        columns = ('id', 'titulo', 'skills')
        self.dem_tree = ttk.Treeview(container, columns=columns, show='headings', height=15)
        self.dem_tree.heading('id', text='ID')
        self.dem_tree.column('id', width=50, anchor='center')
        self.dem_tree.heading('titulo', text='Título da Demanda')
        self.dem_tree.column('titulo', width=250, anchor='w')
        self.dem_tree.heading('skills', text='Habilidades Necessárias')
        self.dem_tree.column('skills', width=400, anchor='w')
        
        self.dem_tree.pack(fill='both', expand=True)
        
        btnf = ttk.Frame(f, padding=10)
        btnf.pack(fill='x')
        ttk.Button(btnf, text="Criar Nova Demanda", command=self.criar_demanda_dialog).pack(side='right', padx=5)
        ttk.Button(btnf, text="Atualizar", command=self.atualizar_dem).pack(side='right', padx=5)

    def atualizar_dem(self):
        for i in self.dem_tree.get_children():
            self.dem_tree.delete(i)
        for d in listar_demandas():
            self.dem_tree.insert('', 'end', values=(d['id'], d['titulo'], d.get('habilidades_requeridas','')))

    def criar_demanda_dialog(self):
        if not self.usuario_atual or self.usuario_atual.get('papel') != 'admin':
            messagebox.showerror('Acesso Negado', 'Apenas administradores podem criar demandas.')
            return
        titulo = simpledialog.askstring('Nova Demanda', 'Título da demanda:')
        habilidades = simpledialog.askstring('Skills', 'Habilidades requeridas (separadas por vírgula):')
        if not titulo or not habilidades: 
            return
        criar_demanda(titulo, habilidades)
        messagebox.showinfo('Sucesso', 'Demanda criada com sucesso!')
        self.atualizar_dem()

    # --- ABA MATCHING ---
    def setup_match_ui(self):
        if hasattr(self, 'match_combo'): return
        f = self.tab_match
        
        container = ttk.Frame(f, padding=20)
        container.pack(fill='both', expand=True)

        ttk.Label(container, text='Sistema de Matching Inteligente', font=("Helvetica", 12, "bold")).pack(anchor='w', pady=(0, 20))
        
        frame_controls = ttk.LabelFrame(container, text="Controles", padding=10)
        frame_controls.pack(fill='x', pady=(0, 10))
        
        ttk.Label(frame_controls, text="Selecione a Demanda:").pack(anchor='w')
        self.match_combo = ttk.Combobox(frame_controls, state='readonly', width=80)
        self.match_combo.pack(fill='x', pady=5)
        
        btn_box = ttk.Frame(frame_controls)
        btn_box.pack(fill='x', pady=5)
        ttk.Button(btn_box, text='Atualizar Lista de Demandas', command=self.atualizar_combo).pack(side='left')
        ttk.Button(btn_box, text='🔍 Gerar Matches', command=self.gerar_matches).pack(side='right')

        ttk.Label(container, text="Resultados:", font=("Helvetica", 10, "bold")).pack(anchor='w', pady=(10, 5))
        self.match_text = tk.Text(container, height=15)
        self.match_text.pack(fill='both', expand=True)

    def atualizar_combo(self):
        arr = [f"{d['id']} - {d['titulo']}" for d in listar_demandas()]
        self.match_combo['values'] = arr

    def gerar_matches(self):
        sel = self.match_combo.get()
        if not sel: 
            messagebox.showwarning("Atenção", "Selecione uma demanda primeiro.")
            return
        demand_id = int(sel.split(' - ')[0])
        demanda = buscar_demanda_por_id(demand_id)
        matches = get_matches_for_demand(demanda, top_n=10)
        self.match_text.delete('1.0', tk.END)
        if not matches:
            self.match_text.insert(tk.END, 'Nenhum match encontrado para esta demanda.')
            return
        for m in matches:
            v = m['voluntario']
            self.match_text.insert(tk.END, f"✅ Score: {m['score']:.2f} — {v['nome']} \n   Skills: {v.get('habilidades','')}\n\n")

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
