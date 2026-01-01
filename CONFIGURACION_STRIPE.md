# 💳 Configuración de Stripe para Pagos

## 📋 Pasos para Configurar Stripe

### 1. Crear Cuenta en Stripe

1. Ve a [https://stripe.com](https://stripe.com)
2. Crea una cuenta (gratis)
3. Completa la información de tu negocio

### 2. Obtener API Keys

1. En el Dashboard de Stripe, ve a **Developers > API keys**
2. Copia tu **Publishable key** (pk_test_...)
3. Copia tu **Secret key** (sk_test_...)
   - ⚠️ **NUNCA** compartas tu Secret key

### 3. Crear Productos y Precios

1. Ve a **Products** en el Dashboard
2. Crea 3 productos:
   - **Básico** - $5.00/mes
   - **Pro** - $7.00/mes
   - **Enterprise** - $9.00/mes

3. Para cada producto:
   - Clic en "Add pricing"
   - Selecciona "Recurring"
   - Establece el precio mensual
   - Guarda el **Price ID** (price_...)

### 4. Configurar Variables de Entorno

Añade a tu archivo `.env`:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_tu_secret_key_aqui
STRIPE_PUBLIC_KEY=pk_test_tu_public_key_aqui

# Stripe Price IDs (obtenidos del dashboard)
STRIPE_PRICE_ID_BASIC=price_tu_price_id_basico
STRIPE_PRICE_ID_PRO=price_tu_price_id_pro
STRIPE_PRICE_ID_ENTERPRISE=price_tu_price_id_enterprise
```

### 5. Configurar Webhooks (Opcional pero Recomendado)

1. En Stripe Dashboard, ve a **Developers > Webhooks**
2. Clic en "Add endpoint"
3. URL: `https://tu-dominio.com/webhook/stripe` (o tu URL de producción)
4. Eventos a escuchar:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copia el **Webhook signing secret** (whsec_...)

Añade a `.env`:
```bash
STRIPE_WEBHOOK_SECRET=whsec_tu_webhook_secret
```

## 🧪 Modo de Prueba

Stripe tiene un modo de prueba perfecto para desarrollo:

- **Tarjetas de prueba:**
  - Éxito: `4242 4242 4242 4242`
  - Rechazada: `4000 0000 0000 0002`
  - Cualquier fecha futura y CVC válido

- **Más tarjetas de prueba:** [Stripe Testing](https://stripe.com/docs/testing)

## 🚀 Producción

Cuando estés listo para producción:

1. Cambia a **Live mode** en Stripe Dashboard
2. Obtén las **Live API keys**
3. Actualiza las variables de entorno con las keys de producción
4. Configura webhooks con tu URL de producción

## 📝 Notas Importantes

- ⚠️ **NUNCA** commitees tus API keys al repositorio
- Usa variables de entorno siempre
- El archivo `.env` está en `.gitignore`
- En producción, usa un servicio de gestión de secretos (AWS Secrets Manager, etc.)

## 🔗 Recursos

- [Documentación de Stripe](https://stripe.com/docs)
- [Stripe Checkout](https://stripe.com/docs/payments/checkout)
- [Stripe Subscriptions](https://stripe.com/docs/billing/subscriptions/overview)

