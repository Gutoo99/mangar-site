// Bolha de IA global (todas as páginas)
(function () {
  const rootId = "ai-floating";
  if (document.getElementById(rootId)) return;

  const box = document.createElement("div");
  box.id = rootId;
  box.style.position = "fixed";
  box.style.right = "18px";
  box.style.bottom = "18px";
  box.style.width = "360px";
  box.style.maxWidth = "90vw";
  box.style.zIndex = "9999";
  box.innerHTML = `
    <div style="background:#0d2818;color:#e8f5e9;border-radius:12px;box-shadow:0 12px 30px rgba(0,0,0,.35);overflow:hidden;border:1px solid rgba(255,255,255,.06)">
      <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:#10321f;border-bottom:1px solid rgba(255,255,255,.06)">
        <strong>Consultor IA</strong>
        <button id="ai-close" style="all:unset;cursor:pointer;font-size:18px;line-height:1">×</button>
      </div>
      <div id="ai-msgs" style="height:220px;overflow:auto;padding:12px;display:flex;flex-direction:column;gap:10px"></div>
      <div style="display:flex;gap:8px;padding:12px;border-top:1px solid rgba(255,255,255,.06)">
        <input id="ai-input" placeholder="Pergunte sobre agroecologia/herbor..." style="flex:1;padding:10px;border-radius:8px;border:1px solid #1b4d2e;background:#0e2015;color:#e8f5e9">
        <button id="ai-send" style="background:#2e7d32;border:0;color:#fff;border-radius:8px;padding:10px 14px;cursor:pointer">Enviar</button>
      </div>
      <div style="font-size:12px;color:#b7cbbb;padding:0 12px 10px">Informativo. Não substitui aconselhamento profissional.</div>
    </div>
  `;
  document.body.appendChild(box);

  const msgs = document.getElementById("ai-msgs");
  const input = document.getElementById("ai-input");
  const send  = document.getElementById("ai-send");

  function add(role, text){
    const b = document.createElement("div");
    b.style.alignSelf = role === "user" ? "flex-end" : "flex-start";
    b.style.maxWidth = "85%";
    b.style.borderRadius = "10px";
    b.style.padding = "8px 10px";
    b.style.whiteSpace = "pre-wrap";
    b.style.background = role === "user" ? "#1b4d2e" : "#123a24";
    b.innerText = text;
    msgs.appendChild(b);
    msgs.scrollTop = msgs.scrollHeight;
  }

  // mensagem inicial
  add("bot", "Olá! Para ajudar, me diga a planta/efeito desejado, sintomas e sua região/bioma.");

  send.addEventListener("click", async () => {
    const q = input.value.trim();
    if (!q) return;
    add("user", q);
    input.value = "";

    const thinking = document.createElement("div");
    thinking.innerText = "Pensando...";
    thinking.style.opacity = ".8";
    thinking.style.alignSelf = "flex-start";
    thinking.style.padding = "6px 8px";
    msgs.appendChild(thinking);
    msgs.scrollTop = msgs.scrollHeight;

    try {
      const r = await fetch("/api/ai", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({prompt: q})
      });
      const data = await r.json();
      thinking.remove();
      add("bot", data.answer || data.error || "Não consegui obter resposta no momento.");
    } catch(e) {
      thinking.remove();
      add("bot", "Erro ao contatar o servidor.");
    }
  });

  document.getElementById("ai-close").onclick = () => box.remove();
})();
