from __future__ import annotations

from copy import deepcopy


INDICADORES = [
    "Biodiversidade",
    "Fertilidade do solo",
    "Agua disponivel",
    "Producao agricola",
    "Equilibrio ecologico",
    "Servicos ecossistemicos",
    "Pressao ambiental",
    "Sustentabilidade geral",
]

INDICE_SUSTENTABILIDADE = "Sustentabilidade geral"

FUNCOES_DOS_PAPEIS = {
    "Agricultor": [
        "Organiza o manejo humano do agroecossistema.",
        "Define a diversidade do plantio, a cobertura do solo e a intensidade de intervencao.",
        "Influencia diretamente producao, biodiversidade, solo, agua e pressao ambiental.",
    ],
    "Solo": [
        "Sustenta as raizes, armazena agua e abriga organismos vivos.",
        "Participa da ciclagem de nutrientes e da decomposicao da materia organica.",
        "Determina parte importante da fertilidade, infiltracao e resiliencia do sistema.",
    ],
    "Agua": [
        "Regula a disponibilidade hidrica para plantas, solo e organismos.",
        "Conecta infiltracao, escoamento superficial e conservacao dos recursos naturais.",
        "Influencia producao agricola, fertilidade e pressao ambiental.",
    ],
    "Planta cultivada": [
        "Transforma energia solar em biomassa agricola.",
        "Demanda agua e nutrientes, mas tambem pode alimentar polinizadores.",
        "Mostra a relacao entre producao, fluxo de energia e equilibrio ecologico.",
    ],
    "Planta espontanea": [
        "Amplia a cobertura viva e pode proteger o solo.",
        "Oferece habitat e alimento para organismos, mas tambem pode competir com a cultura.",
        "Ajuda a discutir biodiversidade funcional no agroecossistema.",
    ],
    "Polinizador": [
        "Realiza a polinizacao e aumenta servicos ecossistemicos.",
        "Depende de flores, vegetacao espontanea e habitat adequado.",
        "Conecta biodiversidade, producao agricola e equilibrio ecologico.",
    ],
    "Decompositor": [
        "Transforma residuos organicos em nutrientes disponiveis.",
        "Fecha ciclos de materia e fortalece a vida do solo.",
        "Depende de solo saudavel, umidade e materia organica.",
    ],
    "Predador natural": [
        "Controla populacoes de pragas e reduz desequilibrios biologicos.",
        "Depende de habitat e diversidade para permanecer no sistema.",
        "Fortalece o equilibrio ecologico e reduz a necessidade de intervencoes agressivas.",
    ],
    "Comunidade rural": [
        "Representa escolhas sociais, valores e pressoes sobre o manejo.",
        "Pode apoiar conservacao ou pressionar por aumento rapido da producao.",
        "Mostra que agroecossistemas tambem sao sistemas sociais.",
    ],
    "Orgao ambiental": [
        "Orienta, regula e incentiva boas praticas ambientais.",
        "Protege areas sensiveis, agua e biodiversidade.",
        "Ajuda a equilibrar uso produtivo e conservacao do agroecossistema.",
    ],
}

ESTADO_INICIAL = {
    "rodada_atual": 1,
    "max_rodadas": 5,
    "rodada_inicio": "",
    "duracao_rodada_seg": 240,
    "Biodiversidade": 72,
    "Fertilidade do solo": 70,
    "Agua disponivel": 68,
    "Producao agricola": 45,
    "Equilibrio ecologico": 72,
    "Servicos ecossistemicos": 68,
    "Pressao ambiental": 30,
    "Sustentabilidade geral": 70,
}

