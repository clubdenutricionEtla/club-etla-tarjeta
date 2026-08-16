import re

# ============================================================
# 1. requirements.txt
# ============================================================
with open('requirements.txt', 'r', encoding='utf-8') as f:
    req = f.read()
if 'requests' not in req:
    req = req.rstrip('\n') + '\nrequests==2.31.0\n'
    print("✅ requests agregado a requirements.txt")
else:
    print("ℹ️ requests ya estaba en requirements.txt")
with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write(req)

# ============================================================
# 2. models.py - modelo Product
# ============================================================
with open('models.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'class Product' not in content:
    anchor = "class VisitHistory(db.Model):"
    product_class = '''class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


'''
    content = content.replace(anchor, product_class + anchor)
    print("✅ Modelo Product agregado a models.py")
else:
    print("ℹ️ Product ya existía en models.py")

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(content)

# ============================================================
# 3. app.py
# ============================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

if 'SUPABASE_SERVICE_KEY' not in app_content:
    old_imports = "from models import db, Client, VisitHistory, Employee, Achievement, ClientAchievement, Promotion, Referral, check_achievements, init_achievements"
    new_imports = old_imports + "\nfrom models import Product\nimport requests as http_requests"
    app_content = app_content.replace(old_imports, new_imports)

    old_cors = "CORS(app)"
    new_cors = '''CORS(app)

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://ijxynllcahohcgfoqpzt.supabase.co')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')

def upload_product_image(file_storage):
    if not file_storage or not SUPABASE_SERVICE_KEY:
        return None
    ext = file_storage.filename.rsplit('.', 1)[-1].lower() if '.' in file_storage.filename else 'jpg'
    filename = f"{secrets.token_hex(8)}.{ext}"
    file_bytes = file_storage.read()
    upload_url = f"{SUPABASE_URL}/storage/v1/object/product-images/{filename}"
    resp = http_requests.post(
        upload_url,
        headers={
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': file_storage.mimetype or 'image/jpeg'
        },
        data=file_bytes
    )
    if resp.status_code in (200, 201):
        return f"{SUPABASE_URL}/storage/v1/object/public/product-images/{filename}"
    return None'''
    app_content = app_content.replace(old_cors, new_cors)
    print("✅ Configuración de Supabase Storage agregada")
else:
    print("ℹ️ La configuración de Supabase Storage ya existía")

if "def admin_products" not in app_content:
    anchor = "# ===== PROMOCIONES ====="
    products_routes = '''# ===== PRODUCTOS (CATÁLOGO) =====

@app.route('/admin/products')
def admin_products():
    if 'employee_id' not in session:
        return redirect(url_for('login'))
    employee = Employee.query.get(session['employee_id'])
    if not employee or employee.role != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/products.html')

@app.route('/api/admin/products', methods=['GET'])
def api_get_products():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    products = Product.query.order_by(Product.id.desc()).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': float(p.price) if p.price is not None else None,
        'image_url': p.image_url,
        'is_active': p.is_active
    } for p in products])

@app.route('/api/admin/products', methods=['POST'])
def api_create_product():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401

    name = request.form.get('name')
    description = request.form.get('description', '')
    price = request.form.get('price')
    image_file = request.files.get('image')

    if not name:
        return jsonify({'error': 'El nombre es requerido'}), 400

    image_url = upload_product_image(image_file) if image_file else None

    product = Product(
        name=name,
        description=description,
        price=float(price) if price else None,
        image_url=image_url,
        is_active=True
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'success': True, 'id': product.id})

@app.route('/api/admin/products/<int:product_id>/toggle', methods=['POST'])
def api_toggle_product(product_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404
    product.is_active = not product.is_active
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
def api_delete_product(product_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'success': True})

'''
    app_content = app_content.replace(anchor, products_routes + anchor)
    print("✅ Rutas de administración de productos agregadas")
else:
    print("ℹ️ Las rutas de productos ya existían")

old_card_render = '''    return render_template('client/card.html',
                         client=client,
                         is_birthday=is_birthday,
                         level_data=client.get_level_data(),
                         referral=referral_data)'''
new_card_render = '''    products = Product.query.filter_by(is_active=True).order_by(Product.id.desc()).all()

    return render_template('client/card.html',
                         client=client,
                         is_birthday=is_birthday,
                         level_data=client.get_level_data(),
                         referral=referral_data,
                         products=products)'''
if old_card_render in app_content:
    app_content = app_content.replace(old_card_render, new_card_render)
    print("✅ Ruta /card ahora envía el catálogo de productos a la tarjeta")
else:
    print("⚠️ No se encontró el render_template exacto de /card (revisar manualmente)")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_content)

print("\nProceso completo. Revisa que todo diga ✅ o ℹ️, ninguno debe fallar.")
