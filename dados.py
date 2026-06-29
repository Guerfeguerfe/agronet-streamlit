from __future__ import annotations

import csv
from datetime import datetime
from io import StringIO
from pathlib import Path
from uuid import uuid4

from regras import ESTADO_INICIAL, INDICADORES


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
JOGADORES_CSV = DATA_DIR / "jogadores.csv"
DECISOES_CSV = DATA_DIR / "decisoes.csv"
ESTADO_CSV = DATA_DIR / "estado_sistema.csv"
HISTORICO_CSV = DATA_DIR / "historico_indicadores.csv"
SESSAO_CSV = DATA_DIR / "sessao_aula.csv"

JOGADORES_COLUNAS = ["id", "sessao_id", "nome", "matricula", "papel", "criado_em"]
DECISOES_COLUNAS = ["id", "sessao_id", "jogador_id", "nome", "matricula", "papel", "rodada", "acoes", "impactos", "feedback", "criado_em"]
ESTADO_COLUNAS = ["rodada_atual", "max_rodadas", "rodada_inicio", "duracao_rodada_seg", *INDICADORES]
HISTORICO_COLUNAS = ["momento", "sessao_id", "evento", "rodada_atual", "max_rodadas", "rodada_inicio", "duracao_rodada_seg", *INDICADORES]
SESSAO_COLUNAS = ["sessao_id", "nome_aula", "ativa", "criado_em"]


def inicializar_dados() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    criar_csv_se_nao_existir(JOGADORES_CSV, JOGADORES_COLUNAS)
    criar_csv_se_nao_existir(DECISOES_CSV, DECISOES_COLUNAS)
    criar_csv_se_nao_existir(SESSAO_CSV, SESSAO_COLUNAS)
    if not ESTADO_CSV.exists():
        salvar_estado(ESTADO_INICIAL)
    if not HISTORICO_CSV.exists():
        escrever_linhas(HISTORICO_CSV, HISTORICO_COLUNAS, [])
        registrar_historico("Estado inicial")


def criar_csv_se_nao_existir(caminho: Path, colunas: list[str]) -> None:
    if not caminho.exists():
        escrever_linhas(caminho, colunas, [])


