"""
Analisador de Vídeo com IA para Storopack
Usa Google Gemini ou OpenAI GPT-4o Vision para analisar vídeos de erros
"""

import os
import base64
import tempfile
import json
from dotenv import load_dotenv

load_dotenv()

# Configurações
MAX_FRAMES = 10
FRAME_SIZE = (512, 512)

# Base de conhecimento de erros visuais por módulo
ERROS_VISUAIS = {
    "airplus": {
        "E1": {
            "nome": "Erro de Sensor de Filme",
            "sinais": ["LED vermelho aceso", "display mostrando E1", "filme desalinhado"],
            "solucao": "1. Desligue a máquina\n2. Verifique o alinhamento do filme\n3. Limpe o sensor com pano seco\n4. Religue e teste",
            "video": "https://www.youtube.com/watch?v=IbG1o-UbrtI"
        },
        "E2": {
            "nome": "Falha na Selagem",
            "sinais": ["almofadas não selam corretamente", "vazamento de ar", "selagem fraca"],
            "solucao": "1. Verifique a temperatura de selagem\n2. Limpe a barra de selagem\n3. Ajuste a pressão\n4. Teste com novo filme",
            "video": "https://www.youtube.com/watch?v=IbG1o-UbrtI"
        },
        "E3": {
            "nome": "Problema de Pressão de Ar",
            "sinais": ["almofadas murchas", "som de vazamento", "mangueiras soltas", "display E3"],
            "solucao": "1. Verifique conexões de ar\n2. Cheque mangueiras\n3. Limpe filtro de ar\n4. Ajuste pressão no regulador",
            "video": "https://www.youtube.com/watch?v=IbG1o-UbrtI"
        },
        "E4": {
            "nome": "Erro no Sensor de Corte",
            "sinais": ["filme não corta", "corte irregular", "lâmina travada"],
            "solucao": "1. Desligue a máquina\n2. Verifique a lâmina de corte\n3. Limpe resíduos\n4. Substitua lâmina se necessário",
            "video": "https://www.youtube.com/watch?v=IbG1o-UbrtI"
        },
        "E5": {
            "nome": "Superaquecimento",
            "sinais": ["máquina muito quente", "cheiro de queimado", "desligamento automático"],
            "solucao": "1. Desligue imediatamente\n2. Aguarde 30 minutos\n3. Verifique ventilação\n4. Limpe filtros de ar",
            "video": "https://www.youtube.com/watch?v=IbG1o-UbrtI"
        },
        "travamento": {
            "nome": "Travamento de Filme",
            "sinais": ["filme preso", "filme embolado", "máquina parada"],
            "solucao": "1. Desligue a máquina\n2. Abra a tampa\n3. Remova o filme preso\n4. Realinhe o filme\n5. Feche e teste",
            "video": "https://www.youtube.com/watch?v=IbG1o-UbrtI"
        }
    },
    "paperplus": {
        "papel_preso": {
            "nome": "Papel Preso",
            "sinais": ["papel amassado", "papel não sai", "travamento"],
            "solucao": "1. Desligue a máquina\n2. Abra a tampa traseira\n3. Remova o papel preso\n4. Verifique rolos\n5. Recarregue o papel",
            "video": "https://www.youtube.com/watch?v=a8iCa46yRu4"
        },
        "corte_irregular": {
            "nome": "Corte Irregular",
            "sinais": ["bordas irregulares", "corte torto", "lâmina gasta"],
            "solucao": "1. Verifique a lâmina\n2. Limpe resíduos\n3. Ajuste a pressão\n4. Substitua lâmina se necessário",
            "video": "https://www.youtube.com/watch?v=a8iCa46yRu4"
        }
    },
    "foamplus": {
        "espuma_nao_expande": {
            "nome": "Espuma Não Expande",
            "sinais": ["espuma líquida", "não forma volume", "mistura incorreta"],
            "solucao": "1. Verifique os químicos\n2. Cheque a proporção\n3. Limpe os bicos\n4. Ajuste a temperatura",
            "video": "https://www.youtube.com/watch?v=bhVK8KCJihs"
        },
        "vazamento": {
            "nome": "Vazamento de Químico",
            "sinais": ["líquido escorrendo", "poça no chão", "conexões molhadas"],
            "solucao": "1. Desligue imediatamente\n2. Ventile a área\n3. Limpe o vazamento\n4. Verifique conexões\n5. Chame suporte técnico",
            "video": "https://www.youtube.com/watch?v=bhVK8KCJihs"
        }
    },
    "airmove": {
        "E1": {
            "nome": "Erro de Sensor",
            "sinais": ["LED vermelho", "display E1"],
            "solucao": "1. Desligue a máquina\n2. Verifique sensores\n3. Limpe com pano seco\n4. Religue",
            "video": "https://www.youtube.com/watch?v=IbG1o-UbrtI"
        }
    }
}


