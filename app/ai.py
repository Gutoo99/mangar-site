import os
import requests
from flask import Blueprint, request, jsonify
from typing import Optional

ai_bp = Blueprint("ai", __name__, url_prefix="/api")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def _call_chat(messages):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "ERRO. Configure OPENAI_API_KEY para respostas completas."
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"model": OPENAI_MODEL, "messages": messages},
            timeout=30,
        )
        print("OpenAI chat status:", r.status_code)
        if r.status_code != 200:
            print("OpenAI chat error body:", r.text[:500])
            return "Não consegui obter resposta da IA no momento."
        data = r.json()
        return (data["choices"][0]["message"]["content"] or "").strip()
    except Exception as e:
        print("OpenAI chat exception:", repr(e))
        return f"Erro ao consultar IA: {e}"

def wikipedia_image_for(term: str) -> Optional[str]:
    """
    Tenta pegar uma imagem da Wikipedia para o termo (ex.: nome da planta).
    Retorna URL da miniatura (https) ou None.
    """
    try:
        # 1) busca página
        s = requests.get(
            "https://pt.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": term, "format": "json"},
            timeout=15,
        ).json()
        hits = s.get("query", {}).get("search", [])
        if not hits:
            return None
        title = hits[0]["title"]

        # 2) pega imagem principal
        p = requests.get(
            "https://pt.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "prop": "pageimages",
                "titles": title,
                "format": "json",
                "pithumbsize": 600,
            },
            timeout=15,
        ).json()
        pages = p.get("query", {}).get("pages", {})
        for _, page in pages.items():
            thumb = page.get("thumbnail", {})
            if thumb.get("source"):
                return thumb["source"]
        return None
    except Exception as e:
        print("wiki image error:", e)
        return None

@ai_bp.route("/ai", methods=["POST"])
def ai_endpoint():
    """Chat genérico (usado na bolha e na página de Assistente)."""
    payload = request.get_json(force=True, silent=True) or {}
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "prompt vazio"}), 400

    messages = [
        {
            "role": "system",
            "content": (
                "Você é um consultor especializado em herbologia e agroecologia. "
                "Responda apenas perguntas do tema. "
                "Se for fora, diga educadamente: "
                "'Desculpe, só posso responder perguntas sobre herbologia e agroecologia.'"
            ),
        },
        {"role": "user", "content": prompt},
    ]
    answer = _call_chat(messages)
    return jsonify({"answer": answer})

@ai_bp.route("/herbario/search", methods=["POST"])
def herbario_search():
    """
    Recebe um formulário com dados da planta e devolve:
    - texto corrido recomendado pela IA
    - URL de imagem (Wikipedia) se possível
    """
    data = request.get_json(force=True, silent=True) or {}
    nome = (data.get("nome") or "").strip()
    nome_cient = (data.get("nome_cientifico") or "").strip()
    usos = (data.get("usos") or "").strip()
    sintomas = (data.get("sintomas") or "").strip()
    regiao = (data.get("regiao") or "").strip()

    if not (nome or nome_cient or sintomas or usos or regiao):
        return jsonify({"error": "Informe pelo menos um campo"}), 400

    # prompt “estruturado” para resposta em texto corrido
    prompt = (
        "Com base nos dados a seguir, sugira a planta mais recomendada (se houver), "
        "incluindo nome popular e científico, formas de preparo/uso, principais cuidados, "
        "possíveis contraindicações e referências tradicionais/éticas. "
        "Responda em PT-BR e de forma responsável (sem substituir orientação médica). "
        "\n\nDADOS:\n"
        f"- Nome popular: {nome or 'n/d'}\n"
        f"- Nome científico: {nome_cient or 'n/d'}\n"
        f"- Usos desejados/efeitos: {usos or 'n/d'}\n"
        f"- Sintomas/alvo: {sintomas or 'n/d'}\n"
        f"- Região/bioma: {regiao or 'n/d'}\n"
    )

    messages = [
        {
            "role": "system",
            "content": (
                "Você é um consultor de herbologia/agroecologia. "
                "Use base tradicional e boas práticas. Não faça promessas médicas. "
                "Quando possível, cite preparo (chá/infusão/decocção), parte da planta, e alertas."
            ),
        },
        {"role": "user", "content": prompt},
    ]
    texto = _call_chat(messages)

    # tenta achar imagem por nome científico, depois popular
    img_url = None
    if nome_cient:
        img_url = wikipedia_image_for(nome_cient)
    if not img_url and nome:
        img_url = wikipedia_image_for(nome)

    return jsonify({"texto": texto, "img_url": img_url})

@ai_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@ai_bp.route("/debug-env", methods=["GET"])
def debug_env():
    api_key = os.getenv("OPENAI_API_KEY")
    model = OPENAI_MODEL
    return jsonify({
        "has_key": bool(api_key),
        "key_prefix": (api_key[:8] + "...") if api_key else None,
        "model": model,
    })
