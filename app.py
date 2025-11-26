from flask import Flask, render_template_string, request, jsonify
from assistente import responder_cliente

app = Flask(__name__)

# 🔹 URLs fornecidas por você
LOGO_URL = "https://www.storopack.com.br/fileadmin/_processed_/4/9/csm_Storopack_Imagefilm_Thumbnail_118bf988a8.jpg"

ASSISTANT_IMG_URL = "https://media.licdn.com/dms/image/v2/D4D05AQHQVQD99MOOug/videocover-low/B4DZoVhdqdK0B4-/0/1761297687645?e=2147483647&v=beta&t=FzJaplIJOhL1snkcWii_p3X9dPGyaSw1hjupd_3URvE"


# ============================= HTML VIEW ======================================

HTML = """
<!doctype html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <title>Assistente Técnico Storopack</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Fonte Google -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

    <style>
        * {
            box-sizing: border-box;
        }
        body {
            margin: 0;
            padding: 0;
            font-family: "Inter", sans-serif;
            background: radial-gradient(circle at top left, #38bdf8 0, #1e293b 45%, #0f172a 100%);
            color: #0f172a;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .page-wrapper {
            width: 100%;
            max-width: 1100px;
            padding: 24px;
        }
        .card {
            background: #f8fafc;
            border-radius: 20px;
            display: grid;
            grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
            gap: 32px;
            padding: 28px;
            box-shadow:
                0 25px 50px -12px rgba(15, 23, 42, 0.45),
                0 0 0 1px rgba(148, 163, 184, 0.15);
            animation: fadeIn 0.6s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @media (max-width: 900px) {
            .card { grid-template-columns: 1fr; }
            .assistant-illustration { display: none; }
        }
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 16px;
        }
        .logo {
            height: 48px;
            border-radius: 10px;
            object-fit: contain;
        }
        .badge {
            background: #dbeafe;
            border-radius: 999px;
            padding: 5px 12px;
            font-size: 12px;
            color: #1e3a8a;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-weight: 600;
        }
        .badge-dot {
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: #22c55e;
        }
        h1 {
            margin: 0;
            font-size: 28px;
            color: #0f172a;
            font-weight: 700;
        }
        .subtitle {
            margin-top: 8px;
            margin-bottom: 10px;
            color: #475569;
            font-size: 14px;
        }
        .chat-wrapper {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        #chat {
            border-radius: 16px;
            background: #e2e8f0;
            padding: 12px;
            height: 330px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .msg-user,
        .msg-bot {
            display: flex;
            width: 100%;
        }
        .msg-user { justify-content: flex-end; }
        .msg-bot { justify-content: flex-start; }

        .msg-user span,
        .msg-bot span {
            max-width: 80%;
            padding: 9px 12px;
            border-radius: 14px;
            font-size: 14px;
            line-height: 1.35;
        }
        .msg-user span {
            background: #0284c7;
            color: white;
            border-bottom-right-radius: 4px;
        }
        .msg-bot span {
            background: white;
            color: #0f172a;
            border-bottom-left-radius: 4px;
        }
        form {
            display: flex;
            gap: 10px;
            margin-top: 4px;
        }
        #mensagem {
            flex: 1;
            padding: 10px 12px;
            border-radius: 999px;
            border: 1px solid #cbd5e1;
            font-size: 14px;
            outline: none;
        }
        #mensagem:focus {
            border-color: #0284c7;
            box-shadow: 0 0 0 1px rgba(14, 165, 233, 0.25);
        }
        button[type="submit"] {
            border-radius: 999px;
            border: none;
            padding: 10px 18px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            background: linear-gradient(to right, #0284c7, #22c55e);
            color: white;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 10px 25px rgba(14, 165, 233, 0.35);
            transition: 0.25s;
        }
        button[type="submit"]:hover {
            transform: scale(1.04);
        }
        .assistant-illustration {
            display: flex;
            flex-direction: column;
            gap: 12px;
            justify-content: center;
            align-items: center;
        }
        .assistant-illustration img {
            width: 300px;
            height: auto;
            object-fit: cover;
            border-radius: 18px;
            box-shadow:
                0 18px 40px rgba(15, 23, 42, 0.45),
                0 0 0 1px rgba(148, 163, 184, 0.3);
        }
        .caption {
            font-size: 13px;
            color: #475569;
            text-align: center;
        }
    </style>
</head>

<body>
<div class="page-wrapper">
    <div class="card">

        <!-- COLUNA DO CHAT -->
        <div>
            <div class="header">
                <img src="{{ logo_url }}" alt="Logo Storopack" class="logo">
                <div class="badge">
                    <span class="badge-dot"></span>
                    Assistente Técnico
                </div>
            </div>

            <h1>Central de Suporte Storopack</h1>
            <p class="subtitle">Dúvidas sobre operação, erros, instalação e manutenção.</p>

            <div class="chat-wrapper">
                <div id="chat">
                    <div class="msg-bot">
                        <span>Olá! 👋 Sou o assistente técnico da Storopack. Como posso ajudar hoje?</span>
                    </div>
                </div>

                <form id="form-chat">
                    <input type="text" id="mensagem" autocomplete="off"
                           placeholder="Descreva seu problema ou dúvida..." />
                    <button type="submit">Enviar ➤</button>
                </form>
            </div>
        </div>

        <!-- COLUNA DA IMAGEM -->
        <div class="assistant-illustration">
            <img src="{{ assistant_img_url }}" alt="Assistente Storopack">
            <div class="caption">
                Suporte inteligente para resolver problemas técnicos rapidamente.
            </div>
        </div>

    </div>
</div>

<script>
    const chat = document.getElementById("chat");
    const form = document.getElementById("form-chat");
    const input = document.getElementById("mensagem");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const text = input.value.trim();
        if (!text) return;

        addMessage("user", text);
        input.value = "";
        input.focus();

        try {
            const resposta = await fetch("/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ message: text })
            });

            const data = await resposta.json();
            addMessage("bot", data.answer || "Erro ao responder.");
        } catch (err) {
            addMessage("bot", "Ocorreu um erro ao falar com o servidor.");
        }
    });

    function addMessage(role, text) {
        const div = document.createElement("div");
        div.className = role === "user" ? "msg-user" : "msg-bot";
        const span = document.createElement("span");
        span.textContent = text;
        div.appendChild(span);
        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
    }
</script>

</body>
</html>
"""

# ============================ ROTAS FLASK ======================================

@app.route("/", methods=["GET"])
def index():
    return render_template_string(
        HTML,
        logo_url=LOGO_URL,
        assistant_img_url=ASSISTANT_IMG_URL
    )

@app.route("/chat", methods=["POST"])
def chat_route():
    data = request.get_json() or {}
    pergunta = data.get("message", "").strip()

    if not pergunta:
        return jsonify({"answer": "Digite uma pergunta."}), 400

    resposta = responder_cliente(pergunta)
    return jsonify({"answer": resposta})


# ========================= RODAR LOCALMENTE ===================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
