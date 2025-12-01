from flask import Flask, send_from_directory, request, jsonify
from assistente import responder_cliente
import os

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

@app.route("/chat", methods=["POST"])
def chat_route():
    try:
        dados = request.get_json()
        mensagem = dados.get("mensagem", "").strip()
        modulo = dados.get("modulo", "").strip()

        if not mensagem:
            return jsonify({"resposta": "Por favor, envie uma mensagem."})

        resposta = responder_cliente(mensagem, modulo=modulo)
        return jsonify({"resposta": resposta})

    except Exception as e:
        return jsonify({"resposta": f"Erro: {str(e)}"})


@app.route("/analyze-video", methods=["POST"])
def analyze_video():
    """Endpoint para análise de vídeo com IA."""
    try:
        # Tenta importar o analisador de vídeo
        try:
            from video_analyzer import analisar_video_erro
            VIDEO_ENABLED = True
        except ImportError as e:
            print(f"Erro ao importar video_analyzer: {e}")
            VIDEO_ENABLED = False
        except Exception as e:
            print(f"Erro ao importar video_analyzer: {e}")
            VIDEO_ENABLED = False
        
        if not VIDEO_ENABLED:
            return jsonify({
                "resposta": "❌ Análise de vídeo não disponível no momento.\n\nPor favor, descreva o problema por texto ou ligue: (11) 5677-4699"
            })

        if 'video' not in request.files:
            return jsonify({"resposta": "Nenhum vídeo enviado."})

        video_file = request.files['video']
        modulo = request.form.get('modulo', 'airplus')
        descricao = request.form.get('descricao', '')

        if video_file.filename == '':
            return jsonify({"resposta": "Arquivo de vídeo inválido."})

        video_bytes = video_file.read()
        
        print(f"Recebido vídeo: {len(video_bytes)} bytes, módulo: {modulo}")

        resposta = analisar_video_erro(
            video_bytes=video_bytes,
            modulo=modulo,
            descricao_cliente=descricao
        )

        return jsonify({"resposta": resposta})

    except Exception as e:
        import traceback
        print(f"Erro ao analisar vídeo: {e}")
        print(traceback.format_exc())
        return jsonify({
            "resposta": "❌ Erro ao analisar vídeo.\n\nDescreva o problema por texto ou ligue: (11) 5677-4699"
        })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)