"""Régénère les jeux de données synthétiques du ML et réentraîne les modèles.
Usage : python scripts/generate_ml_data.py [nb_apprenants] [nb_tentatives]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import ml_engine as ML

n1 = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
n2 = int(sys.argv[2]) if len(sys.argv) > 2 else 40000
ML.generate_synthetic(n1, n2)
print(ML.train_models()["metrics"])
