"""
English Learning Platform - MVP
Plataforma educacional de inglês com interface de voz via OpenAI + Eleven Labs
Design Clean & Flat - Cores da Marca: Azul, Amarelo, Vermelho, Branco
"""

import streamlit as st

# === 1. CONFIGURAÇÃO DE PÁGINA OBRIGATÓRIA (PRIMEIRA LINHA EXECUTÁVEL) ===
st.set_page_config(page_title="English Platform", page_icon="📘", layout="wide")

import os
import json
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
    "aluno@escola.com": {"password": "aluno123", "role": "aluno", "name": "Aluno Demo"},
    "admin@escola.com": {"password": "admin123", "role": "administrador", "name": "Admin Demo"}
}

# Arquivo para persistir aulas criadas pelo administrador
CUSTOM_LESSONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom_lessons.json")

def load_custom_lessons():
    if os.path.exists(CUSTOM_LESSONS_FILE):
        with open(CUSTOM_LESSONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_custom_lessons(lessons):
    with open(CUSTOM_LESSONS_FILE, "w", encoding="utf-8") as f:
        json.dump(lessons, f, ensure_ascii=False, indent=2)

# ============================================================
# CONTEXTOS PEDAGÓGICOS (PROMPTS)
# ============================================================

# 1. Instrução Mestra (Personalidade e Regras Gerais)
KEVIN_BASE_INSTRUCTION = """
Você é um agente de I.A. educacional chamado Kevin.
Seu papel é atuar como assistente pedagógico e co-piloto do professor regente em turmas de Ensino Fundamental (Elementary School). O professor dita o ritmo, mas você sugere os próximos passos e interage com as crianças quando acionado.

=== METODOLOGIA DA AULA ===
Toda aula segue estritamente três momentos. Você deve ajudar o professor a navegar por eles:

1. WARM UP (10-15 min): Preparação e engajamento.
Sua função: Cumprimentar a turma de forma animada, ajudar na rotina inicial (músicas, calendário, sentimentos) e conduzir o jogo de revisão ou prática inicial de forma rápida e lúdica.

2. DEVELOPMENT (30-40 min): Foco principal da aula (Conteúdo, Cultura, etc.).
Sua função: Introduzir o vocabulário e a gramática do dia com clareza. Você fará exercícios de repetição (drills) com os alunos, fará perguntas curtas e ajudará o professor a modelar o uso correto do idioma.

3. CLOSURE (5-10 min): Encerramento.
Sua função: Ajudar a revisar o que foi aprendido de forma rápida, lembrar os alunos do dever de casa (homework) se houver, e conduzir a despedida (música de bye-bye).

=== DIRETRIZES DE COMUNICAÇÃO ===
- Público: Crianças. Seja sempre animado, divertido, encorajador e paciente.
- Idioma: Priorize frases curtas e claras em inglês. Se algo puder gerar confusão, explique em português e retome em inglês. (Ex: "This is a dog. Dog é cachorro. Repeat: dog!").
- Postura: Você NÃO substitui o professor. Você interage COM o professor e COM os alunos. Chame o professor de "Teacher".
- Ritmo: Não dê todas as instruções da aula de uma vez. Vá passo a passo, aguardando a interação do professor ou dos alunos antes de avançar para a próxima atividade ou fase da aula.
- Linguagem: Tornar instrução e linguagem mais compatível com a estrutura da aula (não utilize por exemplo particípio do passado e estruturas ou vocabulário difícil em uma aula de vocabulário e proposta simples)
- Correção dos alunos: Caso o aluno responda algo em português, diga aquilo que ele falou em inglês e peça-o para repetir, ou se você notar que o aluno está tendo dificuldade, ajude-o a melhorar, sempre usando a didática de pronunciar a frase correta em inglês e pedindo a repetição.

=== REGRAS CRÍTICAS SOBRE O PASSO A PASSO ===
- O "PASSO A PASSO" e as "Ações" são o seu ROTEIRO INTERNO. Eles descrevem O QUE você deve fazer, NÃO o que você deve dizer literalmente.
- NUNCA leia as ações em voz alta. NUNCA diga "Ação 1", "Ação 2", "FASE 1", "WARM UP", "DEVELOPMENT", "CLOSURE" ou qualquer marcação do roteiro. Isso é invisível para o Teacher e para os alunos.
- Em vez de ler o roteiro, EXECUTE a ação de forma natural e conversacional. Exemplo: se o roteiro diz "Diga Hello e peça para o Teacher colocar a música", você deve simplesmente dizer algo como "Hello everyone! Teacher, can you play our Hello song?".
- Faça APENAS UMA ação por vez. Após executá-la, PARE e ESPERE o Teacher ou a turma responder antes de avançar para a próxima ação.
- Suas respostas devem ser CURTAS (2-4 frases no máximo). Você está falando com crianças em uma sala de aula real. Não faça monólogos e evite explicações sobre o que está ensinando.
- NUNCA antecipe múltiplas ações em uma única resposta. Uma mensagem = uma ação do roteiro.
"""

# 2. Instruções Específicas de Cada Aula
LESSON_SPECIFIC_CONTEXTS = {
    "year_2": {
        "week_1": {
            "class_1": """
=== CONTEXTO ESPECÍFICO DESTA AULA (U1W1C2 - Content Class) ===

OBJETIVOS: Fazer perguntas com "What's" e usar "a/an".
VOCABULÁRIO: Clock, window, board, desk, picture, chair, notebook, backpack.
GRAMÁTICA: "What’s this? It’s a/an…".

PASSO A PASSO PARA O KEVIN CONDUZIR (Aguarde a resposta do Teacher ou da turma antes de pular de um passo para outro):

[ FASE 1: WARM UP ]
- Ação 1: Diga um "Hello" bem animado e peça para o Teacher colocar a música "Hello!".
- Ação 2: Após a música, conduza uma revisão rápida (Tim's Game) usando o vocabulário da aula. Faça 3 perguntas rápidas para a turma tentar adivinhar qual é o objeto.

[ FASE 2: DEVELOPMENT ]
- Ação 1: Peça atenção da turma. Introduza a estrutura gramatical falando: "Look! What's this? It's a backpack!". Peça para a turma repetir.
- Ação 2: Sugira ao Teacher apontar para objetos reais na sala (window, board, desk, chair) para fazer a prática de repetição (Drills) com a turma, usando a estrutura "What's this? It's a...". Ajude a validar as respostas das crianças elogiando-as ("Great job!", "Exactly!").
- Ação 3: Lembre o Teacher de abrir o livro 'Share It!' na Unidade 1, Lição 2 para as atividades de Listening e Grammar Practice.

[ FASE 3: CLOSURE ]
- Ação 1: Se houver TV na sala, lembre o Teacher de passar o Grammar Video.
- Ação 2: Ajude o Teacher a passar o dever de casa: "Integrated Activities, Unit 1, exercises 1 and 2". Explique brevemente em português para garantir que os alunos entendam.
- Ação 3: Despeça-se da turma de forma calorosa e peça para o Teacher tocar a música "See You Later, Alligator"."""

        }
    }
}

# ============================================================
# CSS ESTILIZADO (FLAT DESIGN)
# ============================================================

def load_custom_css():
    st.markdown("""
    <style>
    /* === PALETA BEBILINGUE: Azul, Vermelho, Cinza-Claro === */
    :root {
        --azul: #2B7DE9;
        --azul-escuro: #1A5FB4;
        --azul-claro: #E8F0FE;
        --vermelho: #D93025;
        --vermelho-suave: #FCEAE9;
        --cinza-fundo: #F0F2F5;
        --cinza-card: #F7F8FA;
        --cinza-borda: #DDE1E6;
        --texto: #1E293B;
        --texto-secundario: #64748B;
    }

    /* GERAL */
    .stApp {
        background-color: var(--cinza-fundo) !important;
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
        background-color: var(--azul-escuro) !important;
        border-right: none;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] small {
        color: #CBD5E1 !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.15) !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        background-color: rgba(255,255,255,0.1);
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 8px;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(255,255,255,0.2);
        transform: none;
    }

    /* BOTÕES GERAIS */
    .stButton > button {
        background-color: var(--azul);
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        transition: all 0.2s;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }

    .stButton > button:hover {
        background-color: var(--azul-escuro);
        transform: translateY(-1px);
        box-shadow: 0 3px 8px rgba(26,95,180,0.25);
        color: #FFFFFF !important;
    }

    .stButton > button:active,
    .stButton > button:focus {
        color: #FFFFFF !important;
    }

    /* BOTÃO PRIMARY (vermelho destaque) */
    .stButton > button[kind="primary"] {
        background-color: var(--vermelho);
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #C12A1F;
        box-shadow: 0 3px 8px rgba(217,48,37,0.3);
    }

    /* FORM SUBMIT BUTTONS */
    .stForm [data-testid="stFormSubmitButton"] > button {
        background-color: var(--azul);
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }

    .stForm [data-testid="stFormSubmitButton"] > button:hover {
        background-color: var(--azul-escuro);
        color: #FFFFFF !important;
    }

    /* INPUTS */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox [data-baseweb="select"],
    .stSelectbox input,
    .stNumberInput input {
        border-radius: 8px !important;
        border: 1px solid var(--cinza-borda) !important;
        background-color: #FFFFFF !important;
        color: var(--texto) !important;
        -webkit-text-fill-color: var(--texto) !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--azul) !important;
        box-shadow: 0 0 0 2px rgba(43,125,233,0.15) !important;
    }

    /* Placeholder */
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: var(--texto-secundario) !important;
        -webkit-text-fill-color: var(--texto-secundario) !important;
        opacity: 0.7;
    }

    /* Selectbox — forçar fundo branco e texto escuro em TODAS as camadas */
    .stSelectbox > div,
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div > div,
    .stSelectbox [data-baseweb="select"] *,
    [data-baseweb="select"] [class*="control"],
    [data-baseweb="select"] [class*="ValueContainer"],
    [data-baseweb="select"] [class*="singleValue"],
    [data-baseweb="select"] [class*="placeholder"] {
        background-color: #FFFFFF !important;
        color: var(--texto) !important;
        -webkit-text-fill-color: var(--texto) !important;
    }

    /* Selectbox dropdown (menu suspenso) — forçar fundo branco */
    [data-baseweb="popover"],
    [data-baseweb="popover"] *,
    [data-baseweb="list"],
    [data-baseweb="list"] *,
    [data-baseweb="menu"],
    [data-baseweb="menu"] *,
    [role="listbox"],
    [role="listbox"] *,
    [role="listbox"] li,
    [role="option"],
    [role="option"] * {
        color: var(--texto) !important;
        -webkit-text-fill-color: var(--texto) !important;
        background-color: #FFFFFF !important;
    }

    [role="option"]:hover,
    [role="option"][aria-selected="true"],
    [data-baseweb="menu"] li:hover,
    [data-baseweb="list"] li:hover {
        background-color: var(--azul-claro) !important;
    }

    /* Selectbox seta/ícone */
    .stSelectbox svg {
        fill: var(--texto-secundario) !important;
    }

    /* Labels dos inputs */
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stNumberInput label {
        color: var(--texto) !important;
    }

    /* CONTAINERS / FORMS */
    [data-testid="stForm"],
    .stContainer > div[data-testid] {
        border-radius: 12px;
    }

    /* CARDS PERSONALIZADOS */
    .content-card {
        background-color: #FFFFFF;
        border: 1px solid var(--cinza-borda);
        border-bottom: 3px solid var(--azul);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        text-align: center;
        transition: all 0.2s;
        color: var(--texto);
    }
    .content-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .content-card h3 {
        margin: 0;
        font-size: 1.2rem;
    }

    .year-card-active {
        background-color: var(--azul);
        color: white !important;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(43,125,233,0.3);
    }

    .year-card-active h2 {
        color: #FFFFFF !important;
    }

    .year-card-active small {
        color: rgba(255,255,255,0.85);
    }

    .year-card-inactive {
        background-color: var(--cinza-card);
        color: var(--texto-secundario);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 2px dashed var(--cinza-borda);
    }

    .year-card-inactive h2 {
        color: var(--texto-secundario) !important;
    }

    /* CHAT BUBBLES */
    .user-message {
        background-color: var(--azul);
        color: #FFFFFF;
        padding: 12px 18px;
        border-radius: 16px 16px 4px 16px;
        margin-left: auto;
        margin-bottom: 10px;
        max-width: 75%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        font-size: 1rem;
    }

    .assistant-message {
        background-color: #FFFFFF;
        color: var(--texto);
        padding: 12px 18px;
        border-radius: 16px 16px 16px 4px;
        margin-right: auto;
        margin-bottom: 10px;
        max-width: 75%;
        border: 1px solid var(--cinza-borda);
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        font-size: 1rem;
    }

    /* HEADER */
    .simple-header {
        border-bottom: 3px solid var(--vermelho);
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    /* CHAT HEADER */
    .chat-header {
        background: linear-gradient(135deg, var(--azul) 0%, var(--azul-escuro) 100%);
        padding: 18px 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(26,95,180,0.25);
    }

    .chat-header h2 {
        color: #FFFFFF !important;
        margin: 0;
    }

    .chat-header p {
        color: rgba(255,255,255,0.85);
        margin: 0;
    }

    /* LOGIN */
    .login-box {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-top: 4px solid var(--vermelho);
    }

    .login-title {
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .login-title h1 {
        color: var(--azul-escuro) !important;
        font-size: 2rem;
        margin-bottom: 0;
    }

    .login-title p {
        color: var(--texto-secundario);
        font-size: 0.95rem;
    }

    /* EXPANDER */
    .streamlit-expanderHeader {
        background-color: var(--cinza-card);
        border-radius: 8px;
    }

    /* ESCONDER MENU PADRÃO */
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
    specific_context = None

    # Primeiro tenta no dicionário hardcoded
    try:
        specific_context = LESSON_SPECIFIC_CONTEXTS[f"year_{year}"][f"week_{week}"][f"class_{class_num}"]
    except KeyError:
        pass

    # Se não encontrou, busca nas aulas customizadas
    if specific_context is None:
        custom_lessons = load_custom_lessons()
        key = f"U{year}W{week}C{class_num}"
        if key in custom_lessons:
            specific_context = custom_lessons[key]["prompt"]

    if specific_context is None:
        return None

    full_context = f"{KEVIN_BASE_INSTRUCTION}\n\n=== CONTEXTO ESPECÍFICO DESTA AULA ===\n{specific_context}"
    st.session_state.current_lesson = {"year": year, "week": week, "class": class_num, "context": full_context}
    st.session_state.chat_history = []
    return full_context

# ============================================================
# PÁGINAS DO APP
# ============================================================

def login_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="login-title">
            <h1>Kevin</h1>
            <p>Plataforma Bebilingue para Escolas</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("##### Acesse sua conta")
            email = st.text_input("E-mail")
            password = st.text_input("Senha", type="password")
            role = st.selectbox("Perfil", ["professor", "aluno", "administrador"])

            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Entrar", use_container_width=True):
                if authenticate(email, password, role):
                    st.rerun()
                else:
                    st.error("E-mail, senha ou perfil incorretos.")

        with st.expander("Dados de Teste"):
            st.markdown("""
            | Perfil | E-mail | Senha |
            |---|---|---|
            | Professor | `professor@escola.com` | `prof123` |
            | Aluno | `aluno@escola.com` | `aluno123` |
            | Admin | `admin@escola.com` | `admin123` |
            """)

def render_sidebar():
    with st.sidebar:
        role = st.session_state.user['role']
        st.markdown(f"### Olá, {st.session_state.user['name'].split()[0]}")
        st.caption(f"Perfil: {role.capitalize()}")
        st.markdown("---")

        if st.button("Home", use_container_width=True):
            st.session_state.current_page = "home"; st.rerun()

        if role in ("professor", "aluno"):
            if st.button("Lessons", use_container_width=True):
                st.session_state.current_page = "lessons"; st.rerun()

            if st.button("Questions", use_container_width=True):
                st.session_state.current_page = "questions"; st.rerun()

        if role == "administrador":
            if st.button("Adicionar Aula", use_container_width=True):
                st.session_state.current_page = "admin_add_lesson"; st.rerun()

            if st.button("Aulas Criadas", use_container_width=True):
                st.session_state.current_page = "admin_list_lessons"; st.rerun()

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
            <h3 style="color: var(--azul-escuro);">Aulas (Lessons)</h3>
            <p>Conteudo curricular do Year 1 ao 5</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ir para Aulas", key="btn_h1", use_container_width=True):
            st.session_state.current_page = "lessons"; st.rerun()

    with c2:
        st.markdown("""
        <div class="content-card" style="border-bottom-color: var(--vermelho);">
            <h3 style="color: var(--vermelho);">Questions</h3>
            <p>Banco de perguntas e respostas</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("See Questions", key="btn_h2", use_container_width=True):
            st.session_state.current_page = "questions"; st.rerun()

    with c3:
        st.markdown("""
        <div class="content-card" style="border-bottom-color: var(--texto-secundario);">
            <h3 style="color: var(--texto-secundario);">Help</h3>
            <p>Configuracoes e ajuda tecnica</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Help", key="btn_h3", use_container_width=True):
            st.session_state.current_page = "help"; st.rerun()

def get_available_units():
    """Retorna set de unit numbers que possuem aulas (hardcoded ou custom)."""
    units = set()
    for key in LESSON_SPECIFIC_CONTEXTS:
        units.add(int(key.replace("year_", "")))
    custom_lessons = load_custom_lessons()
    for code in custom_lessons:
        # code format: U1W2C3
        unit_num = int(code.split("W")[0].replace("U", ""))
        units.add(unit_num)
    return units

def lessons_page():
    st.markdown('<div class="simple-header"><h1>Curriculum (Aulas)</h1></div>', unsafe_allow_html=True)

    available_units = get_available_units()

    cols = st.columns(5)
    for i, col in enumerate(cols, 1):
        with col:
            if i in available_units:
                st.markdown(f'<div class="year-card-active"><h2>Year {i}</h2><small>Disponível</small></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"Abrir Year {i}", key=f"y{i}", use_container_width=True):
                    st.session_state.current_page = f"year_{i}"; st.rerun()
            else:
                st.markdown(f'<div class="year-card-inactive"><h2>Year {i}</h2><small>Bloqueado</small></div>', unsafe_allow_html=True)

def get_available_lessons_for_unit(unit):
    """Retorna dict de weeks -> list de classes disponíveis para uma unit."""
    available = {}

    # Hardcoded lessons
    year_key = f"year_{unit}"
    if year_key in LESSON_SPECIFIC_CONTEXTS:
        for week_key, classes in LESSON_SPECIFIC_CONTEXTS[year_key].items():
            week_num = week_key.replace("week_", "")
            if week_num not in available:
                available[week_num] = set()
            for class_key in classes:
                class_num = class_key.replace("class_", "")
                available[week_num].add(class_num)

    # Custom lessons
    custom_lessons = load_custom_lessons()
    for key in custom_lessons:
        # key format: U1W2C3
        if key.startswith(f"U{unit}W"):
            parts_w = key.split("W")[1]
            week_num = parts_w.split("C")[0]
            class_num = parts_w.split("C")[1]
            if week_num not in available:
                available[week_num] = set()
            available[week_num].add(class_num)

    # Converte sets para listas ordenadas
    return {w: sorted(cls, key=int) for w, cls in sorted(available.items(), key=lambda x: int(x[0]))}

def year_page(unit_num):
    st.markdown(f'<div class="simple-header"><h1>Year {unit_num} - Conteúdo</h1></div>', unsafe_allow_html=True)

    col_nav, col_content = st.columns([1, 3])
    with col_nav:
        if st.button("← Voltar para Aulas", use_container_width=True):
            st.session_state.current_page = "lessons"; st.rerun()

    with col_content:
        available = get_available_lessons_for_unit(str(unit_num))

        if not available:
            st.info(f"Nenhuma aula disponível para Year {unit_num}.")
            return

        with st.container(border=True):
            st.subheader("Configuração da Sessão")
            c1, c2 = st.columns(2)

            week_options = [f"Week {w}" for w in available.keys()]
            with c1:
                week = st.selectbox("Selecione a Semana", week_options)

            week_num_str = week.split()[1]
            class_options = [f"Class {c}" for c in available[week_num_str]]
            with c2:
                cls = st.selectbox("Selecione a Aula", class_options)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Iniciar Atividade com Kevin", type="primary", use_container_width=True):
                if inject_lesson_context(str(unit_num), week_num_str, cls.split()[1]):
                    st.session_state.current_page = "lesson_chat"; st.rerun()
                else:
                    st.error("Aula não encontrada.")

def lesson_chat_page():
    if not st.session_state.current_lesson:
        st.session_state.current_page = "lessons"; st.rerun(); return
    
    lesson = st.session_state.current_lesson
    
    # Header minimalista da aula
    st.markdown(f"""
    <div class="chat-header">
        <h2>Kevin (Assistant)</h2>
        <p>Year {lesson["year"]} - Week {lesson["week"]} - Class {lesson["class"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("Encerrar Sessão"):
            year = st.session_state.current_lesson.get("year", "2") if st.session_state.current_lesson else "2"
            st.session_state.current_lesson = None; st.session_state.chat_history = []; st.session_state.last_audio = None
            st.session_state.current_page = f"year_{year}"; st.rerun()
    
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
# PÁGINAS DE ADMINISTRAÇÃO
# ============================================================

def build_lesson_prompt(code, objetivos, vocabulario, gramatica, warmup_actions, development_actions, closure_actions):
    """Gera o prompt de contexto da aula a partir dos dados do formulário."""
    prompt = f"""=== CONTEXTO ESPECÍFICO DESTA AULA ({code} - Content Class) ===

OBJETIVOS: {objetivos}
VOCABULÁRIO: {vocabulario}
GRAMÁTICA: {gramatica}

PASSO A PASSO PARA O KEVIN CONDUZIR (Aguarde a resposta do Teacher ou da turma antes de pular de um passo para outro):

[ FASE 1: WARM UP ]
"""
    for i, action in enumerate(warmup_actions, 1):
        prompt += f"- Ação {i}: {action}\n"

    prompt += "\n[ FASE 2: DEVELOPMENT ]\n"
    for i, action in enumerate(development_actions, 1):
        prompt += f"- Ação {i}: {action}\n"

    prompt += "\n[ FASE 3: CLOSURE ]\n"
    for i, action in enumerate(closure_actions, 1):
        prompt += f"- Ação {i}: {action}\n"

    return prompt


def admin_add_lesson_page():
    st.markdown('<div class="simple-header"><h1>Adicionar Nova Aula</h1></div>', unsafe_allow_html=True)

    # Inicializa contadores de ações no session_state
    for phase in ["warmup", "development", "closure"]:
        key = f"admin_{phase}_count"
        if key not in st.session_state:
            st.session_state[key] = 1

    with st.container(border=True):
        st.subheader("Código da Aula")
        c1, c2, c3 = st.columns(3)
        with c1:
            unit = st.number_input("Unit (U)", min_value=1, max_value=10, value=1, step=1)
        with c2:
            week = st.number_input("Week (W)", min_value=1, max_value=52, value=1, step=1)
        with c3:
            class_num = st.number_input("Class (C)", min_value=1, max_value=10, value=1, step=1)

        lesson_code = f"U{unit}W{week}C{class_num}"
        st.markdown(f"**Código da aula:** `{lesson_code}`")

        # Verifica se já existe
        custom_lessons = load_custom_lessons()
        hardcoded_exists = False
        try:
            LESSON_SPECIFIC_CONTEXTS[f"year_{unit}"][f"week_{week}"][f"class_{class_num}"]
            hardcoded_exists = True
        except KeyError:
            pass

        if lesson_code in custom_lessons or hardcoded_exists:
            st.warning(f"Já existe uma aula com o código {lesson_code}. Ao salvar, ela será substituída.")

    with st.container(border=True):
        st.subheader("Conteúdo da Aula")
        objetivos = st.text_area("OBJETIVOS", placeholder='Ex: Fazer perguntas com "What\'s" e usar "a/an".')
        vocabulario = st.text_area("VOCABULÁRIO", placeholder="Ex: Clock, window, board, desk, picture, chair, notebook, backpack.")
        gramatica = st.text_area("GRAMÁTICA", placeholder='Ex: "What\'s this? It\'s a/an…".')

    # --- FASE 1: WARM UP ---
    with st.container(border=True):
        st.subheader("FASE 1: WARM UP")
        warmup_count = st.session_state.admin_warmup_count

        warmup_actions = []
        for i in range(warmup_count):
            action = st.text_area(
                f"Ação {i+1}", key=f"warmup_action_{i}",
                placeholder=f"Descreva a ação {i+1} do Warm Up..."
            )
            warmup_actions.append(action)

        col_add, col_rem, _ = st.columns([1, 1, 3])
        with col_add:
            if warmup_count < 10:
                if st.button("+ Ação", key="add_warmup"):
                    st.session_state.admin_warmup_count += 1; st.rerun()
        with col_rem:
            if warmup_count > 1:
                if st.button("- Ação", key="rem_warmup"):
                    st.session_state.admin_warmup_count -= 1; st.rerun()

    # --- FASE 2: DEVELOPMENT ---
    with st.container(border=True):
        st.subheader("FASE 2: DEVELOPMENT")
        dev_count = st.session_state.admin_development_count

        dev_actions = []
        for i in range(dev_count):
            action = st.text_area(
                f"Ação {i+1}", key=f"dev_action_{i}",
                placeholder=f"Descreva a ação {i+1} do Development..."
            )
            dev_actions.append(action)

        col_add, col_rem, _ = st.columns([1, 1, 3])
        with col_add:
            if dev_count < 10:
                if st.button("+ Ação", key="add_dev"):
                    st.session_state.admin_development_count += 1; st.rerun()
        with col_rem:
            if dev_count > 1:
                if st.button("- Ação", key="rem_dev"):
                    st.session_state.admin_development_count -= 1; st.rerun()

    # --- FASE 3: CLOSURE ---
    with st.container(border=True):
        st.subheader("FASE 3: CLOSURE")
        closure_count = st.session_state.admin_closure_count

        closure_actions = []
        for i in range(closure_count):
            action = st.text_area(
                f"Ação {i+1}", key=f"closure_action_{i}",
                placeholder=f"Descreva a ação {i+1} do Closure..."
            )
            closure_actions.append(action)

        col_add, col_rem, _ = st.columns([1, 1, 3])
        with col_add:
            if closure_count < 10:
                if st.button("+ Ação", key="add_closure"):
                    st.session_state.admin_closure_count += 1; st.rerun()
        with col_rem:
            if closure_count > 1:
                if st.button("- Ação", key="rem_closure"):
                    st.session_state.admin_closure_count -= 1; st.rerun()

    # --- SALVAR ---
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Salvar Aula", type="primary", use_container_width=True):
        # Validações
        warmup_filled = [a for a in warmup_actions if a.strip()]
        dev_filled = [a for a in dev_actions if a.strip()]
        closure_filled = [a for a in closure_actions if a.strip()]

        errors = []
        if not objetivos.strip():
            errors.append("Preencha os OBJETIVOS.")
        if not vocabulario.strip():
            errors.append("Preencha o VOCABULÁRIO.")
        if not gramatica.strip():
            errors.append("Preencha a GRAMÁTICA.")
        if len(warmup_filled) < 1:
            errors.append("Adicione pelo menos 1 ação no WARM UP.")
        if len(dev_filled) < 1:
            errors.append("Adicione pelo menos 1 ação no DEVELOPMENT.")
        if len(closure_filled) < 1:
            errors.append("Adicione pelo menos 1 ação no CLOSURE.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            prompt = build_lesson_prompt(
                lesson_code, objetivos.strip(), vocabulario.strip(), gramatica.strip(),
                warmup_filled, dev_filled, closure_filled
            )
            custom_lessons = load_custom_lessons()
            custom_lessons[lesson_code] = {
                "unit": unit,
                "week": week,
                "class": class_num,
                "objetivos": objetivos.strip(),
                "vocabulario": vocabulario.strip(),
                "gramatica": gramatica.strip(),
                "warmup": warmup_filled,
                "development": dev_filled,
                "closure": closure_filled,
                "prompt": prompt
            }
            save_custom_lessons(custom_lessons)

            # Reseta contadores
            for phase in ["warmup", "development", "closure"]:
                st.session_state[f"admin_{phase}_count"] = 1

            st.success(f"Aula {lesson_code} salva com sucesso!")
            st.markdown("**Prompt gerado:**")
            st.code(prompt, language=None)


def admin_list_lessons_page():
    st.markdown('<div class="simple-header"><h1>Aulas Criadas</h1></div>', unsafe_allow_html=True)

    custom_lessons = load_custom_lessons()

    if not custom_lessons:
        st.info("Nenhuma aula customizada foi criada ainda.")
        return

    for code, data in sorted(custom_lessons.items()):
        with st.expander(f"{code} — Unit {data['unit']}, Week {data['week']}, Class {data['class']}"):
            st.markdown(f"**Objetivos:** {data['objetivos']}")
            st.markdown(f"**Vocabulário:** {data['vocabulario']}")
            st.markdown(f"**Gramática:** {data['gramatica']}")

            st.markdown("**Warm Up:**")
            for i, a in enumerate(data['warmup'], 1):
                st.markdown(f"- Ação {i}: {a}")

            st.markdown("**Development:**")
            for i, a in enumerate(data['development'], 1):
                st.markdown(f"- Ação {i}: {a}")

            st.markdown("**Closure:**")
            for i, a in enumerate(data['closure'], 1):
                st.markdown(f"- Ação {i}: {a}")

            st.markdown("---")
            st.markdown("**Prompt completo:**")
            st.code(data['prompt'], language=None)

            if st.button(f"Excluir {code}", key=f"del_{code}"):
                del custom_lessons[code]
                save_custom_lessons(custom_lessons)
                st.rerun()


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
        page = st.session_state.current_page

        pages = {
            "home": home_page,
            "lessons": lessons_page,
            "lesson_chat": lesson_chat_page,
            "questions": questions_page,
            "help": help_page,
            "admin_add_lesson": admin_add_lesson_page,
            "admin_list_lessons": admin_list_lessons_page,
        }

        # Suporta year_1 .. year_10 dinamicamente
        if page.startswith("year_") and page not in pages:
            try:
                unit_num = int(page.replace("year_", ""))
                year_page(unit_num)
                return
            except ValueError:
                pass

        pages.get(page, home_page)()

if __name__ == "__main__":
    main()