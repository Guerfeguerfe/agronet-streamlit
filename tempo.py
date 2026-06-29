from __future__ import annotations

from datetime import datetime


def segundos_restantes(estado: dict) -> int:
    inicio_texto = estado.get("rodada_inicio") or ""
    duracao = int(estado.get("duracao_rodada_seg") or 240)
    try:
        inicio = datetime.strptime(inicio_texto, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return duracao
    decorridos = int((datetime.now() - inicio).total_seconds())
    return max(0, duracao - decorridos)


def rodada_encerrada(estado: dict) -> bool:
    return segundos_restantes(estado) <= 0


def formatar_tempo(segundos: int) -> str:
    minutos, resto = divmod(max(0, segundos), 60)
    return f"{minutos:02d}:{resto:02d}"
