from openai import OpenAI, RateLimitError
from dotenv import load_dotenv
import os

# ============================ CONFIG ============================

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================ VECTOR STORE CONFIG ============================
# Coloque aqui o ID da sua Vector Store (onde está o PDF "Treinamento - Tecnico e Comercial.pdf")
# Para criar: vá em platform.openai.com > Storage > Vector Stores
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID", "")  # Ex: "vs_abc123..."

# ID do Assistant (se já tiver criado um)
ASSISTANT_ID = os.getenv("ASSISTANT_ID", "")  # Ex: "asst_abc123..."

# ============================ DADOS FIXOS ============================

CONTATO_EMAIL = "packaging.br@storopack.com"
CONTATO_TELEFONE = "(11) 5677-4699"

LOGISTICA_STOROPACK = {
    "endereco": "R. Agostino Togneri, 457 - Jurubatuba, São Paulo - SP, 04690-090",
    "horario": "09:00 às 12:00 e 13:00 às 16:00 (intervalo 12h–13h)"
}

VIDEOS_STOROPACK = {
    "airplus": {
        "titulo": "AIRplus - Travesseiro de Ar",
        "url": "https://www.youtube.com/watch?v=IbG1o-UbrtI"
    },
    "airmove": {
        "titulo": "AIRmove - Travesseiros de Ar (linha compacta)",
        "url": "https://www.youtube.com/watch?v=IbG1o-UbrtI"
    },
    "paperplus": {
        "titulo": "PAPERplus - Papel de Proteção",
        "url": "https://www.youtube.com/watch?v=a8iCa46yRu4"
    },
    "foamplus": {
        "titulo": "FOAMplus - Espuma Expandida",
        "url": "https://www.youtube.com/watch?v=bhVK8KCJihs"
    },
    "paperbubble": {
        "titulo": "PAPERbubble - Papel Almofadado",
        "url": "https://www.youtube.com/watch?v=TQYRcHj_v0E"
    }
}

# Configurações específicas de cada módulo
MODULOS_CONFIG = {
    "airplus": {
        "nome": "AIRplus",
        "descricao": "Travesseiros de ar (VOID, BUBBLE, CUSHION, WRAP)",
        "keywords": ["airplus", "void", "bubble", "cushion", "wrap", "travesseiro", "ar", "inflável", "inflar", "almofada de ar", "e1", "e2", "e3", "e4", "e5", "erro"],
        "prompt_extra": """
FOCO: Equipamentos AIRplus (VOID, BUBBLE, CUSHION, WRAP).

ERROS COMUNS E SOLUÇÕES RÁPIDAS:
• E1 - Problema no sensor de filme
• E2 - Falha na selagem
• E3 - Problema com pressão de ar
• E4 - Sensor de corte
• E5 - Superaquecimento

SEMPRE BUSQUE NO ARQUIVO "Treinamento - Tecnico e Comercial.pdf" para erros específicos.
"""
    },
    "paperplus": {
        "nome": "PAPERplus",
        "descricao": "Papel de proteção (Classic, Track, Papillon, PAPERbubble, Shooter, CX, Coiler)",
        "keywords": ["paperplus", "papel", "paper", "classic", "track", "papillon", "paperbubble", "kraft", "reciclado", "shooter", "cx", "coiler"],
        "prompt_extra": """
FOCO: Equipamentos PAPERplus (Classic, Track, Papillon, Shooter, CX, Coiler) e PAPERbubble.

PROBLEMAS COMUNS:
• Papel preso → Verificar tensão e alinhamento
• Corte irregular → Ajustar faca ou lâmina
• Travamento → Limpar rolos e verificar bobina
"""
    },
    "foamplus": {
        "nome": "FOAMplus",
        "descricao": "Espuma expandida (Bagpacker, Handpacker)",
        "keywords": ["foamplus", "foam", "espuma", "bagpacker", "handpacker", "poliuretano", "expansão", "química"],
        "prompt_extra": """
FOCO: Equipamentos FOAMplus (Bagpacker, Handpacker).

⚠️ SEMPRE ALERTAR: Use EPIs (luvas, óculos, avental)!

PROBLEMAS COMUNS:
• Espuma não expande → Verificar proporção química e temperatura
• Vazamento → Checar conexões e bicos
• Entupimento → Limpar bicos com solvente apropriado
"""
    },
    "airmove": {
        "nome": "AIRmove",
        "descricao": "Linha compacta de travesseiros de ar",
        "keywords": ["airmove", "compacto", "portátil", "move", "pequeno"],
        "prompt_extra": """
FOCO: Equipamento AIRmove (linha compacta).

PROBLEMAS COMUNS:
• Almofada não infla → Verificar filme e sensores
• Selagem fraca → Ajustar temperatura
• Máquina não liga → Checar fonte de alimentação
"""
    }
}

