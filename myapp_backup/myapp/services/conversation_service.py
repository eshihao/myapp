from models import db, Conversation


def create_conversation(title="新对话"):
    conv = Conversation(title=title)
    db.session.add(conv)
    db.session.commit()
    return conv


def delete_conversation(conversation_id):
    conv = Conversation.query.get(conversation_id)
    if not conv:
        return False
    db.session.delete(conv)
    db.session.commit()
    return True


def list_conversations():
    return Conversation.query.order_by(Conversation.created_at.desc()).all()


def get_conversation(conversation_id):
    return Conversation.query.get(conversation_id)
