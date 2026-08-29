from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime, date, timedelta
import os
import re
import secrets
import base64
from io import BytesIO
import qrcode
from config import Config
from models import db, Client, VisitHistory, Employee, Achievement, ClientAchievement, Promotion, Referral, check_achievements, init_achievements
from models import Product, ScratchReward, ConsumptionCategory, Evaluation
import requests as http_requests

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://ijxynllcahohcgfoqpzt.supabase.co')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')

def upload_product_image(file_storage):
    if not file_storage:
        print("⚠️ DEBUG upload: no llegó ningún archivo")
        return None
    if not SUPABASE_SERVICE_KEY:
        print("⚠️ DEBUG upload: SUPABASE_SERVICE_KEY no está configurada")
        return None
    ext = file_storage.filename.rsplit('.', 1)[-1].lower() if '.' in file_storage.filename else 'jpg'
    filename = f"{secrets.token_hex(8)}.{ext}"
    file_bytes = file_storage.read()
    print(f"🔍 DEBUG upload: subiendo {filename}, {len(file_bytes)} bytes")
    upload_url = f"{SUPABASE_URL}/storage/v1/object/product-images/{filename}"
    resp = http_requests.post(
        upload_url,
        headers={
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': file_storage.mimetype or 'image/jpeg'
        },
        data=file_bytes
    )
    print(f"🔍 DEBUG upload: respuesta {resp.status_code} - {resp.text[:300]}")
    if resp.status_code in (200, 201):
        return f"{SUPABASE_URL}/storage/v1/object/public/product-images/{filename}"
    return None

def clean_phone(phone):
    phone = re.sub(r'[^\d+]', '', phone)
    if not phone.startswith('+'):
        phone = '+' + phone
    return phone

def generate_qr_secret():
    return secrets.token_hex(16)

def generate_referral_code(name):
    import hashlib
    return hashlib.md5(f"{name}{secrets.token_hex(4)}".encode()).hexdigest()[:8].upper()

def generate_qr(client):
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(client.qr_secret)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        client.qr_code = f"data:image/png;base64,{img_str}"
        db.session.commit()
        return img_str
    except Exception as e:
        print(f"Error generando QR: {e}")
        return None