def extrair_frames_video(video_path, max_frames=MAX_FRAMES):
    """Extrai frames de um vídeo usando OpenCV."""
    try:
        import cv2
        from PIL import Image
        import io
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None, "Não foi possível abrir o vídeo"
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames == 0:
            return None, "Vídeo sem frames"
        
        interval = max(1, total_frames // max_frames)
        
        frames = []
        frame_count = 0
        
        while len(frames) < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                pil_image.thumbnail(FRAME_SIZE, Image.Resampling.LANCZOS)
                
                buffer = io.BytesIO()
                pil_image.save(buffer, format="JPEG", quality=80)
                base64_frame = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                frames.append(base64_frame)
            
            frame_count += 1
        
        cap.release()
        
        if not frames:
            return None, "Não foi possível extrair frames"
        
        return frames, None
        
    except ImportError:
        return None, "OpenCV não instalado. Execute: pip install opencv-python"
    except Exception as e:
        return None, f"Erro ao processar vídeo: {str(e)}"


def extrair_frames_de_bytes(video_bytes, max_frames=MAX_FRAMES):
    """Extrai frames de bytes de vídeo."""
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name
        
        frames, erro = extrair_frames_video(tmp_path, max_frames)
        
        os.unlink(tmp_path)
        
        return frames, erro
        
    except Exception as e:
        return None, f"Erro ao processar vídeo: {str(e)}"


def analisar_com_gemini(frames, modulo, descricao=""):
    """Analisa frames usando Google Gemini."""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return None, "GOOGLE_API_KEY não configurada"
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        erros_modulo = ERROS_VISUAIS.get(modulo.split('_')[0], {})
        erros_lista = "\n".join([f"- {k}: {v['nome']} (sinais: {', '.join(v['sinais'])})" 
                                  for k, v in erros_modulo.items()])
        
        prompt = f"""Você é um técnico especialista em equipamentos Storopack.
Analise estas imagens de um equipamento {modulo.upper()} e identifique possíveis erros.

Erros conhecidos para este equipamento:
{erros_lista}

{f'Descrição do cliente: {descricao}' if descricao else ''}

Responda em JSON:
{{
    "erro_identificado": "codigo_do_erro ou null",
    "nome_erro": "nome do erro",
    "confianca": "alta/media/baixa",
    "sinais_detectados": ["sinal1", "sinal2"],
    "descricao": "breve descrição do que foi visto"
}}

Se não conseguir identificar um erro específico, retorne erro_identificado como null."""

        parts = [prompt]
        for frame_b64 in frames[:5]:
            parts.append({
                "mime_type": "image/jpeg",
                "data": frame_b64
            })
        
        response = model.generate_content(parts)
        texto = response.text
        
        try:
            texto = texto.replace("```json", "").replace("```", "").strip()
            resultado = json.loads(texto)
            return resultado, None
        except:
            return {"erro_identificado": None, "descricao": texto}, None
            
    except ImportError:
        return None, "google-generativeai não instalado"
    except Exception as e:
        return None, f"Erro no Gemini: {str(e)}"


def analisar_com_openai(frames, modulo, descricao=""):
    """Analisa frames usando OpenAI GPT-4o Vision."""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY não configurada"
        
        client = OpenAI(api_key=api_key)
        
        erros_modulo = ERROS_VISUAIS.get(modulo.split('_')[0], {})
        erros_lista = "\n".join([f"- {k}: {v['nome']} (sinais: {', '.join(v['sinais'])})" 
                                  for k, v in erros_modulo.items()])
        
        prompt = f"""Você é um técnico especialista em equipamentos Storopack.
Analise estas imagens de um equipamento {modulo.upper()} e identifique possíveis erros.

Erros conhecidos:
{erros_lista}

{f'Descrição do cliente: {descricao}' if descricao else ''}

Responda APENAS em JSON:
{{
    "erro_identificado": "codigo_do_erro ou null",
    "nome_erro": "nome do erro",
    "confianca": "alta/media/baixa",
    "sinais_detectados": ["sinal1", "sinal2"],
    "descricao": "breve descrição"
}}"""

        content = [{"type": "text", "text": prompt}]
        
        for frame_b64 in frames[:4]:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame_b64}",
                    "detail": "low"
                }
            })
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": content}],
            max_tokens=500
        )
        
        texto = response.choices[0].message.content
        
        try:
            texto = texto.replace("```json", "").replace("```", "").strip()
            resultado = json.loads(texto)
            return resultado, None
        except:
            return {"erro_identificado": None, "descricao": texto}, None
            
    except ImportError:
        return None, "openai não instalado"
    except Exception as e:
        return None, f"Erro no OpenAI: {str(e)}"


