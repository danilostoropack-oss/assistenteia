from flask import Flask, render_template_string, request, jsonify
from assistente import responder_cliente

app = Flask(__name__)

# URLs fornecidas
LOGO_URL = "https://www.storopack.com.br/fileadmin/_processed_/4/9/csm_Storopack_Imagefilm_Thumbnail_118bf988a8.jpg"
ASSISTANT_IMG_URL = "https://media.licdn.com/dms/image/v2/D4D05AQHQVQD99MOOug/videocover-low/B4DZoVhdqdK0B4-/0/1761297687645?e=2147483647&v=beta&t=FzJaplIJOhL1snkcWii_p3X9dPGyaSw1hjupd_3URvE"


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
        :root {
            --sp-blue: #005aa9;
            --sp-blue-light: #e0edfb;
            --sp-bg-dark: #020617;
            --sp-bg-mid: #020c1b;
            --sp-text-main: #e5f0ff;
            --sp-text-soft: #94a3b8;
        }

        * {
            box-sizing: border-box;
        }
        
        body {
            margin: 0;
            padding: 0;
            font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: stretch;
            justify-content: center;
            background:
                radial-gradient(circle at top left, rgba(56,189,248,0.25) 0, transparent 50%),
                radial-gradient(circle at bottom right, rgba(59,130,246,0.25) 0, transparent 55%),
                #020617;
            color: var(--sp-text-main);
        }

        .grid-overlay {
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(rgba(148,163,184,0.06) 1px, transparent 1px),
                linear-gradient(90deg, rgba(148,163,184,0.06) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
            opacity: 0.8;
            z-index: 0;
        }

        .page-wrapper {
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 1180px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .header-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .logo {
            height: 44px;
            border-radius: 10px;
            object-fit: cover;
            box-shadow: 0 0 0 1px rgba(148, 163, 184, 0.4);
        }

        .header-text-main {
            font-size: 15px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #e2ecff;
        }

        .header-text-sub {
            font-size: 12px;
            color: var(--sp-text-soft);
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .badge {
            background: rgba(224, 237, 251, 0.08);
            border-radius: 999px;
            padding: 5px 12px;
            font-size: 12px;
            color: #c7ddff;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-weight: 500;
            border: 1px solid rgba(148, 163, 184, 0.5);
            backdrop-filter: blur(10px);
        }
        
        .badge-dot {
            width: 9px;
            height: 9px;
            border-radius: 999px;
            background: #22c55e;
            box-shadow: 0 0 8px rgba(34,197,94,0.9);
        }

        .phone {
            font-size: 12px;
            color: var(--sp-text-soft);
        }
        
        .phone strong {
            color: #e5f0ff;
        }

        .card {
            margin-top: 4px;
            background: radial-gradient(circle at top left, rgba(15,23,42,0.75) 0, rgba(15,23,42,0.95) 55%);
            border-radius: 20px;
            display: grid;
            grid-template-columns: minmax(0, 1.35fr) minmax(0, 1fr);
            gap: 28px;
            padding: 22px 22px 20px 22px;
            box-shadow:
                0 30px 60px rgba(15, 23, 42, 0.85),
                0 0 0 1px rgba(148, 163, 184, 0.35);
            position: relative;
            overflow: hidden;
        }

        .card::before {
            content: "";
            position: absolute;
            inset: -2px;
            border-radius: 22px;
            background: conic-gradient(
                from 180deg,
                rgba(56,189,248,0.3),
                rgba(59,130,246,0.1),
                rgba(34,197,94,0.2),
                rgba(56,189,248,0.3)
            );
            opacity: 0.7;
            z-index: -1;
            filter: blur(6px);
        }

        @media (max-width: 900px) {
            .page-wrapper {
                padding: 16px;
            }
            .card {
                grid-template-columns: 1fr;
                padding: 18px;
            }
            .assistant-illustration {
                display: none;
            }
        }

        h1 {
            margin: 0;
            font-size: 24px;
            font-weight: 700;
            color: #e5f0ff;
        }
        
        .subtitle {
            margin-top: 6px;
            margin-bottom: 10px;
            color: var(--sp-text-soft);
            font-size: 13px;
        }
        
        .hint {
            font-size: 12px;
            color: #cbd5f5;
            margin-bottom: 14px;
        }
        
        .hint strong {
            color: #ffffff;
        }

        .chat-wrapper {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        #chat {
            border-radius: 14px;
            background: rgba(15,23,42,0.9);
            padding: 10px;
            height: 330px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 8px;
            border: 1px solid rgba(148, 163, 184, 0.6);
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
            padding: 8px 11px;
            border-radius: 14px;
            font-size: 13px;
            line-height: 1.35;
        }
        
        .msg-user span {
            background: linear-gradient(to right, #0ea5e9, #22c55e);
            color: white;
            border-bottom-right-radius: 4px;
            box-shadow: 0 8px 15px rgba(14,165,233,0.5);
        }
        
        .msg-bot span {
            background: rgba(15,23,42,0.95);
            color: #e5e7eb;
            border-bottom-left-radius: 4px;
            border: 1px solid rgba(148, 163, 184, 0.7);
        }
        
        .msg-bot span a {
            color: #38bdf8;
            text-decoration: underline;
        }
        
        .msg-bot span a:hover {
            color: #a5f3fc;
        }

        form {
            display: flex;
            gap: 8px;
            margin-top: 6px;
        }
        
        #mensagem {
            flex: 1;
            padding: 9px 11px;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.8);
            font-size: 13px;
            outline: none;
            background: rgba(15,23,42,0.9);
            color: #e5f0ff;
        }
        
        #mensagem::placeholder {
            color: #64748b;
        }
        
        #mensagem:focus {
            border-color: #38bdf8;
            box-shadow: 0 0 0 1px rgba(56,189,248,0.3);
        }

        button[type="submit"] {
            border-radius: 999px;
            border: none;
            padding: 9px 16px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            background: linear-gradient(to right, #0ea5e9, #22c55e);
            color: white;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 10px 25px rgba(14, 165, 233, 0.5);
            transition: 0.2s ease;
            white-space: nowrap;
        }
        
        button[type="submit"]:hover {
            transform: translateY(-1px);
            filter: brightness(1.05);
        }

        .helper-text {
            font-size: 11px;
            color: var(--sp-text-soft);
        }

        .assistant-illustration {
            display: flex;
            flex-direction: column;
            gap: 12px;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        
        .assistant-illustration img {
            width: 290px;
            max-width: 100%;
            border-radius: 18px;
            object-fit: cover;
            box-shadow:
                0 20px 40px rgba(15, 23, 42, 0.9),
                0 0 0 1px rgba(148, 163, 184, 0.55);
        }
        
        .assistant-pill {
            font-size: 11px;
            background: rgba(224, 237, 251, 0.08);
            color: #c7ddff;
            padding: 4px 10px;
            border-radius: 999px;
            display: inline-flex;
            gap: 4px;
            align-items: center;
            border: 1px solid rgba(148, 163, 184, 0.6);
        }
        
        .assistant-pill span.dot {
            width: 6px;
            height: 6px;
            border-radius: 999px;
            background: #22c55e;
        }
        
        .assistant-caption-title {
            font-size: 13px;
            font-weight: 600;
            color: #e5f0ff;
        }
        
        .assistant-caption-text {
            font-size: 12px;
            color: var(--sp-text-soft);
        }

        .footer {
            margin-top: 4px;
            font-size: 11px;
            color: var(--sp-text-soft);
            text-align: center;
        }

        /* Modal para vídeos */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(4px);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }

        .modal-overlay.active {
            display: flex;
        }

        .modal-content {
            background: #020c1b;
            border-radius: 16px;
            padding: 20px;
            max-width: 800px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.5);
            position: relative;
        }

        .modal-close {
            position: absolute;
            top: 12px;
            right: 12px;
            background: rgba(148, 163, 184, 0.2);
            border: none;
            color: #e5f0ff;
            width: 32px;
            height: 32px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: 0.2s;
        }

        .modal-close:hover {
            background: rgba(148, 163, 184, 0.4);
        }

        .video-container {
            position: relative;
            width: 100%;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            border-radius: 12px;
            background: #000;
            margin-bottom: 16px;
        }

        .video-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }

        .modal-title {
            font-size: 18px;
            font-weight: 600;
            color: #e5f0ff;
            margin-bottom: 12px;
        }

        .modal-description {
            font-size: 13px;
            color: var(--sp-text-soft);
            line-height: 1.5;
        }

        .video-link {
            color: #38bdf8;
            cursor: pointer;
            text-decoration: underline;
        }

        .video-link:hover {
            color: #a5f3fc;
        }
    </style>
