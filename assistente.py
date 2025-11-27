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
    "storopack", "storo", "storo pack", "storo-pack", "storopak", "storopac",
    
    # Produtos principais
    "airplus", "air plus", "airplus bubble", "airplus cushion", "airplus void",
    "air-plus", "airplusminibubble", "air plus mini", "airplus mini bubble",
    "paperplus", "paper plus", "papillon", "classic",
    "foamplus", "foam plus", "bagpacker", "handpacker", "bag packer", "hand packer",
    "airmove", "airmove2", "airmove²", "airmove¹", "air move", "air move 2",
    "paperbubble", "paper bubble", "pillowpack", "pillow pack",
    "flobag", "flo bag", "renofill", "reno fill",
    
    # Materiais e produtos de enchimento
    "travesseiro", "almofada", "almofadado", "air pillow", "air cushion",
    "papel kraft", "papel proteção", "papel expandido", "papel cushion",
    "espuma", "foam", "poliuretano", "expandida",
    "filme", "filme plastico", "filme plástico", "filme reciclado", "filme compostavel",
    "void fill", "preenchimento", "amortecimento", "cushion",
    "bolha", "bubble", "bubble wrap", "plástico bolha", "plastico bolha",
    "saco", "sacola", "embalagem", "envelope",
    
    # Problemas com saquinhos/almofadas
    "saquinho", "saquinho murcho", "saquinho vazio", "saquinho furado",
    "saquinho nao enche", "saquinho não enche", "saquinho mole", "saquinho fraco",
    "murcho", "murcha", "murchos", "murchas", "vazio", "vazios", "vazia", "vazias",
    "nao sela", "não sela", "nao solda", "não solda", "sem solda", "sem selagem",
    "nao enche", "não enche", "nao infla", "não infla", "não preenche", "nao preenche",
    "esvaziando", "esvazia", "perde ar", "vazando ar", "fura", "furado", "furada",
    "desinflando", "desinfla", "sem ar", "pouco ar", "ar fraco", "inflação fraca",
    "enchimento ruim", "enchimento fraco", "mal selado", "selagem fraca",
    "bolha murcha", "bolha vazia", "bolha furada", "almofada murcha", "almofada vazia",
    "travesseiro murcho", "travesseiro vazio", "travesseiro furado",
    "cushion vazio", "cushion murcho", "void fill vazio", "void fill murcho",
    "nao protege", "não protege", "proteção ruim", "proteção fraca",
    
    # Problemas de selagem e soldagem
    "selo aberto", "selo frouxo", "selo fraco", "não fecha", "nao fecha",
    "abertura", "vazamento na solda", "solda ruim", "mal soldado", "sem vedação",
    "nao veda", "não veda", "vedação ruim", "vedação fraca",
    
    # Problemas de qualidade do produto
    "quebrado", "quebrada", "danificado", "danificada", "defeituoso", "defeituosa",
    "ruim", "qualidade ruim", "produto ruim", "material ruim", "filme ruim",
    "rasgado", "rasgada", "perfurado", "perfurada", "cortado", "cortada",
    "fino demais", "grosso demais", "espesso", "resistência baixa", "resistencia baixa",
    "fragil demais", "frágil demais", "estoura fácil", "estoura facil",
    
    # Problemas gerais de funcionamento
    "erro", "error", "code", "codigo", "código", "alarme", "alerta", "avaria", "defeito",
    "travado", "preso", "desalinhado", "desalinha", "entupido", "entupimento",
    "vazamento", "ar", "pressão", "pressao", "fraco", "nao funciona", "não funciona",
    "quebrou", "queimou", "nao liga", "não liga", "faz barulho", "ruido", "ruído",
    "pulsa", "falha", "intermitente", "parou", "trava", "emperrado", "emperrou",
    "nao sai", "não sai", "nao produz", "não produz", "parou de funcionar",
    
    # Erros específicos (E-xx)
    "e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9",
    "e10", "e11", "e12", "e13", "e14", "e15", "e20", "e25", "e30",
    "e-1", "e-2", "e-3", "e-4", "e-5", "e-10", "e-20",
    "erro e", "erro 1", "erro 2", "erro 3", "código de erro", "codigo de erro",
    "error code", "error e", "fault", "alarm",
    
    # Componentes e peças
    "sensor", "lâmina", "lamina", "rolo", "bobina", "teflon", "tubo", "mangueira",
    "válvula", "valvula", "motor", "fusivel", "fusível", "varistor",
    "injetor", "injector", "sealing", "selo", "heat seal", "selagem",
    "tensão", "tensao", "ajuste", "aperto", "parafuso", "porca",
    "óleo", "oleo", "lubrificante", "limpeza", "pó", "po", "poeira",
    "faca", "guilhotina", "cortador", "tesoura", "bico", "bocal",
    "resistência", "resistencia", "aquecedor", "termostato",
    "correia", "esteira", "guia", "trilho", "eixo",
    
    # Manutenção e cuidados
    "manutencao", "manutenção", "troca de peça", "troca de peca", "substituição", "substituicao",
    "reparo", "conserto", "ajuste", "regulagem", "calibração", "calibracao",
    "limpeza", "inspeção", "inspecao", "revisão", "revisao",
    "preventiva", "corretiva", "técnico", "tecnico", "assistência", "assistencia",
    
    # Processos e operações
    "embalagem", "embalar", "acondicionamento", "proteção", "protecao", "proteger",
    "expedição", "expedicao", "envio", "transporte", "logistica", "logística",
    "packing", "fulfillment", "cubagem", "armazém", "armazem", "estoque",
    "linha", "bancada", "bench", "bench de embalagem", "estação", "estacao",
    "separação", "separacao", "picking", "conferência", "conferencia",
    
    # Problemas operacionais
    "lento", "devagar", "velocidade baixa", "produção baixa", "producao baixa",
    "travando muito", "parando muito", "interrompendo", "atrasando",
    "desperdício", "desperdicio", "gasto alto", "consumo alto", "perda",
    
    # Qualidade e otimização
    "qualidade", "quebra", "dano", "danificado", "fragil", "frágil", "impacto",
    "otimizar", "reduzir", "diminuir", "melhorar", "eficiência", "eficiencia",
    "produtividade", "velocidade", "ergonomia", "economia",
    "rendimento", "performance", "desempenho",
    
    # Sustentabilidade - Materiais Reciclados
    "reciclado", "reciclável", "reciclavel", "reciclados", "recicláveis", "reciclaveis",
    "reciclado 30%", "reciclado 30", "30% reciclado", "30 reciclado",
    "reciclado 50%", "reciclado 50", "50% reciclado", "50 reciclado",
    "reciclado 100%", "reciclado 100", "100% reciclado", "100 reciclado",
    "30%", "50%", "100%", "trinta por cento", "cinquenta por cento", "cem por cento",
    "material reciclado", "conteúdo reciclado", "conteudo reciclado",
    "parcialmente reciclado", "totalmente reciclado", "100% reciclável",
    "pcr", "pir", "post consumer", "post-consumer", "pós-consumo", "pos-consumo",
    "post industrial", "post-industrial", "pós-industrial", "pos-industrial",
    
    # Sustentabilidade - Compostável
    "compostavel", "compostável", "compostaveis", "compostáveis",
    "compostagem", "compostável em casa", "compostavel em casa",
    "home compostable", "home compost", "compostagem doméstica", "compostagem domestica",
    "compostagem caseira", "compostável residencial", "compostavel residencial",
    "compostagem industrial", "industrial compostable", "compostável industrial",
    "compost", "compostage", "compostable at home", "compostable casa",
    "biodegradavel", "biodegradável", "biodegradáveis", "biodegraداveis",
    "biodecomposição", "biodecomposicao", "decomposição", "decomposicao",
    
    # Sustentabilidade - Certificações e Normas
    "certificado", "certificação", "certificacao", "norma", "padrão", "padrao",
    "astm d6400", "en 13432", "iso 14855", "din certco", "seedling",
    "ok compost", "ok compost home", "tuv austria", "bpi certified",
    "certificação ambiental", "certificacao ambiental", "selo verde",
    
    # Sustentabilidade - Termos Gerais
    "sustentável", "sustentavel", "sustentáveis", "sustentaveis",
    "eco", "ecológico", "ecologico", "ecológicos", "ecologicos",
    "verde", "green", "amigável ao meio ambiente", "amigavel ao meio ambiente",
    "eco-friendly", "eco friendly", "ecofriendly", "ambientalmente correto",
    "baixo impacto", "impacto zero", "zero waste", "lixo zero",
    "circular", "economia circular", "circularidade",
    "renovável", "renovavel", "renováveis", "renovaveis",
    "carbono neutro", "neutro em carbono", "carbon neutral",
    "pegada de carbono", "emissão zero", "emissao zero",
    
    # Sustentabilidade - Descarte e Reciclagem
    "descarte", "descartar", "descartável", "descartavel",
    "reciclagem", "reciclar", "reutilizável", "reutilizavel",
    "reutilizar", "reusar", "reuso", "reaproveitamento",
    "destinação", "destinacao", "destino final", "fim de vida",
    "ciclo de vida", "lifecycle", "life cycle",
    
    # Sustentabilidade - Alternativas
    "alternativa sustentável", "alternativa sustentavel",
    "substituir plastico", "substituir plástico", "sem plastico", "sem plástico",
    "plastic free", "livre de plastico", "livre de plástico",
    "isopor", "eps", "substituir isopor", "alternativa ao isopor",
    "papel vs plastico", "papel vs plástico", "papel ou plastico",
    
    # Instalação e configuração
    "instalação", "instalacao", "instalar", "configuração", "configuracao", "configurar",
    "setup", "montagem", "montar", "conexão", "conexao", "conectar",
    "elétrica", "eletrica", "voltagem", "tomada", "plugue", "cabo",
    "compressor", "ar comprimido", "pressão de ar", "pressao de ar",
    
    # Treinamento e suporte
    "como usar", "como funciona", "de que serve", "qual a diferença", "qual a diferenca",
    "recomenda", "recomendação", "recomendacao", "indicação", "indicacao",
    "aplicação", "aplicacao", "uso", "tutorial", "video", "vídeo",
    "manual", "especificação", "especificacao", "ficha técnica", "ficha tecnica",
    "tabela", "preço", "preco", "custo", "valor",
    "treinamento", "capacitação", "capacitacao", "curso",
    
    # Comparações e dúvidas
    "diferença", "diferenca", "comparação", "comparacao", "versus", "vs",
    "melhor", "pior", "vantagem", "desvantagem", "benefício", "beneficio",
    "escolher", "decidir", "opção", "opcao", "alternativa",
    
    # Segurança
    "segurança", "seguranca", "risco", "perigo", "cuidado", "atenção", "atencao",
    "epi", "protetor", "luva", "óculos", "oculos",
    
    # Problemas de fornecimento/abastecimento
    "acabou", "falta", "faltando", "sem material", "sem filme", "sem papel",
    "reposição", "reposicao", "recarregar", "reabastecer", "trocar bobina",
    "bobina acabou", "filme acabou", "rolo acabou",
    
    # Tipos de embalagem e aplicações
    "e-commerce", "ecommerce", "varejo", "indústria", "industria",
    "farmacêutica", "farmaceutica", "alimentício", "alimenticio", "cosmético", "cosmetico",
    "eletrônico", "eletronico", "automotivo", "têxtil", "textil",
    "vidro", "cerâmica", "ceramica", "peça delicada", "peca delicada",
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