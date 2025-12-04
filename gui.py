"""Interface gráfica simples e funcional."""  # Docstring do módulo
import tkinter as tk                # Mantemos o tk padrão para Canvas e Text
import ttkbootstrap as ttk          # IMPORTANTE: Importamos o bootstrap com o apelido 'ttk'
from tkinter import messagebox      # Messagebox continua vindo do tkinter padrão
import database
import auth
from matching import encontrar_matches


class App:
    def __init__(self):
        self.root = ttk.Window(themename="cyborg") 
        
        self.root.title("ConectAção - Sistema de Voluntariado")
        self.root.geometry("900x700")
        self.centralizar_janela()  # Chama o método para centralizar a janela na tela
        
        self.usuario_atual = None  # Inicializa a variável que armazena o usuário logado como None
        
        # Criar abas
        self.notebook = ttk.Notebook(self.root)  # Cria um widget Notebook (abas) na janela principal
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)  # Empacota o notebook preenchendo todo o espaço disponível com padding
        
        self.tab_login = ttk.Frame(self.notebook)  # Cria um frame para a aba de login
        self.tab_voluntarios = ttk.Frame(self.notebook)  # Cria um frame para a aba de voluntários
        self.tab_demandas = ttk.Frame(self.notebook)  # Cria um frame para a aba de demandas
        self.tab_matching = ttk.Frame(self.notebook)  # Cria um frame para a aba de matching
        
        self.notebook.add(self.tab_login, text="Login")  # Adiciona a aba de login ao notebook com o texto "Login"
        self.notebook.add(self.tab_voluntarios, text="Voluntários")  # Adiciona a aba de voluntários ao notebook com o texto "Voluntários"
        self.notebook.add(self.tab_demandas, text="Demandas")  # Adiciona a aba de demandas ao notebook com o texto "Demandas"
        self.notebook.add(self.tab_matching, text="Matching")  # Adiciona a aba de matching ao notebook com o texto "Matching"
        
        # Bind para verificar acesso ao mudar de aba
        self.notebook.bind("<<NotebookTabChanged>>", self.verificar_acesso_aba)  # Vincula o evento de mudança de aba ao método verificar_acesso_aba
        
        self.criar_aba_login()  # Chama o método para criar a interface da aba de login
        self.criar_aba_voluntarios()  # Chama o método para criar a interface da aba de voluntários
        self.criar_aba_demandas()  # Chama o método para criar a interface da aba de demandas
        self.criar_aba_matching()  # Chama o método para criar a interface da aba de matching
    
    def centralizar_janela(self):
        """Centraliza a janela na tela."""  # Docstring do método
        self.root.update_idletasks()  # Atualiza as tarefas pendentes da janela para obter dimensões corretas
        width = self.root.winfo_width()  # Obtém a largura atual da janela
        height = self.root.winfo_height()  # Obtém a altura atual da janela
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)  # Calcula a posição x para centralizar horizontalmente
        y = (self.root.winfo_screenheight() // 2) - (height // 2)  # Calcula a posição y para centralizar verticalmente
        self.root.geometry(f'{width}x{height}+{x}+{y}')  # Define a geometria da janela com as novas posições centralizadas
    
    def verificar_acesso_aba(self, event=None):
        """Verifica se o usuário pode acessar a aba selecionada."""  # Docstring do método
        aba_selecionada = self.notebook.index(self.notebook.select())  # Obtém o índice da aba atualmente selecionada
        aba_nome = self.notebook.tab(aba_selecionada, "text")  # Obtém o texto (nome) da aba selecionada
        
        # Aba de Login sempre acessível
        if aba_nome == "Login":  # Verifica se a aba selecionada é a de Login
            return  # Retorna sem fazer nada, pois a aba de login é sempre acessível
        
        # Outras abas requerem login
        if not self.usuario_atual:  # Verifica se não há usuário logado
            messagebox.showwarning(  # Exibe uma mensagem de aviso
                "Acesso Restrito",  # Título da mensagem
                "Você precisa fazer login para acessar esta página.\n\nPor favor, faça login na aba 'Login'."  # Texto da mensagem
            )
            # Voltar para aba de login
            self.notebook.select(self.tab_login)  # Seleciona a aba de login
            return  # Retorna para impedir o acesso à aba
    
    def criar_aba_login(self):
        """Cria a aba de login e registro."""  # Docstring do método
        # Container principal com scroll
        main_container = ttk.Frame(self.tab_login)  # Cria um frame principal dentro da aba de login
        main_container.pack(fill="both", expand=True)  # Empacota o container preenchendo todo o espaço disponível
        
        # Canvas para scroll
        canvas = tk.Canvas(main_container, highlightthickness=0)  # Cria um canvas para permitir scroll, sem borda destacada
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)  # Cria uma barra de rolagem vertical vinculada ao canvas
        scrollable_frame = ttk.Frame(canvas)  # Cria um frame que será rolável dentro do canvas
        
        scrollable_frame.bind(  # Vincula um evento ao frame rolável
            "<Configure>",  # Evento disparado quando o frame é configurado
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))  # Atualiza a região de scroll do canvas quando o frame muda de tamanho
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")  # Cria uma janela no canvas para conter o frame rolável, ancorado no canto superior esquerdo
        canvas.configure(yscrollcommand=scrollbar.set)  # Configura o canvas para atualizar a posição da scrollbar quando rolar
        
        def configurar_largura(event):  # Define função para configurar a largura do canvas
            canvas_width = event.width  # Obtém a largura do evento (nova largura do canvas)
            canvas.itemconfig(canvas.find_all()[0], width=canvas_width)  # Atualiza a largura da janela dentro do canvas
        
        canvas.bind('<Configure>', configurar_largura)  # Vincula o evento de configuração do canvas à função
        
        # Frame principal com padding
        frame = ttk.Frame(scrollable_frame, padding=30)  # Cria um frame principal com padding de 30 pixels
        frame.pack(fill="both", expand=True)  # Empacota o frame preenchendo todo o espaço disponível
        
        # ========== SEÇÃO LOGIN ==========
        login_frame = ttk.LabelFrame(frame, text="Login", padding=20)  # Cria um frame com label "Login" e padding de 20 pixels
        login_frame.pack(fill="x", pady=(0, 20))  # Empacota o frame preenchendo horizontalmente com margem inferior de 20 pixels
        
        ttk.Label(login_frame, text="Email:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5, padx=5)  # Cria um label "Email:" e posiciona na grade
        self.email_entry = ttk.Entry(login_frame, width=45, font=("Arial", 10))  # Cria um campo de entrada para email com largura de 45 caracteres
        self.email_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")  # Posiciona o campo de email na grade, expandindo horizontalmente
        self.email_entry.bind("<Return>", lambda e: self.login())  # Vincula a tecla Enter ao método login
        
        ttk.Label(login_frame, text="Senha:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5, padx=5)  # Cria um label "Senha:" e posiciona na grade
        self.senha_entry = ttk.Entry(login_frame, width=45, show="*", font=("Arial", 10))  # Cria um campo de entrada para senha que oculta o texto com "*"
        self.senha_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")  # Posiciona o campo de senha na grade, expandindo horizontalmente
        self.senha_entry.bind("<Return>", lambda e: self.login())  # Vincula a tecla Enter ao método login
        
        login_frame.columnconfigure(1, weight=1)  # Configura a coluna 1 para expandir quando a janela for redimensionada
        
        btn_login_frame = ttk.Frame(login_frame)  # Cria um frame para conter o botão de login
        btn_login_frame.grid(row=2, column=0, columnspan=2, pady=15)  # Posiciona o frame do botão na grade, ocupando duas colunas
        ttk.Button(btn_login_frame, text="Entrar", command=self.login, width=20).pack()  # Cria um botão "Entrar" que chama o método login quando clicado
        
        # ========== SEÇÃO CADASTRO ==========
        cadastro_frame = ttk.LabelFrame(frame, text="Novo Cadastro", padding=20)  # Cria um frame com label "Novo Cadastro" e padding de 20 pixels
        cadastro_frame.pack(fill="x", pady=(0, 10))  # Empacota o frame preenchendo horizontalmente com margem inferior de 10 pixels
        
        # Nome
        ttk.Label(cadastro_frame, text="Nome completo:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5, padx=5)  # Cria um label "Nome completo:" e posiciona na grade
        self.reg_nome = ttk.Entry(cadastro_frame, width=45, font=("Arial", 10))  # Cria um campo de entrada para nome com largura de 45 caracteres
        self.reg_nome.grid(row=0, column=1, pady=5, padx=5, sticky="ew")  # Posiciona o campo de nome na grade, expandindo horizontalmente
        
        # Email
        ttk.Label(cadastro_frame, text="Email:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5, padx=5)  # Cria um label "Email:" e posiciona na grade
        self.reg_email = ttk.Entry(cadastro_frame, width=45, font=("Arial", 10))  # Cria um campo de entrada para email com largura de 45 caracteres
        self.reg_email.grid(row=1, column=1, pady=5, padx=5, sticky="ew")  # Posiciona o campo de email na grade, expandindo horizontalmente
        
        # Senha
        ttk.Label(cadastro_frame, text="Senha:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5, padx=5)  # Cria um label "Senha:" e posiciona na grade
        self.reg_senha = ttk.Entry(cadastro_frame, width=45, show="*", font=("Arial", 10))  # Cria um campo de entrada para senha que oculta o texto com "*"
        self.reg_senha.grid(row=2, column=1, pady=5, padx=5, sticky="ew")  # Posiciona o campo de senha na grade, expandindo horizontalmente
        
        # Confirmar Senha
        ttk.Label(cadastro_frame, text="Confirmar Senha:", font=("Arial", 10)).grid(row=3, column=0, sticky="w", pady=5, padx=5)  # Cria um label "Confirmar Senha:" e posiciona na grade
        self.reg_confirmar_senha = ttk.Entry(cadastro_frame, width=45, show="*", font=("Arial", 10))  # Cria um campo de entrada para confirmar senha que oculta o texto com "*"
        self.reg_confirmar_senha.grid(row=3, column=1, pady=5, padx=5, sticky="ew")  # Posiciona o campo de confirmar senha na grade, expandindo horizontalmente
        self.reg_confirmar_senha.bind("<Return>", lambda e: self.registrar())  # Vincula a tecla Enter ao método registrar
        
        # Dica de senha forte
        dica_senha = ttk.Label(  # Cria um label com dica sobre senha forte
            cadastro_frame,  # Define o frame pai
            text="A senha deve conter: mínimo 8 caracteres, 1 maiúscula, 1 número e 1 caractere especial",  # Define o texto da dica
            font=("Arial", 8),  # Define a fonte como Arial tamanho 8
            foreground="gray"  # Define a cor do texto como cinza
        )
        dica_senha.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 5))  # Posiciona o label na grade, ocupando duas colunas
        
        cadastro_frame.columnconfigure(1, weight=1)  # Configura a coluna 1 para expandir quando a janela for redimensionada
        
        # Habilidades
        ttk.Label(cadastro_frame, text="Habilidades:", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky="w", pady=(15, 5), padx=5)  # Cria um label "Habilidades:" em negrito e posiciona na grade
        
        # Frame para habilidades com scroll
        hab_container = ttk.Frame(cadastro_frame)  # Cria um frame container para as habilidades
        hab_container.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)  # Posiciona o container na grade, ocupando duas colunas
        hab_container.columnconfigure(0, weight=1)  # Configura a coluna 0 para expandir
        
        hab_canvas = tk.Canvas(hab_container, height=150, highlightthickness=1, relief="sunken", bg="white")  # Cria um canvas para habilidades com altura de 150 pixels e fundo branco
        hab_scrollbar = ttk.Scrollbar(hab_container, orient="vertical", command=hab_canvas.yview)  # Cria uma barra de rolagem vertical para o canvas
        hab_scrollable = ttk.Frame(hab_canvas)  # Cria um frame rolável dentro do canvas
        
        def configurar_scroll_hab(event=None):  # Define função para configurar o scroll das habilidades
            hab_canvas.update_idletasks()  # Atualiza tarefas pendentes do canvas
            bbox = hab_canvas.bbox("all")  # Obtém a caixa delimitadora de todos os itens no canvas
            if bbox:  # Verifica se há uma caixa delimitadora
                hab_canvas.configure(scrollregion=bbox)  # Configura a região de scroll do canvas
        
        hab_scrollable.bind("<Configure>", configurar_scroll_hab)  # Vincula o evento de configuração do frame ao método de scroll
        hab_canvas_frame = hab_canvas.create_window((0, 0), window=hab_scrollable, anchor="nw")  # Cria uma janela no canvas para conter o frame rolável
        
        def configurar_largura_hab(event):  # Define função para configurar a largura do canvas de habilidades
            canvas_width = event.width - 2  # Obtém a largura do evento menos 2 pixels
            hab_canvas.itemconfig(hab_canvas_frame, width=canvas_width)  # Atualiza a largura da janela dentro do canvas
        
        hab_canvas.bind('<Configure>', configurar_largura_hab)  # Vincula o evento de configuração do canvas à função
        hab_canvas.configure(yscrollcommand=hab_scrollbar.set)  # Configura o canvas para atualizar a posição da scrollbar
        
        def _on_mousewheel_hab(event):  # Define função para rolagem com mouse wheel (Windows/Mac)
            hab_canvas.yview_scroll(int(-1*(event.delta/120)), "units")  # Rola o canvas verticalmente baseado no movimento do mouse wheel
        
        def _on_mousewheel_linux_hab(event):  # Define função para rolagem com mouse wheel (Linux)
            if event.num == 4:  # Verifica se é rolagem para cima no Linux
                hab_canvas.yview_scroll(-1, "units")  # Rola o canvas para cima
            elif event.num == 5:  # Verifica se é rolagem para baixo no Linux
                hab_canvas.yview_scroll(1, "units")  # Rola o canvas para baixo
        
        hab_canvas.bind("<MouseWheel>", _on_mousewheel_hab)  # Vincula o evento de mouse wheel (Windows/Mac) à função no canvas específico
        hab_canvas.bind("<Button-4>", _on_mousewheel_linux_hab)  # Vincula o evento de botão 4 (Linux scroll up) à função no canvas específico
        hab_canvas.bind("<Button-5>", _on_mousewheel_linux_hab)  # Vincula o evento de botão 5 (Linux scroll down) à função no canvas específico
        
        self.reg_habilidades_vars = {}  # Inicializa um dicionário vazio para armazenar variáveis booleanas das habilidades
        habilidades = database.listar_habilidades()  # Busca todas as habilidades do banco de dados
        
        for idx, hab in enumerate(habilidades):  # Itera sobre cada habilidade com seu índice
            var = tk.BooleanVar()  # Cria uma variável booleana para cada habilidade
            self.reg_habilidades_vars[hab['id']] = var  # Armazena a variável no dicionário usando o ID da habilidade como chave
            row = idx // 3  # Calcula a linha na grade (3 colunas)
            col = idx % 3  # Calcula a coluna na grade (resto da divisão por 3)
            ttk.Checkbutton(  # Cria um checkbox para a habilidade
                hab_scrollable,  # Define o frame pai
                text=hab['nome'],  # Define o texto do checkbox como o nome da habilidade
                variable=var  # Vincula a variável booleana ao checkbox
            ).grid(row=row, column=col, sticky="w", padx=5, pady=2)  # Posiciona o checkbox na grade
        
        hab_scrollable.update_idletasks()  # Atualiza tarefas pendentes do frame rolável
        hab_canvas.update_idletasks()  # Atualiza tarefas pendentes do canvas
        bbox = hab_canvas.bbox("all")  # Obtém a caixa delimitadora de todos os itens no canvas
        if bbox:  # Verifica se há uma caixa delimitadora
            hab_canvas.configure(scrollregion=bbox)  # Configura a região de scroll do canvas
        
        hab_canvas.grid(row=0, column=0, sticky="ew")  # Posiciona o canvas na grade, expandindo horizontalmente
        hab_scrollbar.grid(row=0, column=1, sticky="ns")  # Posiciona a scrollbar na grade, expandindo verticalmente
        hab_container.columnconfigure(0, weight=1)  # Configura a coluna 0 para expandir
        
        # Botão cadastrar
        btn_cadastro_frame = ttk.Frame(cadastro_frame)  # Cria um frame para conter o botão de cadastro
        btn_cadastro_frame.grid(row=7, column=0, columnspan=2, pady=15)  # Posiciona o frame do botão na grade, ocupando duas colunas (row=7 para ficar depois do container de habilidades)
        ttk.Button(btn_cadastro_frame, text="Cadastrar", command=self.registrar, width=20).pack()  # Cria um botão "Cadastrar" que chama o método registrar quando clicado
        
        # Pack canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)  # Empacota o canvas principal à esquerda, preenchendo todo o espaço
        scrollbar.pack(side="right", fill="y")  # Empacota a scrollbar principal à direita, preenchendo verticalmente
    
    def criar_aba_voluntarios(self):
        """Cria a aba de listagem de voluntários."""  # Docstring do método
        frame = ttk.Frame(self.tab_voluntarios, padding=10)  # Cria um frame principal com padding de 10 pixels
        frame.pack(fill="both", expand=True)  # Empacota o frame preenchendo todo o espaço disponível
        
        ttk.Label(frame, text="Voluntários Cadastrados", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)  # Cria um label de título e posiciona à esquerda
        
        # Treeview com scrollbar
        tree_frame = ttk.Frame(frame)  # Cria um frame para conter a treeview
        tree_frame.pack(fill="both", expand=True)  # Empacota o frame preenchendo todo o espaço disponível
        
        self.vol_tree = ttk.Treeview(tree_frame, columns=("nome", "email", "habilidades"), show="headings", height=20)  # Cria uma treeview com 3 colunas e altura de 20 linhas
        self.vol_tree.heading("nome", text="Nome")  # Define o cabeçalho da coluna "nome"
        self.vol_tree.heading("email", text="Email")  # Define o cabeçalho da coluna "email"
        self.vol_tree.heading("habilidades", text="Habilidades")  # Define o cabeçalho da coluna "habilidades"
        self.vol_tree.column("nome", width=200)  # Define a largura da coluna "nome" como 200 pixels
        self.vol_tree.column("email", width=250)  # Define a largura da coluna "email" como 250 pixels
        self.vol_tree.column("habilidades", width=400)  # Define a largura da coluna "habilidades" como 400 pixels
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.vol_tree.yview)  # Cria uma barra de rolagem vertical para a treeview
        self.vol_tree.configure(yscrollcommand=scrollbar.set)  # Configura a treeview para atualizar a posição da scrollbar
        
        self.vol_tree.pack(side="left", fill="both", expand=True)  # Empacota a treeview à esquerda, preenchendo todo o espaço
        scrollbar.pack(side="right", fill="y")  # Empacota a scrollbar à direita, preenchendo verticalmente
        
        ttk.Button(frame, text="Atualizar", command=self.atualizar_voluntarios).pack(pady=5)  # Cria um botão "Atualizar" que chama o método atualizar_voluntarios
    
    def criar_aba_demandas(self):
        """Cria a aba de demandas."""  # Docstring do método
        frame = ttk.Frame(self.tab_demandas, padding=10)  # Cria um frame principal com padding de 10 pixels
        frame.pack(fill="both", expand=True)  # Empacota o frame preenchendo todo o espaço disponível
        
        ttk.Label(frame, text="Demandas", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)  # Cria um label de título e posiciona à esquerda
        
        # Treeview com scrollbar
        tree_frame = ttk.Frame(frame)  # Cria um frame para conter a treeview
        tree_frame.pack(fill="both", expand=True)  # Empacota o frame preenchendo todo o espaço disponível
        
        self.dem_tree = ttk.Treeview(tree_frame, columns=("titulo", "habilidades"), show="headings", height=20)  # Cria uma treeview com 2 colunas e altura de 20 linhas
        self.dem_tree.heading("titulo", text="Título")  # Define o cabeçalho da coluna "titulo"
        self.dem_tree.heading("habilidades", text="Habilidades Necessárias")  # Define o cabeçalho da coluna "habilidades"
        self.dem_tree.column("titulo", width=300)  # Define a largura da coluna "titulo" como 300 pixels
        self.dem_tree.column("habilidades", width=500)  # Define a largura da coluna "habilidades" como 500 pixels
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.dem_tree.yview)  # Cria uma barra de rolagem vertical para a treeview
        self.dem_tree.configure(yscrollcommand=scrollbar.set)  # Configura a treeview para atualizar a posição da scrollbar
        
        self.dem_tree.pack(side="left", fill="both", expand=True)  # Empacota a treeview à esquerda, preenchendo todo o espaço
        scrollbar.pack(side="right", fill="y")  # Empacota a scrollbar à direita, preenchendo verticalmente
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5) # Transformamos em self.btn_criar_demanda para poder esconder depois
        self.btn_criar_demanda = ttk.Button(btn_frame, text="Criar Demanda", command=self.criar_demanda, bootstyle="success")
        self.btn_criar_demanda.pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Atualizar", command=self.atualizar_demandas, bootstyle="info").pack(side="left", padx=5)
    
    def criar_aba_matching(self):
        """Cria a aba de matching."""  # Docstring do método
        frame = ttk.Frame(self.tab_matching, padding=10)  # Cria um frame principal com padding de 10 pixels
        frame.pack(fill="both", expand=True)  # Empacota o frame preenchendo todo o espaço disponível
        
        # Título
        title_frame = ttk.Frame(frame)  # Cria um frame para o título
        title_frame.pack(fill="x", pady=(0, 15))  # Empacota o frame preenchendo horizontalmente com margem inferior de 15 pixels
        ttk.Label(title_frame, text="Sistema de Matching Inteligente", font=("Arial", 14, "bold")).pack(side="left")  # Cria um label de título em negrito e posiciona à esquerda
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(frame, text="Selecionar Demanda", padding=10)  # Cria um frame com label "Selecionar Demanda" e padding de 10 pixels
        controls_frame.pack(fill="x", pady=(0, 10))  # Empacota o frame preenchendo horizontalmente com margem inferior de 10 pixels
        
        ttk.Label(controls_frame, text="Demanda:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)  # Cria um label "Demanda:" e posiciona na grade
        self.match_combo = ttk.Combobox(controls_frame, state="readonly", width=70, font=("Arial", 10))  # Cria um combobox somente leitura com largura de 70 caracteres
        self.match_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)  # Posiciona o combobox na grade, expandindo horizontalmente
        controls_frame.columnconfigure(1, weight=1)  # Configura a coluna 1 para expandir quando a janela for redimensionada
        
        btn_frame = ttk.Frame(controls_frame)  # Cria um frame para conter os botões
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)  # Posiciona o frame do botão na grade, ocupando duas colunas
        ttk.Button(btn_frame, text="🔄 Atualizar Lista", command=self.atualizar_combo_matching).pack(side="left", padx=5)  # Cria um botão "Atualizar Lista" que chama o método atualizar_combo_matching
        ttk.Button(btn_frame, text="🔍 Gerar Matches", command=self.gerar_matches).pack(side="left", padx=5)  # Cria um botão "Gerar Matches" que chama o método gerar_matches
        
        # Área de resultados
        result_label_frame = ttk.LabelFrame(frame, text="Resultados do Matching", padding=5)  # Cria um frame com label "Resultados do Matching" e padding de 5 pixels
        result_label_frame.pack(fill="both", expand=True)  # Empacota o frame preenchendo todo o espaço disponível
        
        result_frame = ttk.Frame(result_label_frame)  # Cria um frame para os resultados
        result_frame.pack(fill="both", expand=True)  # Empacota o frame preenchendo todo o espaço disponível
        
        self.match_text = tk.Text(result_frame, wrap=tk.WORD, font=("Consolas", 10), bg="#f8f8f8")  # Cria um widget de texto com quebra de palavra, fonte Consolas e fundo cinza claro
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.match_text.yview)  # Cria uma barra de rolagem vertical para o texto
        self.match_text.configure(yscrollcommand=scrollbar.set)  # Configura o texto para atualizar a posição da scrollbar
        
        self.match_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)  # Empacota o texto à esquerda, preenchendo todo o espaço
        scrollbar.pack(side="right", fill="y", pady=5)  # Empacota a scrollbar à direita, preenchendo verticalmente
    
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
            
            # === LÓGICA ADMIN: MOSTRAR TUDO ===
            
            # 1. Botão de criar demanda
            self.btn_criar_demanda.pack(side="left", padx=5)
            
            # 2. Restaurar aba Voluntários (se não estiver lá) - Posição 1 (logo após Login)
            if str(self.tab_voluntarios) not in self.notebook.tabs():
                self.notebook.insert(1, self.tab_voluntarios, text="Voluntários")

            # 3. Restaurar aba Matching (se não estiver lá) - Vai para o final
            if str(self.tab_matching) not in self.notebook.tabs():
                self.notebook.add(self.tab_matching, text="Matching")
            
            # Limpar e ir para demandas
            self.email_entry.delete(0, tk.END)
            self.senha_entry.delete(0, tk.END)
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
        
        # === LÓGICA VOLUNTÁRIO: ESCONDER COISAS ===
        
        # 1. Esconde botão criar demanda
        self.btn_criar_demanda.pack_forget()
        
        # 2. Esconde aba de Matching
        self.notebook.forget(self.tab_matching)
        
        # 3. Esconde aba de Voluntários (NOVO)
        self.notebook.forget(self.tab_voluntarios)

        # Limpar e ir para demandas
        self.email_entry.delete(0, tk.END)
        self.senha_entry.delete(0, tk.END)
        self.atualizar_listas()
        self.notebook.select(self.tab_demandas)
    
    def registrar(self):
        """Registra novo voluntário."""  # Docstring do método
        nome = self.reg_nome.get().strip()  # Obtém o nome digitado e remove espaços em branco
        email = self.reg_email.get().strip()  # Obtém o email digitado e remove espaços em branco
        senha = self.reg_senha.get().strip()  # Obtém a senha digitada e remove espaços em branco
        confirmar_senha = self.reg_confirmar_senha.get().strip()  # Obtém a confirmação de senha digitada e remove espaços em branco
        
        # Coletar habilidades selecionadas
        habilidades_ids = [hab_id for hab_id, var in self.reg_habilidades_vars.items() if var.get()]  # Cria uma lista com os IDs das habilidades selecionadas usando list comprehension
        
        # Validações
        if not nome:  # Verifica se o nome está vazio
            messagebox.showerror("Erro", "Digite seu nome completo")  # Exibe mensagem de erro
            self.reg_nome.focus()  # Foca no campo de nome
            return  # Retorna para interromper a execução
        
        if not email:  # Verifica se o email está vazio
            messagebox.showerror("Erro", "Digite seu email")  # Exibe mensagem de erro
            self.reg_email.focus()  # Foca no campo de email
            return  # Retorna para interromper a execução
        
        # Validação rigorosa de email
        email_valido, msg_email = auth.validar_email(email)  # Valida o formato do email
        if not email_valido:  # Verifica se o email é inválido
            messagebox.showerror("Erro de Validação", msg_email)  # Exibe mensagem de erro com detalhes
            self.reg_email.focus()  # Foca no campo de email
            return  # Retorna para interromper a execução
        
        if not senha:  # Verifica se a senha está vazia
            messagebox.showerror("Erro", "Digite uma senha")  # Exibe mensagem de erro
            self.reg_senha.focus()  # Foca no campo de senha
            return  # Retorna para interromper a execução
        
        if not confirmar_senha:  # Verifica se a confirmação de senha está vazia
            messagebox.showerror("Erro", "Confirme sua senha")  # Exibe mensagem de erro
            self.reg_confirmar_senha.focus()  # Foca no campo de confirmar senha
            return  # Retorna para interromper a execução
        
        # Verificar se as senhas coincidem
        if senha != confirmar_senha:  # Verifica se as senhas não coincidem
            messagebox.showerror("Erro", "As senhas não coincidem. Por favor, digite novamente.")  # Exibe mensagem de erro
            self.reg_senha.delete(0, tk.END)  # Limpa o campo de senha
            self.reg_confirmar_senha.delete(0, tk.END)  # Limpa o campo de confirmar senha
            self.reg_senha.focus()  # Foca no campo de senha
            return  # Retorna para interromper a execução
        
        # Validação de senha forte
        senha_valida, msg_senha = auth.validar_senha_forte(senha)  # Valida se a senha atende aos critérios de segurança
        if not senha_valida:  # Verifica se a senha é inválida
            messagebox.showerror("Erro de Segurança", msg_senha)  # Exibe mensagem de erro com detalhes
            self.reg_senha.delete(0, tk.END)  # Limpa o campo de senha
            self.reg_confirmar_senha.delete(0, tk.END)  # Limpa o campo de confirmar senha
            self.reg_senha.focus()  # Foca no campo de senha
            return  # Retorna para interromper a execução
        
        if not habilidades_ids:  # Verifica se nenhuma habilidade foi selecionada
            messagebox.showerror("Erro", "Selecione pelo menos uma habilidade")  # Exibe mensagem de erro
            return  # Retorna para interromper a execução
        
        # Verifica se não é email de admin
        if auth.ADMIN_EMAIL and email == auth.ADMIN_EMAIL:  # Verifica se o email é do administrador
            messagebox.showerror("Erro", "Este email é reservado para administrador")  # Exibe mensagem de erro
            self.reg_email.focus()  # Foca no campo de email
            return  # Retorna para interromper a execução
        
        if database.buscar_usuario_por_email(email):  # Verifica se o email já está cadastrado
            messagebox.showerror("Erro", "Este email já está cadastrado")  # Exibe mensagem de erro
            self.reg_email.focus()  # Foca no campo de email
            return  # Retorna para interromper a execução
        
        try:  # Inicia um bloco try para capturar exceções
            uid = database.criar_usuario(nome, email, auth.hash_senha(senha))  # Cria um novo usuário no banco de dados e obtém o ID
            database.criar_voluntario(uid, habilidades_ids)  # Cria o perfil de voluntário com as habilidades selecionadas
            messagebox.showinfo("Sucesso", f"Cadastro realizado com sucesso!\n\nBem-vindo, {nome}!\n\nFaça login para continuar.")  # Exibe mensagem de sucesso
            # Limpar campos
            self.reg_nome.delete(0, tk.END)  # Limpa o campo de nome
            self.reg_email.delete(0, tk.END)  # Limpa o campo de email
            self.reg_senha.delete(0, tk.END)  # Limpa o campo de senha
            self.reg_confirmar_senha.delete(0, tk.END)  # Limpa o campo de confirmar senha
            # Limpar checkboxes
            for var in self.reg_habilidades_vars.values():  # Itera sobre todas as variáveis booleanas das habilidades
                var.set(False)  # Desmarca todos os checkboxes
            # Focar no campo de email do login
            self.email_entry.focus()  # Foca no campo de email da aba de login
        except Exception as e:  # Captura qualquer exceção que ocorrer
            messagebox.showerror("Erro", f"Erro ao cadastrar: {str(e)}")  # Exibe mensagem de erro com detalhes da exceção
    
    def criar_demanda(self):
        """Cria nova demanda (apenas admin)."""  # Docstring do método
        if not self.usuario_atual or self.usuario_atual.get('papel') != 'admin':  # Verifica se não há usuário logado ou se não é administrador
            messagebox.showerror("Erro", "Apenas administradores podem criar demandas")  # Exibe mensagem de erro
            return  # Retorna para interromper a execução
        
        # Criar janela de diálogo
        dialog = tk.Toplevel(self.root)  # Cria uma janela de diálogo (top-level) filha da janela principal
        dialog.title("Nova Demanda")  # Define o título da janela de diálogo
        dialog.geometry("500x500")  # Define o tamanho da janela de diálogo
        dialog.transient(self.root)  # Define a janela como transitória (fica sempre acima da janela principal)
        dialog.grab_set()  # Faz a janela capturar todos os eventos (modal)
        
        # Título
        ttk.Label(dialog, text="Título da demanda:", font=("Arial", 10, "bold")).pack(pady=10)  # Cria um label "Título da demanda:" em negrito
        titulo_entry = ttk.Entry(dialog, width=50)  # Cria um campo de entrada para o título com largura de 50 caracteres
        titulo_entry.pack(pady=5)  # Empacota o campo de entrada com margem vertical de 5 pixels
        
        # Habilidades
        ttk.Label(dialog, text="Selecione as habilidades necessárias:", font=("Arial", 10, "bold")).pack(pady=10)  # Cria um label "Selecione as habilidades necessárias:" em negrito
        
        # Frame para checkboxes com scroll
        hab_frame = ttk.Frame(dialog)  # Cria um frame para conter as habilidades
        hab_frame.pack(fill="both", expand=True, padx=10, pady=5)  # Empacota o frame preenchendo todo o espaço disponível
        
        canvas = tk.Canvas(hab_frame, height=250)  # Cria um canvas para permitir scroll com altura de 250 pixels
        scrollbar = ttk.Scrollbar(hab_frame, orient="vertical", command=canvas.yview)  # Cria uma barra de rolagem vertical para o canvas
        scrollable = ttk.Frame(canvas)  # Cria um frame rolável dentro do canvas
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))  # Atualiza a região de scroll quando o frame muda de tamanho
        canvas.create_window((0, 0), window=scrollable, anchor="nw")  # Cria uma janela no canvas para conter o frame rolável
        canvas.configure(yscrollcommand=scrollbar.set)  # Configura o canvas para atualizar a posição da scrollbar
        
        demanda_habs_vars = {}  # Inicializa um dicionário vazio para armazenar variáveis booleanas das habilidades
        habilidades = database.listar_habilidades()  # Busca todas as habilidades do banco de dados
        
        for idx, hab in enumerate(habilidades):  # Itera sobre cada habilidade com seu índice
            var = tk.BooleanVar()  # Cria uma variável booleana para cada habilidade
            demanda_habs_vars[hab['id']] = var  # Armazena a variável no dicionário usando o ID da habilidade como chave
            row = idx // 2  # Calcula a linha na grade (2 colunas)
            col = idx % 2  # Calcula a coluna na grade (resto da divisão por 2)
            ttk.Checkbutton(scrollable, text=hab['nome'], variable=var).grid(row=row, column=col, sticky="w", padx=5, pady=2)  # Cria um checkbox para a habilidade e posiciona na grade
        
        canvas.pack(side="left", fill="both", expand=True)  # Empacota o canvas à esquerda, preenchendo todo o espaço
        scrollbar.pack(side="right", fill="y")  # Empacota a scrollbar à direita, preenchendo verticalmente
        
        def salvar_demanda():  # Define função interna para salvar a demanda
            titulo = titulo_entry.get().strip()  # Obtém o título digitado e remove espaços em branco
            habilidades_ids = [hab_id for hab_id, var in demanda_habs_vars.items() if var.get()]  # Cria uma lista com os IDs das habilidades selecionadas
            
            if not titulo:  # Verifica se o título está vazio
                messagebox.showerror("Erro", "Digite o título da demanda")  # Exibe mensagem de erro
                return  # Retorna para interromper a execução
            
            if not habilidades_ids:  # Verifica se nenhuma habilidade foi selecionada
                messagebox.showerror("Erro", "Selecione pelo menos uma habilidade")  # Exibe mensagem de erro
                return  # Retorna para interromper a execução
            
            try:  # Inicia um bloco try para capturar exceções
                database.criar_demanda(titulo, habilidades_ids)  # Cria a demanda no banco de dados
                messagebox.showinfo("Sucesso", "Demanda criada com sucesso!")  # Exibe mensagem de sucesso
                dialog.destroy()  # Fecha a janela de diálogo
                self.atualizar_demandas()  # Atualiza a lista de demandas
            except Exception as e:  # Captura qualquer exceção que ocorrer
                messagebox.showerror("Erro", f"Erro ao criar demanda: {str(e)}")  # Exibe mensagem de erro com detalhes da exceção
        
        ttk.Button(dialog, text="Criar", command=salvar_demanda).pack(pady=10)  # Cria um botão "Criar" que chama a função salvar_demanda quando clicado
    
    def atualizar_voluntarios(self):
        """Atualiza lista de voluntários."""  # Docstring do método
        for item in self.vol_tree.get_children():  # Itera sobre todos os itens filhos da treeview
            self.vol_tree.delete(item)  # Deleta cada item da treeview
        
        try:  # Inicia um bloco try para capturar exceções
            voluntarios = database.listar_voluntarios()  # Busca todos os voluntários do banco de dados
            for vol in voluntarios:  # Itera sobre cada voluntário
                habilidades_str = ", ".join(vol.get('habilidades_nomes', []))  # Cria uma string com os nomes das habilidades separados por vírgula
                self.vol_tree.insert("", "end", values=(  # Insere uma nova linha na treeview
                    vol.get('nome', ''),  # Obtém o nome do voluntário ou string vazia se não existir
                    vol.get('email', ''),  # Obtém o email do voluntário ou string vazia se não existir
                    habilidades_str  # Insere a string de habilidades
                ))
        except Exception as e:  # Captura qualquer exceção que ocorrer
            messagebox.showerror("Erro", f"Erro ao carregar voluntários: {str(e)}")  # Exibe mensagem de erro com detalhes da exceção
    
    def atualizar_demandas(self):
        """Atualiza lista de demandas."""  # Docstring do método
        for item in self.dem_tree.get_children():  # Itera sobre todos os itens filhos da treeview
            self.dem_tree.delete(item)  # Deleta cada item da treeview
        
        try:  # Inicia um bloco try para capturar exceções
            demandas = database.listar_demandas()  # Busca todas as demandas do banco de dados
            for dem in demandas:  # Itera sobre cada demanda
                self.dem_tree.insert("", "end", values=(  # Insere uma nova linha na treeview
                    dem.get('titulo', ''),  # Obtém o título da demanda ou string vazia se não existir
                    dem.get('habilidades_requeridas', '')  # Obtém as habilidades requeridas ou string vazia se não existir
                ))
        except Exception as e:  # Captura qualquer exceção que ocorrer
            messagebox.showerror("Erro", f"Erro ao carregar demandas: {str(e)}")  # Exibe mensagem de erro com detalhes da exceção
    
    def atualizar_combo_matching(self):
        """Atualiza combo de demandas para matching."""  # Docstring do método
        if not self.usuario_atual:  # Verifica se não há usuário logado
            return  # Retorna para interromper a execução
        try:  # Inicia um bloco try para capturar exceções
            demandas = database.listar_demandas()  # Busca todas as demandas do banco de dados
            if demandas:  # Verifica se há demandas
                valores = [f"{d['id']} - {d['titulo']}" for d in demandas]  # Cria uma lista de strings no formato "ID - Título" para cada demanda
                self.match_combo['values'] = valores  # Define os valores do combobox
                if valores and not self.match_combo.get():  # Verifica se há valores e se o combobox está vazio
                    self.match_combo.current(0)  # Seleciona o primeiro item do combobox
            else:  # Se não houver demandas
                self.match_combo['values'] = []  # Define os valores do combobox como lista vazia
                self.match_combo.set("")  # Limpa o valor selecionado do combobox
        except Exception as e:  # Captura qualquer exceção que ocorrer
            print(f"Erro ao atualizar combo matching: {e}")  # Imprime o erro no console
    
    def gerar_matches(self):
        """Gera matches para uma demanda."""  # Docstring do método
        if not self.usuario_atual:  # Verifica se não há usuário logado
            messagebox.showwarning("Acesso Restrito", "Faça login para usar o sistema de matching")  # Exibe mensagem de aviso
            self.notebook.select(self.tab_login)  # Seleciona a aba de login
            return  # Retorna para interromper a execução
        
        selecao = self.match_combo.get()  # Obtém a seleção do combobox
        if not selecao:  # Verifica se nenhuma demanda foi selecionada
            messagebox.showwarning("Aviso", "Selecione uma demanda primeiro")  # Exibe mensagem de aviso
            return  # Retorna para interromper a execução
        
        try:  # Inicia um bloco try para capturar exceções
            demanda_id = int(selecao.split(" - ")[0])  # Extrai o ID da demanda da string selecionada (formato "ID - Título")
            demanda = database.buscar_demanda_por_id(demanda_id)  # Busca a demanda no banco de dados pelo ID
            if not demanda:  # Verifica se a demanda não foi encontrada
                messagebox.showerror("Erro", "Demanda não encontrada")  # Exibe mensagem de erro
                return  # Retorna para interromper a execução
            
            # Mostrar informações da demanda
            demanda_habs = ", ".join(demanda.get('habilidades_nomes', []))  # Cria uma string com os nomes das habilidades necessárias separados por vírgula
            
            matches = encontrar_matches(demanda)  # Encontra os matches (voluntários compatíveis) para a demanda
            
            self.match_text.delete("1.0", tk.END)  # Limpa todo o conteúdo do widget de texto
            
            # Cabeçalho com informações da demanda
            resultado = "=" * 60 + "\n"  # Cria uma linha de separação com 60 caracteres "="
            resultado += f"DEMANDA: {demanda.get('titulo', 'N/A')}\n"  # Adiciona o título da demanda ao resultado
            resultado += f"HABILIDADES NECESSÁRIAS: {demanda_habs}\n"  # Adiciona as habilidades necessárias ao resultado
            resultado += "=" * 60 + "\n\n"  # Adiciona outra linha de separação e duas quebras de linha
            
            if not matches:  # Verifica se não foram encontrados matches
                resultado += "Nenhum voluntário encontrado com as habilidades necessárias.\n\n"  # Adiciona mensagem de nenhum match encontrado
                resultado += "Sugestão: Verifique se há voluntários cadastrados com essas habilidades."  # Adiciona sugestão ao resultado
                self.match_text.insert("1.0", resultado)  # Insere o resultado no widget de texto
                return  # Retorna para interromper a execução
            
            resultado += f"ENCONTRADOS {len(matches)} VOLUNTÁRIO(S) COMPATÍVEL(IS):\n\n"  # Adiciona o número de matches encontrados ao resultado
            
            for idx, match in enumerate(matches, 1):  # Itera sobre cada match com índice começando em 1
                vol = match['voluntario']  # Obtém os dados do voluntário do match
                habilidades_str = ", ".join(vol.get('habilidades_nomes', []))  # Cria uma string com todas as habilidades do voluntário
                habilidades_comuns = match.get('habilidades_comuns', [])  # Obtém a lista de habilidades comuns entre voluntário e demanda
                habilidades_comuns_str = ", ".join(habilidades_comuns) if habilidades_comuns else "Nenhuma"  # Cria string com habilidades comuns ou "Nenhuma" se não houver
                
                # Calcular porcentagem de match
                porcentagem = match['score'] * 100  # Calcula a porcentagem de compatibilidade multiplicando o score por 100
                
                resultado += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"  # Adiciona linha de separação visual
                resultado += f"MATCH #{idx} - COMPATIBILIDADE: {porcentagem:.0f}%\n"  # Adiciona o número do match e a porcentagem de compatibilidade
                resultado += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"  # Adiciona outra linha de separação visual
                resultado += f"👤 Nome: {vol.get('nome', 'N/A')}\n"  # Adiciona o nome do voluntário ao resultado
                resultado += f"📧 Email: {vol.get('email', 'N/A')}\n"  # Adiciona o email do voluntário ao resultado
                resultado += f"🛠️  Todas as Habilidades: {habilidades_str}\n"  # Adiciona todas as habilidades do voluntário ao resultado
                resultado += f"✅ Habilidades que Correspondem: {habilidades_comuns_str}\n"  # Adiciona as habilidades comuns ao resultado
                resultado += f"⭐ Score: {match['score']:.2f} ({porcentagem:.0f}% de compatibilidade)\n"  # Adiciona o score e porcentagem ao resultado
                resultado += "\n"  # Adiciona uma linha em branco para separar matches
            
            self.match_text.insert("1.0", resultado)  # Insere todo o resultado no widget de texto
        except Exception as e:  # Captura qualquer exceção que ocorrer
            messagebox.showerror("Erro", f"Erro ao gerar matches: {str(e)}")  # Exibe mensagem de erro com detalhes da exceção
    
    def atualizar_listas(self):
        """Atualiza todas as listas."""  # Docstring do método
        if not self.usuario_atual:  # Verifica se não há usuário logado
            return  # Retorna para interromper a execução
        try:  # Inicia um bloco try para capturar exceções
            self.atualizar_voluntarios()  # Chama o método para atualizar a lista de voluntários
            self.atualizar_demandas()  # Chama o método para atualizar a lista de demandas
            self.atualizar_combo_matching()  # Chama o método para atualizar o combobox de matching
        except Exception as e:  # Captura qualquer exceção que ocorrer
            print(f"Erro ao atualizar listas: {e}")  # Imprime o erro no console
    
    def run(self):
        """Inicia a aplicação."""  # Docstring do método
        self.root.mainloop()  # Inicia o loop principal da interface gráfica, mantendo a janela aberta e respondendo a eventos

