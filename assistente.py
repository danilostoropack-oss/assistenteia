from openai import OpenAI, RateLimitError
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===================== BIBLIOTECA DE VÍDEOS =====================

VIDEOS_STOROPACK = {
    "airplus": {
        "titulo": "AIRplus - Travesseiro de Ar",
        "url": "https://www.youtube.com/watch?v=IbG1o-UbrtI&list=PL5I2gNhCWwVIBUHXh4jHOKDU1RxAs6LHx&index=8&t=4s&pp=iAQB",
    },
    "paperplus": {
        "titulo": "PAPERplus - Papel de Proteção",
        "url": "https://www.youtube.com/watch?v=a8iCa46yRu4&list=PL5I2gNhCWwVIBUHXh4jHOKDU1RxAs6LHx&index=7&pp=iAQB",
    },
    "foamplus": {
        "titulo": "FOAMplus - Espuma Expandida",
        "url": "https://www.youtube.com/watch?v=bhVK8KCJihs&list=PL5I2gNhCWwVIBUHXh4jHOKDU1RxAs6LHx&index=11&t=2s&pp=iAQB",
    },
    "paperbubble": {
        "titulo": "PAPERbubble - Papel Almofadado",
        "url": "https://www.youtube.com/watch?v=TQYRcHj_v0E&list=PL5I2gNhCWwVIBUHXh4jHOKDU1RxAs6LHx&index=3&pp=iAQB",
    },
    "storopack": {
        "titulo": "Visão Geral STOROpack",
        "url": "https://www.youtube.com/watch?v=wa4ZO1Z3g2Q&list=PL5I2gNhCWwVIBUHXh4jHOKDU1RxAs6LHx&index=5&pp=iAQB",
    },
    "plasticos": {
        "titulo": "Plásticos - Filmes de Proteção",
        "url": "https://www.youtube.com/watch?v=suKamjQtuGI&list=PL5I2gNhCWwVIBUHXh4jHOKDU1RxAs6LHx&index=4&pp=iAQB",
    },
    "processo": {
        "titulo": "Processo de Embalagens STOROpack",
        "url": "https://www.youtube.com/watch?v=Vq1Wt_mUWQs&list=PL5I2gNhCWwVIBUHXh4jHOKDU1RxAs6LHx&index=6&pp=iAQB",
    },
}

# ===================== PROMPT DO ASSISTENTE (OTIMIZADO) =====================

ASSISTANT_PROMPT = """
Você é um assistente técnico da STOROpack Brasil. Ajude com equipamentos de proteção, 
processos de embalagem e soluções de proteção de produtos.

ESCOPO (responda apenas sobre):
• Equipamentos STOROpack (AIRplus, PAPERplus, FOAMplus, AIRmove, PAPERbubble)
• Materiais de proteção (papel, espuma, filmes, almofadas de ar)
• Problemas técnicos, erros de máquina, ajustes e manutenção
• Processos de embalagem, cubagem e otimizações
• Aplicações e recomendações comerciais

FORA DO ESCOPO (responda apenas isto):
"Posso ajudar só em assuntos técnicos e comerciais da Storopack. Envie sua dúvida sobre 
equipamentos, materiais ou processos de embalagem."

INSTRUÇÕES:
- Responda em português do Brasil, natural e conversacional
- Seja direto e resumido. Máximo 3-4 linhas por resposta principal
- Evite emojis, markdown excessivo ou formatações chamativas
- Se precisar listar passos, use números simples (1. 2. 3.)
- Se for orientar troca de peças, sempre avise: "Desligue o equipamento antes"
- Nunca mencione nomes de pessoas ou colegas
- Não invente códigos de erro ou especificações

TRATAMENTO DE PROBLEMAS:
- Pergunte detalhes sobre o problema (máquina, modelo, situação)
- Ofereça soluções práticas e rápidas
- Se for manutenção, sempre oriente sobre segurança primeiro
"""

# ===================== PALAVRAS-CHAVE OTIMIZADAS =====================

