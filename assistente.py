from openai import OpenAI, RateLimitError
from dotenv import load_dotenv
import os

# ============================ CONFIG ============================

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        "keywords": ["airplus", "void", "bubble", "cushion", "wrap", "travesseiro", "ar", "inflável", "inflar", "almofada de ar"],
        "prompt_extra": """
FOCO: Equipamentos AIRplus (VOID, BUBBLE, CUSHION, WRAP).
- Travesseiros de ar para preenchimento de vazios
- Diferentes modelos de almofadas
- Bobinas e filmes AIRplus
- Erros comuns: E1, E2, E3, E4, etc.
- Manutenção: troca de bobina, regulagem de selagem, limpeza de sensores
"""
    },
    "paperplus": {
        "nome": "PAPERplus",
        "descricao": "Papel de proteção (Classic, Track, Papillon, PAPERbubble)",
        "keywords": ["paperplus", "papel", "paper", "classic", "track", "papillon", "paperbubble", "kraft", "reciclado"],
        "prompt_extra": """
FOCO: Equipamentos PAPERplus (Classic, Track, Papillon) e PAPERbubble.
- Papel kraft para proteção e preenchimento
- Diferentes gramagens e larguras
- Manutenção: troca de bobina de papel, ajuste de corte, tensão do papel
- Problemas comuns: papel preso, corte irregular, travamento
"""
    },
    "foamplus": {
        "nome": "FOAMplus",
        "descricao": "Espuma expandida (Bagpacker, Handpacker)",
        "keywords": ["foamplus", "foam", "espuma", "bagpacker", "handpacker", "poliuretano", "expansão", "química"],
        "prompt_extra": """
FOCO: Equipamentos FOAMplus (Bagpacker, Handpacker).
- Espuma de poliuretano expandida in-loco
- Proteção moldada ao produto
- Manutenção: limpeza de bicos, proporção química, temperatura
- Problemas comuns: espuma não expande, vazamento, entupimento
- IMPORTANTE: Sempre alertar sobre uso de EPIs (luvas, óculos)
"""
    },
    "airmove": {
        "nome": "AIRmove",
        "descricao": "Linha compacta de travesseiros de ar",
        "keywords": ["airmove", "compacto", "portátil", "move", "pequeno"],
        "prompt_extra": """
FOCO: Equipamento AIRmove (linha compacta).
- Versão compacta para menor volume de produção
- Travesseiros de ar em formato menor
- Ideal para e-commerce e pequenas operações
- Manutenção similar ao AIRplus, porém simplificada
"""
    }
}

# ============================ PROMPT BASE ============================

ASSISTANT_PROMPT_BASE = f"""
Você é o Assistente Oficial da STOROpack Brasil, focado em orientar clientes sobre:

• Equipamentos: AIRplus (VOID, BUBBLE, CUSHION, WRAP), AIRmove, PAPERplus Classic, PAPERplus Track, PAPERplus Papillon, PAPERbubble, FOAMplus.
• Materiais de proteção: travesseiros de ar, papel de proteção, espuma, filmes, soluções sustentáveis, etc.
• Manutenção básica e operação dos equipamentos.
• Processos de embalagem, cubagem, ergonomia e otimização de linhas.
• Informações de logística, coleta e dúvidas gerais sobre a empresa.

CONTATO OFICIAL:
• Email: {CONTATO_EMAIL}
• Telefone: {CONTATO_TELEFONE}

LOGÍSTICA:
• Endereço: {LOGISTICA_STOROPACK["endereco"]}
• Horário: {LOGISTICA_STOROPACK["horario"]}

MANUTENÇÃO – O QUE VOCÊ PODE ORIENTAR:
1. Inicializar o equipamento.
2. Troca de modelo de bobina / filme.
3. Regulagem operacional (selagem, enchimento, velocidade).
4. Troca de peças simples (faca, correias, etc).
5. Orientação sobre erros e códigos no display.
6. Sempre mencione que existem vídeos de suporte.

REGRA DE SEGURANÇA (OBRIGATÓRIA):
• Antes de qualquer intervenção física: "Por segurança, desligue o equipamento da tomada antes de realizar qualquer intervenção."

ESTILO DE COMUNICAÇÃO:
• Responda em português do Brasil, com tom natural e profissional.
• Respostas objetivas, dinâmicas, próximas.
• Use listas numeradas quando for procedimento passo a passo.
• Pode usar 1 emoji discreto (🙂) quando fizer sentido.
• Não invente dados técnicos que não sabe.
"""

# ============================ FUNÇÕES AUXILIARES ============================

