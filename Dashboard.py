#streamlit run Dashboard.py
import streamlit as st
import google.generativeai as genai
import json
import os

API_CHAVE = ""

# Funções usadas no programa
def salvar_historico(historico, nome_arquivo="historico.json"):
    """Salva o histórico do chat em um arquivo JSON.

    Args:
        historico: Lista de dicionários representando o histórico da conversa.
        nome_arquivo: Nome do arquivo JSON (opcional).
    """
    with open(nome_arquivo, 'w') as arquivo:
        json.dump(historico, arquivo, indent=2)

def carregar_historico(nome_arquivo="historico.json"):
    """Carrega o histórico do chat de um arquivo JSON.

    Args:
        nome_arquivo: Nome do arquivo JSON (opcional).

    Returns:
        Uma lista de dicionários representando o histórico da conversa, 
        ou uma lista vazia se o arquivo não existir.
    """
    try:
        with open(nome_arquivo, 'r') as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return []

def gerar_texto_gemini(prompt, chave, model="gemini-1.5-pro-latest", temperature=0.7, top_k=40, top_p=0.95):
    """Gera texto usando a API do Google Gemini.

    Args:
        prompt: O texto de entrada para o modelo.
        chave: API key.
        model: O nome do modelo Gemini a ser usado.
        temperature: Controla a aleatoriedade do texto gerado.
        top_k: Número de tokens considerados em cada etapa.
        top_p: Probabilidade acumulada para amostragem de tokens.

    Returns:
        O texto gerado pelo modelo.
    """

    genai.configure(api_key=chave)  # Configure a chave de API

    system_instruction = """
    Você é o Mestre de Jogo (MG) em "A Sombra sobre Valdar". 
    Sua responsabilidade é conduzir a narrativa e gerenciar o sistema de jogo 
    de forma que enriqueça a experiência dos jogadores. 
    Você cria o cenário, narra as consequências das ações dos jogadores 
    e controla os adversários seguindo as regras no estilo de Dungeons & Dragons.

    Apresentação de Opções pelo Mestre de Jogo:

    Durante o jogo, sempre que os jogadores tiverem que fazer uma escolha, 
    o MG apresentará as opções de forma clara e estruturada. 
    Isso é feito para facilitar a decisão e manter o jogo fluindo.

    Os jogadores então discutem e decidem qual opção seguir, 
    facilitando o processo de decisão e mantendo o jogo 
    fluindo de forma dinâmica.

    Gerenciamento de Combate e Diálogos Objetivos:

    Em combate, o MG segue as mecânicas detalhadas para 
    rolagens de ataque e dano. Além disso, todos os diálogos 
    conduzidos pelo MG, especialmente em situações de negociação 
    ou diálogo com NPCs, serão curtos e objetivos, mantendo o 
    ritmo do jogo e a clareza das informações.

    Papel Além do Combate:

    O MG utiliza diálogos e descrições para enriquecer a trama 
    e orientar os jogadores através das complicações do enredo, 
    sempre mantendo a clareza e a brevidade na comunicação. 
    Isso inclui a administração das consequências das escolhas 
    dos jogadores, desenvolvendo a história de forma coesa 
    e envolvente. 

    Você sempre fala em português do Brasil.
    """

    generation_config = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_output_tokens": 8192,
    }

    # A segurança é integrada ao Gemini, então não precisamos definir configurações de segurança.
    
    model = genai.GenerativeModel(model_name=model, 
                                   generation_config=generation_config, 
                                   system_instruction=system_instruction)

    historico = carregar_historico()

    # Formata o histórico para incluir na mensagem
    historico_formatado = "\n".join([f"Usuário: {h['content']}" if h['role'] == 'user' else f"MG: {h['content']}" for h in historico])

    # Inclui o histórico formatado no prompt
    prompt_com_historico = f"{historico_formatado}\nUsuário: {prompt}"

    chat = model.start_chat()
    response = chat.send_message(prompt_com_historico) 

    # Adiciona a resposta ao histórico
    historico.append({"role": "user", "content": prompt})
    historico.append({"role": "assistant", "content": response.text})
    salvar_historico(historico)

    return response.text


st.title("O JOGO: A Sombra sobre Valdar \U00002694")

# Armazenar a 'página' atual e o log de jogo em uma variável de sessão
if 'page' not in st.session_state:
    st.session_state.page = 'setup'
if 'game_log' not in st.session_state:
    st.session_state.game_log = "Bem-vindo ao jogo! Sua aventura começa aqui.\n"

API_CHAVE = st.session_state.get('API_CHAVE', None)

