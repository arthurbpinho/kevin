"""
English Learning Platform - MVP
Plataforma educacional de inglês com interface de voz via OpenAI + Eleven Labs
Design Clean & Flat - Cores da Marca: Azul, Amarelo, Vermelho, Branco
"""

import streamlit as st

# === 1. CONFIGURAÇÃO DE PÁGINA OBRIGATÓRIA (PRIMEIRA LINHA EXECUTÁVEL) ===
st.set_page_config(page_title="English Platform", page_icon="📘", layout="wide")

import os
from dotenv import load_dotenv
from openai import OpenAI
import tempfile
import requests

# Carrega variáveis de ambiente
load_dotenv()

# ============================================================
# CONFIGURAÇÕES E CONSTANTES
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL")

# Inicializa cliente OpenAI
client = None
if OPENAI_API_KEY and OPENAI_API_KEY != "sua-chave-aqui":
    client = OpenAI(api_key=OPENAI_API_KEY)

# Credenciais simuladas para MVP
MOCK_USERS = {
    "professor@escola.com": {"password": "prof123", "role": "professor", "name": "Professor Demo"},
    "aluno@escola.com": {"password": "aluno123", "role": "aluno", "name": "Aluno Demo"}
}

# ============================================================
# CONTEXTOS PEDAGÓGICOS (PROMPTS)
# ============================================================

# 1. Instrução Mestra (Personalidade e Regras Gerais)
KEVIN_BASE_INSTRUCTION = """
Você é um agente de I.A. chamado Kevin.
Seu papel é atuar como assistente pedagógico de Inglês do professor regente em turmas de diferentes anos do Ensino Fundamental.

Função principal
Você auxilia o professor ao:
- Introduzir e reforçar vocabulário básico em inglês
- Praticar palavras, frases curtas e expressões simples
- Ajudar os alunos na pronúncia, repetição e compreensão oral
- Coordenar exercícios lúdicos (repetição, associação, jogos simples)
- Responder dúvidas usando inglês simples, misturado com português sempre que necessário para garantir compreensão

Contexto das aulas
- Toda ativação começa com a lição de inglês do dia, planejada para cerca de 1 hora de aula
- O público-alvo são crianças de 6 a 10 anos de acordo com a lição
- Priorize frases curtas e claras em inglês
- Sempre que algo puder gerar confusão: Explique em português, depois retome em inglês.
- Exemplo de abordagem: "This is a dog. Dog é cachorro. Repeat: dog!"

Estilo e postura
- Seja divertido, entusiasmado e encorajador
- Use repetição, ritmo e perguntas simples
- Fale de forma clara e pausada
- Quando necessário, seja calmo e firme para reorganizar a turma
- Incentive a participação sem corrigir de forma dura

Regras importantes
- Não substitua o professor regente; você atua como apoio pedagógico
- Não avance para conteúdos complexos sem autorização
- Evite explicações longas
- Não use gramática formal; foque em exposição natural ao idioma
- Nunca constranja alunos por erros de pronúncia

Objetivo pedagógico
Seu objetivo é fazer com que os alunos:
- Se sintam seguros ao ouvir e falar inglês
- Reconheçam palavras e expressões básicas
- Participem da aula com curiosidade e confiança

Você deve ajudar a tornar o aprendizado de inglês leve, divertido e acessível, respeitando o ritmo da turma e o planejamento do professor.
"""

