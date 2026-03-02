import os
from flask import Blueprint, request, jsonify, current_app
from services.upload_service import save_npy_file

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/api/upload", methods=["POST"])
def upload_file():
    """
    上传 npy 文件并写入数据库
    可选参数 conversation_id，用于关联已有会话
    """
    file = request.files.get("file")
    conversation_id = request.form.get("conversation_id", type=int)

    if not file:
        return jsonify({"error": "未上传文件"}), 400

    if not file.filename.endswith(".npy"):
        return jsonify({"error": "仅支持 .npy 文件"}), 400

    try:
        result = save_npy_file(file, conversation_id=conversation_id)
        if "error" in result:
            return jsonify(result), 400

        return jsonify({
            "message": "上传成功",
            "file_info": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
