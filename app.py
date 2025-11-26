from flask import Flask, render_template_string, request, jsonify
from assistente import responder_cliente

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <title>Assistente Técnico</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 40px auto; 
        }
        #chat { 
            border: 1px solid #ccc; 
            padding: 10px; 
            height: 400px; 
            overflow-y: auto; 
        }
        .msg-user { text-align: right; margin: 5px 0; }
        .msg-bot { text-align: left; margin: 5px 0; }
        .msg-user span { background:#e0f7fa; padding:5px 8px; border-radius:4px; display:inline-block;}
        .msg-bot span { background:#f1f1f1; padding:5px 8px; border-radius:4px; display:inline-block;}
    </style>
</head>
<body>
    <h1>Assistente Técnico de Equipamentos</h1>

    <div id="chat"></div>

    <form id="form-chat">
        <input type="text" id="mensagem" placeholder="Digite sua pergunta..." style="width:80%;">
        <button type="submit">Enviar</button>
    </form>

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

        const resposta = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ message: text })
        });

        const data = await resposta.json();
        addMessage("bot", data.answer || "Erro ao responder.");
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

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat_route():
    data = request.get_json() or {}
    pergunta = data.get("message", "").strip()

    if not pergunta:
        return jsonify({"answer": "Digite uma pergunta."}), 400

    resposta = responder_cliente(pergunta)
    return jsonify({"answer": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
