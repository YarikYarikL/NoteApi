from flask import jsonify
from api import app, db, request, multi_auth
from api.models.user import UserModel
from api.schemas.user import UserEditSchema, UserSchema, user_schema, users_schema, UserRequestSchema
from flask_apispec import doc, marshal_with, use_kwargs


@app.route("/users/<int:user_id>", provide_automatic_options=False)
@doc(description='Api for getting user by id.', tags=['Users'], summary="Get user by id")
@doc(responses={"404": {"description": "User not found"}})
@marshal_with(UserSchema, code=200)
def get_user_by_id(user_id):
    user = db.get_or_404(UserModel, user_id, description=f"User with id={user_id} not found")
    return user, 200


@app.route("/users", provide_automatic_options=False)
@doc(description='Api for getting list of users.', tags=['Users'], summary="Get user's list")
@marshal_with(UserSchema(many=True), code=200)
def get_users():
    users = db.session.scalars(db.select(UserModel)).all()
    return users


@app.route("/users", methods=["POST"], provide_automatic_options=False)
@doc(description='Api for creating new user.', tags=['Users'], summary="Create new user")
@use_kwargs(UserRequestSchema, location='json')
@marshal_with(UserSchema, code=201)
def create_user(**kwargs):
    user = UserModel(**kwargs)
    # обработчик на создание пользователя с неуникальным username
    if db.session.scalars(db.select(UserModel).where(UserModel.username==user.username)).one_or_none():
        return {"error": "User already exists"}, 409
    user.save()
    return user,201


@app.route("/users/<int:user_id>", methods=["PUT"], provide_automatic_options=False)
# @multi_auth.login_required(role="admin")
@doc(description='Api for user edit', tags=['Users'], summary="Edit user")
@use_kwargs(UserEditSchema, )
@marshal_with(UserSchema, code=200)
def edit_user(user_id, **kwargs):
    user = db.get_or_404(UserModel, user_id, description=f"Note with id={user_id} not found")
    for key, value in kwargs.items():
        setattr(user, key, value)
    user.save()
    return user


@app.route("/users/<int:user_id>", methods=["DELETE"], provide_automatic_options=False)
@multi_auth.login_required(role="admin")
@doc(responses={"404": {"description": "User not found"}})
@doc(description='Api for user delete', tags=['Users'], summary="Delete user")
def delete_user(user_id):
    """
    Пользователь может удалять ТОЛЬКО свои заметки
    """
    user = db.get_or_404(UserModel, user_id, description=f"Note with id={user_id} not found")
    user.delete()
    return jsonify({"message": f"User with={user_id} is deleted"}), 200
    