PAPEIS = {
    "Agricultor": {
        "Plantar monocultura": {
            "impactos": {"Producao agricola": 12, "Biodiversidade": -10, "Equilibrio ecologico": -8, "Pressao ambiental": 8},
            "feedback": "A monocultura amplia a biomassa cultivada no curto prazo, mas simplifica o habitat e reduz conexoes ecologicas.",
        },
        "Plantar consorcio": {
            "impactos": {"Biodiversidade": 8, "Equilibrio ecologico": 7, "Producao agricola": 5, "Servicos ecossistemicos": 5},
            "feedback": "O consorcio cria diversidade funcional e distribui melhor o uso de agua, luz e nutrientes.",
        },
        "Manter cobertura do solo": {
            "impactos": {"Fertilidade do solo": 8, "Agua disponivel": 6, "Sustentabilidade geral": 7, "Pressao ambiental": -5},
            "feedback": "A cobertura protege contra erosao, conserva umidade e alimenta a vida do solo.",
        },
        "Remover vegetacao": {
            "impactos": {"Producao agricola": 7, "Biodiversidade": -9, "Agua disponivel": -6, "Equilibrio ecologico": -7, "Pressao ambiental": 7},
            "feedback": "Remover vegetacao pode abrir area produtiva, mas enfraquece habitats e ciclos de agua e nutrientes.",
        },
        "Aplicar defensivo": {
            "impactos": {"Producao agricola": 8, "Biodiversidade": -8, "Servicos ecossistemicos": -7, "Equilibrio ecologico": -6, "Pressao ambiental": 8},
            "feedback": "O defensivo pode reduzir danos imediatos, mas tambem afeta organismos beneficos e servicos ecossistemicos.",
        },
        "Reduzir revolvimento do solo": {
            "impactos": {"Fertilidade do solo": 7, "Agua disponivel": 5, "Equilibrio ecologico": 5, "Sustentabilidade geral": 6},
            "feedback": "Menos revolvimento preserva estrutura, porosidade e organismos do solo.",
        },
    },
    "Solo": {
        "Aumentar materia organica": {
            "impactos": {"Fertilidade do solo": 10, "Agua disponivel": 5, "Sustentabilidade geral": 7, "Servicos ecossistemicos": 4},
            "feedback": "Materia organica melhora estrutura, retencao de agua e disponibilidade gradual de nutrientes.",
        },
        "Sofrer compactacao": {
            "impactos": {"Fertilidade do solo": -8, "Agua disponivel": -8, "Producao agricola": -5, "Pressao ambiental": 6},
            "feedback": "A compactacao reduz porosidade, limita raizes e dificulta infiltracao de agua.",
        },
        "Liberar nutrientes": {
            "impactos": {"Fertilidade do solo": 6, "Producao agricola": 5, "Servicos ecossistemicos": 3},
            "feedback": "Nutrientes disponiveis conectam decomposicao, solo e crescimento vegetal.",
        },
        "Perder fertilidade": {
            "impactos": {"Fertilidade do solo": -10, "Producao agricola": -6, "Sustentabilidade geral": -7, "Pressao ambiental": 5},
            "feedback": "A perda de fertilidade mostra como o manejo pode romper ciclos de nutrientes.",
        },
        "Aumentar infiltracao": {
            "impactos": {"Agua disponivel": 8, "Fertilidade do solo": 4, "Sustentabilidade geral": 5, "Pressao ambiental": -4},
            "feedback": "Boa infiltracao reduz escoamento superficial e abastece agua no sistema.",
        },
    },
    "Agua": {
        "Aumentar disponibilidade hidrica": {
            "impactos": {"Agua disponivel": 10, "Producao agricola": 5, "Servicos ecossistemicos": 4},
            "feedback": "Agua disponivel sustenta plantas, microrganismos e regulacao do agroecossistema.",
        },
        "Reduzir disponibilidade hidrica": {
            "impactos": {"Agua disponivel": -10, "Producao agricola": -6, "Sustentabilidade geral": -5},
            "feedback": "A escassez hidrica pressiona plantas, solo e relacoes biologicas.",
        },
        "Favorecer infiltracao": {
            "impactos": {"Agua disponivel": 7, "Fertilidade do solo": 4, "Pressao ambiental": -4, "Equilibrio ecologico": 3},
            "feedback": "A infiltracao mantem agua no sistema e reduz perdas por enxurrada.",
        },
        "Gerar escoamento superficial": {
            "impactos": {"Agua disponivel": -7, "Fertilidade do solo": -6, "Pressao ambiental": 7, "Sustentabilidade geral": -5},
            "feedback": "O escoamento remove solo e nutrientes, enfraquecendo a resiliencia do sistema.",
        },
    },
    "Planta cultivada": {
        "Aumentar producao de biomassa": {
            "impactos": {"Producao agricola": 9, "Servicos ecossistemicos": 3, "Agua disponivel": -3},
            "feedback": "A biomassa cultivada e uma entrada de energia biologica, mas depende de agua e nutrientes.",
        },
        "Demandar mais nutrientes": {
            "impactos": {"Fertilidade do solo": -5, "Producao agricola": 4, "Sustentabilidade geral": -3},
            "feedback": "A demanda por nutrientes revela a dependencia da cultura em relacao ao solo vivo.",
        },
        "Demandar mais agua": {
            "impactos": {"Agua disponivel": -6, "Producao agricola": 4, "Pressao ambiental": 3},
            "feedback": "A cultura usa agua para crescer, mas o excesso de demanda pode desequilibrar o sistema.",
        },
        "Oferecer alimento aos polinizadores": {
            "impactos": {"Biodiversidade": 5, "Servicos ecossistemicos": 7, "Producao agricola": 4, "Equilibrio ecologico": 4},
            "feedback": "Flores e recursos alimentares mantem polinizadores ativos e conectam producao a biodiversidade.",
        },
    },
    "Planta espontanea": {
        "Proteger o solo": {
            "impactos": {"Fertilidade do solo": 6, "Agua disponivel": 5, "Sustentabilidade geral": 5},
            "feedback": "A vegetacao espontanea pode proteger o solo e ampliar a cobertura viva.",
        },
        "Competir com a cultura": {
            "impactos": {"Producao agricola": -6, "Biodiversidade": 3, "Agua disponivel": -3},
            "feedback": "A competicao mostra que uma mesma interacao pode ter beneficios e tensoes.",
        },
        "Aumentar biodiversidade": {
            "impactos": {"Biodiversidade": 8, "Equilibrio ecologico": 5, "Servicos ecossistemicos": 5},
            "feedback": "Mais especies ampliam nichos, habitats e estabilidade ecologica.",
        },
        "Servir de abrigo para insetos": {
            "impactos": {"Biodiversidade": 5, "Equilibrio ecologico": 6, "Servicos ecossistemicos": 4},
            "feedback": "Abrigos vegetais favorecem insetos beneficos, polinizadores e predadores naturais.",
        },
    },
    "Polinizador": {
        "Polinizar cultura": {
            "impactos": {"Producao agricola": 8, "Servicos ecossistemicos": 8, "Equilibrio ecologico": 4},
            "feedback": "A polinizacao conecta biodiversidade, servicos ecossistemicos e producao de alimentos.",
        },
        "Buscar alimento na vegetacao espontanea": {
            "impactos": {"Biodiversidade": 4, "Servicos ecossistemicos": 6, "Equilibrio ecologico": 4},
            "feedback": "Recursos fora da cultura mantem polinizadores presentes entre floradas.",
        },
        "Reduzir atividade por falta de habitat": {
            "impactos": {"Servicos ecossistemicos": -7, "Producao agricola": -5, "Biodiversidade": -4, "Equilibrio ecologico": -4},
            "feedback": "Sem habitat, os polinizadores reduzem sua atividade e o sistema perde conexoes.",
        },
        "Migrar": {
            "impactos": {"Servicos ecossistemicos": -6, "Biodiversidade": -5, "Producao agricola": -4},
            "feedback": "A migracao indica que o ambiente deixou de oferecer recursos suficientes.",
        },
    },
    "Decompositor": {
        "Decompor materia organica": {
            "impactos": {"Fertilidade do solo": 9, "Sustentabilidade geral": 6, "Servicos ecossistemicos": 5},
            "feedback": "Decompositores transformam residuos em nutrientes e fecham ciclos de materia.",
        },
        "Liberar nutrientes": {
            "impactos": {"Fertilidade do solo": 7, "Producao agricola": 4, "Servicos ecossistemicos": 4},
            "feedback": "A liberacao de nutrientes alimenta a cultura e depende da vida do solo.",
        },
        "Reduzir atividade por solo degradado": {
            "impactos": {"Fertilidade do solo": -7, "Servicos ecossistemicos": -5, "Sustentabilidade geral": -5},
            "feedback": "Solo degradado reduz a atividade biologica e enfraquece a ciclagem de nutrientes.",
        },
    },
    "Predador natural": {
        "Controlar pragas": {
            "impactos": {"Equilibrio ecologico": 8, "Producao agricola": 5, "Servicos ecossistemicos": 5},
            "feedback": "Predadores naturais regulam populacoes e reduzem desequilibrios biologicos.",
        },
        "Reduzir atividade por perda de habitat": {
            "impactos": {"Equilibrio ecologico": -7, "Producao agricola": -4, "Biodiversidade": -4},
            "feedback": "A perda de habitat reduz o controle biologico e aumenta a vulnerabilidade do agroecossistema.",
        },
        "Aumentar equilibrio biologico": {
            "impactos": {"Equilibrio ecologico": 8, "Biodiversidade": 4, "Sustentabilidade geral": 5},
            "feedback": "O equilibrio biologico nasce de relacoes entre predadores, presas, plantas e manejo.",
        },
    },
    "Comunidade rural": {
        "Apoiar praticas sustentaveis": {
            "impactos": {"Sustentabilidade geral": 8, "Servicos ecossistemicos": 5, "Pressao ambiental": -5},
            "feedback": "A dimensao social influencia as escolhas de manejo e a resiliencia do territorio.",
        },
        "Pressionar por maior producao": {
            "impactos": {"Producao agricola": 7, "Pressao ambiental": 7, "Biodiversidade": -4, "Sustentabilidade geral": -3},
            "feedback": "Buscar apenas producao pode aumentar pressao sobre solo, agua e biodiversidade.",
        },
        "Valorizar conservacao ambiental": {
            "impactos": {"Biodiversidade": 6, "Servicos ecossistemicos": 6, "Sustentabilidade geral": 6, "Pressao ambiental": -5},
            "feedback": "A valorizacao social da conservacao fortalece praticas de cuidado com o agroecossistema.",
        },
    },
    "Orgao ambiental": {
        "Fiscalizar mata ciliar": {
            "impactos": {"Pressao ambiental": -8, "Agua disponivel": 5, "Biodiversidade": 4, "Servicos ecossistemicos": 4},
            "feedback": "A mata ciliar protege cursos d'agua, habitats e servicos ecossistemicos.",
        },
        "Incentivar recuperacao ambiental": {
            "impactos": {"Biodiversidade": 6, "Equilibrio ecologico": 5, "Sustentabilidade geral": 6, "Pressao ambiental": -5},
            "feedback": "A recuperacao ambiental amplia resiliiencia e melhora funcoes ecologicas.",
        },
        "Aplicar restricao de uso": {
            "impactos": {"Pressao ambiental": -7, "Biodiversidade": 5, "Producao agricola": -3, "Sustentabilidade geral": 4},
            "feedback": "Restricoes de uso podem reduzir impactos e proteger areas sensiveis.",
        },
        "Orientar boas praticas": {
            "impactos": {"Sustentabilidade geral": 7, "Fertilidade do solo": 4, "Agua disponivel": 4, "Pressao ambiental": -4},
            "feedback": "Orientacao tecnica ajuda a alinhar producao, conservacao e funcionamento ecologico.",
        },
    },
}