</head>

<body>
<div class="grid-overlay"></div>

<div class="page-wrapper">
    <!-- Barra superior -->
    <div class="header-bar">
        <div class="header-left">
            <img src="{{ logo_url }}" alt="Storopack" class="logo">
            <div>
                <div class="header-text-main">STOROPACK</div>
                <div class="header-text-sub">Assistente Técnico de Embalagens de Proteção</div>
            </div>
        </div>
        <div class="header-right">
            <div class="badge">
                <span class="badge-dot"></span>
                Assistente Técnico
            </div>
            <div class="phone">
                Contato para suporte: <strong>+55 11 5677 4699</strong>
            </div>
        </div>
    </div>

    <!-- Card principal -->
    <div class="card">
        <!-- Coluna do chat -->
        <div>
            <h1>Central de Suporte Storopack</h1>
            <p class="subtitle">
                Atendimento inteligente para dúvidas técnicas sobre equipamentos e soluções de proteção.
            </p>
            <p class="hint">
                Exemplo de pergunta: <strong>"Minha AIRplus está com erro E10, como posso resolver?"</strong>
            </p>

            <div class="chat-wrapper">
                <div id="chat">
                    <div class="msg-bot">
                        <span>Olá! 👋 Sou o assistente técnico Storopack. Como posso te ajudar hoje?</span>
                    </div>
                </div>

                <form id="form-chat">
                    <input
                        type="text"
                        id="mensagem"
                        autocomplete="off"
                        placeholder="Descreva o problema, modelo do equipamento e código de erro, se houver..."
                    />
                    <button type="submit">
                        Enviar
                        <span>➤</span>
                    </button>
                </form>
                <div class="helper-text">
                    Por segurança, não compartilhe dados sensíveis. Este canal é exclusivo para suporte técnico de equipamentos Storopack.
                </div>
            </div>
        </div>

        <!-- Coluna da imagem -->
        <div class="assistant-illustration">
            <img src="{{ assistant_img_url }}" alt="Assistente Storopack">
            <div class="assistant-pill">
                <span class="dot"></span>
                Suporte técnico imediato.
            </div>
            <div class="assistant-caption-title">
                Assistente de Manutenção & Operação
            </div>
            <div class="assistant-caption-text">
                Orientações rápidas e objetivas, com base em manuais técnicos e boas práticas Storopack.
            </div>
        </div>
    </div>

    <div class="footer">
        © Storopack – Assistente Técnico (beta)
    </div>
