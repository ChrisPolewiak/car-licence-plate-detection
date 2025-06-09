import torch
from torch.serialization import safe_globals
from ultralytics import YOLO
from ultralytics.nn.tasks import DetectionModel

# Zezwalamy na globalne klasy użyte w modelu
safe_globals([DetectionModel])

# Wczytujemy model – teraz powinno zadziałać
model = YOLO("best.pt")

# Eksportujemy model do nowego formatu, np. weights-only
model.export(format="torchscript")
  # wygeneruje `best.torchscript.pt` domyślnie
