"""
Módulo de Análise Visual de Vídeos - Storopack
Analisa vídeos de erros enviados pelos clientes e identifica problemas.

Requisitos:
pip install google-generativeai opencv-python pillow python-dotenv

Configuração (.env):
GOOGLE_API_KEY=sua_chave_gemini
OPENAI_API_KEY=sua_chave_openai (fallback)
"""

import os
import base64
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ============================ CONFIGURAÇÃO ============================

# Tenta usar Gemini primeiro (melhor para vídeos), fallback para OpenAI
USE_GEMINI = True
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Configurações de extração de frames
MAX_FRAMES = 10  # Máximo de frames para análise
FRAME_INTERVAL = 2  # Segundos entre frames

# ============================ ERROS DE REFERÊNCIA ============================

# Base de conhecimento de erros visuais (descrições para a IA comparar)
ERROS_VISUAIS = {
    "airplus": {
        "E1": {
            "nome": "Erro de Sensor de Filme",
            "sinais_visuais": [
                "LED vermelho piscando",
                "Display mostrando E1",
                "Filme parado ou desalinhado",
                "Sensor com sujeira visível"
            ],
            "solucao": """
🔧 Erro E1 - Sensor de Filme

1. Desligue da tomada ⚡
2. Abra a tampa do sensor
3. Limpe com pano seco
4. Verifique alinhamento do filme
5. Religue e teste

📹 Vídeo: https://youtube.com/watch?v=xxx
"""
        },
        "E2": {
            "nome": "Falha na Selagem",
            "sinais_visuais": [
                "Display mostrando E2",
                "Almofadas não selando",
                "Vazamento de ar nas almofadas",
                "Barra de selagem com resíduos"
            ],
            "solucao": """
🔧 Erro E2 - Falha na Selagem

1. Desligue da tomada ⚡
2. Espere esfriar (5 min)
3. Limpe barra de selagem
4. Verifique temperatura no menu
5. Teste com filme novo

📹 Vídeo: https://youtube.com/watch?v=xxx
"""
        },
        "E3": {
            "nome": "Problema de Pressão de Ar",
            "sinais_visuais": [
                "Display mostrando E3",
                "Almofadas murchas ou fracas",
                "Som de ar vazando",
                "Compressor fazendo barulho estranho",
                "Mangueiras soltas ou dobradas"
            ],
            "solucao": """
🔧 Erro E3 - Pressão de Ar

1. Desligue da tomada ⚡
2. Cheque mangueiras de ar
3. Verifique conexões
4. Limpe filtro de ar
5. Religue e teste

Se persistir: (11) 5677-4699

📹 Vídeo: https://youtube.com/watch?v=IbG1o-UbrtI
"""
        },
        "E4": {
            "nome": "Erro no Sensor de Corte",
            "sinais_visuais": [
                "Display mostrando E4",
                "Filme não corta",
                "Corte irregular",
                "Lâmina travada"
            ],
            "solucao": """
🔧 Erro E4 - Sensor de Corte

1. Desligue da tomada ⚡
2. Verifique a lâmina
3. Limpe área de corte
4. Cheque sensor óptico
5. Teste o corte manual

📹 Vídeo: https://youtube.com/watch?v=xxx
"""
        },
        "E5": {
            "nome": "Superaquecimento",
            "sinais_visuais": [
                "Display mostrando E5",
                "Máquina quente ao toque",
                "Cheiro de queimado",
                "Ventilador não funciona"
            ],
            "solucao": """
⚠️ Erro E5 - Superaquecimento

1. DESLIGUE IMEDIATAMENTE ⚡
2. Aguarde 30 minutos
3. Verifique ventilação
4. Limpe filtros de ar
5. Não obstrua saídas de ar

ATENÇÃO: Se persistir, NÃO use!
Ligue: (11) 5677-4699

📹 Vídeo: https://youtube.com/watch?v=xxx
"""
        },
        "travamento": {
            "nome": "Travamento de Filme",
            "sinais_visuais": [
                "Filme embolado",
                "Filme preso nos rolos",
                "Máquina parada",
                "Ruído de motor forçando"
            ],
            "solucao": """
🔧 Filme Travado

1. Desligue da tomada ⚡
2. Abra a tampa
3. Remova filme embolado
4. Verifique rolos
5. Recoloque filme corretamente

📹 Vídeo: https://youtube.com/watch?v=IbG1o-UbrtI
"""
        }
    },
    "paperplus": {
        "papel_preso": {
            "nome": "Papel Preso",
            "sinais_visuais": [
                "Papel amassado dentro da máquina",
                "Papel não sai",
                "Rolos parados",
                "Barulho de papel rasgando"
            ],
            "solucao": """
🔧 Papel Preso

1. Desligue da tomada ⚡
2. Abra tampa traseira
3. Remova papel com cuidado
4. Verifique rolos
5. Recoloque bobina

📹 Vídeo: https://youtube.com/watch?v=a8iCa46yRu4
"""
        },
        "corte_irregular": {
            "nome": "Corte Irregular",
            "sinais_visuais": [
                "Papel com bordas irregulares",
                "Corte não completo",
                "Lâmina visível desgastada"
            ],
            "solucao": """
🔧 Corte Irregular

1. Desligue da tomada ⚡
2. Verifique lâmina de corte
3. Limpe área de corte
4. Ajuste pressão da lâmina
5. Substitua se desgastada

📹 Vídeo: https://youtube.com/watch?v=a8iCa46yRu4
"""
        }
    },
    "foamplus": {
        "espuma_nao_expande": {
            "nome": "Espuma Não Expande",
            "sinais_visuais": [
                "Espuma sai líquida",
                "Não forma volume",
                "Cor diferente do normal"
            ],
            "solucao": """
🔧 Espuma Não Expande

⚠️ USE EPIs (luvas, óculos)!

1. Verifique temperatura (20-25°C)
2. Cheque proporção A:B
3. Agite os componentes
4. Limpe bicos de mistura
5. Teste em pequena quantidade

📹 Vídeo: https://youtube.com/watch?v=bhVK8KCJihs
"""
        },
        "vazamento": {
            "nome": "Vazamento de Químico",
            "sinais_visuais": [
                "Líquido escorrendo",
                "Manchas no chão",
                "Conexões molhadas"
            ],
            "solucao": """
⚠️ VAZAMENTO - ATENÇÃO!

1. DESLIGUE IMEDIATAMENTE ⚡
2. Use EPIs (luvas, óculos)
3. Ventile o ambiente
4. NÃO toque no químico
5. Ligue: (11) 5677-4699

📹 Vídeo: https://youtube.com/watch?v=bhVK8KCJihs
"""
        }
    }
}


