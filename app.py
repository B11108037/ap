from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

# 從 models.py 導入 db 和類
from models import db, Product, User, CartItem

# 設置 Flask 應用和資料庫配置
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用於 session 和加密
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# 初始化資料庫
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()


# 提供自定義的 `getattr` 函數給模板
@app.context_processor
def utility_functions():
    return dict(getattr=getattr)


# 檢查檔案類型是否允許
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.context_processor
def inject_user():
    """提供當前用戶信息給模板"""
    current_user = None
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
    return {'current_user': current_user}


# 首頁 - 商品列表
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('products.html', products=products)


# 註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 使用 pbkdf2:sha256 進行密碼雜湊
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash('註冊成功，請登入！', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


# 登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('登入成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('無效的使用者名稱或密碼！', 'danger')
    
    return render_template('login.html')


# 登出
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('已成功登出！', 'success')
    return redirect(url_for('login'))


# 新增商品
@app.route('/product/new', methods=['GET', 'POST'])
def new_product():
    if request.method == 'POST':
        title = request.form['title']
        size = request.form['size']
        content = request.form['content']
        price = float(request.form['price'])

        image_filenames = []
        for i in range(1, 4):
            image_field = f'image{i}'
            if image_field in request.files:
                image = request.files[image_field]
                if image and allowed_file(image.filename):
                    image_filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                    image_filenames.append(image_filename)

        # 創建商品並保存圖片檔案名稱
        new_product = Product(
            title=title,
            size=size,
            content=content,
            price=price,
            image1_filename=image_filenames[0] if len(image_filenames) > 0 else None,
            image2_filename=image_filenames[1] if len(image_filenames) > 1 else None,
            image3_filename=image_filenames[2] if len(image_filenames) > 2 else None
        )
        db.session.add(new_product)
        db.session.commit()
        flash('商品新增成功！', 'success')
        return redirect(url_for('index'))

    return render_template('product_form.html')


# 購物車
@app.route('/cart')
def view_cart():
    user_id = session.get('user_id')
    cart_items = CartItem.query.filter_by(user_id=user_id).all()

    total_price = sum(item.quantity * item.product.price for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@app.route('/cart/remove/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
    if 'user_id' not in session:
        flash("請先登入才能操作購物車！", "danger")
        return redirect(url_for('login'))
    
    cart_item = CartItem.query.get_or_404(cart_item_id)

    if cart_item.user_id != session['user_id']:
        flash("你無法移除此購物車項目！", "danger")
        return redirect(url_for('view_cart'))

    db.session.delete(cart_item)
    db.session.commit()
    flash("已成功移除購物車中的商品。", "success")
    return redirect(url_for('view_cart'))


# 加入購物車
@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash("請先登入才能加入購物車！", "danger")
        return redirect(url_for('login'))

    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))

    cart_item = CartItem.query.filter_by(
        product_id=product_id, user_id=session.get('user_id')
    ).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            product_id=product_id, quantity=quantity, user_id=session.get('user_id')
        )
        db.session.add(cart_item)

    db.session.commit()
    flash(f"已將 {product.title} 加入購物車！", "success")
    return redirect(url_for('view_cart'))


# 商品刪除
@app.route('/product/<int:product_id>/delete', methods=['GET', 'POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('index'))
# Posts 頁面
@app.route('/posts')
def posts():
    return render_template('posts.html')

# About 頁面
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
