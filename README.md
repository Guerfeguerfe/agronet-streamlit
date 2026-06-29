# AgroNet - O Agroecossistema Vivo

Prototipo funcional em Python com Streamlit para a Unidade 1 do curso Agricultura, Economia e Sustentabilidade.

## Estrutura recomendada

```text
.
|-- app.py
|-- aluno.py
|-- professor.py
|-- regras.py
|-- dados.py
|-- tempo.py
|-- qr_utils.py
|-- requirements.txt
|-- render.yaml
|-- README.md
`-- data/
    |-- jogadores.csv
    |-- decisoes.csv
    |-- estado_sistema.csv
    |-- historico_indicadores.csv
    `-- sessao_aula.csv
```

A pasta `data/` e os CSVs sao criados automaticamente na primeira execucao.

## Execucao local

1. Crie e ative um ambiente virtual, se desejar.
2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Rode o app:

```bash
streamlit run app.py
```

4. Abra o endereco exibido no terminal. Em rede local, estudantes podem acessar pelo celular usando o IP do computador do professor e a porta do Streamlit.

## Uso em aula

1. Acesse a aba Professor.
2. Entre com a senha padrao:

```text
agronet
```

3. Informe o nome da aula, o tempo de cada rodada e a URL publica do app no Render.
4. Clique em `Autorizar jogo e gerar sessao`.
5. Mostre o QR Code aos alunos.
6. Cada aluno acessa pelo QR Code, registra nome e matricula, escolhe o papel e envia ate duas acoes por rodada.
7. Depois do primeiro cadastro, o link do aluno passa a conter um identificador do jogador. Assim, ao atualizar a pagina ou entrar na proxima rodada, ele nao precisa digitar nome e matricula novamente.

O tempo padrao de cada rodada e 4 minutos, adequado para turmas de 10 a 15 alunos em uma decisao rapida. O professor pode ajustar entre 2 e 10 minutos ao criar a sessao.

Para trocar a senha no Render, crie uma variavel de ambiente:

```text
AGRONET_SENHA_PROFESSOR=sua-senha
```

## Publicacao basica no Render

1. Envie estes arquivos para um repositorio GitHub.
2. No Render, crie um novo Web Service conectado ao repositorio.
3. O arquivo `render.yaml` ja define:
   - instalacao com `pip install -r requirements.txt`;
   - inicio com `python -m streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`.
4. Confirme o deploy e acesse a URL gerada pelo Render.

## Observacao sobre dados

Esta versao usa CSVs simples, sem banco de dados. Em hospedagens gratuitas, os dados podem ser apagados quando o servico reinicia. Para aulas presenciais, a execucao local costuma ser mais previsivel.