def formatar_resposta(resultado, modulo):
    """Formata a resposta da análise para exibição."""
    
    if not resultado:
        return "❌ Não foi possível analisar o vídeo.\n\nDescreva o problema por texto ou ligue: (11) 5677-4699"
    
    erro_id = resultado.get("erro_identificado")
    confianca = resultado.get("confianca", "baixa").upper()
    sinais = resultado.get("sinais_detectados", [])
    descricao = resultado.get("descricao", "")
    
    modulo_base = modulo.split('_')[0]
    erros_modulo = ERROS_VISUAIS.get(modulo_base, {})
    
    resposta = "🔍 ANÁLISE DO VÍDEO\n\n"
    resposta += f"✅ Confiança: {confianca}\n\n"
    
    if erro_id and erro_id in erros_modulo:
        erro_info = erros_modulo[erro_id]
        resposta += f"❌ Erro Identificado: {erro_info['nome']}\n\n"
        
        if sinais:
            resposta += "Sinais Detectados:\n"
            for sinal in sinais:
                resposta += f"• {sinal}\n"
            resposta += "\n"
        
        resposta += "---\n\n"
        resposta += f"🔧 SOLUÇÃO:\n\n{erro_info['solucao']}\n\n"
        
        if erro_info.get('video'):
            resposta += f"📹 Vídeo de apoio:\n{erro_info['video']}\n\n"
    else:
        resposta += f"Observação: {descricao}\n\n"
        resposta += "Não foi possível identificar um erro específico.\n"
        resposta += "Por favor, descreva o problema com mais detalhes.\n\n"
    
    resposta += "Se precisar de ajuda: (11) 5677-4699"
    
    return resposta


def analisar_video_erro(video_bytes=None, video_path=None, modulo="airplus", descricao_cliente=""):
    """
    Função principal para analisar vídeo de erro.
    """
    
    if video_bytes:
        frames, erro = extrair_frames_de_bytes(video_bytes)
    elif video_path:
        frames, erro = extrair_frames_video(video_path)
    else:
        return "❌ Nenhum vídeo fornecido."
    
    if erro:
        return f"❌ {erro}\n\nDescreva o problema por texto ou ligue: (11) 5677-4699"
    
    if not frames:
        return "❌ Não foi possível extrair frames do vídeo.\n\nTente enviar outro vídeo ou descreva o problema."
    
    # Tentar Gemini primeiro
    resultado, erro_gemini = analisar_com_gemini(frames, modulo, descricao_cliente)
    
    # Se falhar, tentar OpenAI
    if not resultado or erro_gemini:
        resultado, erro_openai = analisar_com_openai(frames, modulo, descricao_cliente)
        
        if not resultado:
            return f"❌ Erro na análise: {erro_openai or erro_gemini}\n\nDescreva o problema por texto ou ligue: (11) 5677-4699"
    
    return formatar_resposta(resultado, modulo)


if __name__ == "__main__":
    print("Video Analyzer para Storopack")
    print("Módulos:", list(ERROS_VISUAIS.keys()))