# ============================ PROMPT BASE (ESTILO WHATSAPP) ============================

ASSISTANT_PROMPT_BASE = f"""
Você é o Assistente Técnico da STOROpack Brasil.

ESTILO DE RESPOSTA (MUITO IMPORTANTE):
• Respostas CURTAS e DIRETAS, estilo WhatsApp
• Use quebras de linha para separar cada passo
• Máximo 5-6 linhas por resposta
• Não use parágrafos longos
• Use emojis com moderação (1-2 por resposta)

FORMATO DE RESPOSTA PARA PROBLEMAS:
```
🔧 [Nome do problema]

1. Primeiro passo
2. Segundo passo
3. Terceiro passo

⚠️ Dica: [dica importante]
```

FORMATO PARA ERROS (Ex: E3):
```
❌ Erro E3 - [Nome do erro]

Causa: [causa principal]

Solução:
1. Passo 1
2. Passo 2
3. Passo 3

Se persistir, ligue: {CONTATO_TELEFONE}
```

REGRAS:
• SEMPRE diga "Desligue da tomada" antes de qualquer intervenção física
• Seja objetivo e vá direto ao ponto
• Não repita informações
• Se não souber, diga que vai verificar

CONTATO:
• Tel: {CONTATO_TELEFONE}
• Email: {CONTATO_EMAIL}
"""

# ============================ FUNÇÕES AUXILIARES ============================

def limpar_formatacao(texto: str) -> str:
    """Remove marcações de markdown mas mantém quebras de linha."""
    texto = texto.replace("**", "")
    texto = texto.replace("*", "")
    texto = texto.replace("```", "")
    texto = texto.replace("###", "")
    texto = texto.replace("##", "")
    texto = texto.replace("#", "")
    return texto.strip()


def encontrar_videos(pergunta: str, modulo: str | None) -> list[dict]:
    """Retorna vídeos relevantes baseados no módulo."""
    videos = []
    
    if modulo:
        # Extrai o módulo base (sem submódulo)
        modulo_base = modulo.split("_")[0].lower()
        if modulo_base in VIDEOS_STOROPACK:
            videos.append(VIDEOS_STOROPACK[modulo_base])

    if not videos:
        p = pergunta.lower()
        for chave, video in VIDEOS_STOROPACK.items():
            if chave in p:
                videos.append(video)
                break

    return videos[:1]  # Só 1 vídeo para não poluir


def verificar_escopo_modulo(pergunta: str, modulo: str) -> bool:
    """Verifica se a pergunta está no escopo do módulo."""
    pergunta_lower = pergunta.lower()
    modulo_base = modulo.split("_")[0].lower()
    
    outros_modulos = {k: v for k, v in MODULOS_CONFIG.items() if k != modulo_base}
    
    for outro_modulo, config in outros_modulos.items():
        if outro_modulo in pergunta_lower:
            return False
    
    return True