def limpar_formatacao(texto: str) -> str:
    """Remove marcações simples de markdown para ficar mais limpo."""
    return texto.replace("**", "").replace("*", "")


def encontrar_videos(pergunta: str, modulo: str | None) -> list[dict]:
    """Retorna vídeos relevantes baseados primeiro no módulo, depois no texto."""
    videos = []

    # Prioriza o módulo
    if modulo:
        chave = modulo.lower()
        if chave in VIDEOS_STOROPACK:
            videos.append(VIDEOS_STOROPACK[chave])

    # Se não encontrou nada pelo módulo, tenta por palavras
    if not videos:
        p = pergunta.lower()
        for chave, video in VIDEOS_STOROPACK.items():
            if chave in p:
                videos.append(video)

    return videos[:2]


def verificar_escopo_modulo(pergunta: str, modulo: str) -> bool:
    """
    Verifica se a pergunta está relacionada ao módulo selecionado.
    Retorna True se está no escopo, False se parece ser sobre outro módulo.
    """
    pergunta_lower = pergunta.lower()
    
    # Palavras que indicam outro módulo
    outros_modulos = {k: v for k, v in MODULOS_CONFIG.items() if k != modulo}
    
    for outro_modulo, config in outros_modulos.items():
        # Verifica se menciona explicitamente outro módulo
        if outro_modulo in pergunta_lower:
            return False
        # Verifica keywords específicas de outro módulo
        for keyword in config["keywords"]:
            if keyword in pergunta_lower and keyword not in MODULOS_CONFIG[modulo]["keywords"]:
                return False
    
    return True


def montar_prompt_modulo(modulo: str) -> str:
    """Monta o prompt específico para o módulo selecionado."""
    config = MODULOS_CONFIG.get(modulo)
    
    if not config:
        return ASSISTANT_PROMPT_BASE
    
    prompt_modulo = f"""
{ASSISTANT_PROMPT_BASE}

═══════════════════════════════════════════════════════
MÓDULO ATIVO: {config['nome']} - {config['descricao']}
═══════════════════════════════════════════════════════
{config['prompt_extra']}

IMPORTANTE:
- Você está atendendo ESPECIFICAMENTE sobre {config['nome']}.
- Foque suas respostas neste equipamento/linha de produtos.
- Se o cliente perguntar sobre OUTRO equipamento (que não seja {config['nome']}), 
  responda educadamente: "Você está no módulo {config['nome']}. Para dúvidas sobre 
  outros equipamentos, por favor volte ao menu inicial e selecione o módulo correto."
"""
    return prompt_modulo


# ============================ FUNÇÃO PRINCIPAL ============================

def responder_cliente(pergunta: str, modulo: str | None = None) -> str:
    """
    Responde ao cliente baseado no módulo selecionado.
    
    Args:
        pergunta: A pergunta do usuário
        modulo: O módulo ativo (airplus, paperplus, foamplus, airmove) - em minúsculo
    
    Returns:
        Resposta do assistente
    """
    pergunta = (pergunta or "").strip()

    if not pergunta:
        return "Oi! Como posso te ajudar hoje? 🙂"

    # Se não tem módulo, não deveria chegar aqui (interface bloqueia)
    # Mas por segurança, retorna mensagem padrão
    if not modulo:
        return "Por favor, selecione um equipamento no menu para começarmos. 🙂"

    # Normaliza o módulo para minúsculo
    modulo = modulo.lower()

    # Verifica se a pergunta está no escopo do módulo
    if not verificar_escopo_modulo(pergunta, modulo):
        nome_modulo = MODULOS_CONFIG.get(modulo, {}).get("nome", modulo.upper())
        return (
            f"Você está no módulo {nome_modulo}. "
            f"Para dúvidas sobre outros equipamentos, por favor clique em 'Voltar' "
            f"e selecione o módulo correto. 🙂"
        )

    # Monta o prompt específico do módulo
    prompt_sistema = montar_prompt_modulo(modulo)

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": pergunta}
            ],
            max_tokens=500,
            temperature=0.6,
        )

        texto = limpar_formatacao(resposta.choices[0].message.content)
        
        # Busca vídeos relevantes
        videos = encontrar_videos(pergunta, modulo)

        if videos:
            texto += "\n\nDá uma olhada nesse vídeo:\n"
            for v in videos:
                texto += f"{v['titulo']}\n{v['url']}\n"

        return texto

    except RateLimitError:
        return "Limite da API foi atingido. Tente novamente em alguns instantes."
    except Exception as e:
        return f"Erro ao acessar serviço: {e}"