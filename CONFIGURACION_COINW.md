# Configuración de CoinW API

Esta guía te ayudará a configurar la integración con CoinW Exchange para ejecutar trades directamente desde la aplicación.

## Requisitos Previos

1. Cuenta activa en CoinW Exchange
2. API Key y API Secret de CoinW
3. Permisos de trading habilitados en tu cuenta de CoinW

## Pasos de Configuración

### 1. Obtener API Credentials de CoinW

1. Inicia sesión en tu cuenta de CoinW
2. Ve a **API Management** o **API Settings**
3. Crea una nueva API Key con los siguientes permisos:
   - ✅ **Read** (lectura de balance y posiciones)
   - ✅ **Trade** (ejecutar órdenes)
   - ❌ **Withdraw** (NO habilitar por seguridad)

4. Guarda tu **API Key** y **API Secret** de forma segura
   - ⚠️ **IMPORTANTE**: El API Secret solo se muestra una vez. Guárdalo inmediatamente.

### 2. Configurar en la Aplicación

#### Opción A: Variables de Entorno (Desarrollo Local)

Crea o edita el archivo `.env` en la raíz del proyecto:

```env
# CoinW API Configuration
COINW_API_KEY=tu_api_key_aqui
COINW_API_SECRET=tu_api_secret_aqui
```

#### Opción B: Streamlit Cloud Secrets (Producción)

1. Ve a tu app en Streamlit Cloud
2. Haz clic en **"Manage app"** → **"Settings"** → **"Secrets"**
3. Añade las siguientes líneas en formato TOML:

```toml
COINW_API_KEY = "tu_api_key_aqui"
COINW_API_SECRET = "tu_api_secret_aqui"
```

### 3. Verificar Configuración

Una vez configurado, deberías ver en el sidebar:
- ✅ Balance disponible de tu cuenta CoinW
- ✅ Posiciones abiertas (si las tienes)
- ✅ El botón "🚀 Trade" estará habilitado

Si ves un mensaje de advertencia, verifica que:
- Las credenciales estén correctamente escritas
- No haya espacios extra en las keys
- Los permisos de la API estén habilitados

## Funcionalidades Disponibles

### Ejecutar Trades

1. Sube una imagen de gráfico
2. Espera el análisis de la IA
3. Revisa los niveles sugeridos (Entry, Stop Loss, Take Profit)
4. Haz clic en **"🚀 Trade"**
5. La orden se ejecutará automáticamente en CoinW

### Visualización en Tiempo Real

El sidebar muestra:
- **Balance Disponible**: Fondos que puedes usar para trading
- **Balance Total**: Balance total de la cuenta
- **Posiciones Abiertas**: Lista de posiciones activas con:
  - Símbolo y dirección (LONG/SHORT)
  - Tamaño de la posición
  - Apalancamiento utilizado
  - Precio de entrada
  - P&L no realizado

## Seguridad

### Mejores Prácticas

1. **Nunca compartas tus credenciales API**
2. **No habilites permisos de retiro (Withdraw)** en la API
3. **Usa IP Whitelist** si CoinW lo permite
4. **Revisa regularmente** las órdenes ejecutadas
5. **Usa límites de trading** en CoinW para protección adicional

### Limitaciones de la API

- Las credenciales se almacenan de forma segura en variables de entorno
- No se guardan en el código fuente
- Las solicitudes se autentican con HMAC-SHA256

## Solución de Problemas

### Error: "CoinW API not configured"

**Solución**: Verifica que `COINW_API_KEY` y `COINW_API_SECRET` estén configurados correctamente.

### Error: "Insufficient balance"

**Solución**: Asegúrate de tener fondos suficientes en tu cuenta CoinW para la operación.

### Error: "Could not fetch balance"

**Solución**: 
- Verifica que las credenciales sean correctas
- Asegúrate de que la API tenga permisos de lectura
- Revisa que CoinW no esté en mantenimiento

### Las posiciones no se muestran

**Solución**: 
- Verifica que tengas posiciones abiertas en CoinW
- Asegúrate de que la API tenga permisos de lectura
- Revisa los logs para más detalles

## Notas Importantes

⚠️ **DISCLAIMER DE TRADING**:
- El trading con apalancamiento conlleva riesgos significativos
- Puedes perder más de tu depósito inicial
- El análisis de IA es informativo y no garantiza ganancias
- Siempre opera con responsabilidad
- Nunca arriesgues más de lo que puedes permitirte perder

## Soporte

Si encuentras problemas con la integración:
1. Revisa los logs de la aplicación
2. Verifica la documentación oficial de CoinW API
3. Contacta al soporte si el problema persiste

---

**Última actualización**: Enero 2025