def init_employee():
    if not Employee.query.filter_by(email='admin@clubetla.com').first():
        admin = Employee(
            name='Administrador',
            email='admin@clubetla.com',
            password='admin123',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

def get_client_from_session():
    if 'client_id' not in session:
        return None
    return Client.query.get(session['client_id'])

# ========== RUTAS PRINCIPALES ==========

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        whatsapp = request.form.get('whatsapp')
        if not whatsapp:
            return jsonify({'error': 'Número requerido'}), 400

        whatsapp = clean_phone(whatsapp)
        client = Client.query.filter_by(whatsapp=whatsapp).first()

        if client:
            session['client_id'] = client.id
            session.permanent = True
            return jsonify({'success': True, 'redirect': url_for('card')})
        else:
            return jsonify({
                'error': 'Número no registrado',
                'redirect_to_register': url_for('register', phone=whatsapp)
            }), 404

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    ref_code = request.args.get('ref')
    phone = request.args.get('phone', '')

    if request.method == 'POST':
        name = request.form.get('name')
        whatsapp = request.form.get('whatsapp')
        birthday = request.form.get('birthday')
        referral = request.form.get('referral')

        if not name or not whatsapp:
            return jsonify({'error': 'Nombre y WhatsApp son requeridos'}), 400

        whatsapp = clean_phone(whatsapp)

        existing = Client.query.filter_by(whatsapp=whatsapp).first()
        if existing:
            session['client_id'] = existing.id
            session.permanent = True
            return jsonify({
                'success': True,
                'message': 'Ya estabas registrado',
                'redirect': url_for('card')
            })

        try:
            client = Client(
                name=name,
                whatsapp=whatsapp,
                birthday=datetime.strptime(birthday, '%Y-%m-%d').date() if birthday else None,
                qr_secret=generate_qr_secret(),
                referral_code=generate_referral_code(name)
            )

            if referral:
                referrer = Client.query.filter_by(referral_code=referral).first()
                if referrer and referrer.id != client.id:
                    client.referred_by = referrer.id
                    referrer.referrals_count += 1
                    db.session.add(referrer)

            db.session.add(client)
            db.session.commit()
            generate_qr(client)
            check_achievements(client)

            session['client_id'] = client.id
            session.permanent = True

            return jsonify({
                'success': True,
                'message': '🎉 Registro exitoso',
                'redirect': url_for('card')
            })

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            return jsonify({'error': str(e)}), 500

    return render_template('register.html', ref_code=ref_code, phone=phone)

@app.route('/card')
def card():
    client = get_client_from_session()
    if not client:
        return redirect(url_for('login'))
    client.check_monthly_reset()
    
    is_birthday = False
    if client.birthday:
        today = date.today()
        if client.birthday.month == today.month and client.birthday.day == today.day:
            is_birthday = True
    
    referral_data = {
        'current': client.referrals_valid,
        'needed': 3,
        'remaining': 3 - client.referrals_valid if client.referrals_valid < 3 else 0,
        'complete': client.referrals_valid >= 3,
        'message': f"🎯 Llevas {client.referrals_valid} de 3 referidos válidos" if client.referrals_valid < 3 else "🎉 ¡Ya ganaste tu recompensa!"
    }
    
    products = Product.query.filter_by(is_active=True).order_by(Product.id.desc()).all()

    return render_template('client/card.html',
                         client=client,
                         is_birthday=is_birthday,
                         level_data=client.get_level_data(),
                         referral=referral_data,
                         products=products)

@app.route('/scratch')
def scratch():
    client = get_client_from_session()
    if not client:
        return redirect(url_for('login'))
    has_welcome = client.has_welcome_scratch() and client.visits > 0
    has_birthday = client.has_birthday_scratch()
    has_normal = client.scratch_available and not client.scratch_used
    if not has_welcome and not has_birthday and not has_normal:
        return redirect(url_for('card'))
    if has_welcome and not client.scratch_reward:
        client.scratch_reward = 'CUPCAKE'
        db.session.commit()
    elif has_birthday and not has_welcome and not client.scratch_reward:
        client.scratch_reward = client.select_scratch_reward()
        db.session.commit()
    return render_template('client/scratch.html',
                         client=client,
                         is_welcome=has_welcome,
                         is_birthday=has_birthday and not has_welcome,
                         has_normal=has_normal,
                         level_data=client.get_level_data())

# ========== API CLIENTE ==========

@app.route('/api/client/<int:client_id>')
def get_client_data(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    return jsonify({
        'id': client.id,
        'name': client.name,
        'whatsapp': client.whatsapp,
        'visits': client.visits,
        'points': client.points,
        'current_streak': client.current_streak,
        'best_streak': client.best_streak,
        'level': client.get_level(),
        'breakfast_count': client.breakfast_count,
        'free_breakfast': client.free_breakfast_available,
        'qr_code': client.qr_code,
        'has_welcome_scratch': client.has_welcome_scratch(),
        'scratch_available': client.scratch_available,
        'is_vip': client.is_vip,
        'registration_date': client.registration_date.strftime('%d/%m/%Y'),
        'last_visit': client.last_visit_date.strftime('%d/%m/%Y') if client.last_visit_date else 'Nunca'
    })

@app.route('/api/claim-free-breakfast', methods=['POST'])
def claim_free_breakfast():
    client = get_client_from_session()
    if not client:
        return jsonify({'error': 'No autorizado'}), 401
    if client.claim_free_breakfast():
        return jsonify({'success': True, 'message': '🎉 ¡Desayuno Gratis Canjeado!'})
    return jsonify({'error': 'No hay desayuno gratis disponible'}), 400

# ===== RASCADITA =====

@app.route('/api/scratch/welcome/status')
def welcome_scratch_status():
    client = get_client_from_session()
    if not client:
        return jsonify({'error': 'No autorizado'}), 401
    return jsonify({
        'has_welcome_scratch': client.has_welcome_scratch(),
        'message': '🎁 ¡Tienes una Rascadita de Bienvenida!' if client.has_welcome_scratch() else None
    })

@app.route('/api/scratch/welcome/claim', methods=['POST'])
def welcome_scratch_claim():
    client = get_client_from_session()
    if not client:
        return jsonify({'error': 'No autorizado'}), 401
    reward = client.claim_welcome_scratch()
    if reward:
        rewards = client.get_scratch_rewards()
        return jsonify({
            'success': True,
            'reward': reward,
            'reward_name': rewards[reward]['name'],
            'reward_icon': rewards[reward]['icon'],
            'message': f'🎉 ¡Bienvenido! Ganaste {rewards[reward]["icon"]} {rewards[reward]["name"]}'
        })
    return jsonify({'error': 'No hay rascadita de bienvenida'}), 400

@app.route('/api/scratch/status')
def scratch_status():
    client = get_client_from_session()
    if not client:
        return jsonify({'error': 'No autorizado'}), 401
    return jsonify({
        'available': client.scratch_available and not client.scratch_used,
        'scratch_available': client.scratch_available,
        'scratch_used': client.scratch_used
    })

@app.route('/api/scratch/claim', methods=['POST'])
def scratch_claim():
    client = get_client_from_session()
    if not client:
        return jsonify({'error': 'No autorizado'}), 401
    reward = client.claim_scratch()
    if reward:
        rewards = client.get_scratch_rewards()
        return jsonify({
            'success': True,
            'reward': reward,
            'reward_name': rewards[reward]['name'],
            'reward_icon': rewards[reward]['icon'],
            'message': f'🎉 ¡Ganaste {rewards[reward]["icon"]} {rewards[reward]["name"]}!'
        })
    else:
        return jsonify({'error': 'No hay rascadita disponible'}), 400

@app.route('/api/scratch/skip', methods=['POST'])
def scratch_skip():
    client = get_client_from_session()
    if not client:
        return jsonify({'error': 'No autorizado'}), 401
    if not client.scratch_available or client.scratch_used:
        return jsonify({'error': 'No hay rascadita disponible'}), 400
    client.skip_scratch()
    return jsonify({'success': True, 'message': '✅ Seguirás acumulando visitas'})

@app.route('/api/scratch/birthday/claim', methods=['POST'])
def birthday_scratch_claim():
    client = get_client_from_session()
    if not client:
        return jsonify({'error': 'No autorizado'}), 401
    reward = client.claim_birthday_scratch()
    if reward:
        rewards = client.get_scratch_rewards()
        return jsonify({
            'success': True,
            'reward': reward,
            'reward_name': rewards[reward]['name'],
            'reward_icon': rewards[reward]['icon'],
            'message': f'🎂 ¡Feliz cumpleaños! Ganaste {rewards[reward]["icon"]} {rewards[reward]["name"]}'
        })
    return jsonify({'error': 'No hay rascadita de cumpleaños disponible'}), 400

# ===== API EMPLEADO =====

@app.route('/api/scan-qr', methods=['POST'])
def scan_qr():
    data = request.json
    qr_data = data.get('qr_data')
    product_type = data.get('product_type', 'BREAKFAST')
    employee_id = session.get('employee_id')
    
    client = Client.query.filter_by(qr_secret=qr_data).first()
    if not client:
        return jsonify({'error': 'QR no válido'}), 404
    
    today = date.today()
    if client.last_visit_date == today:
        return jsonify({
            'error': 'Ya registraste tu visita hoy',
            'client': client.name
        }), 400
    
    try:
        result = client.add_visit(product_type, employee_id)
        check_achievements(client)
        return jsonify({
            'success': True,
            'message': f'✅ Visita registrada para {client.name}',
            'client': client.name,
            'visits': client.visits,
            'points': client.points,
            'streak': client.current_streak,
            'free_breakfast': client.free_breakfast_available,
            'scratch_available': client.scratch_available,
            'has_welcome_scratch': client.has_welcome_scratch(),
            'breakfast_count': client.breakfast_count,
            'points_earned': result['points'],
            'is_vip': client.is_vip,
            'level': client.get_level()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== ADMIN =====

@app.route('/admin')
def admin_dashboard():
    if 'employee_id' not in session:
        return render_template('admin/login.html')
    employee = Employee.query.get(session['employee_id'])
    if not employee or employee.role != 'admin':
        return render_template('admin/login.html')
    stats = {
        'total_clients': Client.query.count(),
        'active_clients': Client.query.filter_by(status='active').count(),
        'total_visits': VisitHistory.query.count(),
        'today_visits': VisitHistory.query.filter_by(visit_date=date.today()).count(),
        'employees': Employee.query.count()
    }
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/clients')
def admin_clients_page():
    if 'employee_id' not in session:
        return render_template('admin/login.html')
    return render_template('admin/clients.html')

@app.route('/api/admin/clients')
def admin_get_clients():
    search = request.args.get('search', '')
    if search:
        clients = Client.query.filter(
            (Client.name.ilike(f'%{search}%')) |
            (Client.whatsapp.like(f'%{search}%'))
        ).all()
    else:
        clients = Client.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'whatsapp': c.whatsapp,
        'visits': c.visits,
        'points': c.points,
        'level': c.get_level(),
        'status': c.status,
        'registration_date': c.registration_date.strftime('%d/%m/%Y') if c.registration_date else None,
        'referral_code': c.referral_code
    } for c in clients])

@app.route('/api/admin/clients/<int:client_id>', methods=['DELETE'])
def admin_delete_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    VisitHistory.query.filter_by(client_id=client_id).delete()
    db.session.delete(client)
    db.session.commit()
    return jsonify({'success': True})

# ===== PRODUCTOS (CATÁLOGO) =====

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

# ===== PROMOCIONES =====

@app.route('/admin/rewards')
def admin_rewards():
    if 'employee_id' not in session:
        return redirect(url_for('login'))
    employee = Employee.query.get(session['employee_id'])
    if not employee or employee.role != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/rewards.html')

@app.route('/api/admin/rewards', methods=['GET'])
def api_get_rewards():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    rewards = ScratchReward.query.order_by(ScratchReward.id).all()
    return jsonify([{'id': r.id, 'code': r.code, 'name': r.name, 'icon': r.icon, 'weight': r.weight, 'active': r.active} for r in rewards])

@app.route('/api/admin/rewards', methods=['POST'])
def api_create_reward():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    data = request.json
    code = (data.get('code') or '').strip().upper()
    name = (data.get('name') or '').strip()
    icon = (data.get('icon') or '').strip()
    weight = data.get('weight')
    if not code or not name or not icon or weight is None:
        return jsonify({'error': 'Todos los campos son requeridos'}), 400
    if ScratchReward.query.filter_by(code=code).first():
        return jsonify({'error': 'Ya existe un premio con ese código'}), 400
    reward = ScratchReward(code=code, name=name, icon=icon, weight=float(weight), active=True)
    db.session.add(reward)
    db.session.commit()
    return jsonify({'success': True, 'id': reward.id})

@app.route('/api/admin/rewards/<int:reward_id>', methods=['PUT'])
def api_update_reward(reward_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    reward = ScratchReward.query.get(reward_id)
    if not reward:
        return jsonify({'error': 'Premio no encontrado'}), 404
    data = request.json
    if 'name' in data:
        reward.name = data['name'].strip()
    if 'icon' in data:
        reward.icon = data['icon'].strip()
    if 'weight' in data:
        reward.weight = float(data['weight'])
    if 'active' in data:
        reward.active = bool(data['active'])
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/admin/rewards/<int:reward_id>', methods=['DELETE'])
def api_delete_reward(reward_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    reward = ScratchReward.query.get(reward_id)
    if not reward:
        return jsonify({'error': 'Premio no encontrado'}), 404
    db.session.delete(reward)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/promotions')
def admin_promotions():
    return render_template('admin/promotions.html')

@app.route('/api/promotions', methods=['GET'])
def get_promotions():
    promotions = Promotion.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'type': p.type,
        'value': p.value,
        'start_date': p.start_date.strftime('%d/%m/%Y'),
        'end_date': p.end_date.strftime('%d/%m/%Y'),
        'is_active': p.is_active,
        'used_count': p.used_count
    } for p in promotions])

