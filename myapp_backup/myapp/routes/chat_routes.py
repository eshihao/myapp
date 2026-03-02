# from flask import Blueprint, request, jsonify
# from services.chat_service import chat_with_image

# chat_bp = Blueprint("chat", __name__)

# @chat_bp.route("/api/chat", methods=["POST"])
# def chat():
#     data = request.json
#     question = data["question"]
#     image_path = "/data/esh/myapp/example_00.npy"

#     answer = chat_with_image(image_path, question)
#     return jsonify({"answer": answer})
from flask import Blueprint, request, jsonify
from services.chat_service import chat_with_image

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    """
    请求 JSON 示例：
    {
        "question": "请分析该病灶",
        "file_id": 1,
        "conversation_id": 1   # 可选
    }
    """
    try:
        data = request.json
        question = data.get("question")
        file_id = data.get("file_id")
        conversation_id = data.get("conversation_id")

        if not question or not file_id:
            return jsonify({"error": "缺少 question 或 file_id"}), 400

        # 调用 chat_service
        result = chat_with_image(
            conversation_id=conversation_id,
            npy_file_id=file_id,
            question=question
        )

        return jsonify({
            "message": "success",
            "conversation_id": result["conversation_id"],
            "chat_message_id": result["chat_message_id"],
            "answer": result["answer"],
            "segmentation": result["segmentation"]  # 前端可视化用
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
