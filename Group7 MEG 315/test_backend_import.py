import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from brayton_cycle import BraytonCycle
    print("✅ Backend import successful!")
    print("✅ Enhanced GUI will have full backend integration")
except ImportError as e:
    print(f"⚠️  Backend import failed: {e}")
    print("⚠️  Enhanced GUI will use fallback calculations")

input("Press Enter to exit...")