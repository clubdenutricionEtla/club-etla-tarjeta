import sys
import os

# Agregar la ruta raíz al PATH de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app
    print("✅ app importada correctamente")
except Exception as e:
    print(f"❌ Error importando app: {e}")
    raise
