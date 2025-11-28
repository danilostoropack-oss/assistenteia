from flask import Flask, render_template_string, request, jsonify
from assistente import responder_cliente

app = Flask(__name__)

LOGO_URL = "https://www.storopack.com.br/fileadmin/_processed_/4/9/csm_Storopack_Imagefilm_Thumbnail_118bf988a8.jpg"
ASSISTANT_IMG_URL = "https://media.licdn.com/dms/image/v2/D4D05AQHQVQD99MOOug/videocover-low/B4DZoVhdqdK0B4-/0/1761297687645?e=2147483647&v=beta&t=FzJaplIJOhL1snkcWii_p3X9dPGyaSw1hjupd_3URvE"

HTML = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <title>Assistente Storopack</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: Inter, sans-serif;
            background: linear-gradient(135deg, #0a1929, #0d2a47, #061e3e);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1100px; margin: 0 auto; }
        
        /* Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        .header-left { display: flex; align-items: center; gap: 15px; }
        .logo { height: 60px; border-radius: 8px; background: white; }
        .header-title { color: white; font-size: 18px; font-weight: 700; }
        .header-sub { color: rgba(255,255,255,0.7); font-size: 12px; }
        .header-right { text-align: right; }
        .status { color: #4ade80; font-size: 13px; }
        .phone { color: rgba(255,255,255,0.7); font-size: 13px; margin-top: 5px; }
        .phone b { color: white; }

        /* Card principal */
        .card {
            background: white;
            border-radius: 16px;
            padding: 25px;
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            gap: 30px;
        }
        h1 { color: #0066cc; font-size: 22px; margin-bottom: 5px; }
        .subtitle { color: #666; font-size: 14px; margin-bottom: 15px; }
        
        /* Hint */
        .hint {
            background: #e8f4fd;
            border-left: 4px solid #0066cc;
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 13px;
            color: #0066cc;
            margin-bottom: 15px;
        }

        /* Badge do módulo */
        .badge {
            display: none;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            color: white;
            margin-bottom: 15px;
            align-items: center;
            gap: 10px;
        }
        .badge.show { display: inline-flex; }
        .badge.airplus { background: #3b82f6; }
        .badge.paperplus { background: #84cc16; }
        .badge.foamplus { background: #f97316; }
        .badge.airmove { background: #8b5cf6; }
        .badge button {
            background: #ef4444;
            color: white;
            border: none;
            padding: 4px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
        }

        /* Chat */
        .chat {
            background: #f5f5f5;
            border-radius: 12px;
            padding: 15px;
            height: 350px;
            overflow-y: auto;
            margin-bottom: 15px;
        }
        .msg { margin-bottom: 12px; }
        .msg-bot { text-align: left; }
        .msg-user { text-align: right; }
        .msg span {
            display: inline-block;
            padding: 10px 15px;
            border-radius: 12px;
            max-width: 85%;
            font-size: 13px;
            line-height: 1.5;
            white-space: pre-wrap;
        }
        .msg-bot span { background: white; border: 1px solid #ddd; }
        .msg-user span { background: linear-gradient(to right, #0ea5e9, #003066); color: white; }

        /* Botões de módulo */
        .modules {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }
        .mod-btn {
            background: white;
            border: 2px solid #e5e5e5;
            border-radius: 12px;
            padding: 0;
            cursor: pointer;
            transition: all 0.2s;
            overflow: hidden;
        }
        .mod-btn:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .mod-btn img { width: 100%; height: 80px; object-fit: contain; background: #f8f8f8; }
        .mod-btn .label {
            padding: 8px;
            text-align: center;
            font-weight: 600;
            font-size: 12px;
            color: white;
        }
        .mod-btn.airplus .label { background: #3b82f6; }
        .mod-btn.paperplus .label { background: #84cc16; }
        .mod-btn.foamplus .label { background: #f97316; }
        .mod-btn.airmove .label { background: #8b5cf6; }
        .mod-btn.airplus:hover { border-color: #3b82f6; }
        .mod-btn.paperplus:hover { border-color: #84cc16; }
        .mod-btn.foamplus:hover { border-color: #f97316; }
        .mod-btn.airmove:hover { border-color: #8b5cf6; }

        /* Sub-módulos */
        .submods {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
        }
        .sub-btn {
            background: white;
            border: 2px solid #e5e5e5;
            border-radius: 8px;
            padding: 0;
            cursor: pointer;
            transition: all 0.2s;
            overflow: hidden;
        }
        .sub-btn:hover { border-color: #0066cc; }
        .sub-btn img { width: 100%; height: 50px; object-fit: contain; background: #f8f8f8; }
        .sub-btn .label { padding: 5px; font-size: 10px; font-weight: 600; background: #f1f1f1; }

        /* Input */
        .input-row { display: flex; gap: 10px; }
        #msgInput {
            flex: 1;
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        #msgInput:disabled { background: #f5f5f5; }
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            font-size: 13px;
        }
        .btn-primary { background: #0066cc; color: white; }
        .btn-primary:disabled { background: #ccc; cursor: not-allowed; }
        .btn-video { background: #8b5cf6; color: white; }
        .btn-video:disabled { background: #ccc; cursor: not-allowed; }
        .btn-back { background: #ef4444; color: white; margin-top: 10px; }

        .tip { font-size: 11px; color: #888; margin-top: 10px; }

        /* Ilustração */
        .illustration { text-align: center; }
        .illustration img { width: 100%; max-width: 350px; border-radius: 12px; }
        .illustration .pill {
            display: inline-block;
            background: #00cccc;
            color: #022c22;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 10px;
        }
        .illustration h3 { font-size: 14px; margin-top: 10px; }
        .illustration p { font-size: 12px; color: #666; }

        .footer { text-align: center; color: rgba(255,255,255,0.6); font-size: 11px; margin-top: 20px; }

        @media (max-width: 800px) {
            .card { grid-template-columns: 1fr; }
            .modules { grid-template-columns: 1fr 1fr; }
            .submods { grid-template-columns: 1fr 1fr; }
            .input-row { flex-wrap: wrap; }
            .btn { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-left">
                <img src="''' + LOGO_URL + '''" class="logo" alt="Storopack">
                <div>
                    <div class="header-title">STOROPACK</div>
                    <div class="header-sub">Assistente Tecnico de Embalagens</div>
                </div>
            </div>
            <div class="header-right">
                <div class="status">● Assistente Online</div>
                <div class="phone">Contato: <b>+55 11 5677 4699</b></div>
            </div>
        </div>

        <div class="card">
            <div>
                <h1>Central de Suporte Storopack</h1>
                <p class="subtitle">Atendimento inteligente para dúvidas técnicas.</p>

                <div class="badge" id="badge">
                    <span id="badgeText"></span>
                    <button onclick="voltar()">← Voltar</button>
                </div>

                <div class="hint" id="hint">Selecione o equipamento sobre o qual deseja suporte:</div>

                <div class="chat" id="chat"></div>

                <div class="input-row">
                    <input type="text" id="msgInput" placeholder="Selecione um equipamento acima..." disabled>
                    <button class="btn btn-primary" id="btnSend" onclick="enviar()" disabled>Enviar ➤</button>
                </div>
                <div class="tip">💡 Selecione um equipamento para começar o atendimento.</div>
            </div>

            <div class="illustration">
                <img src="''' + ASSISTANT_IMG_URL + '''" alt="Assistente">
                <div class="pill">● Suporte técnico imediato</div>
                <h3>Assistente de Manutenção</h3>
                <p>Orientações rápidas baseadas em manuais técnicos.</p>
            </div>
        </div>

        <div class="footer">© Storopack - Assistente Técnico (beta)</div>
    </div>

<script>
// Variáveis globais
var moduloAtivo = null;
var submoduloAtivo = null;
var chat = document.getElementById('chat');
var msgInput = document.getElementById('msgInput');
var btnSend = document.getElementById('btnSend');
var badge = document.getElementById('badge');
var badgeText = document.getElementById('badgeText');
var hint = document.getElementById('hint');

// Dados dos módulos
var modulos = {
    airplus: {
        nome: 'AIRplus',
        img: 'https://img.directindustry.com/pt/images_di/photo-g/34409-10167740.webp',
        subs: null
    },
    airmove: {
        nome: 'AIRmove',
        img: 'https://www.storopack.com.br/fileadmin/_processed_/7/e/csm_PP_AP_AIRmove___machine_front_motive2_cushion_film_low_res_300dpi_061fd19c2b.jpg',
        subs: {
            'AIRmove 1': 'https://www.storopack.com.br/fileadmin/_processed_/7/e/csm_PP_AP_AIRmove___machine_front_motive2_cushion_film_low_res_300dpi_061fd19c2b.jpg',
            'AIRmove 2': 'https://www.storopack.com.br/fileadmin/_processed_/7/e/csm_PP_AP_AIRmove___machine_front_motive2_cushion_film_low_res_300dpi_061fd19c2b.jpg'
        }
    },
    paperplus: {
        nome: 'PAPERplus',
        img: 'https://www.storopack.com.br/fileadmin/_processed_/1/e/csm_PP_PP_Classic_CX_machine_0539_1280x580px_EUROPEAN_STAND_b213d265e2.png',
        subs: {
            'Shooter': 'https://www.storopack.com.br/fileadmin/_processed_/5/9/csm_PP_PP_Shooter_machine_tablestand_motive_1_1280x580px_6913698898.png',
            'Papillon': 'https://www.storopack.com.br/fileadmin/_processed_/c/a/csm_PP_PP_Papillon_machine_tablestand_motive1_1280x580px_b746b18c6a.png',
            'Classic': 'https://img.directindustry.com/pt/images_di/photo-g/34409-12098453.webp',
            'Track': 'https://swiftpak.imgix.net/uploads/Products/Papertech/16_12904_a.jpg',
            'CX': 'https://www.storopack.com.br/fileadmin/_processed_/1/e/csm_PP_PP_Classic_CX_machine_0539_1280x580px_EUROPEAN_STAND_b213d265e2.png',
            'Coiler': 'https://www.storopack.com.br/fileadmin/_processed_/1/4/csm_PP_PP_Coiler2_Classic_CX_machine_1985_low_res_1280x580px_6e072a7d32.png'
        }
    },
    foamplus: {
        nome: 'FOAMplus',
        img: 'https://www.storopack.com.br/fileadmin/_processed_/1/9/csm_PP_FP_Bag_Packer3_machine_6327_1280x580px_277b779f5d.png',
        subs: {
            'Bagpacker': 'https://www.storopack.com.br/fileadmin/_processed_/1/9/csm_PP_FP_Bag_Packer3_machine_6327_1280x580px_277b779f5d.png',
            'Handpacker': 'https://5.imimg.com/data5/HS/KC/MW/SELLER-8794370/foamplus-hand-packer-2-machine-1000x1000.jpg'
        }
    }
};

// Adiciona mensagem
function addMsg(texto, isUser) {
    var div = document.createElement('div');
    div.className = 'msg ' + (isUser ? 'msg-user' : 'msg-bot');
    var span = document.createElement('span');
    span.innerHTML = texto.replace(/\n/g, '<br>');
    div.appendChild(span);
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

// Mostra botões principais
function mostrarModulos() {
    var html = '<div class="modules">';
    for (var key in modulos) {
        html += '<button class="mod-btn ' + key + '" onclick="clicarModulo(\'' + key + '\')">';
        html += '<img src="' + modulos[key].img + '">';
        html += '<div class="label">' + modulos[key].nome + '</div>';
        html += '</button>';
    }
    html += '</div>';
    
    var div = document.createElement('div');
    div.className = 'msg msg-bot';
    div.innerHTML = html;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

// Clique no módulo
function clicarModulo(key) {
    var mod = modulos[key];
    if (mod.subs) {
        mostrarSubmodulos(key);
    } else {
        ativarModulo(key, null);
    }
}

// Mostra sub-módulos
function mostrarSubmodulos(key) {
    var mod = modulos[key];
    chat.innerHTML = '';
    addMsg('Olá! Selecione o modelo de <b>' + mod.nome + '</b>:');
    
    var html = '<div class="submods">';
    for (var nome in mod.subs) {
        html += '<button class="sub-btn" onclick="ativarModulo(\'' + key + '\', \'' + nome + '\')">';
        html += '<img src="' + mod.subs[nome] + '">';
        html += '<div class="label">' + nome + '</div>';
        html += '</button>';
    }
    html += '</div>';
    html += '<button class="btn btn-back" onclick="voltar()">← Voltar</button>';
    
    var div = document.createElement('div');
    div.className = 'msg msg-bot';
    div.innerHTML = html;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    
    hint.innerHTML = '<b>' + mod.nome + '</b> - Escolha o modelo:';
}

// Ativa módulo selecionado
function ativarModulo(key, sub) {
    moduloAtivo = key;
    submoduloAtivo = sub;
    var mod = modulos[key];
    var nome = sub ? mod.nome + ' ' + sub : mod.nome;
    
    // Atualiza badge
    badge.className = 'badge show ' + key;
    badgeText.textContent = 'Módulo: ' + nome;
    
    // Atualiza hint
    hint.innerHTML = '<b>' + nome + '</b> - Descreva o problema:';
    
    // Habilita input
    msgInput.disabled = false;
    msgInput.placeholder = 'Descreva o problema (ex: erro E3, travamento...)';
    btnSend.disabled = false;
    
    // Limpa chat e mostra mensagem
    chat.innerHTML = '';
    addMsg('Você selecionou <b>' + nome + '</b>.\n\nComo posso ajudar?');
    
    msgInput.focus();
}

// Volta ao início
function voltar() {
    moduloAtivo = null;
    submoduloAtivo = null;
    
    badge.className = 'badge';
    hint.textContent = 'Selecione o equipamento sobre o qual deseja suporte:';
    msgInput.disabled = true;
    msgInput.placeholder = 'Selecione um equipamento acima...';
    msgInput.value = '';
    btnSend.disabled = true;
    
    chat.innerHTML = '';
    addMsg('Olá! Sou o assistente técnico da Storopack. Como posso ajudar?');
    mostrarModulos();
}

// Envia mensagem
function enviar() {
    var texto = msgInput.value.trim();
    if (!texto || !moduloAtivo) return;
    
    addMsg(texto, true);
    msgInput.value = '';
    
    var modulo = moduloAtivo;
    if (submoduloAtivo) {
        modulo += '_' + submoduloAtivo.toLowerCase().replace(/ /g, '_');
    }
    
    fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mensagem: texto, modulo: modulo})
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        addMsg(data.resposta || 'Erro ao processar.');
    })
    .catch(function(err) {
        addMsg('Erro de conexão. Tente novamente.');
    });
}

// Enter para enviar
msgInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') enviar();
});

// Inicializa
voltar();
</script>
</body>
</html>
'''

@app.route("/")
def index():
    return HTML

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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)