def listar_papeis() -> list[str]:
    return list(PAPEIS.keys())


def acoes_do_papel(papel: str) -> list[str]:
    return list(PAPEIS.get(papel, {}).keys())


def funcoes_do_papel(papel: str) -> list[str]:
    return FUNCOES_DOS_PAPEIS.get(papel, [])


def impacto_da_acao(papel: str, acao: str) -> dict[str, int]:
    return deepcopy(PAPEIS.get(papel, {}).get(acao, {}).get("impactos", {}))


def feedback_da_acao(papel: str, acao: str) -> str:
    return PAPEIS.get(papel, {}).get(acao, {}).get("feedback", "")


def aplicar_impactos(estado: dict, impactos: list[dict[str, int]]) -> dict:
    novo_estado = deepcopy(estado)
    for impacto in impactos:
        for indicador, delta in impacto.items():
            if indicador in INDICADORES:
                novo_estado[indicador] = limitar(novo_estado.get(indicador, 0) + delta)
    novo_estado["Sustentabilidade geral"] = calcular_sustentabilidade(novo_estado)
    return novo_estado


def limitar(valor: int | float) -> int:
    return max(0, min(100, int(round(valor))))


def calcular_sustentabilidade(estado: dict) -> int:
    """Calcula o indice de sustentabilidade do agroecossistema, de 0 a 100."""
    positivos = [
        estado.get("Biodiversidade", 0),
        estado.get("Fertilidade do solo", 0),
        estado.get("Agua disponivel", 0),
        estado.get("Producao agricola", 0),
        estado.get("Equilibrio ecologico", 0),
        estado.get("Servicos ecossistemicos", 0),
        100 - estado.get("Pressao ambiental", 0),
    ]
    return limitar(sum(positivos) / len(positivos))


def resumo_rodada(estado: dict) -> str:
    sustentabilidade = estado.get("Sustentabilidade geral", 0)
    pressao = estado.get("Pressao ambiental", 0)
    if sustentabilidade >= 75 and pressao <= 35:
        return "O agroecossistema mostra alta resiliencia: diversidade, solo, agua e manejo estao trabalhando em conjunto."
    if sustentabilidade >= 55:
        return "O sistema segue funcional, mas algumas decisoes podem fortalecer ou enfraquecer seus fluxos ecologicos."
    return "O agroecossistema esta sob estresse: ha sinais de perda de resiliencia e simplificacao das relacoes ecologicas."
