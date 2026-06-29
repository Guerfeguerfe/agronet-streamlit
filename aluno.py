from __future__ import annotations

import random

import streamlit as st

from dados import buscar_jogador_por_id, buscar_jogador_por_matricula, buscar_sessao, carregar_estado, jogador_ja_decidiu, registrar_decisao, registrar_jogador, salvar_estado, registrar_historico
from regras import INDICADORES, acoes_do_papel, aplicar_impactos, feedback_da_acao, funcoes_do_papel, impacto_da_acao, listar_papeis
from tempo import formatar_tempo, rodada_encerrada, segundos_restantes


def render_aluno(sessao_id: str | None = None) -> None:
    estado = carregar_estado()
    sessao = buscar_sessao(sessao_id or "")
    if not sessao or sessao.get("ativa") != "sim":
        st.warning("Esta sessao de aula nao esta ativa. Peça ao professor o QR Code da aula atual.")
        return

    st.subheader("Entrada do estudante")
    st.caption(f"Sessao: {sessao['nome_aula']} | Codigo: {sessao['sessao_id']}")
    mostrar_cronometro(estado)

    jogador = obter_jogador(sessao["sessao_id"])
    if not jogador:
        st.write("Registre-se uma vez. Depois, este aparelho/link continua reconhecendo sua participacao na aula.")
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
            jogador = registrar_jogador(nome, matricula, papel, sessao["sessao_id"])
            st.session_state["jogador_id"] = jogador["id"]
            st.session_state["matricula"] = jogador["matricula"]
            st.session_state["sessao_id"] = sessao["sessao_id"]
            st.query_params["sessao"] = sessao["sessao_id"]
            st.query_params["jogador"] = jogador["id"]
            st.success(f"Registro encontrado/criado. Seu papel: {jogador['papel']}.")
            st.rerun()
        mostrar_indicadores(estado)
        st.info("Depois do registro, suas acoes da rodada aparecem aqui.")
        return

    rodada = estado["rodada_atual"]
    st.divider()
    st.subheader(f"Rodada {rodada} de {estado['max_rodadas']}")
    st.caption(f"Papel: {jogador['papel']} | Estudante: {jogador['nome']}")
    mostrar_papel(jogador["papel"])

    if rodada > estado["max_rodadas"]:
        st.info("O jogo foi encerrado pelo professor.")
        return

    if rodada_encerrada(estado):
        st.warning("O tempo desta rodada terminou. Aguarde o professor iniciar a proxima rodada.")
        mostrar_indicadores(estado)
        return

    if jogador_ja_decidiu(jogador["id"], rodada):
        st.success("Voce ja enviou sua decisao nesta rodada. Aguarde a proxima rodada.")
        mostrar_indicadores(estado)
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
        registrar_historico(f"Decisao de {jogador['nome']} na rodada {rodada}", sessao["sessao_id"])
        st.success("Decisao registrada.")
        st.write("Acoes escolhidas:")
        for acao in acoes:
            st.write(f"- {acao}")
        st.write("Efeitos sobre o sistema:")
        for indicador, delta in impactos.items():
            st.write(f"- {indicador}: {delta:+d}")
        st.info(" ".join(feedbacks))
        mostrar_indicadores(novo_estado)


def somar_impactos(papel: str, acoes: list[str]) -> dict[str, int]:
    total: dict[str, int] = {}
    for acao in acoes:
        for indicador, delta in impacto_da_acao(papel, acao).items():
            total[indicador] = total.get(indicador, 0) + delta
    return total


def obter_jogador(sessao_id: str) -> dict | None:
    jogador_id = st.session_state.get("jogador_id") or st.query_params.get("jogador", "")
    if jogador_id:
        jogador = buscar_jogador_por_id(jogador_id, sessao_id)
        if jogador:
            st.session_state["jogador_id"] = jogador["id"]
            st.session_state["matricula"] = jogador["matricula"]
            return jogador

    matricula = st.session_state.get("matricula", "")
    if matricula:
        return buscar_jogador_por_matricula(matricula, sessao_id)
    return None


def mostrar_cronometro(estado: dict) -> None:
    restante = segundos_restantes(estado)
    st.metric("Tempo restante da rodada", formatar_tempo(restante))
    st.progress(restante / max(1, int(estado.get("duracao_rodada_seg") or 240)))


def mostrar_papel(papel: str) -> None:
    with st.expander("Meu papel no agroecossistema", expanded=True):
        st.write("Funcoes agroecossistemicas:")
        for funcao in funcoes_do_papel(papel):
            st.write(f"- {funcao}")
        st.write("Alternativas de acao nesta rodada:")
        for acao in acoes_do_papel(papel):
            feedback = feedback_da_acao(papel, acao)
            st.write(f"- **{acao}**: {feedback}")


def mostrar_indicadores(estado: dict) -> None:
    st.divider()
    st.subheader("Desempenho do agroecossistema")
    indice = estado.get("Sustentabilidade geral", 0)
    st.metric("Indice de sustentabilidade do agroecossistema", f"{indice}/100")
    st.progress(indice / 100)
    cols = st.columns(2)
    for posicao, indicador in enumerate(INDICADORES):
        valor = estado.get(indicador, 0)
        cols[posicao % 2].caption(indicador)
        cols[posicao % 2].progress(valor / 100, text=f"{valor}/100")
