from api import app, db, multi_auth, request
from api.models.note import NoteModel
from api.schemas.note import note_schema, notes_schema
from flask import abort
from sqlalchemy import or_


@app.route("/notes/<int:note_id>", methods=["GET"])
@multi_auth.login_required
def get_note_by_id(note_id):
    # авторизованный пользователь может получить только свою заметку или публичную заметку других пользователей
    # Попытка получить чужую приватную заметку, возвращает ответ с кодом 403
    user = multi_auth.current_user()
    note = db.get_or_404(NoteModel, note_id, description=f"Note with id={note_id} not found")
    print(f"{user.id = }")
    print(f"{note.private= }")
    if note.user_id == user.id or not note.private:
        return note_schema.dump(note), 200
    abort(403, {"message":"You cann't get this note"})


@app.route("/notes", methods=["GET"])
@multi_auth.login_required
def get_notes():
    # авторизованный пользователь получает только свои заметки и публичные заметки других пользователей
    user = multi_auth.current_user()
    notes = db.session.scalars(db.select(NoteModel).where(or_(NoteModel.user_id==user.id, NoteModel.private==False))).all()
    return notes_schema.dump(notes), 200


@app.route("/notes", methods=["POST"])
@multi_auth.login_required
def create_note():
    user = multi_auth.current_user()
    note_data = request.json
    note = NoteModel(user_id=user.id, **note_data)
    note.save()
    return note_schema.dump(note), 201


@app.route("/notes/<int:note_id>", methods=["PUT"])
@multi_auth.login_required
def edit_note(note_id):
    # Пользователь может редактировать ТОЛЬКО свои заметки.
    #  Попытка редактировать чужую заметку, возвращает ответ с кодом 403
    author = multi_auth.current_user()
    note = db.get_or_404(NoteModel, note_id, description=f"Note with id={note_id} not found")
    if note.user_id == author.id:
        note_data = request.json
        note.text = note_data.get("text") or note.private
        note.private = note_data.get("private") or note.private
        note.save()
        return note_schema.dump(note), 200
    abort(403, message="You cann't edit this note")


@app.route("/notes/<int:note_id>", methods=["DELETE"])
@multi_auth.login_required
def delete_note(self, note_id):
    # Пользователь может удалять ТОЛЬКО свои заметки.
    # Попытка удалить чужую заметку, возвращает ответ с кодом 403
    author = multi_auth.current_user()
    note = db.get_or_404(NoteModel, note_id, description=f"Note with id={note_id} not found")
    if note.user_id == author.id:
        note.delete()
        return {"message": f"Note with id={note_id} is deleted"}, 200
    return {"error": "This note is owned by other person"}, 403



    raise NotImplemented("Метод не реализован")
