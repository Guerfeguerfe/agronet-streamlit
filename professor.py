from __future__ import annotations

import streamlit as st

from dados import avancar_rodada, carregar_decisoes, carregar_estado, carregar_historico, carregar_jogadores, exportar_todos_csv, reiniciar_jogo
from regras import INDICADORES, resumo_rodada


def render_professor() -> None:
    estado = carregar_estado()
    jogadores = carregar_jogadores()
    decisoes = carregar_decisoes()
    historico = carregar_historico()

    st.subheader("Painel do professor")
    st.write("Acompanhe estudantes, decisoes coletivas e mudancas do agroecossistema.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Rodada atual", f"{estado['rodada_atual']} / {estado['max_rodadas']}")
    col2.metric("Alunos registrados", len(jogadores))
    col3.metric("Decisoes registradas", len(decisoes))

    st.info(resumo_rodada(estado))

    st.divider()
    st.subheader("Indicadores atuais")
    cols = st.columns(2)
    for indice, indicador in enumerate(INDICADORES):
        valor = estado.get(indicador, 0)
        cols[indice % 2].metric(indicador, valor)
        cols[indice % 2].progress(valor / 100)

    st.divider()
    acao1, acao2, acao3 = st.columns(3)
    if acao1.button("Iniciar nova rodada", use_container_width=True):
        avancar_rodada()
        st.rerun()
    if acao2.button("Reiniciar jogo", use_container_width=True):
        reiniciar_jogo()
        st.rerun()
    acao3.download_button(
        "Baixar dados CSV",
        data=exportar_todos_csv(),
        file_name="agronet_dados.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.divider()
    st.subheader("Alunos registrados")
    st.dataframe(jogadores, use_container_width=True, hide_index=True)

    st.subheader("Decisoes por rodada")
    st.dataframe(decisoes, use_container_width=True, hide_index=True)

    st.subheader("Historico dos indicadores")
    st.dataframe(historico, use_container_width=True, hide_index=True)
    grafico_historico(historico)


def grafico_historico(historico: list[dict[str, str]]) -> None:
    if not historico:
        return
    dados = []
    for linha in historico:
        dados.append({indicador: int(float(linha.get(indicador) or 0)) for indicador in INDICADORES})
    st.line_chart(dados)
