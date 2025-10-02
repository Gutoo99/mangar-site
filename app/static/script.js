(function(){
  const fab = document.getElementById("ia-fab");
  const panel = document.getElementById("ia-panel");
  const closeBtn = document.getElementById("ia-close");
  const log = document.getElementById("ia-log");
  const input = document.getElementById("ia-prompt");
  const send = document.getElementById("ia-send");

  function appendMsg(cls, text){
    const el = document.createElement("div");
    el.className = "ia-msg " + cls;
    el.textContent = text;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
  }

  async function ask(){
    const prompt = (input.value || "").trim();
    if(!prompt) return;
    appendMsg("me", prompt);
    input.value = "";
    appendMsg("ai", "Pensando...");
    try{
      const res = await fetch("/api/ai", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ prompt })
      });
      const data = await res.json();
      const last = log.querySelector(".ia-msg.ai:last-child");
      last.textContent = data.answer || data.error || "Erro.";
    }catch(e){
      const last = log.querySelector(".ia-msg.ai:last-child");
      last.textContent = "Erro ao consultar IA.";
    }
  }

  window.__toggleIA = function(){
    panel.style.display = (panel.style.display === "flex") ? "none" : "flex";
  };

  if(fab) fab.addEventListener("click", window.__toggleIA);
  if(closeBtn) closeBtn.addEventListener("click", () => panel.style.display = "none");
  if(send) send.addEventListener("click", ask);
  if(input) input.addEventListener("keydown", (e)=>{ if(e.key==="Enter") ask(); });
})();
