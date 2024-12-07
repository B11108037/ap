from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 商品模型
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 確保有主鍵欄位
    title = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(50), nullable=True)
    content = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)
    image1_filename = db.Column(db.String(100), nullable=True)
    image2_filename = db.Column(db.String(100), nullable=True)
    image3_filename = db.Column(db.String(100), nullable=True)


# 用戶模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)



# 購物車項目模型
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # 關聯到 Product 模型
    product = db.relationship('Product', backref='cart_items')
    # 關聯到 User 模型
    user = db.relationship('User', backref='cart_items')
