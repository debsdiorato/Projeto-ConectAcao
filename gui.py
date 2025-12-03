import tkinter as tk                # Mantemos o tk padrão para Canvas e Text
import ttkbootstrap as ttk         #  bootstrap com o apelido
from tkinter import messagebox      # Messagebox continua vindo do tkinter padrão
import database
import auth
from matching import encontrar_matches


class App:
    def __init__(self):
        self.root = ttk.Window(themename="superhero") 
        
        self.root.title("ConectAção - Sistema de Voluntariado")
        self.root.geometry("900x700")
        self.centralizar_janela()
        
        self.usuario_atual = None
        
        # Criar abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_login = ttk.Frame(self.notebook)
        self.tab_voluntarios = ttk.Frame(self.notebook)
        self.tab_demandas = ttk.Frame(self.notebook)
        self.tab_matching = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_login, text="Login")
        self.notebook.add(self.tab_voluntarios, text="Voluntários")
        self.notebook.add(self.tab_demandas, text="Demandas")
        self.notebook.add(self.tab_matching, text="Matching")
        
        # Bind para verificar acesso ao mudar de aba
        self.notebook.bind("<<NotebookTabChanged>>", self.verificar_acesso_aba)
        
        self.criar_aba_login()
        self.criar_aba_voluntarios()
        self.criar_aba_demandas()
        self.criar_aba_matching()
        
        # Carregar dados iniciais (apenas se logado)
        if self.usuario_atual:
            self.atualizar_listas()
    
    def centralizar_janela(self):
        """Centraliza a janela na tela."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def verificar_acesso_aba(self, event=None):
        """Verifica se o usuário pode acessar a aba selecionada."""
        aba_selecionada = self.notebook.index(self.notebook.select())
        aba_nome = self.notebook.tab(aba_selecionada, "text")
        
        # Aba de Login sempre acessível
        if aba_nome == "Login":
            return
        
        # Outras abas requerem login
        if not self.usuario_atual:
            messagebox.showwarning(
                "Acesso Restrito",
                "Você precisa fazer login para acessar esta página.\n\nPor favor, faça login na aba 'Login'."
            )
            # Voltar para aba de login
            self.notebook.select(self.tab_login)
            return
    
    def criar_aba_login(self):
        """Cria a aba de login e registro."""
        # Container principal com scroll
        main_container = ttk.Frame(self.tab_login)
        main_container.pack(fill="both", expand=True)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def configurar_largura(event):
            canvas_width = event.width
            canvas.itemconfig(canvas.find_all()[0], width=canvas_width)
        
        canvas.bind('<Configure>', configurar_largura)
        
        # Frame principal com padding
        frame = ttk.Frame(scrollable_frame, padding=30)
        frame.pack(fill="both", expand=True)
        
        # ========== SEÇÃO LOGIN ==========
        login_frame = ttk.Labelframe(frame, text="Login", padding=20)
        login_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(login_frame, text="Email:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.email_entry = ttk.Entry(login_frame, width=45, font=("Arial", 10))
        self.email_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        self.email_entry.bind("<Return>", lambda e: self.login())
        
        ttk.Label(login_frame, text="Senha:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.senha_entry = ttk.Entry(login_frame, width=45, show="*", font=("Arial", 10))
        self.senha_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        self.senha_entry.bind("<Return>", lambda e: self.login())
        
        login_frame.columnconfigure(1, weight=1)
        
        btn_login_frame = ttk.Frame(login_frame)
        btn_login_frame.grid(row=2, column=0, columnspan=2, pady=15)
        ttk.Button(btn_login_frame, text="Entrar", command=self.login, width=20).pack()
        
        # ========== SEÇÃO CADASTRO ==========
        cadastro_frame = ttk.Labelframe(frame, text="Novo Cadastro", padding=20)
        cadastro_frame.pack(fill="x", pady=(0, 10))
        
        # Nome
        ttk.Label(cadastro_frame, text="Nome completo:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.reg_nome = ttk.Entry(cadastro_frame, width=45, font=("Arial", 10))
        self.reg_nome.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        
        # Email
        ttk.Label(cadastro_frame, text="Email:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.reg_email = ttk.Entry(cadastro_frame, width=45, font=("Arial", 10))
        self.reg_email.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        
        # Senha
        ttk.Label(cadastro_frame, text="Senha:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.reg_senha = ttk.Entry(cadastro_frame, width=45, show="*", font=("Arial", 10))
        self.reg_senha.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
        
        # Confirmar Senha
        ttk.Label(cadastro_frame, text="Confirmar Senha:", font=("Arial", 10)).grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.reg_confirmar_senha = ttk.Entry(cadastro_frame, width=45, show="*", font=("Arial", 10))
        self.reg_confirmar_senha.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
        self.reg_confirmar_senha.bind("<Return>", lambda e: self.registrar())
        
        # Dica de senha forte
        dica_senha = ttk.Label(
            cadastro_frame, 
            text="A senha deve conter: mínimo 8 caracteres, 1 maiúscula, 1 número e 1 caractere especial",
            font=("Arial", 8),
            foreground="gray"
        )
        dica_senha.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 5))
        
        cadastro_frame.columnconfigure(1, weight=1)
        
        # Habilidades
        ttk.Label(cadastro_frame, text="Habilidades:", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky="w", pady=(15, 5), padx=5)
        
        # Frame para habilidades com scroll
        hab_container = ttk.Frame(cadastro_frame)
        hab_container.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)
        hab_container.columnconfigure(0, weight=1)
        
        hab_canvas = tk.Canvas(hab_container, height=150, highlightthickness=1, relief="sunken", bg="white")
        hab_scrollbar = ttk.Scrollbar(hab_container, orient="vertical", command=hab_canvas.yview)
        hab_scrollable = ttk.Frame(hab_canvas)
        
        def configurar_scroll_hab(event=None):
            hab_canvas.update_idletasks()
            bbox = hab_canvas.bbox("all")
            if bbox:
                hab_canvas.configure(scrollregion=bbox)
        
        hab_scrollable.bind("<Configure>", configurar_scroll_hab)
        hab_canvas_frame = hab_canvas.create_window((0, 0), window=hab_scrollable, anchor="nw")
        
        def configurar_largura_hab(event):
            canvas_width = event.width - 2
            hab_canvas.itemconfig(hab_canvas_frame, width=canvas_width)
        
        hab_canvas.bind('<Configure>', configurar_largura_hab)
        hab_canvas.configure(yscrollcommand=hab_scrollbar.set)
        
        def _on_mousewheel_hab(event):
            hab_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_mousewheel_linux_hab(event):
            if event.num == 4:
                hab_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                hab_canvas.yview_scroll(1, "units")
        
        hab_canvas.bind_all("<MouseWheel>", _on_mousewheel_hab)
        hab_canvas.bind_all("<Button-4>", _on_mousewheel_linux_hab)
        hab_canvas.bind_all("<Button-5>", _on_mousewheel_linux_hab)
        
        self.reg_habilidades_vars = {}
        habilidades = database.listar_habilidades()
        
        for idx, hab in enumerate(habilidades):
            var = tk.BooleanVar()
            self.reg_habilidades_vars[hab['id']] = var
            row = idx // 3
            col = idx % 3
            ttk.Checkbutton(
                hab_scrollable,
                text=hab['nome'],
                variable=var
            ).grid(row=row, column=col, sticky="w", padx=5, pady=2)
        
        hab_scrollable.update_idletasks()
        hab_canvas.update_idletasks()
        bbox = hab_canvas.bbox("all")
        if bbox:
            hab_canvas.configure(scrollregion=bbox)
        
        hab_canvas.grid(row=0, column=0, sticky="ew")
        hab_scrollbar.grid(row=0, column=1, sticky="ns")
        hab_container.columnconfigure(0, weight=1)
        
        # Botão cadastrar
        btn_cadastro_frame = ttk.Frame(cadastro_frame)
        btn_cadastro_frame.grid(row=5, column=0, columnspan=2, pady=15)
        ttk.Button(btn_cadastro_frame, text="Cadastrar", command=self.registrar, width=20).pack()
        
        # Pack canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def criar_aba_voluntarios(self):
        """Cria a aba de listagem de voluntários."""
        frame = ttk.Frame(self.tab_voluntarios, padding=10)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Voluntários Cadastrados", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        
        # Treeview com scrollbar
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True)
        
        self.vol_tree = ttk.Treeview(tree_frame, columns=("nome", "email", "habilidades"), show="headings", height=20)
        self.vol_tree.heading("nome", text="Nome")
        self.vol_tree.heading("email", text="Email")
        self.vol_tree.heading("habilidades", text="Habilidades")
        self.vol_tree.column("nome", width=200)
        self.vol_tree.column("email", width=250)
        self.vol_tree.column("habilidades", width=400)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.vol_tree.yview)
        self.vol_tree.configure(yscrollcommand=scrollbar.set)
        
        self.vol_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Button(frame, text="Atualizar", command=self.atualizar_voluntarios).pack(pady=5)
    
    def criar_aba_demandas(self):
        """Cria a aba de demandas."""
        frame = ttk.Frame(self.tab_demandas, padding=10)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Demandas", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        
        # Treeview com scrollbar
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True)
        
        self.dem_tree = ttk.Treeview(tree_frame, columns=("titulo", "habilidades"), show="headings", height=20)
        self.dem_tree.heading("titulo", text="Título")
        self.dem_tree.heading("habilidades", text="Habilidades Necessárias")
        self.dem_tree.column("titulo", width=300)
        self.dem_tree.column("habilidades", width=500)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.dem_tree.yview)
        self.dem_tree.configure(yscrollcommand=scrollbar.set)
        
        self.dem_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Criar Demanda", command=self.criar_demanda).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Atualizar", command=self.atualizar_demandas).pack(side="left", padx=5)
    
    def criar_aba_matching(self):
        """Cria a aba de matching."""
        frame = ttk.Frame(self.tab_matching, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Título
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill="x", pady=(0, 15))
        ttk.Label(title_frame, text="Sistema de Matching Inteligente", font=("Arial", 14, "bold")).pack(side="left")
        
        # Frame de controles
        controls_frame = ttk.Labelframe(frame, text="Selecionar Demanda", padding=10)
        controls_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(controls_frame, text="Demanda:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.match_combo = ttk.Combobox(controls_frame, state="readonly", width=70, font=("Arial", 10))
        self.match_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        controls_frame.columnconfigure(1, weight=1)
        
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="🔄 Atualizar Lista", command=self.atualizar_combo_matching).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔍 Gerar Matches", command=self.gerar_matches).pack(side="left", padx=5)
        
        # Área de resultados
        result_label_frame = ttk.Labelframe(frame, text="Resultados do Matching", padding=5)
        result_label_frame.pack(fill="both", expand=True)
        
        result_frame = ttk.Frame(result_label_frame)
        result_frame.pack(fill="both", expand=True)
        
        self.match_text = tk.Text(result_frame, wrap=tk.WORD, font=("Consolas", 10), bg="#f8f8f8")
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.match_text.yview)
        self.match_text.configure(yscrollcommand=scrollbar.set)
        
        self.match_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
    
    def login(self):
        """Realiza login do usuário."""
        email = self.email_entry.get().strip()
        senha = self.senha_entry.get().strip()
        
        if not email:
            messagebox.showerror("Erro", "Digite seu email")
            self.email_entry.focus()
            return
        
        if not senha:
            messagebox.showerror("Erro", "Digite sua senha")
            self.senha_entry.focus()
            return
        
        # Verifica se é admin do .env
        if auth.verificar_admin(email, senha):
            self.usuario_atual = auth.get_admin_info()
            messagebox.showinfo("Sucesso", f"Bem-vindo, {self.usuario_atual['nome']}!\nPerfil: Administrador")
            # Limpar campos
            self.email_entry.delete(0, tk.END)
            self.senha_entry.delete(0, tk.END)
            # Atualizar listas e ir para demandas
            self.atualizar_listas()
            self.notebook.select(self.tab_demandas)
            return
        
        # Login normal
        usuario = database.buscar_usuario_por_email(email)
        if not usuario:
            messagebox.showerror("Erro", "Email não cadastrado")
            self.email_entry.focus()
            return
        
        if not auth.verificar_senha(usuario['senha_hash'], senha):
            messagebox.showerror("Erro", "Senha incorreta")
            self.senha_entry.delete(0, tk.END)
            self.senha_entry.focus()
            return
        
        self.usuario_atual = dict(usuario)
        messagebox.showinfo("Sucesso", f"Bem-vindo, {usuario['nome']}!\nPerfil: {usuario['papel'].title()}")
        # Limpar campos
        self.email_entry.delete(0, tk.END)
        self.senha_entry.delete(0, tk.END)
        self.atualizar_listas()
        self.notebook.select(self.tab_demandas)
    
    def registrar(self):
        """Registra novo voluntário."""
        nome = self.reg_nome.get().strip()
        email = self.reg_email.get().strip()
        senha = self.reg_senha.get().strip()
        confirmar_senha = self.reg_confirmar_senha.get().strip()
        
        # Coletar habilidades selecionadas
        habilidades_ids = [hab_id for hab_id, var in self.reg_habilidades_vars.items() if var.get()]
        
        # Validações
        if not nome:
            messagebox.showerror("Erro", "Digite seu nome completo")
            self.reg_nome.focus()
            return
        
        if not email:
            messagebox.showerror("Erro", "Digite seu email")
            self.reg_email.focus()
            return
        
        # Validação rigorosa de email
        email_valido, msg_email = auth.validar_email(email)
        if not email_valido:
            messagebox.showerror("Erro de Validação", msg_email)
            self.reg_email.focus()
            return
        
        if not senha:
            messagebox.showerror("Erro", "Digite uma senha")
            self.reg_senha.focus()
            return
        
        if not confirmar_senha:
            messagebox.showerror("Erro", "Confirme sua senha")
            self.reg_confirmar_senha.focus()
            return
        
        # Verificar se as senhas coincidem
        if senha != confirmar_senha:
            messagebox.showerror("Erro", "As senhas não coincidem. Por favor, digite novamente.")
            self.reg_senha.delete(0, tk.END)
            self.reg_confirmar_senha.delete(0, tk.END)
            self.reg_senha.focus()
            return
        
        # Validação de senha forte
        senha_valida, msg_senha = auth.validar_senha_forte(senha)
        if not senha_valida:
            messagebox.showerror("Erro de Segurança", msg_senha)
            self.reg_senha.delete(0, tk.END)
            self.reg_confirmar_senha.delete(0, tk.END)
            self.reg_senha.focus()
            return
        
        if not habilidades_ids:
            messagebox.showerror("Erro", "Selecione pelo menos uma habilidade")
            return
        
        # Verifica se não é email de admin
        if auth.ADMIN_EMAIL and email == auth.ADMIN_EMAIL:
            messagebox.showerror("Erro", "Este email é reservado para administrador")
            self.reg_email.focus()
            return
        
        if database.buscar_usuario_por_email(email):
            messagebox.showerror("Erro", "Este email já está cadastrado")
            self.reg_email.focus()
            return
        
        try:
            uid = database.criar_usuario(nome, email, auth.hash_senha(senha))
            database.criar_voluntario(uid, habilidades_ids)
            messagebox.showinfo("Sucesso", f"Cadastro realizado com sucesso!\n\nBem-vindo, {nome}!\n\nFaça login para continuar.")
            # Limpar campos
            self.reg_nome.delete(0, tk.END)
            self.reg_email.delete(0, tk.END)
            self.reg_senha.delete(0, tk.END)
            self.reg_confirmar_senha.delete(0, tk.END)
            # Limpar checkboxes
            for var in self.reg_habilidades_vars.values():
                var.set(False)
            # Focar no campo de email do login
            self.email_entry.focus()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {str(e)}")
    
    def criar_demanda(self):
        """Cria nova demanda (apenas admin)."""
        if not self.usuario_atual or self.usuario_atual.get('papel') != 'admin':
            messagebox.showerror("Erro", "Apenas administradores podem criar demandas")
            return
        
        # Criar janela de diálogo
        dialog = tk.Toplevel(self.root)
        dialog.title("Nova Demanda")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Título
        ttk.Label(dialog, text="Título da demanda:", font=("Arial", 10, "bold")).pack(pady=10)
        titulo_entry = ttk.Entry(dialog, width=50)
        titulo_entry.pack(pady=5)
        
        # Habilidades
        ttk.Label(dialog, text="Selecione as habilidades necessárias:", font=("Arial", 10, "bold")).pack(pady=10)
        
        # Frame para checkboxes com scroll
        hab_frame = ttk.Frame(dialog)
        hab_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(hab_frame, height=250)
        scrollbar = ttk.Scrollbar(hab_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        demanda_habs_vars = {}
        habilidades = database.listar_habilidades()
        
        for idx, hab in enumerate(habilidades):
            var = tk.BooleanVar()
            demanda_habs_vars[hab['id']] = var
            row = idx // 2
            col = idx % 2
            ttk.Checkbutton(scrollable, text=hab['nome'], variable=var).grid(row=row, column=col, sticky="w", padx=5, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def salvar_demanda():
            titulo = titulo_entry.get().strip()
            habilidades_ids = [hab_id for hab_id, var in demanda_habs_vars.items() if var.get()]
            
            if not titulo:
                messagebox.showerror("Erro", "Digite o título da demanda")
                return
            
            if not habilidades_ids:
                messagebox.showerror("Erro", "Selecione pelo menos uma habilidade")
                return
            
            try:
                database.criar_demanda(titulo, habilidades_ids)
                messagebox.showinfo("Sucesso", "Demanda criada com sucesso!")
                dialog.destroy()
                self.atualizar_demandas()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao criar demanda: {str(e)}")
        
        ttk.Button(dialog, text="Criar", command=salvar_demanda).pack(pady=10)
    
    def atualizar_voluntarios(self):
        """Atualiza lista de voluntários."""
        for item in self.vol_tree.get_children():
            self.vol_tree.delete(item)
        
        try:
            voluntarios = database.listar_voluntarios()
            for vol in voluntarios:
                habilidades_str = ", ".join(vol.get('habilidades_nomes', []))
                self.vol_tree.insert("", "end", values=(
                    vol.get('nome', ''),
                    vol.get('email', ''),
                    habilidades_str
                ))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar voluntários: {str(e)}")
    
    def atualizar_demandas(self):
        """Atualiza lista de demandas."""
        for item in self.dem_tree.get_children():
            self.dem_tree.delete(item)
        
        try:
            demandas = database.listar_demandas()
            for dem in demandas:
                self.dem_tree.insert("", "end", values=(
                    dem.get('titulo', ''),
                    dem.get('habilidades_requeridas', '')
                ))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar demandas: {str(e)}")
    
    def atualizar_combo_matching(self):
        """Atualiza combo de demandas para matching."""
        if not self.usuario_atual:
            return
        try:
            demandas = database.listar_demandas()
            if demandas:
                valores = [f"{d['id']} - {d['titulo']}" for d in demandas]
                self.match_combo['values'] = valores
                if valores and not self.match_combo.get():
                    self.match_combo.current(0)
            else:
                self.match_combo['values'] = []
                self.match_combo.set("")
        except Exception as e:
            print(f"Erro ao atualizar combo matching: {e}")
    
    def gerar_matches(self):
        """Gera matches para uma demanda."""
        if not self.usuario_atual:
            messagebox.showwarning("Acesso Restrito", "Faça login para usar o sistema de matching")
            self.notebook.select(self.tab_login)
            return
        
        selecao = self.match_combo.get()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione uma demanda primeiro")
            return
        
        try:
            demanda_id = int(selecao.split(" - ")[0])
            demanda = database.buscar_demanda_por_id(demanda_id)
            if not demanda:
                messagebox.showerror("Erro", "Demanda não encontrada")
                return
            
            # Mostrar informações da demanda
            demanda_habs = ", ".join(demanda.get('habilidades_nomes', []))
            
            matches = encontrar_matches(demanda)
            
            self.match_text.delete("1.0", tk.END)
            
            # Cabeçalho com informações da demanda
            resultado = "=" * 60 + "\n"
            resultado += f"DEMANDA: {demanda.get('titulo', 'N/A')}\n"
            resultado += f"HABILIDADES NECESSÁRIAS: {demanda_habs}\n"
            resultado += "=" * 60 + "\n\n"
            
            if not matches:
                resultado += "Nenhum voluntário encontrado com as habilidades necessárias.\n\n"
                resultado += "Sugestão: Verifique se há voluntários cadastrados com essas habilidades."
                self.match_text.insert("1.0", resultado)
                return
            
            resultado += f"ENCONTRADOS {len(matches)} VOLUNTÁRIO(S) COMPATÍVEL(IS):\n\n"
            
            for idx, match in enumerate(matches, 1):
                vol = match['voluntario']
                habilidades_str = ", ".join(vol.get('habilidades_nomes', []))
                habilidades_comuns = match.get('habilidades_comuns', [])
                habilidades_comuns_str = ", ".join(habilidades_comuns) if habilidades_comuns else "Nenhuma"
                
                # Calcular porcentagem de match
                porcentagem = match['score'] * 100
                
                resultado += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                resultado += f"MATCH #{idx} - COMPATIBILIDADE: {porcentagem:.0f}%\n"
                resultado += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                resultado += f"👤 Nome: {vol.get('nome', 'N/A')}\n"
                resultado += f"📧 Email: {vol.get('email', 'N/A')}\n"
                resultado += f"🛠️  Todas as Habilidades: {habilidades_str}\n"
                resultado += f"✅ Habilidades que Correspondem: {habilidades_comuns_str}\n"
                resultado += f"⭐ Score: {match['score']:.2f} ({porcentagem:.0f}% de compatibilidade)\n"
                resultado += "\n"
            
            self.match_text.insert("1.0", resultado)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar matches: {str(e)}")
    
    def atualizar_listas(self):
        """Atualiza todas as listas."""
        if not self.usuario_atual:
            return
        try:
            self.atualizar_voluntarios()
            self.atualizar_demandas()
            self.atualizar_combo_matching()
        except Exception as e:
            print(f"Erro ao atualizar listas: {e}")
    
    def run(self):
        """Inicia a aplicação."""
        self.root.mainloop()