# ============================ FUNÇÕES DE EXTRAÇÃO DE FRAMES ============================

def extrair_frames_video(video_path: str, max_frames: int = MAX_FRAMES) -> list[str]:
    """
    Extrai frames de um vídeo e retorna como lista de base64.
    
    Args:
        video_path: Caminho do arquivo de vídeo
        max_frames: Número máximo de frames a extrair
    
    Returns:
        Lista de strings base64 das imagens
    """
    try:
        import cv2
    except ImportError:
        raise ImportError("Instale opencv-python: pip install opencv-python")
    
    frames_base64 = []
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Não foi possível abrir o vídeo: {video_path}")
    
    # Pega informações do vídeo
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    # Calcula intervalo entre frames
    if duration <= 0:
        interval = 1
    else:
        interval = max(1, int(total_frames / max_frames))
    
    frame_count = 0
    extracted = 0
    
    while cap.isOpened() and extracted < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % interval == 0:
            # Redimensiona para economizar tokens
            frame = cv2.resize(frame, (512, 512))
            
            # Converte para base64
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            frames_base64.append(frame_base64)
            extracted += 1
        
        frame_count += 1
    
    cap.release()
    return frames_base64


def extrair_frames_de_bytes(video_bytes: bytes, max_frames: int = MAX_FRAMES) -> list[str]:
    """
    Extrai frames de bytes de vídeo (para upload via web).
    """
    # Salva temporariamente
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        tmp.write(video_bytes)
        tmp_path = tmp.name
    
    try:
        frames = extrair_frames_video(tmp_path, max_frames)
    finally:
        os.unlink(tmp_path)  # Remove arquivo temporário
    
    return frames


