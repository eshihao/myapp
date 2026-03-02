import os
from werkzeug.utils import secure_filename
from models import db, NpyFile, Conversation
from config import Config
from datetime import datetime

# 支持的文件类型
ALLOWED_EXT = {".npy"}

def allowed_file(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXT

def save_npy_file(file, conversation_id: int = None) -> dict:

    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        return {"error": "Only .npy files are allowed"}, 400

    # -------------------
    # 确定保存路径
    # -------------------
    save_dir = Config.UPLOAD_DIR
    os.makedirs(save_dir, exist_ok=True)

    # 防止重名覆盖
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    filename_unique = f"{timestamp}_{filename}"
    filepath = os.path.join(save_dir, filename_unique)
    file.save(filepath)

    # -------------------
    # 读取 npy 文件 shape/dtype
    # -------------------
    try:
        import numpy as np
        data = np.load(filepath)
        shape = str(data.shape)
        dtype = str(data.dtype)
    except Exception as e:
        return {"error": f"Failed to read npy file: {e}"}, 500

    # -------------------
    # 关联 Conversation
    # -------------------
    conversation = None
    if conversation_id:
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            conversation = Conversation()
            db.session.add(conversation)
            db.session.commit()

    # -------------------
    # 写入数据库
    # -------------------
    npy_record = NpyFile(
        conversation_id=conversation.id if conversation else None,
        filename=filename,
        filepath=filepath,
        shape=shape,
        dtype=dtype
    )

    db.session.add(npy_record)
    db.session.commit()

    return {
        "file_id": npy_record.id,
        "filename": filename,
        "filepath": filepath,
        "shape": shape,
        "dtype": dtype,
        "conversation_id": conversation.id if conversation else None
    }
