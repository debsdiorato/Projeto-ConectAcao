from banco.database import listar_voluntarios
import re

def normalize(s: str): #transforma o texto em uma lista de habilidades:
    if not s:
        return []
    
    return [x.strip().lower() for x in re.split(r",|;", s) if x.strip()]

def score(voluntario: dict, demanda: dict): #calcula o quanto o voluntário combina com a demanda
    v = set(normalize(voluntario.get("habilidades", "")))
    d = set(normalize(demanda.get("habilidades_requeridas", "")))
    if not d:
        return 0.0
    common = v.intersection(d)
    return round(len(common) / len(d), 3)

def get_matches_for_demand(demanda: dict, top_n: int = 5): #retorna os melhores voluntários
    voluntarios = listar_voluntarios()
    results = []
    for v in voluntarios:
        s = score(v, demanda)
        if s > 0:
            results.append((s, v))
    results.sort(key=lambda x: x[0], reverse=True)
    return [{"score": s, "voluntario": v} for s, v in results[:top_n]]