# ============================ ANÁLISE COM GEMINI ============================

def analisar_com_gemini(frames_base64: list[str], modulo: str, descricao_cliente: str = "") -> dict:
    """
    Analisa frames usando Google Gemini.
    
    Args:
        frames_base64: Lista de frames em base64
        modulo: Módulo do equipamento (airplus, paperplus, etc.)
        descricao_cliente: Descrição opcional do problema pelo cliente
    
    Returns:
        Dict com erro_identificado, confianca, solucao
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("Instale google-generativeai: pip install google-generativeai")
    
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY não configurada no .env")
    
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Monta contexto dos erros conhecidos
    erros_modulo = ERROS_VISUAIS.get(modulo.split("_")[0], {})
    erros_conhecidos = "\n".join([
        f"- {codigo}: {info['nome']} - Sinais: {', '.join(info['sinais_visuais'])}"
        for codigo, info in erros_modulo.items()
    ])
    
    prompt = f"""
Você é um técnico especialista em equipamentos Storopack ({modulo.upper()}).

ERROS CONHECIDOS DESTE EQUIPAMENTO:
{erros_conhecidos}

TAREFA:
Analise estas imagens/frames de um vídeo enviado por um cliente.
Identifique qual erro está ocorrendo baseado nos sinais visuais.

{f"DESCRIÇÃO DO CLIENTE: {descricao_cliente}" if descricao_cliente else ""}

RESPONDA APENAS NO FORMATO JSON:
{{
    "erro_identificado": "código do erro (ex: E3) ou 'desconhecido'",
    "nome_erro": "nome do erro",
    "confianca": "alta/media/baixa",
    "sinais_detectados": ["sinal 1", "sinal 2"],
    "descricao": "breve descrição do que foi visto"
}}
"""
    
    # Prepara as imagens para o Gemini
    import PIL.Image
    import io
    
    images = []
    for frame_b64 in frames_base64[:5]:  # Limita a 5 frames
        img_bytes = base64.b64decode(frame_b64)
        img = PIL.Image.open(io.BytesIO(img_bytes))
        images.append(img)
    
    # Envia para análise
    response = model.generate_content([prompt] + images)
    
    # Parse da resposta
    try:
        import json
        # Extrai JSON da resposta
        texto = response.text
        # Tenta encontrar o JSON na resposta
        inicio = texto.find('{')
        fim = texto.rfind('}') + 1
        if inicio >= 0 and fim > inicio:
            resultado = json.loads(texto[inicio:fim])
        else:
            resultado = {
                "erro_identificado": "desconhecido",
                "confianca": "baixa",
                "descricao": texto
            }
    except:
        resultado = {
            "erro_identificado": "desconhecido",
            "confianca": "baixa",
            "descricao": response.text
        }
    
    return resultado


# ============================ ANÁLISE COM OPENAI GPT-4o ============================

def analisar_com_openai(frames_base64: list[str], modulo: str, descricao_cliente: str = "") -> dict:
    """
    Analisa frames usando OpenAI GPT-4o Vision (fallback).
    """
    from openai import OpenAI
    
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY não configurada no .env")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Monta contexto dos erros conhecidos
    erros_modulo = ERROS_VISUAIS.get(modulo.split("_")[0], {})
    erros_conhecidos = "\n".join([
        f"- {codigo}: {info['nome']} - Sinais: {', '.join(info['sinais_visuais'])}"
        for codigo, info in erros_modulo.items()
    ])
    
    prompt = f"""
Você é um técnico especialista em equipamentos Storopack ({modulo.upper()}).

ERROS CONHECIDOS:
{erros_conhecidos}

Analise as imagens e identifique o erro. 
{f"Cliente disse: {descricao_cliente}" if descricao_cliente else ""}

