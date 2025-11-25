"""Módulo de matching - encontra voluntários para demandas."""
import database


def calcular_score(voluntario, demanda):
    """Calcula o score de match entre voluntário e demanda."""
    # Obter IDs das habilidades do voluntário
    vol_habs_ids = set()
    if 'habilidades' in voluntario:
        vol_habs_ids = {h['id'] for h in voluntario['habilidades']}
    
    # Obter IDs das habilidades da demanda
    dem_habs_ids = set()
    if 'habilidades' in demanda:
        dem_habs_ids = {h['id'] for h in demanda['habilidades']}
    
    if not dem_habs_ids:
        return 0.0, []
    
    # Score baseado na interseção de habilidades
    comum = vol_habs_ids.intersection(dem_habs_ids)
    score = len(comum) / len(dem_habs_ids)
    
    # Obter nomes das habilidades correspondentes
    habilidades_comuns = []
    if 'habilidades' in voluntario:
        for hab in voluntario['habilidades']:
            if hab['id'] in comum:
                habilidades_comuns.append(hab['nome'])
    
    return round(score, 3), habilidades_comuns


def encontrar_matches(demanda, top_n=10):
    """Encontra os melhores matches para uma demanda."""
    voluntarios = database.listar_voluntarios()
    matches = []
    
    for vol in voluntarios:
        score, habilidades_comuns = calcular_score(vol, demanda)
        if score > 0:
            matches.append({
                'score': score,
                'voluntario': vol,
                'habilidades_comuns': habilidades_comuns
            })
    
    # Ordena por score (maior primeiro)
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    return matches[:top_n]

