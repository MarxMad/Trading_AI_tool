"""
Manejador de pagos con Stripe.
"""

import os
from typing import Dict, Optional, Tuple
from utils.logger import logger
from utils.config_loader import config

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logger.warning("stripe no está instalado. La funcionalidad de pagos no estará disponible.")


class StripeHandler:
    """Maneja las operaciones de pago con Stripe."""
    
    def __init__(self):
        """Inicializa el manejador de Stripe."""
        self.logger = logger.bind(name="StripeHandler")
        
        if STRIPE_AVAILABLE:
            # Configurar Stripe
            self.secret_key = config.get_env('STRIPE_SECRET_KEY')
            self.public_key = config.get_env('STRIPE_PUBLIC_KEY')
            
            if self.secret_key and self.secret_key != 'your_stripe_secret_key':
                stripe.api_key = self.secret_key
                self.enabled = True
                self.logger.info("Stripe configurado correctamente")
            else:
                self.enabled = False
                self.logger.warning("Stripe no configurado. Usa modo de prueba.")
        else:
            self.enabled = False
            self.logger.warning("Stripe no disponible. Instala: pip install stripe")
    
    def create_checkout_session(
        self,
        plan_name: str,
        price_id: str,
        user_email: Optional[str] = None,
        success_url: str = "http://localhost:8501/?payment=success",
        cancel_url: str = "http://localhost:8501/?payment=cancelled"
    ) -> Dict:
        """
        Crea una sesión de checkout de Stripe.
        
        Args:
            plan_name: Nombre del plan
            price_id: ID del precio en Stripe
            user_email: Email del usuario (opcional)
            success_url: URL de éxito
            cancel_url: URL de cancelación
            
        Returns:
            Diccionario con session_id y url
        """
        if not self.enabled:
            return {
                'error': 'Stripe no está configurado',
                'session_id': None,
                'url': None
            }
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user_email,
                metadata={
                    'plan': plan_name
                }
            )
            
            return {
                'session_id': session.id,
                'url': session.url,
                'error': None
            }
        except Exception as e:
            self.logger.error(f"Error creando sesión de checkout: {str(e)}")
            return {
                'error': str(e),
                'session_id': None,
                'url': None
            }
    
    def get_subscription_status(self, customer_id: str) -> Dict:
        """
        Obtiene el estado de una suscripción.
        
        Args:
            customer_id: ID del cliente en Stripe
            
        Returns:
            Diccionario con información de la suscripción
        """
        if not self.enabled:
            return {'error': 'Stripe no está configurado'}
        
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status='all',
                limit=1
            )
            
            if subscriptions.data:
                sub = subscriptions.data[0]
                return {
                    'status': sub.status,
                    'plan': sub.items.data[0].price.nickname if sub.items.data else 'unknown',
                    'current_period_end': sub.current_period_end,
                    'cancel_at_period_end': sub.cancel_at_period_end
                }
            else:
                return {'status': 'none'}
        except Exception as e:
            self.logger.error(f"Error obteniendo suscripción: {str(e)}")
            return {'error': str(e)}
    
    def cancel_subscription(self, subscription_id: str) -> Tuple[bool, str]:
        """
        Cancela una suscripción.
        
        Args:
            subscription_id: ID de la suscripción
            
        Returns:
            Tupla (éxito, mensaje)
        """
        if not self.enabled:
            return False, "Stripe no está configurado"
        
        try:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return True, "Suscripción cancelada al final del período"
        except Exception as e:
            self.logger.error(f"Error cancelando suscripción: {str(e)}")
            return False, str(e)
    
    def is_test_mode(self) -> bool:
        """Verifica si está en modo de prueba."""
        if not self.secret_key:
            return True
        return self.secret_key.startswith('sk_test_')


# IDs de precios de Stripe (deben crearse en el dashboard de Stripe)
# Para desarrollo, estos son placeholders
STRIPE_PRICE_IDS = {
    'basic': config.get_env('STRIPE_PRICE_ID_BASIC', 'price_basic_monthly'),
    'pro': config.get_env('STRIPE_PRICE_ID_PRO', 'price_pro_monthly'),
    'enterprise': config.get_env('STRIPE_PRICE_ID_ENTERPRISE', 'price_enterprise_monthly')
}

