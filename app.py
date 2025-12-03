#!/usr/bin/env python  # Define o interpretador Python a ser usado (shebang)
# -*- coding: utf-8 -*-  # Define a codificação do arquivo como UTF-8
"""Aplicação principal - ConectAção."""  # Docstring do módulo
import database  # Importa o módulo database para operações com banco de dados
import gui  # Importa o módulo gui para interface gráfica


def main():
    """Função principal."""  # Docstring da função
    # Inicializa banco de dados
    database.init_db()  # Chama a função init_db do módulo database para inicializar o banco de dados
    
    # Inicia interface gráfica
    app = gui.App()  # Cria uma instância da classe App do módulo gui
    app.run()  # Executa o método run() da instância app para iniciar a interface gráfica


if __name__ == "__main__":  # Verifica se o script está sendo executado diretamente (não importado)
    main()  # Chama a função main() quando o script é executado diretamente

