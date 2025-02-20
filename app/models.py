from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin

mysql = MySQL()
bcrypt = Bcrypt()
login_manager = LoginManager()

class User(UserMixin):
    pass

class Product:
    def __init__(self, id, name, description, price, image, category):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.image = image
        self.category = category

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    
    if user:
        user_obj = User()
        user_obj.id = user[0]
        user_obj.username = user[1]
        return user_obj
    return None