def ler_linhas(caminho: Path) -> list[dict[str, str]]:
    if not caminho.exists():
        return []
    with caminho.open("r", encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def escrever_linhas(caminho: Path, colunas: list[str], linhas: list[dict]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        for linha in linhas:
            escritor.writerow({coluna: linha.get(coluna, "") for coluna in colunas})


def carregar_jogadores() -> list[dict[str, str]]:
    inicializar_dados()
    return ler_linhas(JOGADORES_CSV)


def carregar_decisoes() -> list[dict[str, str]]:
    inicializar_dados()
    return ler_linhas(DECISOES_CSV)


def carregar_historico() -> list[dict[str, str]]:
    inicializar_dados()
    return ler_linhas(HISTORICO_CSV)


def carregar_sessao() -> dict | None:
    inicializar_dados()
    sessoes = ler_linhas(SESSAO_CSV)
    for sessao in reversed(sessoes):
        if sessao.get("ativa") == "sim":
            return sessao
    return sessoes[-1] if sessoes else None


def buscar_sessao(sessao_id: str) -> dict | None:
    inicializar_dados()
    for sessao in reversed(ler_linhas(SESSAO_CSV)):
        if sessao.get("sessao_id") == sessao_id:
            return sessao
    return None


def criar_sessao(nome_aula: str, duracao_rodada_seg: int = 240) -> dict:
    sessao = {
        "sessao_id": uuid4().hex[:8],
        "nome_aula": nome_aula.strip() or f"Aula {agora()}",
        "ativa": "sim",
        "criado_em": agora(),
    }
    escrever_linhas(SESSAO_CSV, SESSAO_COLUNAS, [sessao])
    estado = ESTADO_INICIAL.copy()
    estado["rodada_inicio"] = agora()
    estado["duracao_rodada_seg"] = duracao_rodada_seg
    salvar_estado(estado)
    escrever_linhas(JOGADORES_CSV, JOGADORES_COLUNAS, [])
    escrever_linhas(DECISOES_CSV, DECISOES_COLUNAS, [])
    escrever_linhas(HISTORICO_CSV, HISTORICO_COLUNAS, [])
    registrar_historico("Sessao iniciada", sessao["sessao_id"])
    return sessao


def carregar_estado() -> dict:
    DATA_DIR.mkdir(exist_ok=True)
    if not ESTADO_CSV.exists():
        salvar_estado(ESTADO_INICIAL)
    linhas = ler_linhas(ESTADO_CSV)
    if not linhas:
        return ESTADO_INICIAL.copy()
    linha = linhas[-1]
    estado = {
        "rodada_atual": int(float(linha.get("rodada_atual") or ESTADO_INICIAL["rodada_atual"])),
        "max_rodadas": int(float(linha.get("max_rodadas") or ESTADO_INICIAL["max_rodadas"])),
        "rodada_inicio": linha.get("rodada_inicio") or agora(),
        "duracao_rodada_seg": int(float(linha.get("duracao_rodada_seg") or ESTADO_INICIAL["duracao_rodada_seg"])),
    }
    for indicador in INDICADORES:
        estado[indicador] = int(float(linha.get(indicador) or ESTADO_INICIAL[indicador]))
    return estado


def salvar_estado(estado: dict) -> None:
    escrever_linhas(ESTADO_CSV, ESTADO_COLUNAS, [estado])


def registrar_jogador(nome: str, matricula: str, papel: str, sessao_id: str) -> dict:
    jogadores = carregar_jogadores()
    for jogador in jogadores:
        if jogador.get("sessao_id") == sessao_id and jogador["matricula"].strip() == matricula.strip():
            return jogador

    jogador = {
        "id": str(uuid4()),
        "sessao_id": sessao_id,
        "nome": nome.strip(),
        "matricula": matricula.strip(),
        "papel": papel,
        "criado_em": agora(),
    }
    jogadores.append(jogador)
    escrever_linhas(JOGADORES_CSV, JOGADORES_COLUNAS, jogadores)
    return jogador


def buscar_jogador_por_matricula(matricula: str, sessao_id: str) -> dict | None:
    for jogador in carregar_jogadores():
        if jogador.get("sessao_id") == sessao_id and jogador["matricula"].strip() == matricula.strip():
            return jogador
    return None


def buscar_jogador_por_id(jogador_id: str, sessao_id: str) -> dict | None:
    for jogador in carregar_jogadores():
        if jogador.get("sessao_id") == sessao_id and jogador.get("id") == jogador_id:
            return jogador
    return None


def jogador_ja_decidiu(jogador_id: str, rodada: int) -> bool:
    for decisao in carregar_decisoes():
        if decisao["jogador_id"] == jogador_id and str(decisao["rodada"]) == str(rodada):
            return True
    return False


def registrar_decisao(jogador: dict, rodada: int, acoes: list[str], impactos: dict[str, int], feedback: str) -> None:
    decisoes = carregar_decisoes()
    decisoes.append(
        {
            "id": str(uuid4()),
            "sessao_id": jogador.get("sessao_id", ""),
            "jogador_id": jogador["id"],
            "nome": jogador["nome"],
            "matricula": jogador["matricula"],
            "papel": jogador["papel"],
            "rodada": rodada,
            "acoes": " | ".join(acoes),
            "impactos": formatar_impactos(impactos),
            "feedback": feedback,
            "criado_em": agora(),
        }
    )
    escrever_linhas(DECISOES_CSV, DECISOES_COLUNAS, decisoes)


def registrar_historico(evento: str, sessao_id: str | None = None) -> None:
    sessao = carregar_sessao()
    historico = ler_linhas(HISTORICO_CSV)
    historico.append({"momento": agora(), "sessao_id": sessao_id or (sessao or {}).get("sessao_id", ""), "evento": evento, **carregar_estado()})
    escrever_linhas(HISTORICO_CSV, HISTORICO_COLUNAS, historico)


def avancar_rodada() -> None:
    estado = carregar_estado()
    if estado["rodada_atual"] < estado["max_rodadas"]:
        estado["rodada_atual"] += 1
        estado["rodada_inicio"] = agora()
        salvar_estado(estado)
        registrar_historico(f"Inicio da rodada {estado['rodada_atual']}")


def reiniciar_jogo() -> None:
    sessao = carregar_sessao()
    estado = ESTADO_INICIAL.copy()
    estado["rodada_inicio"] = agora()
    salvar_estado(estado)
    escrever_linhas(JOGADORES_CSV, JOGADORES_COLUNAS, [])
    escrever_linhas(DECISOES_CSV, DECISOES_COLUNAS, [])
    escrever_linhas(HISTORICO_CSV, HISTORICO_COLUNAS, [])
    registrar_historico("Estado inicial", (sessao or {}).get("sessao_id", ""))


def exportar_todos_csv() -> bytes:
    partes = [
        "# jogadores.csv\n" + linhas_para_csv(JOGADORES_COLUNAS, carregar_jogadores()),
        "# decisoes.csv\n" + linhas_para_csv(DECISOES_COLUNAS, carregar_decisoes()),
        "# historico_indicadores.csv\n" + linhas_para_csv(HISTORICO_COLUNAS, carregar_historico()),
    ]
    return "\n\n".join(partes).encode("utf-8")


def linhas_para_csv(colunas: list[str], linhas: list[dict]) -> str:
    buffer = StringIO()
    escritor = csv.DictWriter(buffer, fieldnames=colunas)
    escritor.writeheader()
    for linha in linhas:
        escritor.writerow({coluna: linha.get(coluna, "") for coluna in colunas})
    return buffer.getvalue()


def formatar_impactos(impactos: dict[str, int]) -> str:
    return " | ".join(f"{indicador}: {delta:+d}" for indicador, delta in impactos.items())


def agora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