ALLOWED_KEYWORDS = [
    # Marca e variações
    "storopack", "storo", "storo pack", "storo-pack",

    # Produtos principais
    "airplus", "air plus", "airplus bubble", "airplus cushion", "airplus void",
    "paperplus", "paper plus", "papillon", "classic",
    "foamplus", "foam plus", "bagpacker", "handpacker",
    "airmove", "airmove2", "airmove²", "airmove¹", "air move",
    "paperbubble", "paper bubble", "pillowpack",

    # Materiais
    "travesseiro", "almofada", "almofadado", "air pillow", "air cushion",
    "papel kraft", "papel proteção", "papel expandido", "papel cushion",
    "espuma", "foam", "poliuretano", "expandida",
    "filme", "filme plastico", "filme plástico", "filme reciclado", "filme compostavel",
    "void fill", "preenchimento", "amortecimento", "cushion",

    # Problemas comuns
    "erro", "error", "code", "codigo", "alarme", "alerta", "avaria", "defeito",
    "travado", "preso", "desalinhado", "desalinha", "entupido", "entupimento",
    "vazamento", "ar", "pressão", "pressao", "fraco", "nao funciona", "não funciona",
    "quebrou", "queimou", "nao liga", "não liga", "faz barulho", "ruido", "ruído",
    "pulsa", "falha", "intermitente", "parou", "trava",

    # Erros específicos (E-xx)
    "e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9",
    "e10", "e11", "e12", "e13", "e14", "e15", "e20", "e25", "e30",
    "erro e", "erro 1", "erro 2", "código de erro", "codigo de erro",

    # Componentes e manutenção
    "sensor", "lâmina", "lamina", "rolo", "bobina", "teflon", "tubo", "mangueira",
    "válvula", "valvula", "motor", "fusivel", "fusível", "varistor",
    "injetor", "injector", "sealing", "selo", "heat seal", "selagem",
    "tensão", "tensao", "ajuste", "aperto", "parafuso", "porca",
    "óleo", "oleo", "lubrificante", "limpeza", "pó", "po", "poeira",

    # Manutenção e cuidados
    "manutencao", "manutenção", "troca de peça", "substituição", "reparo",
    "conserto", "ajuste", "regulagem", "limpeza", "inspeção", "inspecao",

    # Processos
    "embalagem", "embalar", "acondicionamento", "proteção", "protecao", "proteger",
    "expedição", "expedicao", "envio", "transporte", "logistica", "logística",
    "packing", "fulfillment", "cubagem", "armazém", "armazem", "estoque",
    "linha", "bancada", "bench", "bench de embalagem",

    # Qualidade e otimização
    "qualidade", "quebra", "dano", "danificado", "fragil", "frágil", "impacto",
    "otimizar", "reduzir", "diminuir", "melhorar", "eficiência", "eficiencia",
    "produtividade", "velocidade", "ergonomia", "economia",

    # Sustentabilidade
    "reciclado", "reciclado 30%", "biodegradavel", "biodegradável", "compostavel", "compostável",
    "sustentável", "sustentavel", "eco", "ecológico", "ecologico",

    # Genéricos relacionados
    "como usar", "como funciona", "de que serve", "qual a diferença", "recomenda",
    "aplicação", "aplicacao", "uso", "tutorial", "video", "vídeo",
    "manual", "especificação", "especificacao", "tabela", "preço", "preco",
]

def _esta_no_escopo(pergunta: str) -> bool:
    """Retorna True se a pergunta está ligada a Storopack/embalagens."""
    lower = pergunta.lower()
    return any(palavra in lower for palavra in ALLOWED_KEYWORDS)


def _encontrar_videos_relevantes(pergunta: str) -> list:
    """Busca vídeos relevantes baseado na pergunta."""
    lower = pergunta.lower()
    videos_encontrados = []
    
    palavras_chave_video = {
        "airplus": "airplus",
        "paperplus": "paperplus",
        "foamplus": "foamplus",
        "paperbubble": "paperbubble",
        "storopack": "storopack",
        "plastico": "plasticos",
        "filme": "plasticos",
        "processo": "processo",
    }
    
    for termo, chave in palavras_chave_video.items():
        if termo in lower and chave in VIDEOS_STOROPACK:
            videos_encontrados.append(VIDEOS_STOROPACK[chave])
    
    return videos_encontrados[:2]


def _formatar_resposta(texto_ia: str, videos: list) -> str:
    """Formata a resposta de forma natural e compacta."""
    resposta = texto_ia.strip()
    
    if videos:
        resposta += "\n\nVocê pode ver mais em detalhes nestes vídeos:"
        for video in videos:
            resposta += f"\n• {video['titulo']}\n  {video['url']}"
    
    return resposta


# ===================== FUNÇÃO PRINCIPAL =====================

def responder_cliente(pergunta: str) -> str:
    pergunta = pergunta.strip()

    if not pergunta:
        return "Qual é sua dúvida ou problema sobre os equipamentos e materiais Storopack?"

    if not _esta_no_escopo(pergunta):
        return (
            "Posso ajudar só em assuntos técnicos e comerciais da Storopack. "
            "Envie sua dúvida sobre equipamentos, materiais ou processos de embalagem."
        )

    try:
        # Chamada correta para a API do OpenAI
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": ASSISTANT_PROMPT},
                {"role": "user", "content": pergunta},
            ],
            max_tokens=500,
            temperature=0.7,
        )

        texto_ia = resposta.choices[0].message.content
        videos = _encontrar_videos_relevantes(pergunta)
        
        return _formatar_resposta(texto_ia, videos)

    except RateLimitError:
        return "No momento não consigo acessar o serviço. Verifique os créditos da OpenAI com o suporte."
    except Exception as e:
        return f"Erro ao acessar o serviço: {str(e)}"