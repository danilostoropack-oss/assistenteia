from flask import Flask, session, request, jsonify, render_template_string
from openai import OpenAI, RateLimitError
from dotenv import load_dotenv
import os

# ============================ CONFIG ============================

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
app.secret_key = "storopack_secret_key"

# ============================ DADOS FIXOS ============================

CONTATO_EMAIL = "packaging.br@storopack.com"
CONTATO_TELEFONE = "(11) 5677-4699"

LOGISTICA_STOROPACK = {
    "endereco": "R. Agostino Togneri, 457 - Jurubatuba, São Paulo - SP, 04690-090",
    "horario": "09:00 às 12:00 e 13:00 às 16:00 (intervalo 12h–13h)"
}

VIDEOS_STOROPACK = {
    "airplus": {
        "titulo": "AIRplus - Travesseiro de Ar",
        "url": "https://www.youtube.com/watch?v=IbG1o-UbrtI"
    },
    "airmove": {
        "titulo": "AIRmove - Travesseiros de Ar (linha compacta)",
        "url": "https://www.youtube.com/watch?v=IbG1o-UbrtI"  # ajuste se tiver vídeo específico
    },
    "paperplus": {
        "titulo": "PAPERplus - Papel de Proteção",
        "url": "https://www.youtube.com/watch?v=a8iCa46yRu4"
    },
    "foamplus": {
        "titulo": "FOAMplus - Espuma Expandida",
        "url": "https://www.youtube.com/watch?v=bhVK8KCJihs"
    },
    "paperbubble": {
        "titulo": "PAPERbubble - Papel Almofadado",
        "url": "https://www.youtube.com/watch?v=TQYRcHj_v0E"
    }
}

# Palavras que ligam a Storopack de forma geral (quando não há módulo)
ALLOWED_KEYWORDS_GLOBAL = [
    "storopack", "airplus", "airmove", "paperplus", "foamplus", "paperbubble",
    "embalagem", "proteção", "protecao", "jurubatuba", "coleta", "pallet",
    "saquinho", "travesseiro", "bolha", "cushion", "void", "bubble", "filme", "bobina",
    "erro", "manutencao", "manutenção", "ajuste", "parada automática", "parada automatica"
]

# Palavras específicas por módulo (pra reforçar o foco, se você quiser usar depois)
MODULE_KEYWORDS = {
    "AIRplus": ["airplus", "travesseiro", "void", "bubble", "cushion", "wrap", "filme de ar", "almofada de ar"],
    "AIRmove": ["airmove", "airmove²", "air move", "bobina compacta", "máquina pequena", "mini travesseiro"],
    "PAPERplus": ["paperplus", "papel", "papillon", "classic", "track", "paper bubble", "paperbubble"],
    "FOAMplus": ["foamplus", "espuma", "foam", "bagpacker", "handpacker", "espuma expandida"]
}

# ============================ PROMPT BASE ============================

ASSISTANT_PROMPT = f"""
Você é o Assistente Oficial da STOROpack Brasil.

O que você pode ajudar:
• Dúvidas sobre AIRplus, AIRmove, PAPERplus, FOAMplus e PAPERbubble.
• Manutenção simples, erros, operação e ajustes.
• Vídeos de suporte.
• Logística e endereço da unidade de Jurubatuba.
• Contato oficial da empresa.

CONTATO OFICIAL:
• Email: {CONTATO_EMAIL}
• Telefone: {CONTATO_TELEFONE}

LOGÍSTICA:
• Endereço: {LOGISTICA_STOROPACK["endereco"]}
• Horário: {LOGISTICA_STOROPACK["horario"]}

ESTILO WHATSAPP:
• Frases curtas e diretas.
• Sempre separe ideias com quebras de linha.
• Quando for passo a passo, use:
  1) Passo
  2) Passo
  3) Passo
• Não use markdown (sem **negrito**, #, listas com "-").
• Pode usar 1 emoji discreto, se fizer sentido.

MÓDULOS E REGRAS:
• O sistema pode informar uma linha como "MÓDULO ATUAL: AIRplus", "AIRmove", "PAPERplus" ou "FOAMplus".
• Quando houver MÓDULO ATUAL:
  - Responda somente sobre essa linha de solução.
  - Exemplos:
    - Se MÓDULO ATUAL = AIRplus:
      Fale apenas de travesseiros de ar AIRplus (VOID, BUBBLE, CUSHION, WRAP), operação, manutenção e erros do AIRplus.
    - Se MÓDULO ATUAL = AIRmove:
      Fale apenas sobre a máquina AIRmove, seus filmes, ajustes e problemas de operação.
    - Se MÓDULO ATUAL = PAPERplus:
      Fale apenas sobre PAPERplus Classic, Track, Papillon e PAPERbubble.
    - Se MÓDULO ATUAL = FOAMplus:
      Fale apenas sobre FOAMplus, espuma expandida, Bagpacker, Handpacker e sua operação.
  - Se o cliente perguntar sobre outra linha (por exemplo, está no AIRplus e pergunta sobre PAPERplus), responda educadamente algo como:
    "Você está no módulo AIRplus. Para falar de outra solução, clique em 'Voltar ao Menu' e escolha a linha que você quer."

FORA DO ESCOPO:
• Se a pergunta não tiver relação com embalagens, equipamentos ou logística da STOROPack, responda apenas:
  "Posso ajudar apenas com assuntos técnicos, comerciais ou logísticos da STOROpack."
"""

