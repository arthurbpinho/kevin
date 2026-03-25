# Kevin - English Learning Platform

Plataforma educacional de inglês com interface de voz via OpenAI + Eleven Labs.

---

## Como rodar o projeto no seu computador (passo a passo)

### 1. Instale o Python

1. Acesse [python.org/downloads](https://www.python.org/downloads/) e baixe a versão mais recente (3.9 ou superior).
2. Durante a instalação, **marque a opção "Add Python to PATH"** (muito importante!).
3. Finalize a instalação normalmente.

Para verificar se deu certo, abra o **Prompt de Comando** (Windows) ou **Terminal** (Mac/Linux) e digite:

```bash
python --version
```

Deve aparecer algo como `Python 3.12.x`.

### 2. Instale o VS Code

1. Acesse [code.visualstudio.com](https://code.visualstudio.com/) e baixe o instalador.
2. Instale normalmente.
3. (Opcional) Instale a extensão **Python** dentro do VS Code para ter destaque de código e autocomplete.

### 3. Instale o Git

1. Acesse [git-scm.com/downloads](https://git-scm.com/downloads) e baixe o instalador para o seu sistema.
2. Instale com as opções padrão.

### 4. Baixe o projeto (clone o repositório)

1. Abra o **VS Code**.
2. Abra o terminal integrado: menu **Terminal > New Terminal** (ou `Ctrl + '`).
3. Navegue até a pasta onde deseja salvar o projeto. Exemplo:

```bash
cd Desktop
```

4. Clone o repositório:

```bash
git clone https://github.com/arthurbpinho/kevin.git
```

5. Entre na pasta do projeto:

```bash
cd kevin/kevin
```

6. No VS Code, abra essa pasta: menu **File > Open Folder** e selecione a pasta `kevin/kevin`.

### 5. Crie um ambiente virtual (recomendado)

No terminal do VS Code, execute:

```bash
python -m venv venv
```

Ative o ambiente virtual:

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```

Você verá `(venv)` no início da linha do terminal, indicando que o ambiente está ativo.

### 6. Instale as dependências

Com o ambiente virtual ativo, execute:

```bash
pip install -r requirements.txt
```

### 7. Configure as chaves de API

O projeto precisa de chaves de API para funcionar. Crie um arquivo chamado `.env` na raiz do projeto (mesma pasta do `app.py`) com o seguinte conteúdo:

```
OPENAI_API_KEY=sua_chave_openai_aqui
ELEVENLABS_API_KEY=sua_chave_elevenlabs_aqui
ELEVENLABS_VOICE_ID=seu_voice_id_aqui
ELEVENLABS_MODEL=seu_modelo_aqui
```

Substitua os valores pelas suas chaves reais.

- **OpenAI:** crie uma conta em [platform.openai.com](https://platform.openai.com/) e gere uma API key.
- **ElevenLabs:** crie uma conta em [elevenlabs.io](https://elevenlabs.io/) e obtenha sua API key e Voice ID.

### 8. Execute o projeto

No terminal do VS Code (com o ambiente virtual ativo), execute:

```bash
python -m streamlit run app.py
```

O navegador abrirá automaticamente com a aplicação rodando em `http://localhost:8501`.

---

## Resumo rápido dos comandos

```bash
git clone https://github.com/arthurbpinho/kevin.git
cd kevin/kevin
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
# crie o arquivo .env com suas chaves
python -m streamlit run app.py
```
