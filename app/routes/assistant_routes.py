from flask import Blueprint, render_template, request, jsonify
from app.services.llm_assistant import LLMAssistant

assistant_bp = Blueprint("assistant", __name__, template_folder="../templates")


@assistant_bp.route("/")
def assistant_page():
    return render_template("assistant.html")


@assistant_bp.route("/chat", methods=["POST"])
def chat():
    """Handle chat with LLM assistant"""
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"status": "error", "message": "No message provided"}), 400

        assistant = LLMAssistant()
        response = assistant.chat(user_message)

        return jsonify({"status": "success", "response": response})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
