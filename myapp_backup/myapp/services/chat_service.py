# from models import db, ChatHistory
# from services.model_service import MedicalChatModel

# model = MedicalChatModel()

# def chat_with_image(image_path, question):
#     answer, _ = model.infer(image_path, question)

#     record = ChatHistory(
#         user_message=question,
#         bot_message=answer
#     )
#     db.session.add(record)
#     db.session.commit()

#     return answer

from models import db, Conversation, ChatMessage, NpyFile
from services.model_service import MedicalChatModel
from typing import Optional, List, Dict

# 单例模型加载（全局）
MODEL_PATH = "/data/esh/myapp/3dmodel/M3D-LaMed-Phi-3-4B"
model = MedicalChatModel(model_name=MODEL_PATH)


# ========================================
# 核心对话接口
# ========================================
def chat_with_image(
    conversation_id: Optional[int],
    npy_file_id: int,
    question: str
) -> Dict:
    """
    根据上传的 npy 文件和问题，生成 AI 回复，并记录对话历史

    参数:
        conversation_id: 可选，指定 Conversation，会话不存在则新建
        npy_file_id: 必须，关联的 NpyFile ID
        question: 用户问题

    返回:
        dict: {
            "conversation_id": ...,
            "chat_message_id": ...,
            "answer": "...",
            "segmentation": np.ndarray or None
        }
    """

    npy_file = NpyFile.query.get(npy_file_id)
    if not npy_file:
        raise ValueError(f"NPY file id {npy_file_id} not found")

    npy_path = npy_file.filepath


    if conversation_id:
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            # 如果指定 id 不存在，重新创建
            conversation = Conversation()
            db.session.add(conversation)
            db.session.commit()
    else:
        conversation = Conversation()
        db.session.add(conversation)
        db.session.commit()


    history_msgs: List[Dict] = [
        {"role": msg.role, "content": msg.content}
        for msg in ChatMessage.query.filter_by(conversation_id=conversation.id).order_by(ChatMessage.timestamp.asc()).all()
    ]

    result = model.infer(
        npy_path=npy_path,
        question=question,
        chat_history=history_msgs
    )

    answer_text = result["answer"]
    seg_mask = result["segmentation"]

    chat_msg = ChatMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=answer_text
    )

    db.session.add(chat_msg)
    db.session.commit()

    return {
        "conversation_id": conversation.id,
        "chat_message_id": chat_msg.id,
        "answer": answer_text,
        "segmentation": seg_mask
    }