# 2. Instruções Específicas de Cada Aula
LESSON_SPECIFIC_CONTEXTS = {
    "year_2": {
        "week_1": {
            "class_1": """
Contexto adicional para Kevin: Unidade 1: At School
Nesta aula, seu foco é o ambiente escolar. Utilize o vocabulário: Clock, window, board, desk, picture, chair, notebook, backpack, além de números (1-10) e cores básicas.

Dinâmica de Interação:
- Pergunte ao Professor: Peça para o professor apontar para um objeto da sala e use a estrutura: "Teacher, point to an object! Class, what’s this?".
- Desafie os Alunos: Peça para um aluno identificar um material escolar específico: "It’s a...?".
- Jogo de Sim/Não: Faça perguntas de verificação como "Is it a notebook?" para que os alunos respondam "Yes, it is" ou "No, it isn’t".

Base da Aula: Toda a sua interação deve reforçar o uso de "a/an" e a identificação visual dos itens listados.""",

            "class_2": """
Unidade 2: Family, Friends and Toys
Contexto Adicional para Kevin:
Nesta aula, o vocabulário abrange família (Mom, Dad, Brother, Sister, Grandma, Grandpa) e brinquedos (Teddy bear, Car, Doll, Truck, Robot), além de cores básicas.

Dinâmica de Interação:
- Interação com o Professor: Peça ao professor para mostrar uma imagem de família ou um brinquedo: "Teacher, show them a toy! Is it a truck or a car?".
- Engajamento dos Alunos: Peça para os alunos descreverem cores de brinquedos ou membros da família: "What color is the robot?" ou "Is it the Grandma?".

Base da Aula: Use as estruturas "Is it a/an...?" e as respostas curtas confirmando ou negando, sempre incentivando a participação ativa com o material visual disponível.""",

            "class_3": """
Unidade 3: Jobs
Contexto Adicional para Kevin:
O objetivo desta aula é identificar profissões e usar pronomes pessoais. Vocabulário: Artist, Farmer, Doctor, Teacher, Cook, Vet, Bus driver, Pilot, Singer, Dentist, Firefighter, Mail carrier, Police officer, Astronaut.

Dinâmica de Interação:
- Foco Gramatical: Suas interações devem priorizar o uso de "He is / He isn’t" e "She is / She isn’t".
- Comando ao Professor: Peça para o professor fazer mímicas ou mostrar flashcards de profissões: "Teacher, act like a professional! Class, is he a doctor?".
- Desafio de Identificação: Aponte para as imagens e incentive os alunos a corrigirem ou confirmarem: "She is a singer. Is that right?".

Base da Aula: Toda resposta sua deve reforçar o gênero correto (He/She) associado à profissão mencionada."""
        }
    }
}

# ============================================================
# CSS ESTILIZADO (FLAT DESIGN)
# ============================================================

