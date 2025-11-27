from flask import Flask, render_template_string, request, jsonify
from assistente import responder_cliente

app = Flask(__name__)

LOGO_URL = "https://www.storopack.com.br/fileadmin/_processed_/4/9/csm_Storopack_Imagefilm_Thumbnail_118bf988a8.jpg"
ASSISTANT_IMG_URL = "https://media.licdn.com/dms/image/v2/D4D05AQHQVQD99MOOug/videocover-low/B4DZoVhdqdK0B4-/0/1761297687645?e=2147483647&v=beta&t=FzJaplIJOhL1snkcWii_p3X9dPGyaSw1hjupd_3URvE"

HTML = r"""
<!doctype html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <title>Assistente Tecnico Storopack</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='75' font-size='75' fill='%23005aa9'>S</text></svg>" type="image/svg+xml">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

    <style>
        :root {
            --sp-primary: #0066cc;
            --sp-primary-dark: #003066;
            --sp-secondary: #00cccc;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #0a1929, #0d2a47, #061e3e);
            min-height: 100vh;
            font-family: Inter, sans-serif;
            display: flex;
            justify-content: center;
        }

        .page-wrapper {
            width: 100%;
            max-width: 900px;
            padding: 24px;
        }

        .header-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 16px;
            border-bottom: 1px solid rgba(255,255,255,0.12);
            color: white;
        }

        .logo {
            height: 72px;
            border-radius: 6px;
        }

        .card {
            margin-top: 24px;
            background: white;
            border-radius: 12px;
            padding: 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }

        @media(max-width: 900px){
            .card { grid-template-columns: 1fr; }
        }

        #chat {
            height: 60vh;
            background: #f6f6f6;
            border-radius: 12px;
            padding: 12px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .msg-user span {
            background: linear-gradient(to right, #0ea5e9, #003066);
            color: white;
            padding: 10px 14px;
            border-radius: 14px;
            max-width: 80%;
            align-self: flex-end;
        }

        .msg-bot span {
            background: white;
            border: 1px solid #ddd;
            padding: 10px 14px;
            border-radius: 14px;
            max-width: 80%;
            align-self: flex-start;
        }

        .assistant-illustration img {
            width: 100%;
            max-width: 360px;
            border-radius: 12px;
        }

        form { display: flex; gap: 8px; margin-top: 12px; }
        #mensagem { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #ccc; }
        button { background: var(--sp-primary); border: none; padding: 12px 20px; color: white; border-radius: 8px; }
        @media(max-width: 900px){ form{ flex-direction: column; } button{ width:100%; } }
    </style>
</head>

<body>

<div class="page-wrapper">

    <div class="header-bar">
        <div style="display:flex; align-items:center; gap:14px;">
            <img src="{{ logo_url }}" class="logo">
            <div>
                <b style="font-size:20px;">STOROPACK</b><br>
                <span style="font-size:13px; opacity:.8;">Assistente Técnico</span>
            </div>
        </div>
    </div>

    <div class="card">
        <div>
            <h1 style="color:#0066cc; margin-top:0;">Central de Suporte</h1>
            <p>Atendimento inteligente para dúvidas técnicas.</p>

            <div id="chat">
                <div class="msg-bot"><span>Olá! Como posso ajudar hoje?</span></div>
            </div>

            <form id="form-chat">
                <input id="mensagem" placeholder="Descreva o problema…">
                <button>Enviar ➤</button>
            </form>
        </div>

        <div class="assistant-illustration">
            <img src="{{ assistant_img_url }}">
        </div>
    </div>

</div>

<script>
    const chat = document.getElementById("chat");
    const input = document.getElementById("mensagem");
    const form = document.getElementById("form-chat");

    function scroll(){ chat.scrollTop = chat.scrollHeight; }

    form.addEventListener("submit", e => {
        e.preventDefault();
        let msg = input.value.trim();
        if(!msg) return;

        chat.innerHTML += `<div class="msg-user"><span>${msg}</span></div>`;
        scroll();
        input.value = "";

        fetch("/chat", {
            method:"POST",
            headers:{ "Content-Type":"application/json" },
            body: JSON.stringify({ mensagem: msg })
        })
        .then(r=>r.json())
        .then(data=>{
            chat.innerHTML += `<div class="msg-bot"><span>${data.resposta}</span></div>`;
            scroll();
        })
        .catch(()=>{
            chat.innerHTML += `<div class="msg-bot"><span>Erro ao conectar.</span></div>`;
            scroll();
        });
    });
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML, logo_url=LOGO_URL, assistant_img_url=ASSISTANT_IMG_URL)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        dados = request.get_json()
        mensagem = dados.get("mensagem", "")
        if not mensagem.strip():
            return jsonify({"resposta": "Por favor, escreva sua dúvida."})
        resposta = responder_cliente(mensagem)
        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"resposta": f"Erro interno: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