Responda em JSON:
{{"erro_identificado": "código", "nome_erro": "nome", "confianca": "alta/media/baixa", "sinais_detectados": [], "descricao": "..."}}
"""
    
    # Prepara mensagens com imagens
    content = [{"type": "text", "text": prompt}]
    
    for frame_b64 in frames_base64[:4]:  # Limita a 4 frames (custo)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{frame_b64}",
                "detail": "low"  # Usa low detail para economizar tokens
            }
        })
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=500
    )
    
    # Parse da resposta
    try:
        import json
        texto = response.choices[0].message.content
        inicio = texto.find('{')
        fim = texto.rfind('}') + 1
        if inicio >= 0 and fim > inicio:
            resultado = json.loads(texto[inicio:fim])
        else:
            resultado = {"erro_identificado": "desconhecido", "descricao": texto}
    except:
        resultado = {"erro_identificado": "desconhecido", "descricao": response.choices[0].message.content}
    
    return resultado


# ============================ FUNÇÃO PRINCIPAL ============================

def analisar_video_erro(
    video_bytes: bytes = None,
    video_path: str = None,
    modulo: str = "airplus",
    descricao_cliente: str = ""
) -> str:
    """
    Função principal para analisar vídeo de erro.
    
    Args:
        video_bytes: Bytes do vídeo (upload web)
        video_path: Caminho do arquivo de vídeo
        modulo: Módulo do equipamento
        descricao_cliente: Descrição do problema pelo cliente
    
    Returns:
        Resposta formatada com diagnóstico e solução
    """
    try:
        # Extrai frames
        if video_bytes:
            frames = extrair_frames_de_bytes(video_bytes)
        elif video_path:
            frames = extrair_frames_video(video_path)
        else:
            return "❌ Nenhum vídeo fornecido."
        
        if not frames:
            return "❌ Não foi possível extrair frames do vídeo."
        
        # Tenta análise com Gemini primeiro
        resultado = None
        if USE_GEMINI and GOOGLE_API_KEY:
            try:
                resultado = analisar_com_gemini(frames, modulo, descricao_cliente)
            except Exception as e:
                print(f"Erro Gemini: {e}")
        
        # Fallback para OpenAI
        if not resultado and OPENAI_API_KEY:
            try:
                resultado = analisar_com_openai(frames, modulo, descricao_cliente)
            except Exception as e:
                print(f"Erro OpenAI: {e}")
        
        if not resultado:
            return "❌ Não foi possível analisar o vídeo. Tente novamente ou descreva o problema."
        
        # Busca solução na base de conhecimento
        erro_id = resultado.get("erro_identificado", "desconhecido").lower()
        modulo_base = modulo.split("_")[0].lower()
        erros_modulo = ERROS_VISUAIS.get(modulo_base, {})
        
        # Procura o erro na base
        solucao = None
        for codigo, info in erros_modulo.items():
            if codigo.lower() == erro_id or erro_id in codigo.lower():
                solucao = info.get("solucao", "")
                break
        
        # Monta resposta
        confianca = resultado.get("confianca", "média")
        sinais = resultado.get("sinais_detectados", [])
        descricao = resultado.get("descricao", "")
        nome_erro = resultado.get("nome_erro", erro_id.upper())
        
        resposta = f"""🔍 **ANÁLISE DO VÍDEO**

{"✅" if confianca == "alta" else "⚠️"} Confiança: {confianca.upper()}

**Erro Identificado:** {nome_erro}

**Sinais Detectados:**
{chr(10).join(f"• {s}" for s in sinais) if sinais else "• Análise visual realizada"}

{descricao}

---

{solucao if solucao else f"Não encontrei solução específica para esse erro. Por favor, ligue: (11) 5677-4699"}
"""
        
        return resposta.replace("**", "")  # Remove markdown
        
    except Exception as e:
        return f"❌ Erro ao processar vídeo: {str(e)}\n\nPor favor, descreva o problema ou ligue: (11) 5677-4699"


# ============================ TESTE ============================

if __name__ == "__main__":
    # Teste com um vídeo local
    # resultado = analisar_video_erro(video_path="teste.mp4", modulo="airplus")
    # print(resultado)
    
    print("Módulo de análise de vídeo carregado!")
    print(f"Gemini configurado: {'Sim' if GOOGLE_API_KEY else 'Não'}")
    print(f"OpenAI configurado: {'Sim' if OPENAI_API_KEY else 'Não'}")