def load_custom_css():
    st.markdown("""
    <style>
    /* VARIÁVEIS DE COR */
    :root {
        --azul: #5DADE2;
        --azul-escuro: #3498DB;
        --vermelho: #F1948A;
        --amarelo: #F7DC6F;
        --branco: #FFFFFF;
        --cinza-fundo: #FAFAFA;
        --texto: #2C3E50;
    }

    /* GERAL */
    .stApp {
        background-color: var(--branco);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    h1, h2, h3 {
        color: var(--azul-escuro) !important;
        font-weight: 700;
    }
    
    p, label, .stMarkdown {
        color: var(--texto);
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #EBF5FB; /* Azul muito claro */
        border-right: 2px solid var(--azul);
    }
    
    /* BOTÕES */
    .stButton > button {
        background-color: var(--azul);
        color: white;
        border: none;
        border-radius: 25px; /* Bem arredondado, amigável */
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background-color: var(--azul-escuro);
        transform: translateY(-2px);
    }

    /* CARDS PERSONALIZADOS */
    .content-card {
        background-color: white;
        border: 2px solid #EAEAEA;
        border-bottom: 4px solid var(--azul); 
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        text-align: center;
        transition: transform 0.2s;
        color: var(--texto);
    }
    .content-card:hover {
        transform: scale(1.02);
        border-color: var(--azul);
    }
    
    .content-card h3 {
        margin: 0;
        color: var(--azul-escuro);
        font-size: 1.2rem;
    }

    .year-card-active {
        background-color: var(--azul);
        color: white !important;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(93, 173, 226, 0.3);
    }
    
    .year-card-inactive {
        background-color: #F0F2F4;
        color: #95A5A6;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 2px dashed #D0D3D4;
    }

    /* CHAT BUBBLES */
    .user-message {
        background-color: var(--azul);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin-left: auto; /* Alinha à direita */
        margin-bottom: 10px;
        max-width: 75%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        font-size: 1.1rem;
    }
    
    .assistant-message {
        background-color: var(--amarelo); /* Amarelo da marca */
        color: #5D4037; /* Marrom escuro para contraste no amarelo */
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin-right: auto; /* Alinha à esquerda */
        margin-bottom: 10px;
        max-width: 75%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        font-size: 1.1rem;
    }
    
    /* Header Simples */
    .simple-header {
        border-bottom: 3px solid var(--amarelo);
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    /* Esconder Menu Padrão */
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# FUNÇÕES DE AUTENTICAÇÃO E ESTADO
# ============================================================

def init_session_state():
    defaults = {"authenticated": False, "user": None, "current_page": "home", "chat_history": [], 
                "current_lesson": None, "lesson_context_sent": False, "last_audio": None}
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def authenticate(email, password, role):
    if email in MOCK_USERS and MOCK_USERS[email]["password"] == password and MOCK_USERS[email]["role"] == role:
        st.session_state.authenticated = True
        st.session_state.user = {"email": email, "name": MOCK_USERS[email]["name"], "role": role}
        return True
    return False

def logout():
    for key in ["authenticated", "user", "current_page", "chat_history", "current_lesson", "lesson_context_sent", "last_audio"]:
        st.session_state[key] = None if key != "authenticated" else False
    st.session_state.current_page = "home"
    st.session_state.chat_history = []

# ============================================================
# FUNÇÕES API
# ============================================================

def speech_to_text(audio_bytes):
    if not client: return "Erro: API Key não configurada"
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=f, language="pt")
        os.unlink(tmp_path)
        return transcript.text
    except Exception as e:
        return f"Erro: {e}"

def text_to_speech(text):
    if not ELEVENLABS_API_KEY:
        st.warning("⚠️ Áudio desativado (Sem chave API)")
        return None
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {"Accept": "audio/mpeg", "xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    data = {"text": text, "model_id": ELEVENLABS_MODEL, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200: return response.content
        return None
    except: return None

def get_chat_response(user_message, system_context):
    if not client: return "⚠️ API não conectada."
    try:
        messages = [{"role": "system", "content": system_context}]
        messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history[-10:]])
        messages.append({"role": "user", "content": user_message})
        response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.7)
        return response.choices[0].message.content
    except Exception as e: return f"Erro: {e}"

def inject_lesson_context(year, week, class_num):
    try:
        # Busca a instrução específica daquela aula
        specific_context = LESSON_SPECIFIC_CONTEXTS[f"year_{year}"][f"week_{week}"][f"class_{class_num}"]
        
        # COMBINA: Instrução Base + Instrução Específica
        full_context = f"{KEVIN_BASE_INSTRUCTION}\n\n=== CONTEXTO ESPECÍFICO DESTA AULA ===\n{specific_context}"
        
        st.session_state.current_lesson = {"year": year, "week": week, "class": class_num, "context": full_context}
        st.session_state.chat_history = []
        return full_context
    except KeyError: return None

# ============================================================
# PÁGINAS DO APP
# ============================================================

def login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div style="text-align: center;"><h1 style="color:#5DADE2;">Kevin Platform</h1><p style="color:#999;">Platform for Schools</p></div>', unsafe_allow_html=True)
        
        with st.container(border=True):
            with st.form("login_form"):
                st.markdown("### Acesso")
                email = st.text_input("E-mail")
                password = st.text_input("Senha", type="password")
                role = st.selectbox("Perfil", ["professor", "aluno"])
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Entrar no Sistema", use_container_width=True):
                    if authenticate(email, password, role):
                        st.rerun()
                    else:
                        st.error("Dados incorretos.")
        
        with st.expander("Dados de Teste"):
            st.code("professor@escola.com / prof123")

def render_sidebar():
    with st.sidebar:
        st.markdown(f"### Olá, {st.session_state.user['name'].split()[0]}")
        st.markdown("---")
        
        if st.button("Home", use_container_width=True): 
            st.session_state.current_page = "home"; st.rerun()
        
        if st.button("Lessons", use_container_width=True): 
            st.session_state.current_page = "lessons"; st.rerun()
            
        if st.button("Questions", use_container_width=True): 
            st.session_state.current_page = "questions"; st.rerun()
            
        if st.button("Help", use_container_width=True): 
            st.session_state.current_page = "help"; st.rerun()
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        if st.button("Logout", key="logout_btn", use_container_width=True): 
            logout(); st.rerun()

def home_page():
    st.markdown('<div class="simple-header"><h1>Painel Principal</h1></div>', unsafe_allow_html=True)
    
    st.markdown("Selecione uma área para começar:")
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="content-card">
            <h3 style="color: #5DADE2;">Aulas (Lessons)</h3>
            <p>Conteúdo curricular do Year 1 ao 5</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ir para Aulas", key="btn_h1", use_container_width=True):
            st.session_state.current_page = "lessons"; st.rerun()
            
    with c2:
        st.markdown("""
        <div class="content-card">
            <h3 style="color: #F1948A;">Questions</h3>
            <p>Banco de perguntas e respostas</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("See Questions", key="btn_h2", use_container_width=True):
            st.session_state.current_page = "questions"; st.rerun()

    with c3:
        st.markdown("""
        <div class="content-card">
            <h3 style="color: #F7DC6F; color: #DAA520;">Help</h3>
            <p>Configurações e ajuda técnica</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Help", key="btn_h3", use_container_width=True):
            st.session_state.current_page = "help"; st.rerun()

def lessons_page():
    st.markdown('<div class="simple-header"><h1>Curriculum (Aulas)</h1></div>', unsafe_allow_html=True)
    
    cols = st.columns(5)
    for i, col in enumerate(cols, 1):
        with col:
            if i == 2: # Year 2 Ativo
                st.markdown(f'<div class="year-card-active"><h2>Year {i}</h2><small>Disponível</small></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"Abrir Year {i}", key=f"y{i}", use_container_width=True):
                    st.session_state.current_page = "year_2"; st.rerun()
            else:
                st.markdown(f'<div class="year-card-inactive"><h2>Year {i}</h2><small>Bloqueado</small></div>', unsafe_allow_html=True)

def year_2_page():
    st.markdown('<div class="simple-header"><h1>Year 2 - Conteúdo</h1></div>', unsafe_allow_html=True)
    
    col_nav, col_content = st.columns([1, 3])
    with col_nav:
        if st.button("← Voltar para Aulas", use_container_width=True):
            st.session_state.current_page = "lessons"; st.rerun()
            
    with col_content:
        with st.container(border=True):
            st.subheader("Configuração da Sessão")
            c1, c2 = st.columns(2)
            with c1: week = st.selectbox("Selecione a Semana", ["Week 1"]) # Simplifiquei para Week 1 que é a editada
            with c2: cls = st.selectbox("Selecione a Aula", ["Class 1", "Class 2", "Class 3"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Iniciar Atividade com Kevin", type="primary", use_container_width=True):
                if inject_lesson_context("2", week.split()[1], cls.split()[1]):
                    st.session_state.current_page = "lesson_chat"; st.rerun()

def lesson_chat_page():
    if not st.session_state.current_lesson:
        st.session_state.current_page = "year_2"; st.rerun(); return
    
    lesson = st.session_state.current_lesson
    
    # Header minimalista da aula
    st.markdown(f"""
    <div style="background-color: #5DADE2; padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px;">
        <h2 style="color: white !important; margin:0;">Kevin (Assistant)</h2>
        <p style="color: white; margin:0; opacity: 0.9;">Year {lesson["year"]} • Week {lesson["week"]} • Class {lesson["class"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("Encerrar Sessão"):
            st.session_state.current_lesson = None; st.session_state.chat_history = []; st.session_state.last_audio = None
            st.session_state.current_page = "year_2"; st.rerun()
    
    # Área de Chat
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            css_class = "user-message" if msg["role"] == "user" else "assistant-message"
            st.markdown(f'<div class="{css_class}">{msg["content"]}</div>', unsafe_allow_html=True)

    # Player de Áudio
    if st.session_state.last_audio:
        st.markdown("<br>", unsafe_allow_html=True)
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
    
    st.markdown("---")
    
    # Área de Input
    st.markdown("### Interação")
    tab1, tab2 = st.tabs(["Falar (Microfone)", "Digitar (Texto)"])
    
    with tab1:
        # Importação SEGURA (dentro do tab, com tratamento de erro)
        try:
            from streamlit_mic_recorder import mic_recorder
            c_mic, c_info = st.columns([1, 4])
            with c_mic:
                audio = mic_recorder(start_prompt="Gravar", stop_prompt="Parar", just_once=True, key="rec")
            with c_info:
                if audio:
                    st.info("Processando áudio...")
                    text = speech_to_text(audio['bytes'])
                    if text and not text.startswith("Erro"):
                        st.session_state.chat_history.append({"role": "user", "content": text})
                        resp = get_chat_response(text, lesson['context'])
                        st.session_state.chat_history.append({"role": "assistant", "content": resp})
                        st.session_state.last_audio = text_to_speech(resp)
                        st.rerun()
        except ImportError:
            st.error("⚠️ Biblioteca de gravação não encontrada. Instale com: `pip install streamlit-mic-recorder`")
    
    with tab2:
        with st.form("txt_form", clear_on_submit=True):
            txt = st.text_area("Digite sua mensagem para o Kevin:", height=70)
            if st.form_submit_button("Enviar Mensagem") and txt:
                st.session_state.chat_history.append({"role": "user", "content": txt})
                resp = get_chat_response(txt, lesson['context'])
                st.session_state.chat_history.append({"role": "assistant", "content": resp})
                st.session_state.last_audio = text_to_speech(resp)
                st.rerun()

def questions_page():
    st.markdown('<div class="simple-header"><h1>Perguntas Frequentes</h1></div>', unsafe_allow_html=True)
    st.info("Módulo em desenvolvimento.")
    if st.button("Voltar"): st.session_state.current_page = "home"; st.rerun()

def help_page():
    st.markdown('<div class="simple-header"><h1>Ajuda & Status</h1></div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### Instruções Rápidas")
        st.markdown("""
        1. Acesse o menu **Aulas**.
        2. Escolha o **Year 2** (os outros estão bloqueados).
        3. Selecione a Semana e a Aula desejada.
        4. Clique em **Iniciar Atividade**.
        5. Use o microfone para falar com o assistente Kevin.
        """)

    st.markdown("### Status do Sistema")
    c1, c2 = st.columns(2)
    with c1:
        if client: st.success("OpenAI Conectado") 
        else: st.error("OpenAI Desconectado")
    with c2:
        if ELEVENLABS_API_KEY: st.success("Voice Engine Conectado")
        else: st.error("Voice Engine Desconectado")
        
    if st.button("Home"): st.session_state.current_page = "home"; st.rerun()

# ============================================================
# MAIN
# ============================================================

def main():
    load_custom_css()
    init_session_state()
    if not st.session_state.authenticated:
        login_page()
    else:
        render_sidebar()
        pages = {
            "home": home_page, 
            "lessons": lessons_page, 
            "year_2": year_2_page, 
            "lesson_chat": lesson_chat_page, 
            "questions": questions_page, 
            "help": help_page
        }
        pages.get(st.session_state.current_page, home_page)()

if __name__ == "__main__":
    main()