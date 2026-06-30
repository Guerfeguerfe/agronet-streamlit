from __future__ import annotations

import streamlit as st

from aluno import render_aluno
from dados import inicializar_dados
from professor import render_professor


st.set_page_config(
    page_title="AgroNet - O Agroecossistema Vivo",
    page_icon="AG",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inicializar_dados()

st.title("AgroNet - O Agroecossistema Vivo")
st.markdown(
    """
**Universidade Federal do Ceara**  
**Departamento de Economia Agricola**  
**Curso:** Agricultura, Economia e Sustentabilidade  
**Unidade 1:** Ecossistema e Agroecossistema  
**Jogo:** AgroNet - O Agroecossistema Vivo  
**Prof. Rogerio Cesar Pereira de Araujo**
"""
)

st.write(
    "Um jogo educacional multiplayer sobre componentes bioticos, abioticos e sociais "
    "de um agroecossistema. As decisoes coletivas alteram biodiversidade, solo, agua, "
    "producao, equilibrio ecologico, servicos ecossistemicos e sustentabilidade."
)

sessao_qr = st.query_params.get("sessao")

if sessao_qr:
    render_aluno(sessao_qr)
else:
    render_professor()
