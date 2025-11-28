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

        .status-label { white-space: nowrap; }
        .phone { color: rgba(255,255,255,0.7); }
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
            height: 420px;
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
            line-height: 1.5;
            white-space: pre-wrap;
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

        /* ========== BOTÕES DE MÓDULO COM IMAGEM ========== */
        .module-buttons {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-top: 10px;
            padding: 5px;
        }

        .module-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border: 2px solid transparent;
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

        /* ========== SUB-BOTÕES ========== */
        .submodule-container { margin-top: 10px; }
        .submodule-title {
            font-size: 13px;
            font-weight: 600;
            color: #555;
            margin-bottom: 8px;
            text-align: center;
        }

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
            transition: all 0.25s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border: 2px solid #e5e7eb;
        }

        .submodule-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
            border-color: var(--sp-primary);
        }

        .submodule-card-img {
            width: 100%;
            height: 60px;
            object-fit: contain;
            background: #f8f9fa;
            padding: 4px;
        }

        .submodule-card-label {
            padding: 6px;
            text-align: center;
            font-weight: 600;
            font-size: 11px;
            color: #333;
            background: #f1f5f9;
            border-top: 1px solid #e5e7eb;
        }

        /* ========== BADGE DO MÓDULO ATIVO ========== */
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
            transition: 0.2s;
        }

        .back-btn:hover { background: #dc2626; }

        /* ========== FORMULÁRIO ========== */
        .input-row {
            display: flex;
            gap: 8px;
            margin-top: 6px;
            align-items: center;
        }

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

        /* ========== BOTÃO DE VÍDEO ========== */
        .video-upload-btn {
            background: linear-gradient(135deg, #8b5cf6, #7c3aed);
            color: white;
            border: none;
            padding: 12px 14px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            font-weight: 600;
            transition: 0.2s;
        }

        .video-upload-btn:hover {
            background: linear-gradient(135deg, #7c3aed, #6d28d9);
            transform: translateY(-1px);
        }

        .video-upload-btn:disabled {
            background: #94a3b8;
            cursor: not-allowed;
            transform: none;
        }

        .video-upload-btn .icon { font-size: 16px; }

        #videoInput { display: none; }

        /* ========== PREVIEW DE VÍDEO ========== */
        .video-preview {
            background: #1e293b;
            border-radius: 8px;
            padding: 10px;
            margin-top: 8px;
            display: none;
        }

        .video-preview.active { display: block; }

        .video-preview video {
            width: 100%;
            max-height: 150px;
            border-radius: 6px;
        }

        .video-preview-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .video-preview-title {
            color: white;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .video-preview-close {
            background: #ef4444;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
        }

        .video-analyze-btn {
            width: 100%;
            margin-top: 8px;
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 13px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .video-analyze-btn:hover {
            background: linear-gradient(135deg, #059669, #047857);
        }

        .video-analyze-btn:disabled {
            background: #94a3b8;
            cursor: not-allowed;
        }

        /* ========== LOADING ========== */
        .loading-spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #ffffff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
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

        .helper-text { font-size: 12px; color: #6b7280; margin-top: 6px; }

        /* ========== ILUSTRAÇÃO ========== */
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

        /* ========== MODAL DE VÍDEO ========== */
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

        .modal-close:hover { background: #e5e7eb; }

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
            .page-wrapper { padding: 16px 12px 20px; }
            .header-bar { flex-direction: column; align-items: flex-start; gap: 8px; }
            .header-right { align-items: flex-start; }
            .card { grid-template-columns: 1fr; padding: 18px 14px 20px; gap: 22px; }
            #chat { height: 55vh; max-height: none; }
            .input-row { flex-wrap: wrap; }
            button[type="submit"] { width: 100%; justify-content: center; }
            .video-upload-btn { width: 100%; justify-content: center; }
            .assistant-illustration img { max-width: 280px; }
            .module-buttons { grid-template-columns: repeat(2, 1fr); }
            .submodule-buttons { grid-template-columns: repeat(2, 1fr); }
        }

        @media (max-width: 500px) {
            .module-buttons { grid-template-columns: 1fr; }
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
                    <div class="msg-bot" id="moduleButtonsContainer">
                        <div class="module-buttons" id="mainModuleButtons">
                            <div class="module-card airplus" onclick="selecionarModulo('airplus')">
                                <img class="module-card-img" src="https://img.directindustry.com/pt/images_di/photo-g/34409-10167740.webp" alt="AIRplus">
                                <div class="module-card-label">AIRplus</div>
                            </div>
                            <div class="module-card airmove" onclick="mostrarSubmodulos('airmove')">
                                <img class="module-card-img" src="https://www.storopack.com.br/fileadmin/_processed_/7/e/csm_PP_AP_AIRmove___machine_front_motive2_cushion_film_low_res_300dpi_061fd19c2b.jpg" alt="AIRmove">
                                <div class="module-card-label">AIRmove</div>
                            </div>
                            <div class="module-card paperplus" onclick="mostrarSubmodulos('paperplus')">
                                <img class="module-card-img" src="https://www.storopack.com.br/fileadmin/_processed_/1/e/csm_PP_PP_Classic_CX_machine_0539_1280x580px_EUROPEAN_STAND_b213d265e2.png" alt="PAPERplus">
                                <div class="module-card-label">PAPERplus</div>
                            </div>
                            <div class="module-card foamplus" onclick="mostrarSubmodulos('foamplus')">
                                <img class="module-card-img" src="https://www.storopack.com.br/fileadmin/_processed_/1/9/csm_PP_FP_Bag_Packer3_machine_6327_1280x580px_277b779f5d.png" alt="FOAMplus">
                                <div class="module-card-label">FOAMplus</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Preview de vídeo -->
                <div class="video-preview" id="videoPreview">
                    <div class="video-preview-header">
                        <span class="video-preview-title">📹 Vídeo selecionado</span>
                        <button class="video-preview-close" onclick="removerVideo()">✕ Remover</button>
                    </div>
                    <video id="videoPreviewPlayer" controls></video>
                    <button class="video-analyze-btn" id="btnAnalyze" onclick="analisarVideo()">
                        🔍 Analisar Vídeo com IA
                    </button>
                </div>

                <form id="form-chat">
                    <div class="input-row">
                        <input type="text" id="mensagem" autocomplete="off" placeholder="Primeiro, selecione um equipamento acima..." disabled>
                        <input type="file" id="videoInput" accept="video/*" onchange="videoSelecionado(this)">
                        <button type="button" class="video-upload-btn" id="btnVideo" onclick="document.getElementById('videoInput').click()" disabled>
                            <span class="icon">📹</span> Enviar Vídeo
                        </button>
                        <button type="submit" id="btnEnviar" disabled>Enviar <span>➤</span></button>
                    </div>
                </form>
                <div class="helper-text">💡 Dica: Envie um vídeo do erro para análise automática pela IA!</div>
            </div>
        </div>

        <div class="assistant-illustration">
            <img src="{{ assistant_img_url }}" alt="Assistente Storopack">
            <div class="assistant-pill">
                <span class="dot"></span>
                Suporte tecnico imediato
            </div>
            <div class="assistant-caption-title">Assistente de Manutencao & Operacao</div>
            <div class="assistant-caption-text">Agora com análise de vídeo por IA! Envie um vídeo do erro e receba o diagnóstico.</div>
        </div>
    </div>

    <div class="footer">© Storopack - Assistente Tecnico (beta) - Análise Visual por IA</div>
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
    var btnVideo = document.getElementById("btnVideo");
    var btnAnalyze = document.getElementById("btnAnalyze");
    var moduleBadge = document.getElementById("moduleBadge");
    var moduleBadgeText = document.getElementById("moduleBadgeText");
    var moduleButtonsContainer = document.getElementById("moduleButtonsContainer");
    var hintText = document.getElementById("hintText");
    var videoInput = document.getElementById("videoInput");
    var videoPreview = document.getElementById("videoPreview");
    var videoPreviewPlayer = document.getElementById("videoPreviewPlayer");

    var moduloAtivo = null;
    var submoduloAtivo = null;
    var videoSelecionadoFile = null;

    // Configurações dos módulos (mesmo código anterior)
    var modulosConfig = {
        airplus: {
            nome: "AIRplus",
            cor: "airplus",
            placeholder: "Descreva o problema ou envie um vídeo do erro...",
            hint: "Dica: Envie um vídeo do display mostrando o erro para diagnóstico automático!",
            img: "https://img.directindustry.com/pt/images_di/photo-g/34409-10167740.webp",
            submodulos: null
        },
        airmove: {
            nome: "AIRmove",
            cor: "airmove",
            placeholder: "Descreva o problema ou envie um vídeo...",
            hint: "Dica: Envie um vídeo do equipamento para análise visual!",
            img: "https://www.storopack.com.br/fileadmin/_processed_/7/e/csm_PP_AP_AIRmove___machine_front_motive2_cushion_film_low_res_300dpi_061fd19c2b.jpg",
            submodulos: {
                "AIRmove 1": "https://www.storopack.com.br/fileadmin/_processed_/7/e/csm_PP_AP_AIRmove___machine_front_motive2_cushion_film_low_res_300dpi_061fd19c2b.jpg",
                "AIRmove 2": "https://www.storopack.com.br/fileadmin/_processed_/7/e/csm_PP_AP_AIRmove___machine_front_motive2_cushion_film_low_res_300dpi_061fd19c2b.jpg"
            }
        },
        paperplus: {
            nome: "PAPERplus",
            cor: "paperplus",
            placeholder: "Descreva o problema ou envie um vídeo...",
            hint: "Dica: Filme o papel travando para diagnóstico preciso!",
            img: "https://www.storopack.com.br/fileadmin/_processed_/1/e/csm_PP_PP_Classic_CX_machine_0539_1280x580px_EUROPEAN_STAND_b213d265e2.png",
            submodulos: {
                "Shooter": "https://www.storopack.com.br/fileadmin/_processed_/5/9/csm_PP_PP_Shooter_machine_tablestand_motive_1_1280x580px_6913698898.png",
                "Papillon": "https://www.storopack.com.br/fileadmin/_processed_/c/a/csm_PP_PP_Papillon_machine_tablestand_motive1_1280x580px_b746b18c6a.png",
                "Classic": "https://img.directindustry.com/pt/images_di/photo-g/34409-12098453.webp",
                "Track": "https://swiftpak.imgix.net/uploads/Products/Papertech/16_12904_a.jpg?w=1135&fit=crop&crop=edges,focalpoint&q=75&auto=format&fm=png",
                "CX": "https://www.storopack.com.br/fileadmin/_processed_/1/e/csm_PP_PP_Classic_CX_machine_0539_1280x580px_EUROPEAN_STAND_b213d265e2.png",
                "Coiler": "https://www.storopack.com.br/fileadmin/_processed_/1/4/csm_PP_PP_Coiler2_Classic_CX_machine_1985_low_res_1280x580px_6e072a7d32.png"
            }
        },
        foamplus: {
            nome: "FOAMplus",
            cor: "foamplus",
            placeholder: "Descreva o problema ou envie um vídeo...",
            hint: "Dica: Filme a espuma sendo aplicada para análise!",
            img: "https://www.storopack.com.br/fileadmin/_processed_/1/9/csm_PP_FP_Bag_Packer3_machine_6327_1280x580px_277b779f5d.png",
            submodulos: {
                "Bagpacker": "https://www.storopack.com.br/fileadmin/_processed_/1/9/csm_PP_FP_Bag_Packer3_machine_6327_1280x580px_277b779f5d.png",
                "Handpacker": "https://5.imimg.com/data5/HS/KC/MW/SELLER-8794370/foamplus-hand-packer-2-machine-1000x1000.jpg"
            }
        }
    };

    // Funções de vídeo
    function videoSelecionado(inputElement) {
        var file = inputElement.files[0];
        if (file) {
            videoSelecionadoFile = file;
            var url = URL.createObjectURL(file);
            videoPreviewPlayer.src = url;
            videoPreview.classList.add("active");
        }
    }

    function removerVideo() {
        videoSelecionadoFile = null;
        videoInput.value = "";
        videoPreviewPlayer.src = "";
        videoPreview.classList.remove("active");
    }

    function analisarVideo() {
        if (!videoSelecionadoFile) {
            alert("Selecione um vídeo primeiro.");
            return;
        }

        if (!moduloAtivo) {
            alert("Selecione um equipamento primeiro.");
            return;
        }

        // Mostra loading
        btnAnalyze.disabled = true;
        btnAnalyze.innerHTML = '<span class="loading-spinner"></span> Analisando...';

        // Adiciona mensagem do usuário
        var divUser = document.createElement("div");
        divUser.className = "msg-user";
        var spanUser = document.createElement("span");
        spanUser.textContent = "📹 [Vídeo enviado para análise]";
        divUser.appendChild(spanUser);
        chat.appendChild(divUser);
        scrollChat();

        // Envia para análise
        var formData = new FormData();
        formData.append("video", videoSelecionadoFile);
        formData.append("modulo", moduloAtivo + (submoduloAtivo ? "_" + submoduloAtivo.toLowerCase().replace(/ /g, "_") : ""));
        formData.append("descricao", input.value.trim());

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/analyze-video", true);

        xhr.onload = function() {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = '🔍 Analisar Vídeo com IA';

            if (xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    var resposta = data.resposta || "Não foi possível analisar o vídeo.";
                    addBotMessage(resposta);
                } catch (e) {
                    addBotMessage("Erro ao processar resposta da análise.");
                }
            } else {
                addBotMessage("Erro " + xhr.status + " ao analisar vídeo.");
            }

            removerVideo();
        };

        xhr.onerror = function() {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = '🔍 Analisar Vídeo com IA';
            addBotMessage("Erro ao conectar com o servidor.");
            removerVideo();
        };

        xhr.send(formData);
    }

    function addBotMessage(texto) {
        var divBot = document.createElement("div");
        divBot.className = "msg-bot";
        var spanBot = document.createElement("span");
        spanBot.innerHTML = processText(texto);
        divBot.appendChild(spanBot);
        chat.appendChild(divBot);
        scrollChat();
    }

    function processText(texto) {
        // Processa URLs e quebras de linha
        texto = escapeHtml(texto);
        texto = texto.replace(/\n/g, "<br>");
        
        // Processa URLs do YouTube
        var urlRegex = /(https?:\/\/[^\s<]+)/g;
        texto = texto.replace(urlRegex, function(url) {
            if (url.indexOf("youtube.com") > -1 || url.indexOf("youtu.be") > -1) {
                return '<a href="' + url + '" target="_blank" style="color: #0066cc;">📹 Ver vídeo</a>';
            }
            return '<a href="' + url + '" target="_blank">' + url + '</a>';
        });
        
        return texto;
    }

    // Funções de módulo (mesmo código anterior)
    function mostrarSubmodulos(modulo) {
        var config = modulosConfig[modulo];
        if (!config.submodulos) {
            selecionarModulo(modulo);
            return;
        }

        var html = '<div class="submodule-container">';
        html += '<div class="submodule-title">Selecione o modelo de ' + config.nome + ':</div>';
        html += '<div class="submodule-buttons">';

        for (var nome in config.submodulos) {
            html += '<div class="submodule-card" onclick="selecionarSubmodulo(\'' + modulo + '\', \'' + nome + '\')">';
            html += '<img class="submodule-card-img" src="' + config.submodulos[nome] + '" alt="' + nome + '">';
            html += '<div class="submodule-card-label">' + nome + '</div>';
            html += '</div>';
        }

        html += '</div>';
        html += '<div style="text-align: center; margin-top: 12px;"><button class="back-btn" onclick="voltarModulos()">← Voltar aos equipamentos</button></div>';
        html += '</div>';

        moduleButtonsContainer.innerHTML = html;
        hintText.innerHTML = '<strong>' + config.nome + '</strong> - Escolha o modelo:';
        scrollChat();
    }

    function voltarModulos() {
        moduleButtonsContainer.innerHTML = gerarBotoesModulos();
        hintText.textContent = "Selecione abaixo o equipamento sobre o qual deseja suporte:";
        scrollChat();
    }

    function gerarBotoesModulos() {
        return '<div class="module-buttons" id="mainModuleButtons">' +
            '<div class="module-card airplus" onclick="selecionarModulo(\'airplus\')">' +
                '<img class="module-card-img" src="https://img.directindustry.com/pt/images_di/photo-g/34409-10167740.webp" alt="AIRplus">' +
                '<div class="module-card-label">AIRplus</div>' +
            '</div>' +
            '<div class="module-card airmove" onclick="mostrarSubmodulos(\'airmove\')">' +
                '<img class="module-card-img" src="https://www.storopack.com.br/fileadmin/_processed_/7/e/csm_PP_AP_AIRmove___machine_front_motive2_cushion_film_low_res_300dpi_061fd19c2b.jpg" alt="AIRmove">' +
                '<div class="module-card-label">AIRmove</div>' +
            '</div>' +
            '<div class="module-card paperplus" onclick="mostrarSubmodulos(\'paperplus\')">' +
                '<img class="module-card-img" src="https://www.storopack.com.br/fileadmin/_processed_/1/e/csm_PP_PP_Classic_CX_machine_0539_1280x580px_EUROPEAN_STAND_b213d265e2.png" alt="PAPERplus">' +
                '<div class="module-card-label">PAPERplus</div>' +
            '</div>' +
            '<div class="module-card foamplus" onclick="mostrarSubmodulos(\'foamplus\')">' +
                '<img class="module-card-img" src="https://www.storopack.com.br/fileadmin/_processed_/1/9/csm_PP_FP_Bag_Packer3_machine_6327_1280x580px_277b779f5d.png" alt="FOAMplus">' +
                '<div class="module-card-label">FOAMplus</div>' +
            '</div>' +
        '</div>';
    }

    function selecionarSubmodulo(modulo, submodulo) {
        moduloAtivo = modulo;
        submoduloAtivo = submodulo;
        var config = modulosConfig[modulo];

        moduleButtonsContainer.style.display = "none";

        var nomeCompleto = config.nome + " " + submodulo;
        moduleBadge.className = "module-badge active " + config.cor;
        moduleBadgeText.textContent = "Modulo: " + nomeCompleto;

        hintText.innerHTML = "<strong>" + nomeCompleto + "</strong> - " + config.hint;
        input.placeholder = config.placeholder;

        input.disabled = false;
        btnEnviar.disabled = false;
        btnVideo.disabled = false;

        addBotMessage("Voce selecionou " + nomeCompleto + ".\n\n📹 Envie um vídeo do erro OU descreva o problema.");
        input.focus();
    }

    function selecionarModulo(modulo) {
        moduloAtivo = modulo;
        submoduloAtivo = null;
        var config = modulosConfig[modulo];

        moduleButtonsContainer.style.display = "none";

        moduleBadge.className = "module-badge active " + config.cor;
        moduleBadgeText.textContent = "Modulo: " + config.nome;

        hintText.innerHTML = "<strong>" + config.nome + "</strong> - " + config.hint;
        input.placeholder = config.placeholder;

        input.disabled = false;
        btnEnviar.disabled = false;
        btnVideo.disabled = false;

        addBotMessage("Voce selecionou " + config.nome + ".\n\n📹 Envie um vídeo do erro OU descreva o problema.");
        input.focus();
    }

    function voltarInicio() {
        moduloAtivo = null;
        submoduloAtivo = null;
        removerVideo();

        chat.innerHTML = "";

        var divBot = document.createElement("div");
        divBot.className = "msg-bot";
        var spanBot = document.createElement("span");
        spanBot.textContent = "Ola! Sou o assistente tecnico da Storopack. Como posso te ajudar hoje?";
        divBot.appendChild(spanBot);
        chat.appendChild(divBot);

        var divBotoes = document.createElement("div");
        divBotoes.className = "msg-bot";
        divBotoes.id = "moduleButtonsContainer";
        divBotoes.innerHTML = gerarBotoesModulos();
        chat.appendChild(divBotoes);

        moduleButtonsContainer = divBotoes;

        moduleBadge.className = "module-badge";

        hintText.textContent = "Selecione abaixo o equipamento sobre o qual deseja suporte:";
        input.placeholder = "Primeiro, selecione um equipamento acima...";
        input.disabled = true;
        btnEnviar.disabled = true;
        btnVideo.disabled = true;
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

    function openVideoModal(url, title) {
        // ... código do modal de vídeo
    }

    function closeVideoModal() {
        document.getElementById("videoModal").classList.remove("active");
        document.getElementById("modalVideoContainer").innerHTML = "";
    }

    // Form submit
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
                    addBotMessage(resposta);
                } catch (e) {
                    addBotMessage("Erro ao processar resposta.");
                }
            } else {
                addBotMessage("Erro " + xhr.status + " ao conectar.");
            }
        };

        xhr.onerror = function() {
            addBotMessage("Erro ao conectar com o servidor.");
        };

        var moduloEnviar = moduloAtivo;
        if (submoduloAtivo) {
            moduloEnviar = moduloAtivo + "_" + submoduloAtivo.toLowerCase().replace(/ /g, "_");
        }

        xhr.send(JSON.stringify({ 
            mensagem: mensagem,
            modulo: moduloEnviar,
            submodulo: submoduloAtivo
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
        modulo = dados.get("modulo", "").strip()

        if not mensagem:
            return jsonify({"resposta": "Por favor, envie uma mensagem."}), 400

        resposta = responder_cliente(mensagem, modulo=modulo)
        return jsonify({"resposta": resposta}), 200

    except Exception as e:
        return jsonify({"resposta": f"Erro: {str(e)}"}), 500


@app.route("/analyze-video", methods=["POST"])
def analyze_video():
    """Endpoint para análise de vídeo com IA."""
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

        if video_file.filename == '':
            return jsonify({"resposta": "Arquivo de vídeo inválido."}), 400

        # Lê os bytes do vídeo
        video_bytes = video_file.read()

        # Analisa o vídeo
        resposta = analisar_video_erro(
            video_bytes=video_bytes,
            modulo=modulo,
            descricao_cliente=descricao
        )

        return jsonify({"resposta": resposta}), 200

    except Exception as e:
        print(f"Erro ao analisar vídeo: {e}")
        return jsonify({
            "resposta": f"❌ Erro ao analisar vídeo.\n\nDescreva o problema ou ligue: (11) 5677-4699"
        }), 500


if __name__ == "__main__":
    print(f"📹 Análise de vídeo: {'Habilitada' if VIDEO_ANALYSIS_ENABLED else 'Desabilitada'}")
    app.run(debug=False, host="0.0.0.0", port=5000)