def montar_prompt_modulo(modulo: str) -> str:
    """Monta o prompt específico para o módulo."""
    modulo_base = modulo.split("_")[0].lower()
    config = MODULOS_CONFIG.get(modulo_base)
    
    if not config:
        return ASSISTANT_PROMPT_BASE
    
    # Verifica se tem submódulo
    submódulo = ""
    if "_" in modulo:
        partes = modulo.split("_")
        submódulo = " ".join(partes[1:]).replace("_", " ").title()
    
    prompt = f"""
{ASSISTANT_PROMPT_BASE}

══════════════════════════════════
MÓDULO: {config['nome']} {submódulo}
══════════════════════════════════
{config['prompt_extra']}

LEMBRE-SE:
• Respostas curtas, estilo WhatsApp
• Quebra de linha entre cada passo
• Máximo 5-6 linhas
• Vá direto ao ponto!
"""
    return prompt


def responder_com_assistants_api(pergunta: str, modulo: str) -> str:
    """
    Usa a Assistants API com File Search para buscar no PDF.
    Requer ASSISTANT_ID e VECTOR_STORE_ID configurados.
    """
    try:
        # Cria uma thread
        thread = client.beta.threads.create()
        
        # Adiciona a mensagem do usuário
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=pergunta
        )
        
        # Executa o assistant
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
            instructions=montar_prompt_modulo(modulo)
        )
        
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for msg in messages.data:
                if msg.role == "assistant":
                    texto = msg.content[0].text.value
                    return limpar_formatacao(texto)
        
        return "Não consegui processar sua pergunta. Tente novamente."
        
    except Exception as e:
        print(f"Erro Assistants API: {e}")
        return None


def responder_com_chat_completions(pergunta: str, modulo: str) -> str:
    """Usa Chat Completions (fallback se não tiver Assistants configurado)."""
    prompt_sistema = montar_prompt_modulo(modulo)
    
    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": pergunta}
        ],
        max_tokens=400,  # Reduzido para respostas mais curtas
        temperature=0.5,  # Mais focado
    )
    
    return resposta.choices[0].message.content


# ============================ FUNÇÃO PRINCIPAL ============================

def responder_cliente(pergunta: str, modulo: str | None = None) -> str:
    """
    Responde ao cliente baseado no módulo selecionado.
    
    Args:
        pergunta: A pergunta do usuário
        modulo: O módulo ativo (ex: airplus, paperplus_classic, foamplus_bagpacker)
    
    Returns:
        Resposta formatada estilo WhatsApp
    """
    pergunta = (pergunta or "").strip()

    if not pergunta:
        return "Oi! 👋\n\nComo posso te ajudar?"

    if not modulo:
        return "Por favor, selecione um equipamento no menu. 🙂"

    modulo = modulo.lower()
    modulo_base = modulo.split("_")[0]

    # Verifica escopo
    if not verificar_escopo_modulo(pergunta, modulo):
        nome_modulo = MODULOS_CONFIG.get(modulo_base, {}).get("nome", modulo_base.upper())
        return (
            f"⚠️ Você está no módulo {nome_modulo}.\n\n"
            f"Para outros equipamentos, clique em 'Voltar' e selecione o módulo correto."
        )

    try:
        # Tenta usar Assistants API (com Vector Store) se configurado
        if ASSISTANT_ID and VECTOR_STORE_ID:
            resposta = responder_com_assistants_api(pergunta, modulo)
            if resposta:
                texto = limpar_formatacao(resposta)
            else:
                texto = limpar_formatacao(responder_com_chat_completions(pergunta, modulo))
        else:
            # Fallback para Chat Completions
            texto = limpar_formatacao(responder_com_chat_completions(pergunta, modulo))
        
        # Adiciona vídeo se relevante
        videos = encontrar_videos(pergunta, modulo)
        if videos:
            texto += f"\n\n📹 Vídeo de apoio:\n{videos[0]['url']}"

        return texto

    except RateLimitError:
        return "⏳ Muitas requisições.\n\nTente novamente em alguns segundos."
    except Exception as e:
        print(f"Erro: {e}")
        return f"❌ Erro ao processar.\n\nTente novamente ou ligue: {CONTATO_TELEFONE}"