# Página de Configuração
if st.session_state.page == 'setup':
    # Lista de raças
    racas = ["Elfo", "Humano", "Anão", "Orc", "Gnomo", "Halfling"]
    # Lista de classes
    classes = ["Guerreiro", "Mago", "Ladino", "Clérigo", "Bardo", 
               "Ranger", "Paladino", "Druida", "Feiticeiro", "Monge"]
    # Equipamentos disponíveis
    armaduras = ["Nenhuma", "Couro", "Malha", "Placas"]
    armas = ["Nenhuma", "Espada", "Arco", "Machado", "Cajado"]
    escudos = ["Nenhum", "Escudo Pequeno", "Escudo Médio", "Escudo Grande"]
    # Opções de sexo
    sexos = ["Masculino", "Feminino", "Outro", "Prefiro não dizer"]

    # Campo para digitar a API KEY
    API_CHAVE = st.text_input("Digite a sua API_KEY do Google Gemini:")
    # Armazena a chave na sessão
    if API_CHAVE:
        st.session_state.API_CHAVE = API_CHAVE
   
   
    # Campo para digitar o nome do personagem
    nome_personagem = st.text_input("Digite o nome do seu personagem:")

    # Seleções de características
    raca_selecionada = st.selectbox("Escolha sua raça:", racas)
    classe_selecionada = st.selectbox("Escolha sua classe:", classes)
    sexo_selecionado = st.selectbox("Escolha seu sexo:", sexos)
    armadura_selecionada = st.selectbox("Escolha sua armadura:", armaduras)
    arma_selecionada = st.selectbox("Escolha sua arma:", armas)
    escudo_selecionado = st.selectbox("Escolha seu escudo:", escudos)

    # Criando uma descrição do personagem
    descricao_armadura = "sem armadura" if armadura_selecionada == "Nenhuma" else f"com armadura de {armadura_selecionada.lower()}"
    descricao_arma = "sem arma" if arma_selecionada == "Nenhuma" else f"arma: {arma_selecionada.lower()}"
    descricao_escudo = "e sem escudo" if escudo_selecionado == "Nenhum" else f"e escudo: {escudo_selecionado.lower()}"

    if nome_personagem:  # Apenas mostra a descrição se o nome for inserido
        descri = f"Eu me chamo {nome_personagem} e sou do sexo {sexo_selecionado.lower()} {raca_selecionada.lower()} {classe_selecionada.lower()} {descricao_armadura}, {descricao_arma} {descricao_escudo}."
        st.write(descri)

        # Botão para iniciar o jogo
        if st.button("Iniciar Jogo"):
            resposta_gemini = gerar_texto_gemini(descri, API_CHAVE)
            st.session_state.page = 'game'
            st.session_state.game_log += f"\n{nome_personagem} entrou no jogo como um {sexo_selecionado} {raca_selecionada} {classe_selecionada}, equipado com {armadura_selecionada}, {arma_selecionada} e {escudo_selecionado}.\n"
            st.session_state.game_log += f"{resposta_gemini}"


elif st.session_state.page == 'game':
    # Recupera a chave da API da sessão
    API_CHAVE = st.session_state.get('API_CHAVE', None)

    # Verifica se a chave foi definida
    if API_CHAVE is None:
        st.error("API KEY não encontrada. Por favor, configure na página de configuração.")
    else:
        # Campo superior para mostrar o conteúdo do jogo (apenas a última mensagem)
        st.text_area("História do Jogo:", value=st.session_state.game_log, height=300, disabled=True)

        # Variável de controle para limpar o input
        if 'clear_input' not in st.session_state:
            st.session_state.clear_input = False

        # Campo de entrada para o jogador interagir com o jogo
        user_input = st.text_input("Digite sua ação:", key="user_input", value="" if st.session_state.clear_input else st.session_state.get("user_input", ""))

        # Botão para processar a entrada do jogador
        if st.button("Enviar Ação"):
            # Atualiza o log de jogo com a entrada do jogador
            st.session_state.game_log = f"Você disse: {user_input}\n"

            # Obtém a resposta do Gemini
            resposta_gemini = gerar_texto_gemini(user_input, API_CHAVE)

            # Substitui o conteúdo do game_log pela última resposta
            st.session_state.game_log = f"{resposta_gemini}\n"

            # Define a variável de controle para limpar o input
            st.session_state.clear_input = True
        else:
            # Reseta a variável de controle se o botão não for clicado
            st.session_state.clear_input = False

    # Botão para reiniciar o jogo
    if st.button("Reiniciar Jogo"):
        st.session_state.game_log = "O jogo foi reiniciado. Sua nova aventura começa...\n"
        st.session_state.page = 'setup'

        # Apaga o arquivo de histórico JSON
        try:
            os.remove("historico.json")
        except FileNotFoundError:
            pass  # Ignora se o arquivo não existir