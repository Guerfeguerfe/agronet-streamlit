from __future__ import annotations

import os

import streamlit as st

from dados import avancar_rodada, carregar_decisoes, carregar_estado, carregar_historico, carregar_jogadores, carregar_sessao, criar_sessao, exportar_todos_csv, reiniciar_jogo
from qr_utils import gerar_qr_png
from regras import INDICADORES, resumo_rodada


def render_professor() -> None:
    if not professor_autenticado():
        return

    estado = carregar_estado()
    sessao = carregar_sessao()
    jogadores = carregar_jogadores()
    decisoes = carregar_decisoes()
    historico = carregar_historico()

    st.subheader("Painel do professor")
    st.write("Acompanhe estudantes, decisoes coletivas e mudancas do agroecossistema.")

    render_sessao(sessao)

    col1, col2, col3 = st.columns(3)
    col1.metric("Rodada atual", f"{estado['rodada_atual']} / {estado['max_rodadas']}")
    col2.metric("Alunos registrados", len(jogadores))
    col3.metric("Decisoes registradas", len(decisoes))
    st.metric("Indice de sustentabilidade do agroecossistema", f"{estado.get('Sustentabilidade geral', 0)}/100")

    st.info(resumo_rodada(estado))

    st.divider()
    st.subheader("Indicadores atuais")
    mostrar_barras(estado)

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


def professor_autenticado() -> bool:
    senha_correta = os.getenv("AGRONET_SENHA_PROFESSOR", "agronet")
    if st.session_state.get("professor_autenticado"):
        return True

    st.subheader("Acesso do professor")
    st.caption("Senha padrao nesta versao: agronet. No Render, voce pode trocar criando a variavel AGRONET_SENHA_PROFESSOR.")
    with st.form("senha_professor"):
        senha = st.text_input("Senha do professor", type="password")
        entrar = st.form_submit_button("Entrar", use_container_width=True)
    if entrar:
        if senha == senha_correta:
            st.session_state["professor_autenticado"] = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    return False


def render_sessao(sessao: dict | None) -> None:
    st.divider()
    st.subheader("Sessao da aula e QR Code")
    with st.form("nova_sessao"):
        nome_aula = st.text_input("Nome da aula", value=(sessao or {}).get("nome_aula", "Unidade 1 - Ecossistema e Agroecossistema"))
        base_url = st.text_input("URL publica do app no Render", value=st.session_state.get("base_url", ""))
        criar = st.form_submit_button("Autorizar jogo e gerar sessao", use_container_width=True)
    if criar:
        st.session_state["base_url"] = base_url.strip()
        criar_sessao(nome_aula)
        st.rerun()

    sessao = carregar_sessao()
    if not sessao:
        st.info("Crie uma sessao para liberar o acesso dos alunos.")
        return

    st.success(f"Sessao ativa: {sessao['nome_aula']} | Codigo: {sessao['sessao_id']}")
    url_aluno = montar_url_aluno(st.session_state.get("base_url", ""), sessao["sessao_id"])
    if url_aluno:
        st.write("Link dos alunos:")
        st.code(url_aluno)
        st.image(gerar_qr_png(url_aluno), caption="QR Code para acesso dos alunos", width=240)
    else:
        st.warning("Informe a URL publica do Render para gerar o QR Code completo.")


def montar_url_aluno(base_url: str, sessao_id: str) -> str:
    if not base_url.strip():
        return ""
    base = base_url.strip().rstrip("/")
    return f"{base}/?sessao={sessao_id}"


def mostrar_barras(estado: dict) -> None:
    cols = st.columns(2)
    for indice, indicador in enumerate(INDICADORES):
        valor = estado.get(indicador, 0)
        cols[indice % 2].metric(indicador, valor)
        cols[indice % 2].progress(valor / 100)
