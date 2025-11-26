from openai import OpenAI, RateLimitError
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ASSISTANT_PROMPT = """
Você é um assistente técnico especializado nos equipamentos de embalagens fornecidos pela empresa do Danilo.

Regras importantes:
- Sempre responda em português do Brasil.
- Explique em linguagem simples e direta.
- Sempre que for procedimento técnico, use passos numerados.
- Antes de qualquer intervenção física no equipamento, diga: "Desligue o equipamento da tomada."
- Use sempre que possível os documentos da base de conhecimento (file_search).
- Se a informação não estiver nos documentos, seja honesto e diga que não encontrou.
"""

VECTOR_STORE_ID = os.getenv("OPENAI_VECTOR_STORE_ID")


def responder_cliente(pergunta: str) -> str:
    texto = ASSISTANT_PROMPT + "\nPergunta do cliente: " + pergunta

    tools = []

    # Só ativa o file_search se a variável existir
    if VECTOR_STORE_ID:
        tools.append({
            "type": "file_search",
            "vector_store_ids": [VECTOR_STORE_ID],
        })

    try:
        resposta = client.responses.create(
            model="gpt-4.1-mini",
            input=texto,
            tools=tools if tools else None,
        )

        return resposta.output_text

    except RateLimitError:
        return "No momento estou sem créditos na API. Peça para o suporte verificar o plano/créditos da OpenAI."

    except Exception as e:
        return f"Ocorreu um erro ao falar com a IA: {e}"
