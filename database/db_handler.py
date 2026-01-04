"""
Manejador de base de datos para usuarios y suscripciones.
Usa SQLite para desarrollo, PostgreSQL para producción.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from utils.logger import logger
from utils.config_loader import config


class DatabaseHandler:
    """Maneja las operaciones de base de datos."""
    
    def __init__(self, db_path: str = "data/trading.db"):
        """
        Inicializa el manejador de base de datos.
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logger.bind(name="DatabaseHandler")
        self.init_database()
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Inicializa las tablas de la base de datos."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                plan TEXT DEFAULT 'free',
                stripe_customer_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de suscripciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan TEXT,
                stripe_subscription_id TEXT,
                status TEXT,
                current_period_start TIMESTAMP,
                current_period_end TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Tabla de pagos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subscription_id INTEGER,
                amount REAL,
                currency TEXT DEFAULT 'USD',
                stripe_payment_intent_id TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
            )
        """)
        
        conn.commit()
        conn.close()
        self.logger.info("Base de datos inicializada")
    
    def create_user(self, email: str, plan: str = 'free') -> int:
        """
        Crea un nuevo usuario.
        
        Args:
            email: Email del usuario
            plan: Plan inicial
            
        Returns:
            ID del usuario creado
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (email, plan)
                VALUES (?, ?)
            """, (email, plan))
            user_id = cursor.lastrowid
            conn.commit()
            self.logger.info(f"Usuario creado: {email} (ID: {user_id})")
            return user_id
        except sqlite3.IntegrityError:
            # Usuario ya existe
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            result = cursor.fetchone()
            return result['id'] if result else None
        finally:
            conn.close()
    
    def get_user(self, email: str) -> Optional[Dict]:
        """
        Obtiene un usuario por email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Diccionario con información del usuario o None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def update_user_plan(self, user_id: int, plan: str) -> bool:
        """
        Actualiza el plan de un usuario.
        
        Args:
            user_id: ID del usuario
            plan: Nuevo plan
            
        Returns:
            True si se actualizó correctamente
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET plan = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (plan, user_id))
        
        conn.commit()
        conn.close()
        self.logger.info(f"Plan actualizado para usuario {user_id}: {plan}")
        return True
    
    def create_subscription(
        self,
        user_id: int,
        plan: str,
        stripe_subscription_id: str,
        status: str = 'active'
    ) -> int:
        """
        Crea una nueva suscripción.
        
        Args:
            user_id: ID del usuario
            plan: Nombre del plan
            stripe_subscription_id: ID de suscripción en Stripe
            status: Estado de la suscripción
            
        Returns:
            ID de la suscripción creada
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO subscriptions (user_id, plan, stripe_subscription_id, status, current_period_start, current_period_end)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, datetime('now', '+1 month'))
        """, (user_id, plan, stripe_subscription_id, status))
        
        subscription_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.logger.info(f"Suscripción creada: {subscription_id} para usuario {user_id}")
        return subscription_id
    
    def get_user_subscription(self, user_id: int) -> Optional[Dict]:
        """
        Obtiene la suscripción activa de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Diccionario con información de la suscripción o None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM subscriptions 
            WHERE user_id = ? AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None


