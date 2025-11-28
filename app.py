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
            --sp-gray-light: #f5f5f5;
            --sp-text-dark: #1a1a1a;
        }

        * { box-sizing: border-box; }
        
        body {
            margin: 0;
            padding: 0;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: stretch;
            justify-content: center;
            background: linear-gradient(135deg, #0a1929 0%, #0d2a47 50%, #061e3e 100%);
            color: var(--sp-text-dark);
        }

        .page-wrapper {
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 1200px;
            padding: 32px 20px;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        .header-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding-bottom: 16px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.12);
        }

        .header-left { display: flex; align-items: center; gap: 16px; }
        .logo {
            height: 72px;
            border-radius: 6px;
            object-fit: contain;
            background: rgba(255,255,255,0.95);
        }
        .header-text-main { font-size: 18px; font-weight: 700; color: white; letter-spacing: 0.5px; }
        .header-text-sub { font-size: 13px; color: rgba(255, 255, 255, 0.7); margin-top: 4px; }

        .header-right {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 6px;
            font-size: 13px;
        }

        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 16px;
            background: rgba(15, 118, 110, 0.15);
            color: #e5fdf7;
            font-weight: 500;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            background: #22c55e;
            box-shadow: 0 0 10px rgba(34, 197, 94, 0.9);
        }

        .status-label {
            white-space: nowrap;
        }

        .phone {
            color: rgba(255,255,255,0.7);
        }
        .phone strong { color: white; }

        .card {
            margin-top: 4px;
            background: rgba(255, 255, 255, 0.98);
            border-radius: 14px;
            display: grid;
            grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr);
            gap: 32px;
            padding: 28px;
            box-shadow: 0 18px 45px rgba(0, 0, 0, 0.35);
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.24);
        }

        .card::before {
            content: "";
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at top left, rgba(0, 102, 204, 0.06), transparent 55%),
                        radial-gradient(circle at bottom right, rgba(0, 204, 204, 0.06), transparent 55%);
            pointer-events: none;
        }

        h1 { margin: 0; font-size: 24px; font-weight: 700; color: var(--sp-primary); }
        .subtitle { margin-top: 6px; margin-bottom: 10px; color: #555; font-size: 14px; }

        .hint {
            font-size: 13px;
            color: #0066cc;
            margin-bottom: 14px;
            background: #f0f7ff;
            padding: 10px 12px;
            border-radius: 8px;
            border-left: 4px solid #0066cc;
        }

        .chat-wrapper { display: flex; flex-direction: column; gap: 10px; }

        #chat {
            border-radius: 12px;
            background: #f8f9fa;
            padding: 12px;
            height: 360px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
            border: 1px solid #e0e0e0;
        }

        .msg-user, .msg-bot {
            display: flex;
            width: 100%;
        }
        .msg-user { justify-content: flex-end; }
        .msg-bot { justify-content: flex-start; }

        .msg-user span, .msg-bot span {
            max-width: 80%;
            padding: 8px 11px;
            border-radius: 14px;
            font-size: 13px;
            line-height: 1.35;
        }

        .msg-user span {
            background: linear-gradient(to right, #0ea5e9, #003066);
            color: white;
            border-bottom-right-radius: 4px;
            box-shadow: 0 8px 15px rgba(14, 165, 233, 0.5);
        }

        .msg-bot span {
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
            border: 1px solid #e0e0e0;
        }

        .msg-bot span a {
            color: var(--sp-primary);
            text-decoration: underline;
        }

        .msg-bot span a:hover {
            color: var(--sp-primary-dark);
        }

        /* Estilos dos botões de módulo */
        .module-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
            justify-content: center;
        }

        .module-btn {
            padding: 12px 20px;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .module-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
        }

        .module-btn.airplus {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
        }

        .module-btn.paperplus {
            background: linear-gradient(135deg, #84cc16, #65a30d);
            color: white;
        }

        .module-btn.foamplus {
            background: linear-gradient(135deg, #f97316, #ea580c);
            color: white;
        }

        .module-btn.airmove {
            background: linear-gradient(135deg, #8b5cf6, #7c3aed);
            color: white;
        }

        .module-btn .icon {
            font-size: 18px;
        }

        /* Badge do módulo ativo */
        .module-badge {
            display: none;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 10px;
            color: white;
        }

        .module-badge.active {
            display: inline-flex;
        }

        .module-badge.airplus { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
        .module-badge.paperplus { background: linear-gradient(135deg, #84cc16, #65a30d); }
        .module-badge.foamplus { background: linear-gradient(135deg, #f97316, #ea580c); }
        .module-badge.airmove { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }

        .back-btn {
            background: #ef4444;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            margin-left: 10px;
            transition: 0.2s;
        }

        .back-btn:hover {
            background: #dc2626;
        }

        form { display: flex; gap: 8px; margin-top: 6px; }
        
        #mensagem {
            flex: 1;
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            font-size: 14px;
            outline: none;
            background: white;
            color: #333;
        }

        #mensagem::placeholder { color: #94a3b8; }
        #mensagem:focus {
            border-color: var(--sp-primary);
            box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.18);
        }

        #mensagem:disabled {
            background: #f1f5f9;
            cursor: not-allowed;
        }

        button[type="submit"] {
            border-radius: 8px;
            border: none;
            padding: 12px 22px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            background: var(--sp-primary);
            color: white;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.3);
            transition: 0.18s ease;
            white-space: nowrap;
        }

        button[type="submit"]:hover {
            background: var(--sp-primary-dark);
            transform: translateY(-1px);
        }

        button[type="submit"]:disabled {
            background: #94a3b8;
            cursor: not-allowed;
            transform: none;
        }

        .helper-text { font-size: 12px; color: #6b7280; }

        .assistant-illustration {
            display: flex;
            flex-direction: column;
            gap: 10px;
            justify-content: center;
            align-items: center;
            text-align: center;
            position: relative;
            z-index: 1;
        }

        .assistant-illustration img {
            width: 100%;
            max-width: 360px;
            border-radius: 12px;
            object-fit: cover;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.35);
        }

        .assistant-pill {
            font-size: 12px;
            background: var(--sp-secondary);
            color: #022c22;
            padding: 6px 12px;
            border-radius: 20px;
            display: inline-flex;
            gap: 6px;
            align-items: center;
            font-weight: 600;
        }

        .assistant-pill span.dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #22c55e;
        }

        .assistant-caption-title { font-size: 14px; font-weight: 600; color: #111827; }
        .assistant-caption-text { font-size: 13px; color: #4b5563; }

        .footer {
            margin-top: 16px;
            font-size: 11px;
            color: rgba(209,213,219,0.85);
            text-align: center;
        }

        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(4px);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }

        .modal-overlay.active { display: flex; }

        .modal-content {
            background: white;
            border-radius: 12px;
            padding: 20px;
            max-width: 800px;
            width: 92%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 50px rgba(15, 23, 42, 0.45);
            position: relative;
        }

        .modal-close {
            position: absolute;
            top: 12px;
            right: 12px;
            background: #f3f4f6;
            border: none;
            color: #111827;
            width: 32px;
            height: 32px;
            border-radius: 999px;
            cursor: pointer;
            font-size: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: 0.18s;
        }

        .modal-close:hover {
            background: #e5e7eb;
        }

        .video-container {
            position: relative;
            width: 100%;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            border-radius: 10px;
            background: #000;
            margin-bottom: 12px;
        }

        .video-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }

        .modal-title { font-size: 18px; font-weight: 600; color: var(--sp-primary); margin-bottom: 6px; }
        .modal-description { font-size: 13px; color: #4b5563; }

        .video-thumbnail {
            position: relative;
            width: 100%;
            max-width: 320px;
            background: #000;
            border-radius: 10px;
            overflow: hidden;
            cursor: pointer;
            margin-top: 6px;
        }

        .video-thumbnail img {
            width: 100%;
            height: auto;
            display: block;
        }

        .video-play-btn {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 60px;
            height: 60px;
            background: rgba(0, 102, 204, 0.95);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
            cursor: pointer;
            transition: 0.25s;
            border: 3px solid white;
        }

        .video-thumbnail:hover .video-play-btn {
            background: var(--sp-primary-dark);
            transform: translate(-50%, -50%) scale(1.08);
        }

        @media (max-width: 900px) {
            .page-wrapper {
                padding: 16px 12px 20px;
            }

            .header-bar {
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }

            .header-right {
                align-items: flex-start;
            }

            .card {
                grid-template-columns: 1fr;
                padding: 18px 14px 20px;
                gap: 22px;
            }

            #chat {
                height: 55vh;
                max-height: none;
            }

            form {
                flex-direction: column;
            }

            button[type="submit"] {
                width: 100%;
                justify-content: center;
            }

            .assistant-illustration img {
                max-width: 280px;
            }

            .module-buttons {
                flex-direction: column;
            }

            .module-btn {
                width: 100%;
                justify-content: center;
            }
        }
    </style>
</head>

<body>
<div class="page-wrapper">
    <div class="header-bar">
        <div class="header-left">
            <img src="{{ logo_url }}" alt="Storopack" class="logo">
            <div>
                <div class="header-text-main">STOROPACK</div>
                <div class="header-text-sub">Assistente Tecnico de Embalagens de Protecao</div>
            </div>
        </div>
        <div class="header-right">
            <div class="status-indicator">
                <span class="status-dot"></span>
                <span class="status-label">Assistente Tecnico · Online</span>
            </div>
            <div class="phone">
                Contato humano: <strong>+55 11 5677 4699</strong>
            </div>
        </div>
    </div>

    <div class="card">
        <div style="position: relative; z-index: 1;">
            <h1>Central de Suporte Storopack</h1>
            <p class="subtitle">Atendimento inteligente para duvidas tecnicas sobre equipamentos e solucoes de protecao.</p>
            
            <!-- Badge do módulo ativo -->
            <div id="moduleBadge" class="module-badge">
                <span id="moduleBadgeText"></span>
                <button class="back-btn" onclick="voltarInicio()">← Voltar</button>
            </div>

            <p class="hint" id="hintText">Selecione abaixo o equipamento sobre o qual deseja suporte:</p>

            <div class="chat-wrapper">
                <div id="chat">
                    <div class="msg-bot">
                        <span>Ola! Sou o assistente tecnico da Storopack. Como posso te ajudar hoje?</span>
                    </div>
                    <!-- Botões de módulo -->
                    <div class="msg-bot" id="moduleButtonsContainer">
                        <div class="module-buttons">
                            <button class="module-btn airplus" onclick="selecionarModulo('airplus')">
                                <span class="icon">💨</span> AIRplus
                            </button>
                            <button class="module-btn paperplus" onclick="selecionarModulo('paperplus')">
                                <span class="icon">📄</span> PAPERplus
                            </button>
                            <button class="module-btn foamplus" onclick="selecionarModulo('foamplus')">
                                <span class="icon">🧽</span> FOAMplus
                            </button>
                            <button class="module-btn airmove" onclick="selecionarModulo('airmove')">
                                <span class="icon">📦</span> AIRmove
                            </button>
                        </div>
                    </div>
                </div>

                <form id="form-chat">
                    <input type="text" id="mensagem" autocomplete="off" placeholder="Primeiro, selecione um equipamento acima..." disabled>
                    <button type="submit" id="btnEnviar" disabled>Enviar <span>➤</span></button>
                </form>
                <div class="helper-text">Por seguranca, nao compartilhe dados sensiveis. Este canal e exclusivo para suporte tecnico de equipamentos Storopack.</div>
            </div>
        </div>

        <div class="assistant-illustration">
            <img src="{{ assistant_img_url }}" alt="Assistente Storopack">
            <div class="assistant-pill">
                <span class="dot"></span>
                Suporte tecnico imediato
            </div>
            <div class="assistant-caption-title">Assistente de Manutencao & Operacao</div>
            <div class="assistant-caption-text">Orientacoes rapidas e objetivas, com base em manuais tecnicos e boas praticas Storopack.</div>
        </div>
    </div>

    <div class="footer">© Storopack - Assistente Tecnico (beta)</div>
</div>

<div class="modal-overlay" id="videoModal">
    <div class="modal-content">
        <button class="modal-close" onclick="closeVideoModal()">✕</button>
        <div id="modalVideoContainer"></div>
    </div>
</div>

<script>
    var chat = document.getElementById("chat");
    var form = document.getElementById("form-chat");
    var input = document.getElementById("mensagem");
    var btnEnviar = document.getElementById("btnEnviar");
    var moduleBadge = document.getElementById("moduleBadge");
    var moduleBadgeText = document.getElementById("moduleBadgeText");
    var moduleButtonsContainer = document.getElementById("moduleButtonsContainer");
    var hintText = document.getElementById("hintText");

    // Módulo ativo atual
    var moduloAtivo = null;

    // Configurações dos módulos
    var modulosConfig = {
        airplus: {
            nome: "AIRplus",
            cor: "airplus",
            placeholder: "Descreva seu problema com AIRplus (ex: erro E3, travamento, etc.)...",
            hint: "Exemplo: Minha AIRplus esta com erro E3, como posso resolver?"
        },
        paperplus: {
            nome: "PAPERplus",
            cor: "paperplus",
            placeholder: "Descreva seu problema com PAPERplus (ex: papel preso, corte irregular, etc.)...",
            hint: "Exemplo: O papel esta prendendo na maquina PAPERplus, o que fazer?"
        },
        foamplus: {
            nome: "FOAMplus",
            cor: "foamplus",
            placeholder: "Descreva seu problema com FOAMplus (ex: espuma nao expande, vazamento, etc.)...",
            hint: "Exemplo: A espuma do FOAMplus nao esta expandindo corretamente."
        },
        airmove: {
            nome: "AIRmove",
            cor: "airmove",
            placeholder: "Descreva seu problema com AIRmove (ex: almofada nao infla, sensor com defeito, etc.)...",
            hint: "Exemplo: As almofadas do AIRmove nao estao inflando direito."
        }
    };

    function selecionarModulo(modulo) {
        moduloAtivo = modulo;
        var config = modulosConfig[modulo];

        // Esconder botões de módulo
        moduleButtonsContainer.style.display = "none";

        // Mostrar badge do módulo ativo
        moduleBadge.className = "module-badge active " + config.cor;
        moduleBadgeText.textContent = "Modulo: " + config.nome;

        // Atualizar hint e placeholder
        hintText.innerHTML = "<strong>" + config.nome + "</strong> - " + config.hint;
        input.placeholder = config.placeholder;

        // Habilitar input e botão
        input.disabled = false;
        btnEnviar.disabled = false;

        // Adicionar mensagem no chat
        var divBot = document.createElement("div");
        divBot.className = "msg-bot";
        var spanBot = document.createElement("span");
        spanBot.innerHTML = "Voce selecionou <strong>" + config.nome + "</strong>. Como posso ajudar com esse equipamento?";
        divBot.appendChild(spanBot);
        chat.appendChild(divBot);
        scrollChat();

        // Focar no input
        input.focus();
    }

    function voltarInicio() {
        moduloAtivo = null;

        // Limpar chat
        chat.innerHTML = "";

        // Mensagem inicial
        var divBot = document.createElement("div");
        divBot.className = "msg-bot";
        var spanBot = document.createElement("span");
        spanBot.textContent = "Ola! Sou o assistente tecnico da Storopack. Como posso te ajudar hoje?";
        divBot.appendChild(spanBot);
        chat.appendChild(divBot);

        // Recriar botões de módulo
        var divBotoes = document.createElement("div");
        divBotoes.className = "msg-bot";
        divBotoes.id = "moduleButtonsContainer";
        divBotoes.innerHTML = '<div class="module-buttons">' +
            '<button class="module-btn airplus" onclick="selecionarModulo(\'airplus\')"><span class="icon">💨</span> AIRplus</button>' +
            '<button class="module-btn paperplus" onclick="selecionarModulo(\'paperplus\')"><span class="icon">📄</span> PAPERplus</button>' +
            '<button class="module-btn foamplus" onclick="selecionarModulo(\'foamplus\')"><span class="icon">🧽</span> FOAMplus</button>' +
            '<button class="module-btn airmove" onclick="selecionarModulo(\'airmove\')"><span class="icon">📦</span> AIRmove</button>' +
            '</div>';
        chat.appendChild(divBotoes);

        // Atualizar referência
        moduleButtonsContainer = divBotoes;

        // Esconder badge
        moduleBadge.className = "module-badge";

        // Resetar hint e input
        hintText.textContent = "Selecione abaixo o equipamento sobre o qual deseja suporte:";
        input.placeholder = "Primeiro, selecione um equipamento acima...";
        input.disabled = true;
        btnEnviar.disabled = true;
        input.value = "";

        scrollChat();
    }

    function escapeHtml(text) {
        var div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    function scrollChat() {
        chat.scrollTop = chat.scrollHeight;
    }

    function extractYouTubeId(url) {
        var regex1 = /youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})/;
        var regex2 = /youtu\.be\/([a-zA-Z0-9_-]{11})/;
        var regex3 = /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/;
        
        var match = url.match(regex1);
        if (match) return match[1];
        match = url.match(regex2);
        if (match) return match[1];
        match = url.match(regex3);
        if (match) return match[1];
        return null;
    }

    function getYouTubeThumbnail(videoId) {
        if (!videoId) return "";
        return "https://img.youtube.com/vi/" + videoId + "/hqdefault.jpg";
    }

    function openVideoModal(url, title) {
        if (!url) return;
        var videoId = extractYouTubeId(url);
        if (!videoId) return;

        var modalContainer = document.getElementById("modalVideoContainer");
        var titleEscaped = escapeHtml(title || "Video Storopack");
        var html = '<div class="video-container"><iframe src="https://www.youtube.com/embed/' + videoId + '?autoplay=1" allowfullscreen></iframe></div>';
        html += '<div class="modal-title">' + titleEscaped + "</div>";
        html += '<div class="modal-description">Clique no botao ✕ para fechar.</div>';
        
        modalContainer.innerHTML = html;
        document.getElementById("videoModal").classList.add("active");
    }

    function closeVideoModal() {
        document.getElementById("videoModal").classList.remove("active");
        document.getElementById("modalVideoContainer").innerHTML = "";
    }

    function linkify(text) {
        if (!text || typeof text !== "string") {
            return { text: "", youtubeUrl: "", hasYouTube: false, videoId: "" };
        }

        var urlRegex = /(https?:\/\/[^\s]+)/g;
        var hasYouTube = false;
        var youtubeUrl = "";
        var videoId = "";
        
        var matches = text.match(urlRegex);
        if (matches && matches.length > 0) {
            for (var i = 0; i < matches.length; i++) {
                var url = matches[i];
                var isYouTube = url.indexOf("youtube.com") > -1 || url.indexOf("youtu.be") > -1;
                if (isYouTube) {
                    hasYouTube = true;
                    youtubeUrl = url;
                    videoId = extractYouTubeId(url);
                    break;
                }
            }
        }
        
        var result = text.replace(urlRegex, function(url) {
            var isYouTube = url.indexOf("youtube.com") > -1 || url.indexOf("youtu.be") > -1;
            if (isYouTube) {
                return "";
            }
            return '<a href="' + url + '" target="_blank">' + url + "</a>";
        });
        
        return { 
            text: (result || "").trim(), 
            youtubeUrl: youtubeUrl, 
            hasYouTube: hasYouTube, 
            videoId: videoId 
        };
    }

    form.addEventListener("submit", function(e) {
        e.preventDefault();

        if (!moduloAtivo) {
            alert("Por favor, selecione um equipamento primeiro.");
            return;
        }

        var mensagem = input.value.trim();
        if (!mensagem) return;

        var divUser = document.createElement("div");
        divUser.className = "msg-user";
        var spanUser = document.createElement("span");
        spanUser.textContent = mensagem;
        divUser.appendChild(spanUser);
        chat.appendChild(divUser);

        input.value = "";
        scrollChat();

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/chat", true);
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onload = function() {
            if (xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    var resposta = data.resposta || "Desculpe, ocorreu um erro.";

                    var processedText = linkify(escapeHtml(resposta));

                    var divBot = document.createElement("div");
                    divBot.className = "msg-bot";
                    var spanBot = document.createElement("span");
                    spanBot.innerHTML = processedText.text || "";
                    divBot.appendChild(spanBot);
                    chat.appendChild(divBot);

                    if (processedText.hasYouTube && processedText.videoId) {
                        var divVideo = document.createElement("div");
                        divVideo.className = "msg-bot";
                        var spanVideo = document.createElement("span");
                        spanVideo.style.padding = "0";
                        spanVideo.style.background = "transparent";
                        spanVideo.style.border = "none";
                        
                        var thumbnail = document.createElement("div");
                        thumbnail.className = "video-thumbnail";
                        thumbnail.onclick = function() {
                            openVideoModal(processedText.youtubeUrl, "Video Storopack");
                        };
                        
                        var img = document.createElement("img");
                        img.src = getYouTubeThumbnail(processedText.videoId);
                        img.alt = "Video Storopack";
                        img.onerror = function() {
                            img.src = "data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22180%22%3E%3Crect fill=%22%23333%22 width=%22300%22 height=%22180%22/%3E%3C/svg%3E";
                        };
                        
                        var playBtn = document.createElement("div");
                        playBtn.className = "video-play-btn";
                        playBtn.textContent = "▶";
                        
                        thumbnail.appendChild(img);
                        thumbnail.appendChild(playBtn);
                        spanVideo.appendChild(thumbnail);
                        divVideo.appendChild(spanVideo);
                        chat.appendChild(divVideo);
                    }

                    scrollChat();
                } catch (e) {
                    var divBot = document.createElement("div");
                    divBot.className = "msg-bot";
                    var spanBot = document.createElement("span");
                    spanBot.textContent = "Erro ao processar resposta.";
                    divBot.appendChild(spanBot);
                    chat.appendChild(divBot);
                    scrollChat();
                }
            } else {
                var divBot = document.createElement("div");
                divBot.className = "msg-bot";
                var spanBot = document.createElement("span");
                spanBot.textContent = "Erro " + xhr.status + " ao conectar com o servidor.";
                divBot.appendChild(spanBot);
                chat.appendChild(divBot);
                scrollChat();
            }
        };

        xhr.onerror = function() {
            var divBot = document.createElement("div");
            divBot.className = "msg-bot";
            var spanBot = document.createElement("span");
            spanBot.textContent = "Erro ao conectar com o servidor.";
            divBot.appendChild(spanBot);
            chat.appendChild(divBot);
            scrollChat();
        };

        // Envia mensagem COM o módulo ativo
        xhr.send(JSON.stringify({ 
            mensagem: mensagem,
            modulo: moduloAtivo 
        }));
    });
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
        modulo = dados.get("modulo", "").strip()  # Recebe o módulo ativo

        if not mensagem:
            return jsonify({"resposta": "Por favor, envie uma mensagem."}), 400

        # Passa o módulo para o assistente
        resposta = responder_cliente(mensagem, modulo=modulo)
        return jsonify({"resposta": resposta}), 200

    except Exception as e:
        return jsonify({"resposta": "Erro: " + str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)