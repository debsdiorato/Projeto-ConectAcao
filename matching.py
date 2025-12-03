"""Módulo de matching - encontra voluntários para demandas."""  # Docstring do módulo
import database  # Importa o módulo database para acessar funções de banco de dados


def calcular_score(voluntario, demanda):
    """Calcula o score de match entre voluntário e demanda."""  # Docstring da função
    # Obter IDs das habilidades do voluntário
    vol_habs_ids = set()  # Cria um conjunto vazio para armazenar os IDs das habilidades do voluntário
    if 'habilidades' in voluntario:  # Verifica se o voluntário tem a chave 'habilidades'
        vol_habs_ids = {h['id'] for h in voluntario['habilidades']}  # Cria um conjunto com os IDs das habilidades do voluntário usando comprehension
    
    # Obter IDs das habilidades da demanda
    dem_habs_ids = set()  # Cria um conjunto vazio para armazenar os IDs das habilidades da demanda
    if 'habilidades' in demanda:  # Verifica se a demanda tem a chave 'habilidades'
        dem_habs_ids = {h['id'] for h in demanda['habilidades']}  # Cria um conjunto com os IDs das habilidades da demanda usando comprehension
    
    if not dem_habs_ids:  # Verifica se não há habilidades na demanda
        return 0.0, []  # Retorna score 0 e lista vazia se não houver habilidades na demanda
    
    # Score baseado na interseção de habilidades
    comum = vol_habs_ids.intersection(dem_habs_ids)  # Calcula a interseção entre as habilidades do voluntário e da demanda
    score = len(comum) / len(dem_habs_ids)  # Calcula o score dividindo o número de habilidades comuns pelo total de habilidades necessárias
    
    # Obter nomes das habilidades correspondentes
    habilidades_comuns = []  # Cria uma lista vazia para armazenar os nomes das habilidades comuns
    if 'habilidades' in voluntario:  # Verifica se o voluntário tem a chave 'habilidades'
        for hab in voluntario['habilidades']:  # Itera sobre cada habilidade do voluntário
            if hab['id'] in comum:  # Verifica se o ID da habilidade está no conjunto de habilidades comuns
                habilidades_comuns.append(hab['nome'])  # Adiciona o nome da habilidade à lista de habilidades comuns
    
    return round(score, 3), habilidades_comuns  # Retorna o score arredondado para 3 casas decimais e a lista de habilidades comuns


def encontrar_matches(demanda, top_n=10):
    """Encontra os melhores matches para uma demanda."""  # Docstring da função
    voluntarios = database.listar_voluntarios()  # Busca todos os voluntários do banco de dados
    matches = []  # Cria uma lista vazia para armazenar os matches encontrados
    
    for vol in voluntarios:  # Itera sobre cada voluntário da lista
        score, habilidades_comuns = calcular_score(vol, demanda)  # Calcula o score de match entre o voluntário e a demanda
        if score > 0:  # Verifica se o score é maior que zero (há pelo menos uma habilidade em comum)
            matches.append({  # Adiciona um dicionário com informações do match à lista
                'score': score,  # Armazena o score calculado
                'voluntario': vol,  # Armazena os dados do voluntário
                'habilidades_comuns': habilidades_comuns  # Armazena a lista de habilidades comuns
            })
    
    # Ordena por score (maior primeiro)
    matches.sort(key=lambda x: x['score'], reverse=True)  # Ordena a lista de matches pelo score em ordem decrescente
    
    return matches[:top_n]  # Retorna apenas os top_n melhores matches (padrão 10)

