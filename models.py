from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from sqlalchemy import UniqueConstraint
import json
import secrets
import random

db = SQLAlchemy()

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whatsapp = db.Column(db.String(20), unique=True, nullable=False)
    birthday = db.Column(db.Date, nullable=True)
    birthday_scratch_year = db.Column(db.Integer, nullable=True)
    avatar = db.Column(db.String(200), nullable=True)
    
    visits = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    last_visit_date = db.Column(db.Date, nullable=True)
    last_visit_time = db.Column(db.DateTime, nullable=True)
    
    breakfast_count = db.Column(db.Integer, default=0)
    free_breakfast_available = db.Column(db.Boolean, default=False)
    
    collection = db.Column(db.Text, default='{}')
    
    referral_code = db.Column(db.String(20), unique=True)
    referred_by = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    referrals_count = db.Column(db.Integer, default=0)
    referrals_valid = db.Column(db.Integer, default=0)
    
    scratch_available = db.Column(db.Boolean, default=False)
    scratch_reward = db.Column(db.String(50), nullable=True)
    scratch_used = db.Column(db.Boolean, default=False)
    scratch_visits_used = db.Column(db.Integer, default=0)
    
    welcome_scratch_used = db.Column(db.Boolean, default=False)
    scratch_redeemed = db.Column(db.Boolean, default=True)
    scratch_redeemed_at = db.Column(db.DateTime, nullable=True)
    
    status = db.Column(db.String(20), default='active')
    is_vip = db.Column(db.Boolean, default=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    qr_code = db.Column(db.String(500), nullable=True)
    qr_secret = db.Column(db.String(64), unique=True)
    cycle_month = db.Column(db.String(7), nullable=True)
    
    visits_history = db.relationship('VisitHistory', backref='client', lazy=True)
    achievements = db.relationship('ClientAchievement', backref='client', lazy=True)
    
    def check_monthly_reset(self):
        current_month = date.today().strftime('%Y-%m')
        if self.cycle_month != current_month:
            self.cycle_month = current_month
            self.visits = 0
            self.points = 0
            self.breakfast_count = 0
            self.free_breakfast_available = False
            self.scratch_available = False
            self.scratch_used = False
            self.scratch_reward = None
            self.scratch_visits_used = 0
            self.scratch_redeemed = True
            self.scratch_redeemed_at = None
            db.session.commit()

    def get_tier_index(self):
        if self.visits <= 0:
            return 0
        return min((self.visits - 1) // 10, 3)

    def get_tier_name(self):
        tiers = ['BRONCE', 'PLATA', 'ORO', 'DIAMANTE']
        return tiers[self.get_tier_index()]

    def get_cycle_progress(self):
        if self.visits <= 0:
            return 0
        return ((self.visits - 1) % 10) + 1

    def get_level(self):
        from config import Config
        for level, data in Config.LEVELS.items():
            if data['min_visits'] <= self.visits <= data['max_visits']:
                return level
        return 'BRONCE'
    
    def get_level_data(self):
        from config import Config
        level = self.get_level()
        return Config.LEVELS.get(level, {})
    
    def get_collection(self):
        return json.loads(self.collection) if self.collection else {}
    
    def add_consumption(self, product_type):
        col = self.get_collection()
        col[product_type] = col.get(product_type, 0) + 1
        self.collection = json.dumps(col)
        db.session.commit()
    
    def get_scratch_rewards(self):
        return {
            'CUPCAKE': {'name': 'Cupcake Gratis', 'icon': '🧁', 'weight': 50},
            'COFFEE': {'name': 'Café Herbalife Individual', 'icon': '☕', 'weight': 12.5},
            'TEA': {'name': 'Té Individual', 'icon': '🍵', 'weight': 12.5},
            'ALOE': {'name': 'Aloe Individual', 'icon': '🌿', 'weight': 12.5},
            'PROTEIN': {'name': 'Porción de Proteína Extra', 'icon': '💪', 'weight': 12.5}
        }
    
    def select_scratch_reward(self):
        rewards = self.get_scratch_rewards()
        codes = list(rewards.keys())
        weights = [rewards[c]['weight'] for c in codes]
        chosen = random.choices(codes, weights=weights, k=1)[0]
        self.scratch_reward = chosen
        return chosen
    
    def has_welcome_scratch(self):
        return not self.welcome_scratch_used
    
    def claim_welcome_scratch(self):
        if not self.welcome_scratch_used:
            self.scratch_reward = 'CUPCAKE'
            reward = 'CUPCAKE'
            self.scratch_redeemed = False
            self.welcome_scratch_used = True
            self.points += 5
            db.session.commit()
            return reward
        return None
    
    def claim_scratch(self):
        if self.scratch_available and not self.scratch_used:
            reward = self.scratch_reward
            self.scratch_used = True
            self.scratch_available = False
            self.scratch_redeemed = False
            self.scratch_visits_used += 5
            db.session.commit()
            return reward
        return None
    
    def redeem_scratch(self):
        if self.scratch_used and self.scratch_reward and not self.scratch_redeemed:
            reward = self.scratch_reward
            self.scratch_redeemed = True
            self.scratch_redeemed_at = datetime.utcnow()
            db.session.commit()
            return reward
        return None

    def has_birthday_scratch(self):
        if not self.birthday:
            return False
        today = date.today()
        if self.birthday.month != today.month or self.birthday.day != today.day:
            return False
        return self.birthday_scratch_year != today.year

    def claim_birthday_scratch(self):
        if self.has_birthday_scratch():
            reward = self.select_scratch_reward()
            self.scratch_used = True
            self.scratch_redeemed = False
            self.birthday_scratch_year = date.today().year
            db.session.commit()
            return reward
        return None

    def add_visit(self, product_type='BREAKFAST', employee_id=None):
        from config import Config
        self.check_monthly_reset()
        today = date.today()
        now = datetime.now()
        
        points = Config.POINTS_BREAKFAST
        
        self.visits += 1
        self.points += points
        self.breakfast_count += 1
        self.add_consumption(product_type)
        self.last_visit_time = now
        
        if self.visits % 10 == 0:
            self.free_breakfast_available = True
        
        cycle_progress = self.get_cycle_progress()
        if cycle_progress == 5 and not self.scratch_available:
            self.select_scratch_reward()
            self.scratch_available = True
            self.scratch_used = False
        
        if self.last_visit_date == today - timedelta(days=1):
            self.current_streak += 1
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
        elif self.last_visit_date != today:
            self.current_streak = 1
            
        self.last_visit_date = today
        
        history = VisitHistory(
            client_id=self.id,
            visit_date=today,
            visit_time=now,
            product_type=product_type,
            points_earned=points,
            breakfast_count=self.breakfast_count,
            employee_id=employee_id
        )
        db.session.add(history)
        db.session.commit()
        
        check_achievements(self)
        
        return {
            'points': points, 
            'breakfast_count': self.breakfast_count,
            'scratch_available': self.scratch_available
        }
    
    def claim_free_breakfast(self):
        if self.free_breakfast_available:
            self.free_breakfast_available = False
            db.session.commit()
            return True
        return False

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class VisitHistory(db.Model):
    __tablename__ = 'visit_history'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    visit_time = db.Column(db.DateTime, default=datetime.utcnow)
    product_type = db.Column(db.String(50), nullable=False)
    points_earned = db.Column(db.Integer, default=10)
    breakfast_count = db.Column(db.Integer, default=1)
    employee_id = db.Column(db.Integer, nullable=True)
    reward_claimed = db.Column(db.String(100), nullable=True)
    observations = db.Column(db.Text, nullable=True)

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='employee')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    condition_type = db.Column(db.String(50), nullable=False)
    condition_value = db.Column(db.Integer, nullable=False)

class ScratchReward(db.Model):
    __tablename__ = 'scratch_rewards'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    weight = db.Column(db.Float, nullable=False, default=10)
    active = db.Column(db.Boolean, default=True)


class ClientAchievement(db.Model):
    __tablename__ = 'client_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    unlocked_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('client_id', 'achievement_id', name='unique_client_achievement'),)

class Promotion(db.Model):
    __tablename__ = 'promotions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    used_count = db.Column(db.Integer, default=0)

class Referral(db.Model):
    __tablename__ = 'referrals'
    
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    referred_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

def check_achievements(client):
    achievements = Achievement.query.all()
    
    for achievement in achievements:
        existing = ClientAchievement.query.filter_by(
            client_id=client.id,
            achievement_id=achievement.id
        ).first()
        if existing:
            continue
        
        unlocked = False
        if achievement.condition_type == 'visits':
            if client.visits >= achievement.condition_value:
                unlocked = True
        elif achievement.condition_type == 'streak':
            if client.current_streak >= achievement.condition_value:
                unlocked = True
        elif achievement.condition_type == 'level':
            level = client.get_level()
            if level == 'ORO' and achievement.condition_value == 50:
                unlocked = True
            elif level == 'DIAMANTE' and achievement.condition_value == 100:
                unlocked = True
        elif achievement.condition_type == 'referrals':
            if client.referrals_valid >= achievement.condition_value:
                unlocked = True
        
        if unlocked:
            ca = ClientAchievement(
                client_id=client.id,
                achievement_id=achievement.id
            )
            db.session.add(ca)
            db.session.commit()

def init_achievements():
    default_achievements = [
        {'code': 'FIRST_BREAKFAST', 'name': 'Primer Desayuno', 'description': 'Primer desayuno en el club', 'icon': '🥤', 'condition_type': 'visits', 'condition_value': 1},
        {'code': 'FIVE_VISITS', 'name': 'Cliente Frecuente', 'description': '5 visitas al club', 'icon': '⭐', 'condition_type': 'visits', 'condition_value': 5},
        {'code': 'TEN_VISITS', 'name': 'Cliente Leal', 'description': '10 visitas al club', 'icon': '🌟', 'condition_type': 'visits', 'condition_value': 10},
        {'code': 'TWENTY_FIVE_VISITS', 'name': 'Cliente Premium', 'description': '25 visitas', 'icon': '💎', 'condition_type': 'visits', 'condition_value': 25},
        {'code': 'FIFTY_VISITS', 'name': 'Cliente Oro', 'description': 'Alcanzaste nivel Oro', 'icon': '🥇', 'condition_type': 'level', 'condition_value': 50},
        {'code': 'ONE_HUNDRED_VISITS', 'name': 'Cliente Diamante', 'description': 'Alcanzaste nivel Diamante', 'icon': '👑', 'condition_type': 'level', 'condition_value': 100},
        {'code': 'THIRTY_DAY_STREAK', 'name': 'Imparable', 'description': '30 días de racha', 'icon': '🔥', 'condition_type': 'streak', 'condition_value': 30},
        {'code': 'FIRST_REFERRAL', 'name': 'Embajador', 'description': 'Primer referido válido', 'icon': '🤝', 'condition_type': 'referrals', 'condition_value': 1},
    ]
    
    for ach_data in default_achievements:
        if not Achievement.query.filter_by(code=ach_data['code']).first():
            achievement = Achievement(**ach_data)
            db.session.add(achievement)
    db.session.commit()

    # ===== REFERIDOS =====
    def get_referral_link(self):
        """Genera el enlace de referido"""
        return f"/register?ref={self.referral_code}"
    
    def get_referral_progress(self):
        from config import Config
        needed = Config.REFERRAL_REWARD
        return {
            'current': self.referrals_valid,
            'needed': needed,
            'remaining': needed - self.referrals_valid if self.referrals_valid < needed else 0,
            'complete': self.referrals_valid >= needed,
            'message': f"🎯 Llevas {self.referrals_valid} de {needed} referidos válidos" if self.referrals_valid < needed else "🎉 ¡Ya ganaste tu recompensa!"
        }

    # ===== REFERIDOS =====
    def get_referral_link(self):
        """Genera el enlace de referido"""
        return f"/register?ref={self.referral_code}"
    
    def get_referral_progress(self):
        from config import Config
        needed = getattr(Config, 'REFERRAL_REWARD', 3)
        return {
            'current': self.referrals_valid,
            'needed': needed,
            'remaining': needed - self.referrals_valid if self.referrals_valid < needed else 0,
            'complete': self.referrals_valid >= needed,
            'message': f"🎯 Llevas {self.referrals_valid} de {needed} referidos válidos" if self.referrals_valid < needed else "🎉 ¡Ya ganaste tu recompensa!"
        }
