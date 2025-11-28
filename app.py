from flask import Flask, render_template_string, request, jsonify
from assistente import responder_cliente
import os

# Importa o analisador de vídeo (se disponível)
try:
    from video_analyzer import analisar_video_erro
    VIDEO_ANALYSIS_ENABLED = True
except ImportError:
    VIDEO_ANALYSIS_ENABLED = False
    print("⚠️ Módulo video_analyzer não encontrado. Análise de vídeo desabilitada.")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

LOGO_URL = "https://www.storopack.com.br/fileadmin/_processed_/4/9/csm_Storopack_Imagefilm_Thumbnail_118bf988a8.jpg"
ASSISTANT_IMG_URL = "https://media.licdn.com/dms/image/v2/D4D05AQHQVQD99MOOug/videocover-low/B4DZoVhdqdK0B4-/0/1761297687645?e=2147483647&v=beta&t=FzJaplIJOhL1snkcWii_p3X9dPGyaSw1hjupd_3URvE"

HTML = """
<!doctype html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <title>Assistente Tecnico Storopack</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
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
            font-family: Inter, sans-serif;
            min-height: 100vh;
            background: linear-gradient(135deg, #0a1929 0%, #0d2a47 50%, #061e3e 100%);
        }

        .page-wrapper {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 32px 20px;
        }

        .header-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 16px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.12);
            margin-bottom: 24px;
        }

        .header-left { display: flex; align-items: center; gap: 16px; }
        .logo {
            height: 72px;
            border-radius: 6px;
            background: rgba(255,255,255,0.95);
        }
        .header-text-main { font-size: 18px; font-weight: 700; color: white; }
        .header-text-sub { font-size: 13px; color: rgba(255, 255, 255, 0.7); margin-top: 4px; }

        .header-right { text-align: right; }
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 16px;
            background: rgba(15, 118, 110, 0.15);
            color: #e5fdf7;
            font-size: 13px;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #22c55e;
        }
        .phone { color: rgba(255,255,255,0.7); font-size: 13px; margin-top: 6px; }
        .phone strong { color: white; }

        .card {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 14px;
            display: grid;
            grid-template-columns: 1.4fr 1fr;
            gap: 32px;
            padding: 28px;
            box-shadow: 0 18px 45px rgba(0, 0, 0, 0.35);
        }

        h1 { margin: 0 0 6px 0; font-size: 24px; color: var(--sp-primary); }
        .subtitle { color: #555; font-size: 14px; margin-bottom: 10px; }

        .hint {
            font-size: 13px;
            color: #0066cc;
            background: #f0f7ff;
            padding: 10px 12px;
            border-radius: 8px;
            border-left: 4px solid #0066cc;
            margin-bottom: 14px;
        }

        #chat {
            border-radius: 12px;
            background: #f8f9fa;
            padding: 12px;
            height: 380px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
        }

        .msg-user, .msg-bot { display: flex; width: 100%; margin-bottom: 10px; }
        .msg-user { justify-content: flex-end; }
        .msg-bot { justify-content: flex-start; }

        .msg-user span, .msg-bot span {
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 14px;
            font-size: 13px;
            line-height: 1.5;
            white-space: pre-wrap;
        }

        .msg-user span {
            background: linear-gradient(to right, #0ea5e9, #003066);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .msg-bot span {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }

        /* MÓDULOS */
        .module-buttons {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-top: 10px;
        }

        .module-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }

        .module-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }

        .module-card.airplus:hover { border-color: #3b82f6; }
        .module-card.paperplus:hover { border-color: #84cc16; }
        .module-card.foamplus:hover { border-color: #f97316; }
        .module-card.airmove:hover { border-color: #8b5cf6; }

        .module-card-img {
            width: 100%;
            height: 100px;
            object-fit: contain;
            background: #f8f9fa;
            padding: 8px;
        }

        .module-card-label {
            padding: 10px;
            text-align: center;
            font-weight: 600;
            font-size: 13px;
            color: white;
        }

        .module-card.airplus .module-card-label { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
        .module-card.paperplus .module-card-label { background: linear-gradient(135deg, #84cc16, #65a30d); }
        .module-card.foamplus .module-card-label { background: linear-gradient(135deg, #f97316, #ea580c); }
        .module-card.airmove .module-card-label { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }

        /* SUB-MÓDULOS */
        .submodule-buttons {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
        }

        .submodule-card {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border: 2px solid #e5e7eb;
            transition: all 0.25s ease;
        }

        .submodule-card:hover {
            transform: translateY(-2px);
            border-color: var(--sp-primary);
        }

        .submodule-card-img {
            width: 100%;
            height: 60px;
            object-fit: contain;
            background: #f8f9fa;
        }

        .submodule-card-label {
            padding: 6px;
            text-align: center;
            font-weight: 600;
            font-size: 11px;
            background: #f1f5f9;
        }

        /* BADGE */
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
        .module-badge.active { display: inline-flex; }
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
        }
        .back-btn:hover { background: #dc2626; }

        /* FORM */
        .input-row {
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }

        #mensagem {
            flex: 1;
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            font-size: 14px;
            outline: none;
        }
        #mensagem:focus { border-color: var(--sp-primary); }
        #mensagem:disabled { background: #f1f5f9; }

        .btn-primary {
            background: var(--sp-primary);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
        }
        .btn-primary:hover { background: var(--sp-primary-dark); }
        .btn-primary:disabled { background: #94a3b8; cursor: not-allowed; }

        .btn-video {
            background: linear-gradient(135deg, #8b5cf6, #7c3aed);
            color: white;
            border: none;
            padding: 12px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }
        .btn-video:hover { background: #7c3aed; }
        .btn-video:disabled { background: #94a3b8; cursor: not-allowed; }

        .helper-text { font-size: 12px; color: #6b7280; margin-top: 8px; }

        /* VIDEO PREVIEW */
        .video-preview {
            background: #1e293b;
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
            display: none;
        }
        .video-preview.active { display: block; }
        .video-preview video { width: 100%; max-height: 120px; border-radius: 6px; }
        .video-preview-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            color: white;
            font-size: 12px;
        }
        .btn-analyze {
            width: 100%;
            margin-top: 8px;
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }

        /* ILUSTRAÇÃO */
        .assistant-illustration {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 10px;
        }
        .assistant-illustration img {
            width: 100%;
            max-width: 360px;
            border-radius: 12px;
        }
        .assistant-pill {
            background: var(--sp-secondary);
            color: #022c22;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .assistant-caption-title { font-size: 14px; font-weight: 600; color: #111827; }
        .assistant-caption-text { font-size: 13px; color: #4b5563; }

        .footer {
            text-align: center;
            color: rgba(255,255,255,0.7);
            font-size: 11px;
            margin-top: 20px;
        }

        @media (max-width: 900px) {
            .card { grid-template-columns: 1fr; }
            .input-row { flex-wrap: wrap; }
            .btn-primary, .btn-video { width: 100%; }
            .submodule-buttons { grid-template-columns: repeat(2, 1fr); }
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
                <span>Assistente Tecnico · Online</span>
            </div>
            <div class="phone">Contato humano: <strong>+55 11 5677 4699</strong></div>
        </div>
    </div>

    <div class="card">
        <div>
            <h1>Central de Suporte Storopack</h1>
            <p class="subtitle">Atendimento inteligente para duvidas tecnicas sobre equipamentos.</p>
            
            <div id="moduleBadge" class="module-badge">
                <span id="moduleBadgeText"></span>
                <button class="back-btn" id="btnVoltar">← Voltar</button>
            </div>

            <p class="hint" id="hintText">Selecione abaixo o equipamento sobre o qual deseja suporte:</p>

            <div id="chat"></div>

            <div class="video-preview" id="videoPreview">
                <div class="video-preview-header">
                    <span>📹 Vídeo selecionado</span>
                    <button class="back-btn" id="btnRemoveVideo">✕ Remover</button>
                </div>
                <video id="videoPlayer" controls></video>
                <button class="btn-analyze" id="btnAnalyze">🔍 Analisar Vídeo com IA</button>
            </div>

            <div class="input-row">
                <input type="text" id="mensagem" placeholder="Primeiro, selecione um equipamento acima..." disabled>
                <input type="file" id="videoInput" accept="video/*" style="display:none">
                <button class="btn-video" id="btnVideo" disabled>📹 Enviar Vídeo</button>
                <button class="btn-primary" id="btnEnviar" disabled>Enviar ➤</button>
            </div>
            <div class="helper-text">💡 Dica: Envie um vídeo do erro para análise automática pela IA!</div>
        </div>

        <div class="assistant-illustration">
            <img src="{{ assistant_img_url }}" alt="Assistente Storopack">
            <div class="assistant-pill">● Suporte tecnico imediato</div>
            <div class="assistant-caption-title">Assistente de Manutencao & Operacao</div>
            <div class="assistant-caption-text">Agora com análise de vídeo por IA!</div>
        </div>
    </div>

    <div class="footer">© Storopack - Assistente Tecnico (beta)</div>
</div>

<script>
(function() {
    // Elementos
    var chat = document.getElementById("chat");
    var input = document.getElementById("mensagem");
    var btnEnviar = document.getElementById("btnEnviar");
    var btnVideo = document.getElementById("btnVideo");
    var btnVoltar = document.getElementById("btnVoltar");
    var btnRemoveVideo = document.getElementById("btnRemoveVideo");
    var btnAnalyze = document.getElementById("btnAnalyze");
    var moduleBadge = document.getElementById("moduleBadge");
    var moduleBadgeText = document.getElementById("moduleBadgeText");
    var hintText = document.getElementById("hintText");
    var videoInput = document.getElementById("videoInput");
    var videoPreview = document.getElementById("videoPreview");
    var videoPlayer = document.getElementById("videoPlayer");

    var moduloAtivo = null;
    var submoduloAtivo = null;
    var videoFile = null;

    // Config dos módulos
    var modulosConfig = {
        airplus: {
            nome: "AIRplus",
            cor: "airplus",
            placeholder: "Descreva o problema ou envie um vídeo...",
            hint: "Dica: Envie um vídeo do display mostrando o erro!",
            submodulos: null
        },
        airmove: {
            nome: "AIRmove",
            cor: "airmove",
            placeholder: "Descreva o problema...",
            hint: "Envie um vídeo do equipamento para análise!",
            submodulos: {
                "AIRmove 1": "https://www.storopack.com.br/fileadmin/_processed_/7/e/csm_PP_AP_AIRmove___machine_front_motive2_cushion_film_low_res_300dpi_061fd19c2b.jpg",
                "AIRmove 2": "https://www.storopack.com.br/fileadmin/_processed_/7/e/csm_PP_AP_AIRmove___machine_front_motive2_cushion_film_low_res_300dpi_061fd19c2b.jpg"
            }
        },
        paperplus: {
            nome: "PAPERplus",
            cor: "paperplus",
            placeholder: "Descreva o problema...",
            hint: "Filme o papel travando para diagnóstico!",
            submodulos: {
                "Shooter": "https://www.storopack.com.br/fileadmin/_processed_/5/9/csm_PP_PP_Shooter_machine_tablestand_motive_1_1280x580px_6913698898.png",
                "Papillon": "https://www.storopack.com.br/fileadmin/_processed_/c/a/csm_PP_PP_Papillon_machine_tablestand_motive1_1280x580px_b746b18c6a.png",
                "Classic": "https://img.directindustry.com/pt/images_di/photo-g/34409-12098453.webp",
                "Track": "https://swiftpak.imgix.net/uploads/Products/Papertech/16_12904_a.jpg",
                "CX": "https://www.storopack.com.br/fileadmin/_processed_/1/e/csm_PP_PP_Classic_CX_machine_0539_1280x580px_EUROPEAN_STAND_b213d265e2.png",
                "Coiler": "https://www.storopack.com.br/fileadmin/_processed_/1/4/csm_PP_PP_Coiler2_Classic_CX_machine_1985_low_res_1280x580px_6e072a7d32.png"
            }
        },
        foamplus: {
            nome: "FOAMplus",
            cor: "foamplus",
            placeholder: "Descreva o problema...",
            hint: "Filme a espuma sendo aplicada!",
            submodulos: {
                "Bagpacker": "https://www.storopack.com.br/fileadmin/_processed_/1/9/csm_PP_FP_Bag_Packer3_machine_6327_1280x580px_277b779f5d.png",
                "Handpacker": "https://5.imimg.com/data5/HS/KC/MW/SELLER-8794370/foamplus-hand-packer-2-machine-1000x1000.jpg"
            }
        }
    };

    // Inicializa
    function init() {
        mostrarBotoesModulos();
        addBotMessage("Ola! Sou o assistente tecnico da Storopack. Como posso te ajudar hoje?");
    }

    // Adiciona mensagem do bot
    function addBotMessage(texto) {
        var div = document.createElement("div");
        div.className = "msg-bot";
        var span = document.createElement("span");
        span.innerHTML = texto.replace(/\\n/g, "<br>").replace(/\n/g, "<br>");
        div.appendChild(span);
        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
    }

    // Adiciona mensagem do usuário
    function addUserMessage(texto) {
        var div = document.createElement("div");
        div.className = "msg-user";
        var span = document.createElement("span");
        span.textContent = texto;
        div.appendChild(span);
        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
    }

    // Mostra botões de módulos
    function mostrarBotoesModulos() {
        var html = '<div class="module-buttons">';
        html += '<div class="module-card airplus" data-modulo="airplus">';
        html += '<img class="module-card-img" src="https://img.directindustry.com/pt/images_di/photo-g/34409-10167740.webp" alt="AIRplus">';
        html += '<div class="module-card-label">AIRplus</div></div>';
        
        html += '<div class="module-card airmove" data-modulo="airmove">';
        html += '<img class="module-card-img" src="https://www.storopack.com.br/fileadmin/_processed_/7/e/csm_PP_AP_AIRmove___machine_front_motive2_cushion_film_low_res_300dpi_061fd19c2b.jpg" alt="AIRmove">';
        html += '<div class="module-card-label">AIRmove</div></div>';
        
        html += '<div class="module-card paperplus" data-modulo="paperplus">';
        html += '<img class="module-card-img" src="https://www.storopack.com.br/fileadmin/_processed_/1/e/csm_PP_PP_Classic_CX_machine_0539_1280x580px_EUROPEAN_STAND_b213d265e2.png" alt="PAPERplus">';
        html += '<div class="module-card-label">PAPERplus</div></div>';
        
        html += '<div class="module-card foamplus" data-modulo="foamplus">';
        html += '<img class="module-card-img" src="https://www.storopack.com.br/fileadmin/_processed_/1/9/csm_PP_FP_Bag_Packer3_machine_6327_1280x580px_277b779f5d.png" alt="FOAMplus">';
        html += '<div class="module-card-label">FOAMplus</div></div>';
        html += '</div>';

        var div = document.createElement("div");
        div.className = "msg-bot";
        div.innerHTML = html;
        chat.appendChild(div);

        // Adiciona event listeners
        var cards = div.querySelectorAll(".module-card");
        cards.forEach(function(card) {
            card.addEventListener("click", function() {
                var modulo = this.getAttribute("data-modulo");
                clicarModulo(modulo);
            });
        });

        chat.scrollTop = chat.scrollHeight;
    }

    // Clique no módulo
    function clicarModulo(modulo) {
        var config = modulosConfig[modulo];
        
        if (config.submodulos) {
            mostrarSubmodulos(modulo);
        } else {
            selecionarModulo(modulo);
        }
    }

    // Mostra sub-módulos
    function mostrarSubmodulos(modulo) {
        var config = modulosConfig[modulo];
        
        var html = '<div style="text-align:center;margin-bottom:10px;font-weight:600;">Selecione o modelo de ' + config.nome + ':</div>';
        html += '<div class="submodule-buttons">';
        
        for (var nome in config.submodulos) {
            html += '<div class="submodule-card" data-modulo="' + modulo + '" data-sub="' + nome + '">';
            html += '<img class="submodule-card-img" src="' + config.submodulos[nome] + '" alt="' + nome + '">';
            html += '<div class="submodule-card-label">' + nome + '</div></div>';
        }
        
        html += '</div>';
        html += '<div style="text-align:center;margin-top:12px;"><button class="back-btn" id="btnVoltarSub">← Voltar aos equipamentos</button></div>';

        chat.innerHTML = "";
        addBotMessage("Ola! Sou o assistente tecnico da Storopack.");
        
        var div = document.createElement("div");
        div.className = "msg-bot";
        div.innerHTML = html;
        chat.appendChild(div);

        // Event listeners
        var cards = div.querySelectorAll(".submodule-card");
        cards.forEach(function(card) {
            card.addEventListener("click", function() {
                var mod = this.getAttribute("data-modulo");
                var sub = this.getAttribute("data-sub");
                selecionarSubmodulo(mod, sub);
            });
        });

        var btnVoltarSub = div.querySelector("#btnVoltarSub");
        if (btnVoltarSub) {
            btnVoltarSub.addEventListener("click", voltarInicio);
        }

        hintText.innerHTML = "<strong>" + config.nome + "</strong> - Escolha o modelo:";
        chat.scrollTop = chat.scrollHeight;
    }

    // Seleciona módulo
    function selecionarModulo(modulo) {
        moduloAtivo = modulo;
        submoduloAtivo = null;
        var config = modulosConfig[modulo];

        moduleBadge.className = "module-badge active " + config.cor;
        moduleBadgeText.textContent = "Modulo: " + config.nome;

        hintText.innerHTML = "<strong>" + config.nome + "</strong> - " + config.hint;
        input.placeholder = config.placeholder;
        input.disabled = false;
        btnEnviar.disabled = false;
        btnVideo.disabled = false;

        chat.innerHTML = "";
        addBotMessage("Voce selecionou <strong>" + config.nome + "</strong>.<br><br>📹 Envie um vídeo do erro OU descreva o problema.");
        
        input.focus();
    }

    // Seleciona sub-módulo
    function selecionarSubmodulo(modulo, sub) {
        moduloAtivo = modulo;
        submoduloAtivo = sub;
        var config = modulosConfig[modulo];
        var nomeCompleto = config.nome + " " + sub;

        moduleBadge.className = "module-badge active " + config.cor;
        moduleBadgeText.textContent = "Modulo: " + nomeCompleto;

        hintText.innerHTML = "<strong>" + nomeCompleto + "</strong> - " + config.hint;
        input.placeholder = config.placeholder;
        input.disabled = false;
        btnEnviar.disabled = false;
        btnVideo.disabled = false;

        chat.innerHTML = "";
        addBotMessage("Voce selecionou <strong>" + nomeCompleto + "</strong>.<br><br>📹 Envie um vídeo do erro OU descreva o problema.");
        
        input.focus();
    }

    // Voltar ao início
    function voltarInicio() {
        moduloAtivo = null;
        submoduloAtivo = null;
        videoFile = null;
        videoPreview.classList.remove("active");

        moduleBadge.className = "module-badge";
        hintText.textContent = "Selecione abaixo o equipamento sobre o qual deseja suporte:";
        input.placeholder = "Primeiro, selecione um equipamento acima...";
        input.disabled = true;
        input.value = "";
        btnEnviar.disabled = true;
        btnVideo.disabled = true;

        chat.innerHTML = "";
        addBotMessage("Ola! Sou o assistente tecnico da Storopack. Como posso te ajudar hoje?");
        mostrarBotoesModulos();
    }

    // Enviar mensagem
    function enviarMensagem() {
        var texto = input.value.trim();
        if (!texto || !moduloAtivo) return;

        addUserMessage(texto);
        input.value = "";

        var modulo = moduloAtivo;
        if (submoduloAtivo) {
            modulo = moduloAtivo + "_" + submoduloAtivo.toLowerCase().replace(/ /g, "_");
        }

        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mensagem: texto, modulo: modulo })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            addBotMessage(data.resposta || "Erro ao processar.");
        })
        .catch(function() {
            addBotMessage("Erro ao conectar com o servidor.");
        });
    }

    // Vídeo selecionado
    function onVideoSelect(e) {
        var file = e.target.files[0];
        if (file) {
            videoFile = file;
            videoPlayer.src = URL.createObjectURL(file);
            videoPreview.classList.add("active");
        }
    }

    // Remover vídeo
    function removerVideo() {
        videoFile = null;
        videoInput.value = "";
        videoPlayer.src = "";
        videoPreview.classList.remove("active");
    }

    // Analisar vídeo
    function analisarVideo() {
        if (!videoFile || !moduloAtivo) return;

        addUserMessage("📹 [Vídeo enviado para análise]");
        btnAnalyze.textContent = "⏳ Analisando...";
        btnAnalyze.disabled = true;

        var formData = new FormData();
        formData.append("video", videoFile);
        formData.append("modulo", moduloAtivo + (submoduloAtivo ? "_" + submoduloAtivo.toLowerCase().replace(/ /g, "_") : ""));
        formData.append("descricao", input.value.trim());

        fetch("/analyze-video", {
            method: "POST",
            body: formData
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            addBotMessage(data.resposta || "Erro ao analisar.");
            removerVideo();
        })
        .catch(function() {
            addBotMessage("Erro ao conectar.");
            removerVideo();
        })
        .finally(function() {
            btnAnalyze.textContent = "🔍 Analisar Vídeo com IA";
            btnAnalyze.disabled = false;
        });
    }

    // Event listeners
    btnEnviar.addEventListener("click", enviarMensagem);
    input.addEventListener("keypress", function(e) {
        if (e.key === "Enter") enviarMensagem();
    });
    btnVoltar.addEventListener("click", voltarInicio);
    btnVideo.addEventListener("click", function() { videoInput.click(); });
    videoInput.addEventListener("change", onVideoSelect);
    btnRemoveVideo.addEventListener("click", removerVideo);
    btnAnalyze.addEventListener("click", analisarVideo);

    // Inicializa
    init();
})();
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
def chat_route():
    try:
        dados = request.get_json()
        mensagem = dados.get("mensagem", "").strip()
        modulo = dados.get("modulo", "").strip()

        if not mensagem:
            return jsonify({"resposta": "Por favor, envie uma mensagem."}), 400

        resposta = responder_cliente(mensagem, modulo=modulo)
        return jsonify({"resposta": resposta}), 200

    except Exception as e:
        return jsonify({"resposta": f"Erro: {str(e)}"}), 500


@app.route("/analyze-video", methods=["POST"])
def analyze_video():
    if not VIDEO_ANALYSIS_ENABLED:
        return jsonify({
            "resposta": "❌ Análise de vídeo não disponível.\n\nDescreva o problema por texto ou ligue: (11) 5677-4699"
        }), 200

    try:
        if 'video' not in request.files:
            return jsonify({"resposta": "Nenhum vídeo enviado."}), 400

        video_file = request.files['video']
        modulo = request.form.get('modulo', 'airplus')
        descricao = request.form.get('descricao', '')

        video_bytes = video_file.read()

        resposta = analisar_video_erro(
            video_bytes=video_bytes,
            modulo=modulo,
            descricao_cliente=descricao
        )

        return jsonify({"resposta": resposta}), 200

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({
            "resposta": "❌ Erro ao analisar vídeo.\n\nLigue: (11) 5677-4699"
        }), 500


if __name__ == "__main__":
    print(f"📹 Análise de vídeo: {'Habilitada' if VIDEO_ANALYSIS_ENABLED else 'Desabilitada'}")
    app.run(debug=False, host="0.0.0.0", port=5000)