# ============================ FUNÇÕES AUXILIARES ============================

def esta_no_escopo_global(texto: str) -> bool:
    t = texto.lower()
    return any(k in t for k in ALLOWED_KEYWORDS_GLOBAL)

def limpar_formatacao(texto: str) -> str:
    # Remove marcações simples de markdown para ficar mais "WhatsApp"
    return texto.replace("**", "").replace("*", "")

def encontrar_videos(pergunta: str, modulo: str | None) -> list[dict]:
    """Retorna vídeos relevantes baseados primeiro no módulo, depois no texto."""
    videos = []

    # Prioriza o módulo
    if modulo:
        chave = modulo.lower()
        if chave in VIDEOS_STOROPACK:
            videos.append(VIDEOS_STOROPACK[chave])

    # Se não encontrou nada pelo módulo, tenta por palavras
    if not videos:
        p = pergunta.lower()
        for chave, video in VIDEOS_STOROPACK.items():
            if chave in p:
                videos.append(video)

    return videos[:2]

def responder_cliente(pergunta: str, modulo: str | None = None) -> str:
    pergunta = (pergunta or "").strip()

    if not pergunta:
        return "Oi! Como posso te ajudar hoje? 🙂"

    # Sem módulo: valida se está no escopo geral
    if not modulo and not esta_no_escopo_global(pergunta):
        return "Posso ajudar apenas com assuntos técnicos, comerciais ou logísticos da STOROpack."

    # Monta contexto de módulo para o modelo
    contexto_modulo = ""
    if modulo:
        contexto_modulo = f"\n\nMÓDULO ATUAL: {modulo}."

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": ASSISTANT_PROMPT + contexto_modulo},
                {"role": "user", "content": pergunta}
            ],
            max_tokens=500,
            temperature=0.6,
        )

        texto = limpar_formatacao(resposta.choices[0].message.content)
        videos = encontrar_videos(pergunta, modulo)

        if videos:
            texto += "\n\nDá uma olhada nesse vídeo:\n"
            for v in videos:
                texto += f"{v['titulo']}\n{v['url']}\n"

        return texto

    except RateLimitError:
        return "Limite da API foi atingido. Tente novamente em alguns instantes."
    except Exception as e:
        return f"Erro ao acessar serviço: {e}"

# ============================ FRONT HTML ============================

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Assistente STOROpack</title>

