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

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

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
    
    return render_template('client/card.html',
                         client=client,
                         is_birthday=is_birthday,
                         level_data=client.get_level_data(),
                         referral=referral_data)

@app.route('/scratch')
def scratch():
    client = get_client_from_session()
    if not client:
        return redirect(url_for('login'))
    has_welcome = client.has_welcome_scratch()
    has_normal = client.scratch_available and not client.scratch_used
    if not has_welcome and not has_normal:
        return redirect(url_for('card'))
    return render_template('client/scratch.html',
                         client=client,
                         is_welcome=has_welcome,
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

# ===== PROMOCIONES =====

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