</div>

<!-- Modal para vídeos -->
<div class="modal-overlay" id="videoModal">
    <div class="modal-content">
        <button class="modal-close" onclick="closeVideoModal()">✕</button>
        <div id="modalVideoContainer"></div>
    </div>
</div>

<script>
    const chat = document.getElementById("chat");
    const form = document.getElementById("form-chat");
    const input = document.getElementById("mensagem");

    function linkify(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, '<a href="$1" target="_blank">$1</a>');
    }

    function scrollChat() {
        chat.scrollTop = chat.scrollHeight;
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const mensagem = input.value.trim();
        if (!mensagem) return;

        // Exibir mensagem do usuário
        const divUser = document.createElement("div");
        divUser.className = "msg-user";
        divUser.innerHTML = `<span>${escapeHtml(mensagem)}</span>`;
        chat.appendChild(divUser);

        input.value = "";
        scrollChat();

        try {
            // Enviar para o backend
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mensagem: mensagem }),
            });

            const data = await response.json();
            const resposta = data.resposta || "Desculpe, ocorreu um erro.";

            // Exibir resposta do bot
            const divBot = document.createElement("div");
            divBot.className = "msg-bot";
            divBot.innerHTML = `<span>${linkify(escapeHtml(resposta))}</span>`;
            chat.appendChild(divBot);

            scrollChat();
        } catch (error) {
            const divBot = document.createElement("div");
            divBot.className = "msg-bot";
            divBot.innerHTML = `<span>❌ Erro ao conectar com o servidor. Tente novamente.</span>`;
            chat.appendChild(divBot);
            scrollChat();
        }
    });

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    function extractYouTubeId(url) {
        const regexps = [
            /youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})/,
            /youtu\.be\/([a-zA-Z0-9_-]{11})/,
            /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/
        ];
        for (let regex of regexps) {
            const match = url.match(regex);
            if (match) return match[1];
        }
        return null;
    }

    function openVideoModal(url, title) {
        const videoId = extractYouTubeId(url);
        if (!videoId) return;

        const modalContainer = document.getElementById("modalVideoContainer");
        modalContainer.innerHTML = `
            <div class="video-container">
                <iframe src="https://www.youtube.com/embed/${videoId}?autoplay=1" allowfullscreen></iframe>
            </div>
            <div class="modal-title">${escapeHtml(title)}</div>
            <div class="modal-description">
                Clique no botão X para fechar o vídeo.
            </div>
        `;

        document.getElementById("videoModal").classList.add("active");
    }

    function closeVideoModal() {
        document.getElementById("videoModal").classList.remove("active");
    }

    function linkify(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, (url) => {
            const isYouTube = url.includes("youtube.com") || url.includes("youtu.be");
            if (isYouTube) {
                const title = extractYouTubeTitle(text, url) || "Vídeo Storopack";
                return `<span class="video-link" onclick="openVideoModal('${url}', '${title}')">🎬 ${escapeHtml(url.substring(0, 50))}...</span>`;
            }
            return `<a href="${url}" target="_blank">${url}</a>`;
        });
    }

    function extractYouTubeTitle(text, url) {
        // Tenta extrair o título mencionado antes do link
        const lines = text.split("\n");
        for (let i = lines.length - 1; i >= 0; i--) {
            if (lines[i].includes("http")) {
                return lines[i - 1] || "Vídeo Storopack";
            }
        }
        return "Vídeo Storopack";
    }
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(
        HTML,
        logo_url=LOGO_URL,
        assistant_img_url=ASSISTANT_IMG_URL,
    )


@app.route("/chat", methods=["POST"])
def chat():
    try:
        dados = request.get_json()
        mensagem = dados.get("mensagem", "").strip()

        if not mensagem:
            return jsonify({"resposta": "Por favor, envie uma mensagem."}), 400

        resposta = responder_cliente(mensagem)
        return jsonify({"resposta": resposta}), 200

    except Exception as e:
        return jsonify({"resposta": f"Erro: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)