#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Aplicação principal - ConectAção."""
import database
import gui


def main():
    """Função principal."""
    # Inicializa banco de dados
    database.init_db()
    
    # Inicia interface gráfica
    app = gui.App()
    app.run()


if __name__ == "__main__":
    main()

