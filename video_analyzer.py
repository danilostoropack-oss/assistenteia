"""
Analisador de Vídeo com IA para Storopack
Versão simplificada para economizar memória
"""

import os
import base64
import json
from dotenv import load_dotenv

load_dotenv()

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


def analisar_com_gemini_video(video_bytes, modulo, descricao=""):
    """Analisa vídeo diretamente com Gemini (suporta vídeo nativo)."""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return None, "GOOGLE_API_KEY não configurada"
        
        genai.configure(api_key=api_key)
        
        # Usar modelo que suporta vídeo
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        erros_modulo = ERROS_VISUAIS.get(modulo.split('_')[0], {})
        erros_lista = "\n".join([f"- {k}: {v['nome']} (sinais: {', '.join(v['sinais'])})" 
                                  for k, v in erros_modulo.items()])
        
        prompt = f"""Você é um técnico especialista em equipamentos Storopack.
Analise este vídeo de um equipamento {modulo.upper()} e identifique possíveis erros.

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

        # Enviar vídeo como bytes
        video_part = {
            "mime_type": "video/mp4",
            "data": base64.b64encode(video_bytes).decode('utf-8')
        }
        
        response = model.generate_content([prompt, video_part])
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
    Usa Gemini diretamente com vídeo (sem OpenCV).
    """
    
    if video_path:
        try:
            with open(video_path, 'rb') as f:
                video_bytes = f.read()
        except Exception as e:
            return f"❌ Erro ao ler vídeo: {str(e)}"
    
    if not video_bytes:
        return "❌ Nenhum vídeo fornecido."
    
    # Limitar tamanho do vídeo (max 20MB para Gemini)
    max_size = 20 * 1024 * 1024
    if len(video_bytes) > max_size:
        return "❌ Vídeo muito grande (máximo 20MB).\n\nEnvie um vídeo menor ou descreva o problema por texto."
    
    # Analisar com Gemini
    resultado, erro = analisar_com_gemini_video(video_bytes, modulo, descricao_cliente)
    
    if erro:
        return f"❌ {erro}\n\nDescreva o problema por texto ou ligue: (11) 5677-4699"
    
    return formatar_resposta(resultado, modulo)


if __name__ == "__main__":
    print("Video Analyzer para Storopack (versão lite)")
    print("Módulos:", list(ERROS_VISUAIS.keys()))
