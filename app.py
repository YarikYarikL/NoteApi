from api import app, docs
from config import Config
from api.handlers import user

#все endpoint-ы должны быть зарегистрированы
docs.register(user.get_user_by_id)
docs.register(user.get_users)
docs.register(user.create_user)
docs.register(user.edit_user)
docs.register(user.delete_user)


if __name__ == '__main__':
    app.run(debug=Config.DEBUG, port=Config.PORT)
