from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/sobre")
def sobre():
    return render_template("sobre.html")

@main_bp.route("/herbario")
def herbario():
    # página com formulário
    return render_template("herbario.html")

@main_bp.route("/assistente")
def assistente():
    # página com chat dedicado
    return render_template("assistente.html")
