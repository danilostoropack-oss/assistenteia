# Assistente Tecnico de Equipamentos

## Como rodar localmente

1. Crie um arquivo .env com:

   OPENAI_API_KEY=SUAS_CHAVE_AQUI
   OPENAI_VECTOR_STORE_ID=se_quiser_usar_file_search

2. Ative o ambiente virtual:

   - Windows: ".venv\Scripts\activate"

3. Instale as dependencias:

   pip install -r requirements.txt

4. Rode o servidor Flask:

   python app.py

Acesse http://localhost:5000 no navegador.

## Deploy no Render

- Build Command: "pip install -r requirements.txt"
- Start Command: "gunicorn app:app"
