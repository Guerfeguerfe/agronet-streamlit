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

JOGADORES_COLUNAS = ["id", "nome", "matricula", "papel", "criado_em"]
DECISOES_COLUNAS = ["id", "jogador_id", "nome", "matricula", "papel", "rodada", "acoes", "impactos", "feedback", "criado_em"]
ESTADO_COLUNAS = ["rodada_atual", "max_rodadas", *INDICADORES]
HISTORICO_COLUNAS = ["momento", "evento", "rodada_atual", "max_rodadas", *INDICADORES]


def inicializar_dados() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    criar_csv_se_nao_existir(JOGADORES_CSV, JOGADORES_COLUNAS)
    criar_csv_se_nao_existir(DECISOES_CSV, DECISOES_COLUNAS)
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
    }
    for indicador in INDICADORES:
        estado[indicador] = int(float(linha.get(indicador) or ESTADO_INICIAL[indicador]))
    return estado


def salvar_estado(estado: dict) -> None:
    escrever_linhas(ESTADO_CSV, ESTADO_COLUNAS, [estado])


def registrar_jogador(nome: str, matricula: str, papel: str) -> dict:
    jogadores = carregar_jogadores()
    for jogador in jogadores:
        if jogador["matricula"].strip() == matricula.strip():
            return jogador

    jogador = {
        "id": str(uuid4()),
        "nome": nome.strip(),
        "matricula": matricula.strip(),
        "papel": papel,
        "criado_em": agora(),
    }
    jogadores.append(jogador)
    escrever_linhas(JOGADORES_CSV, JOGADORES_COLUNAS, jogadores)
    return jogador


def buscar_jogador_por_matricula(matricula: str) -> dict | None:
    for jogador in carregar_jogadores():
        if jogador["matricula"].strip() == matricula.strip():
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


def registrar_historico(evento: str) -> None:
    historico = ler_linhas(HISTORICO_CSV)
    historico.append({"momento": agora(), "evento": evento, **carregar_estado()})
    escrever_linhas(HISTORICO_CSV, HISTORICO_COLUNAS, historico)


def avancar_rodada() -> None:
    estado = carregar_estado()
    if estado["rodada_atual"] < estado["max_rodadas"]:
        estado["rodada_atual"] += 1
        salvar_estado(estado)
        registrar_historico(f"Inicio da rodada {estado['rodada_atual']}")


def reiniciar_jogo() -> None:
    salvar_estado(ESTADO_INICIAL)
    escrever_linhas(JOGADORES_CSV, JOGADORES_COLUNAS, [])
    escrever_linhas(DECISOES_CSV, DECISOES_COLUNAS, [])
    escrever_linhas(HISTORICO_CSV, HISTORICO_COLUNAS, [])
    registrar_historico("Estado inicial")


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
