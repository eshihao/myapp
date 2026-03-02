from flask import Blueprint, jsonify, request
from services.conversation_service import (
    create_conversation,
    delete_conversation,
    list_conversations,
)

conversation_bp = Blueprint("conversation", __name__)


@conversation_bp.route("/api/conversations", methods=["GET"])
def get_conversations():
    conversations = list_conversations()
    return jsonify([
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at.isoformat()
        } for c in conversations
    ])


@conversation_bp.route("/api/conversations", methods=["POST"])
def new_conversation():
    title = request.json.get("title", "新对话")
    conv = create_conversation(title)
    return jsonify({
        "conversation_id": conv.id,
        "title": conv.title
    })


@conversation_bp.route("/api/conversations/<int:conversation_id>", methods=["DELETE"])
def remove_conversation(conversation_id):
    ok = delete_conversation(conversation_id)
    if not ok:
        return jsonify({"error": "对话不存在"}), 404
    return jsonify({"message": "对话已删除"})
