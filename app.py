from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Product

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 初始化資料庫
with app.app_context():
    db.create_all()

# 商品列表頁面
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('products.html', products=products)

# 帖子頁面
@app.route('/posts')
def posts():
    return render_template('posts.html')

# 關於頁面
@app.route('/about')
def about():
    return render_template('about.html')

# RESTful API - 新增商品
@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json
    new_product = Product(title=data['title'], size=data.get('size'), content=data.get('content'))
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201

# RESTful API - 查詢單篇商品
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

# RESTful API - 更新商品
@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.json
    product.title = data.get('title', product.title)
    product.size = data.get('size', product.size)
    product.content = data.get('content', product.content)
    db.session.commit()
    return jsonify(product.to_dict())

# RESTful API - 刪除商品
@app.route('/product/<int:product_id>/delete', methods=['GET', 'POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('index'))

# 顯示單篇商品頁面
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

# 新增商品頁面
@app.route('/product/new', methods=['GET', 'POST'])
def new_product():
    if request.method == 'POST':
        title = request.form['title']
        size = request.form['size']
        content = request.form['content']
        new_product = Product(title=title, size=size, content=content)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('product_form.html')

# 編輯商品頁面
@app.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.title = request.form['title']
        product.size = request.form['size']
        product.content = request.form['content']
        db.session.commit()
        return redirect(url_for('product_detail', product_id=product.id))
    return render_template('product_form.html', product=product)

if __name__ == '__main__': 
    app.run(debug=True)
