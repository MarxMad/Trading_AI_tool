# 🚀 Comandos Rápidos

## Ejecutar la Interfaz (Forma Simple)

Si ya tienes todas las dependencias instaladas, simplemente ejecuta:

```bash
./run_simple.sh
```

O manualmente:

```bash
source venv/bin/activate
streamlit run app.py
```

## Ejecutar la Interfaz (Con Instalación)

Si necesitas instalar/actualizar dependencias:

```bash
./run_app.sh
```

## Otros Comandos Útiles

### Activar entorno virtual manualmente
```bash
source venv/bin/activate
```

### Instalar dependencias manualmente
```bash
pip install -r requirements.txt
```

### Verificar que streamlit está instalado
```bash
source venv/bin/activate
streamlit --version
```

### Ejecutar script principal (sin interfaz)
```bash
source venv/bin/activate
python main.py
```

### Desactivar entorno virtual
```bash
deactivate
```

## Notas

- **run_simple.sh**: Solo activa el venv y ejecuta streamlit (rápido)
- **run_app.sh**: Crea venv, instala dependencias y ejecuta (completo)
- Siempre asegúrate de tener el entorno virtual activado antes de ejecutar comandos Python