<style>
body { font-family: Arial; max-width: 720px; margin: auto; }
.chat { border: 1px solid #ccc; height: 470px; padding: 10px; overflow-y: auto; border-radius: 6px; }
.msg-user { text-align: right; margin: 8px 0; }
.msg-bot { text-align: left; margin: 8px 0; }
.msg-user span { background: #DCF8C6; padding: 8px 12px; border-radius: 8px; display: inline-block; }
.msg-bot span { background: #eee; padding: 8px 12px; border-radius: 8px; display: inline-block; }
button { margin: 4px; padding: 6px 12px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; }
#msg { padding: 6px; }
.top-bar { margin-bottom: 8px; }
.info-modulo { font-size: 0.9rem; color: #555; margin-bottom: 8px; }
</style>

</head>
<body>

<h2>Assistente STOROpack</h2>

<div class="top-bar">
    <button onclick="selecionarModulo('AIRplus')">AIRplus</button>
    <button onclick="selecionarModulo('AIRmove')">AIRmove</button>
    <button onclick="selecionarModulo('PAPERplus')">PAPERplus</button>
    <button onclick="selecionarModulo('FOAMplus')">FOAMplus</button>
    <button onclick="voltarMenu()">Voltar ao Menu</button>
</div>

<div class="info-modulo" id="info-modulo">
    Nenhum módulo selecionado. Você pode escolher uma linha acima ou simplesmente mandar sua dúvida.
</div>

<div class="chat" id="chat">
    <div class="msg-bot"><span>Bom dia! Em que posso ajudar hoje? 🙂</span></div>
</div>

<br>

<input type="text" id="msg" placeholder="Digite sua mensagem..." style="width:80%">
<button onclick="enviar()">Enviar</button>

<script>
function addUser(msg){
    let c = document.getElementById("chat");
    c.innerHTML += "<div class='msg-user'><span>"+escapeHtml(msg)+"</span></div>";
    c.scrollTop = c.scrollHeight;
}

function addBot(msg){
    let c = document.getElementById("chat");
    msg = escapeHtml(msg).replace(/\\n/g,"<br>");
    c.innerHTML += "<div class='msg-bot'><span>"+msg+"</span></div>";
    c.scrollTop = c.scrollHeight;
}

function setInfoModulo(texto){
    document.getElementById("info-modulo").innerText = texto;
}

function escapeHtml(texto){
    return texto
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

async function selecionarModulo(modulo){
    const r = await fetch("/api/modulo", {
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body:JSON.stringify({ modulo })
    });

    const data = await r.json();
    setInfoModulo(data.modulo_texto);
    addBot(data.resposta);
}

async function voltarMenu(){
    const r = await fetch("/api/voltar", {
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body:"{}"
    });

    const data = await r.json();
    setInfoModulo(data.modulo_texto);
    addBot(data.resposta);
}

async function enviar(){
    const campo = document.getElementById("msg");
    const texto = campo.value.trim();
    if(!texto) return;

    addUser(texto);
    campo.value = "";

    const r = await fetch("/api/msg", {
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body:JSON.stringify({ mensagem:texto })
    });

    const data = await r.json();
    addBot(data.resposta);
}
</script>

</body>
</html>
"""

# ============================ ROTAS FLASK ============================

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/modulo", methods=["POST"])
def api_modulo():
    data = request.get_json()
    modulo = data.get("modulo")
    session["modulo"] = modulo

    texto_modulo = ""
    if modulo == "AIRplus":
        texto_modulo = "Módulo atual: AIRplus (travesseiros de ar: VOID, BUBBLE, CUSHION, WRAP)."
    elif modulo == "AIRmove":
        texto_modulo = "Módulo atual: AIRmove (linha compacta de travesseiros de ar)."
    elif modulo == "PAPERplus":
        texto_modulo = "Módulo atual: PAPERplus (Classic, Track, Papillon e PAPERbubble)."
    elif modulo == "FOAMplus":
        texto_modulo = "Módulo atual: FOAMplus (espuma expandida, Bagpacker, Handpacker)."
    else:
        texto_modulo = "Nenhum módulo selecionado."

    resposta = f"Beleza! Vamos falar sobre {modulo}. Pode mandar sua dúvida 🙂"
    return jsonify({"resposta": resposta, "modulo_texto": texto_modulo})

@app.route("/api/voltar", methods=["POST"])
def api_voltar():
    session["modulo"] = None
    resposta = (
        "Voltei para o menu principal.\n\n"
        "Agora você pode escolher outra solução nos botões acima "
        "ou mandar uma dúvida geral sobre Storopack."
    )
    texto_modulo = "Nenhum módulo selecionado. Você pode escolher uma linha acima ou mandar sua dúvida."
    return jsonify({"resposta": resposta, "modulo_texto": texto_modulo})

@app.route("/api/msg", methods=["POST"])
def api_msg():
    data = request.get_json()
    texto = data.get("mensagem", "")
    modulo = session.get("modulo")
    resposta = responder_cliente(texto, modulo)
    return jsonify({"resposta": resposta})

# ============================ RUN ============================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
