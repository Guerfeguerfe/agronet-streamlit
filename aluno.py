from __future__ import annotations

import random

import streamlit as st

from dados import buscar_jogador_por_matricula, carregar_estado, jogador_ja_decidiu, registrar_decisao, registrar_jogador, salvar_estado, registrar_historico
from regras import acoes_do_papel, aplicar_impactos, feedback_da_acao, impacto_da_acao, listar_papeis


def render_aluno() -> None:
    estado = carregar_estado()
    st.subheader("Entrada do estudante")
    st.write("Registre-se, escolha ou sorteie seu papel e envie ate duas acoes na rodada atual.")

    with st.form("form_registro"):
        nome = st.text_input("Nome")
        matricula = st.text_input("Matricula")
        modo_papel = st.radio("Papel no agroecossistema", ["Escolher papel", "Sortear papel"], horizontal=True)
        papel_escolhido = st.selectbox("Escolha seu papel", listar_papeis(), disabled=modo_papel == "Sortear papel")
        registrar = st.form_submit_button("Entrar no jogo", use_container_width=True)

    if registrar:
        if not nome.strip() or not matricula.strip():
            st.error("Informe nome e matricula para continuar.")
            st.stop()
        papel = random.choice(listar_papeis()) if modo_papel == "Sortear papel" else papel_escolhido
        jogador = registrar_jogador(nome, matricula, papel)
        st.session_state["matricula"] = jogador["matricula"]
        st.success(f"Registro encontrado/criado. Seu papel: {jogador['papel']}.")

    matricula_atual = st.session_state.get("matricula", "")
    if not matricula_atual:
        st.info("Depois do registro, suas acoes da rodada aparecem aqui.")
        return

    jogador = buscar_jogador_por_matricula(matricula_atual)
    if not jogador:
        st.warning("Nao encontrei seu cadastro. Registre-se novamente.")
        return

    rodada = estado["rodada_atual"]
    st.divider()
    st.subheader(f"Rodada {rodada} de {estado['max_rodadas']}")
    st.caption(f"Papel: {jogador['papel']} | Estudante: {jogador['nome']}")

    if rodada > estado["max_rodadas"]:
        st.info("O jogo foi encerrado pelo professor.")
        return

    if jogador_ja_decidiu(jogador["id"], rodada):
        st.success("Voce ja enviou sua decisao nesta rodada. Aguarde a proxima rodada.")
        return

    opcoes = acoes_do_papel(jogador["papel"])
    with st.form("form_decisao"):
        acoes = st.multiselect("Escolha ate 2 acoes", opcoes, max_selections=2)
        enviar = st.form_submit_button("Enviar decisao", use_container_width=True)

    if enviar:
        if not acoes:
            st.error("Escolha pelo menos uma acao.")
            st.stop()
        impactos = somar_impactos(jogador["papel"], acoes)
        feedbacks = [feedback_da_acao(jogador["papel"], acao) for acao in acoes]
        novo_estado = aplicar_impactos(estado, [impactos])
        salvar_estado(novo_estado)
        registrar_decisao(jogador, rodada, acoes, impactos, " ".join(feedbacks))
        registrar_historico(f"Decisao de {jogador['nome']} na rodada {rodada}")
        st.success("Decisao registrada.")
        st.write("Acoes escolhidas:")
        for acao in acoes:
            st.write(f"- {acao}")
        st.write("Efeitos sobre o sistema:")
        for indicador, delta in impactos.items():
            st.write(f"- {indicador}: {delta:+d}")
        st.info(" ".join(feedbacks))
        st.rerun()


def somar_impactos(papel: str, acoes: list[str]) -> dict[str, int]:
    total: dict[str, int] = {}
    for acao in acoes:
        for indicador, delta in impacto_da_acao(papel, acao).items():
            total[indicador] = total.get(indicador, 0) + delta
    return total