@app.route('/api/promotions', methods=['POST'])
def create_promotion():
    data = request.json
    try:
        promo = Promotion(
            name=data['name'],
            description=data.get('description', ''),
            type=data['type'],
            value=data['value'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        )
        db.session.add(promo)
        db.session.commit()
        return jsonify({'success': True, 'id': promo.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/promotions/<int:promo_id>/toggle', methods=['POST'])
def toggle_promotion(promo_id):
    promo = Promotion.query.get(promo_id)
    if not promo:
        return jsonify({'error': 'Promoción no encontrada'}), 404
    promo.is_active = not promo.is_active
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/promotions/<int:promo_id>', methods=['DELETE'])
def delete_promotion(promo_id):
    promo = Promotion.query.get(promo_id)
    if not promo:
        return jsonify({'error': 'Promoción no encontrada'}), 404
    db.session.delete(promo)
    db.session.commit()
    return jsonify({'success': True})

# ===== REFERIDOS =====

@app.route('/api/referral/info')
def referral_info():
    client = get_client_from_session()
    if not client:
        return jsonify({'error': 'No autorizado'}), 401
    return jsonify({
        'code': client.referral_code,
        'link': f"/register?ref={client.referral_code}",
        'count': client.referrals_count,
        'valid': client.referrals_valid,
        'progress': {
            'current': client.referrals_valid,
            'needed': 3,
            'remaining': 3 - client.referrals_valid if client.referrals_valid < 3 else 0,
            'complete': client.referrals_valid >= 3,
            'message': f"🎯 Llevas {client.referrals_valid} de 3 referidos válidos" if client.referrals_valid < 3 else "🎉 ¡Ya ganaste tu recompensa!"
        },
        'points_earned': client.referral_points_earned
    })

# ===== QR =====

@app.route('/qr-registro')
def qr_registro():
    import qrcode
    from io import BytesIO
    import base64
    registro_url = url_for('register', _external=True)
    qr = qrcode.QRCode(version=5, box_size=10, border=2)
    qr.add_data(registro_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    qr_data = f"data:image/png;base64,{img_str}"
    return render_template('qr_registro.html', qr_registro=qr_data)

# ============================================================
# INICIALIZACIÓN
# ============================================================
with app.app_context():
    db.create_all()
    init_achievements()
    init_employee()
    print("✅ Base de datos lista")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# ===== ESCÁNER DE EMPLEADO =====
@app.route('/employee/scan')
def employee_scan():
    if 'employee_id' not in session:
        return redirect(url_for('login'))
    return render_template('employee/scan.html')

@app.route('/api/employee/scan', methods=['POST'])
def api_employee_scan():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.json
    qr_secret = data.get('qr_secret')
    product_type = data.get('product_type', 'BREAKFAST')
    
    client = Client.query.filter_by(qr_secret=qr_secret).first()
    if not client:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    
    # Registrar visita
    result = client.add_visit(product_type, session['employee_id'])
    
    return jsonify({
        'success': True,
        'client_name': client.name,
        'visits': client.visits,
        'points': client.points,
        'level': client.get_level(),
        'message': f'✅ Visita registrada para {client.name}'
    })

@app.route('/api/employee/check-reward', methods=['POST'])
def api_employee_check_reward():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    data = request.json
    qr_secret = data.get('qr_secret')
    client = Client.query.filter_by(qr_secret=qr_secret).first()
    if not client:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    pending = client.scratch_used and client.scratch_reward and not client.scratch_redeemed
    reward_name = None
    if pending:
        rewards = client.get_scratch_rewards()
        reward_name = rewards.get(client.scratch_reward, {}).get('name', client.scratch_reward)
    return jsonify({
        'client_name': client.name,
        'pending_reward': pending,
        'reward_code': client.scratch_reward if pending else None,
        'reward_name': reward_name
    })

@app.route('/api/employee/redeem-scratch', methods=['POST'])
def api_employee_redeem_scratch():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    data = request.json
    qr_secret = data.get('qr_secret')
    client = Client.query.filter_by(qr_secret=qr_secret).first()
    if not client:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    reward = client.redeem_scratch()
    if reward:
        rewards = client.get_scratch_rewards()
        reward_name = rewards.get(reward, {}).get('name', reward)
        return jsonify({'success': True, 'reward_name': reward_name, 'message': f'✅  Premio canjeado: {reward_name}'})
    return jsonify({'error': 'No hay premio pendiente de canje'}), 400

@app.route('/admin/consumption')
def admin_consumption():
    if 'employee_id' not in session:
        return redirect(url_for('login'))
    employee = Employee.query.get(session['employee_id'])
    if not employee or employee.role != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/consumption.html')

@app.route('/api/admin/consumption-categories', methods=['GET'])
def api_get_consumption_categories():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    cats = ConsumptionCategory.query.order_by(ConsumptionCategory.id).all()
    return jsonify([{'id': c.id, 'code': c.code, 'name': c.name, 'icon': c.icon, 'active': c.active} for c in cats])

@app.route('/api/admin/consumption-categories', methods=['POST'])
def api_create_consumption_category():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    data = request.json
    code = (data.get('code') or '').strip().upper()
    name = (data.get('name') or '').strip()
    icon = (data.get('icon') or '').strip()
    if not code or not name or not icon:
        return jsonify({'error': 'Todos los campos son requeridos'}), 400
    if ConsumptionCategory.query.filter_by(code=code).first():
        return jsonify({'error': 'Ya existe una categoria con ese codigo'}), 400
    cat = ConsumptionCategory(code=code, name=name, icon=icon, active=True)
    db.session.add(cat)
    db.session.commit()
    return jsonify({'success': True, 'id': cat.id})

@app.route('/api/admin/consumption-categories/<int:cat_id>', methods=['PUT'])
def api_update_consumption_category(cat_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    cat = ConsumptionCategory.query.get(cat_id)
    if not cat:
        return jsonify({'error': 'Categoria no encontrada'}), 404
    data = request.json
    if 'name' in data:
        cat.name = data['name'].strip()
    if 'icon' in data:
        cat.icon = data['icon'].strip()
    if 'active' in data:
        cat.active = bool(data['active'])
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/admin/consumption-categories/<int:cat_id>', methods=['DELETE'])
def api_delete_consumption_category(cat_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    cat = ConsumptionCategory.query.get(cat_id)
    if not cat:
        return jsonify({'error': 'Categoria no encontrada'}), 404
    db.session.delete(cat)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/admin/consumption-stats', methods=['GET'])
def api_consumption_stats():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    totals = {}
    for client in Client.query.all():
        col = client.get_collection()
        for code, qty in col.items():
            totals[code] = totals.get(code, 0) + qty
    cats = {c.code: {'name': c.name, 'icon': c.icon} for c in ConsumptionCategory.query.all()}
    result = []
    for code, total in totals.items():
        info = cats.get(code, {'name': code, 'icon': '❓'})
        result.append({'code': code, 'name': info['name'], 'icon': info['icon'], 'total': total})
    result.sort(key=lambda x: x['total'], reverse=True)
    return jsonify(result)

@app.route('/api/employee/consumption-categories', methods=['GET'])
def api_employee_consumption_categories():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    cats = ConsumptionCategory.query.filter_by(active=True).order_by(ConsumptionCategory.id).all()
    return jsonify([{'code': c.code, 'name': c.name, 'icon': c.icon} for c in cats])

@app.route('/admin/evaluations')
def admin_evaluations():
    if 'employee_id' not in session:
        return redirect(url_for('login'))
    employee = Employee.query.get(session['employee_id'])
    if not employee or employee.role != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/evaluations.html')

@app.route('/api/admin/evaluations/search-clients')
def api_evaluations_search_clients():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    clients = Client.query.filter(
        db.or_(Client.name.ilike(f'%{q}%'), Client.whatsapp.ilike(f'%{q}%'))
    ).limit(15).all()
    return jsonify([{'id': c.id, 'name': c.name, 'whatsapp': c.whatsapp, 'gender': c.gender} for c in clients])

@app.route('/api/admin/clients/<int:client_id>/profile', methods=['GET'])
def api_client_eval_profile(client_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    evals = Evaluation.query.filter_by(client_id=client_id).order_by(Evaluation.eval_date).all()
    return jsonify({
        'id': client.id,
        'name': client.name,
        'gender': client.gender,
        'goals': {
            'goal_weight': client.goal_weight,
            'goal_imc': client.goal_imc,
            'goal_body_fat': client.goal_body_fat,
            'goal_muscle': client.goal_muscle,
            'goal_visceral': client.goal_visceral
        },
        'evaluations': [{
            'id': e.id,
            'eval_date': e.eval_date.strftime('%Y-%m-%d'),
            'weight': e.weight,
            'imc': e.imc,
            'body_fat_pct': e.body_fat_pct,
            'muscle_pct': e.muscle_pct,
            'basal_metabolism': e.basal_metabolism,
            'body_age': e.body_age,
            'visceral_fat': e.visceral_fat
        } for e in evals]
    })

@app.route('/api/admin/clients/<int:client_id>/gender', methods=['PUT'])
def api_update_client_gender(client_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    data = request.json
    gender = data.get('gender')
    if gender not in ('M', 'F'):
        return jsonify({'error': 'Sexo invalido'}), 400
    client.gender = gender
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/admin/clients/<int:client_id>/goals', methods=['PUT'])
def api_update_client_goals(client_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    data = request.json
    for field in ['goal_weight', 'goal_imc', 'goal_body_fat', 'goal_muscle', 'goal_visceral']:
        if field in data and data[field] not in (None, ''):
            setattr(client, field, float(data[field]))
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/admin/evaluations', methods=['POST'])
def api_create_evaluation():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    data = request.json
    client_id = data.get('client_id')
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    eval_date = data.get('eval_date')
    try:
        eval_date_obj = datetime.strptime(eval_date, '%Y-%m-%d').date() if eval_date else date.today()
    except ValueError:
        return jsonify({'error': 'Fecha invalida'}), 400
    ev = Evaluation(
        client_id=client_id,
        eval_date=eval_date_obj,
        weight=data.get('weight'),
        imc=data.get('imc'),
        body_fat_pct=data.get('body_fat_pct'),
        muscle_pct=data.get('muscle_pct'),
        basal_metabolism=data.get('basal_metabolism'),
        body_age=data.get('body_age'),
        visceral_fat=data.get('visceral_fat'),
        created_by=session.get('employee_id')
    )
    db.session.add(ev)
    db.session.commit()
    return jsonify({'success': True, 'id': ev.id})

@app.route('/api/admin/evaluations/<int:eval_id>', methods=['DELETE'])
def api_delete_evaluation(eval_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    ev = Evaluation.query.get(eval_id)
    if not ev:
        return jsonify({'error': 'Evaluacion no encontrada'}), 404
    db.session.delete(ev)
    db.session.commit()
    return jsonify({'success': True})

# ===== ADMIN - GESTIÓN DE EMPLEADOS =====
@app.route('/admin/employees')
def admin_employees():
    if 'employee_id' not in session:
        return redirect(url_for('login'))
    employee = Employee.query.get(session['employee_id'])
    if not employee or employee.role != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/employees.html')

@app.route('/api/admin/employees', methods=['GET'])
def api_get_employees():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    employees = Employee.query.all()
    return jsonify([{
        'id': e.id,
        'name': e.name,
        'email': e.email,
        'role': e.role,
        'active': e.active
    } for e in employees])

@app.route('/api/admin/employees', methods=['POST'])
def api_create_employee():
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({'error': 'Todos los campos son requeridos'}), 400
    
    if Employee.query.filter_by(email=email).first():
        return jsonify({'error': 'El correo ya está registrado'}), 400
    
    employee = Employee(
        name=name,
        email=email,
        password=password,
        role='employee',
        active=True
    )
    db.session.add(employee)
    db.session.commit()
    return jsonify({'success': True, 'id': employee.id})

@app.route('/api/admin/employees/<int:employee_id>', methods=['DELETE'])
def api_delete_employee(employee_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    admin_emp = Employee.query.get(session['employee_id'])
    if not admin_emp or admin_emp.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 401
    
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'error': 'Empleado no encontrado'}), 404
    if employee.role == 'admin':
        return jsonify({'error': 'No se puede eliminar al administrador'}), 400
    
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/employee/login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        employee = Employee.query.filter_by(email=email, active=True).first()
        if employee and employee.password == password:
            session['employee_id'] = employee.id
            session['employee_role'] = employee.role
            return jsonify({'success': True, 'redirect': url_for('employee_dashboard')})
        return jsonify({'error': 'Credenciales inválidas'}), 401
    return render_template('employee/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/employee/logout')
def employee_logout():
    session.pop('employee_id', None)
    session.pop('employee_role', None)
    return redirect(url_for('login'))

@app.route('/employee')
def employee_dashboard():
    if 'employee_id' not in session:
        return redirect(url_for('employee_login'))
    return render_template('employee/dashboard.html')

@app.route('/api/client/register-visit', methods=['POST'])
def api_client_register_visit():
    if 'client_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.json
    client_id = data.get('client_id')
    
    if not client_id or client_id != session['client_id']:
        return jsonify({'error': 'ID inválido'}), 400
    
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    
    # Verificar si ya visitó hoy
    from datetime import date
    if client.last_visit_date == date.today():
        return jsonify({'error': 'Ya registraste tu visita hoy'}), 400
    
    # Registrar visita
    result = client.add_visit('BREAKFAST', None)
    check_achievements(client)
    
    return jsonify({
        'success': True,
        'visits': client.visits,
        'points': client.points,
        'message': f'Visita {client.visits} de 10'
    })
