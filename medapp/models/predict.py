import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import efficientnet_b5
from PIL import Image
import sys
import os

# Проверка аргумента
if len(sys.argv) != 2:
    print("Использование: python predict.py path/to/image.jpg")
    sys.exit(1)

image_path = sys.argv[1]

if not os.path.exists(image_path):
    print(f"Файл не найден: {image_path}")
    sys.exit(1)

# Абсолютный путь к директории, где находится сам скрипт
base_dir = os.path.dirname(os.path.abspath(__file__))
class_file_path = os.path.join(base_dir, "class_names.txt")

# Загрузка имён классов
with open(class_file_path, "r") as f:
    class_names = [line.strip() for line in f.readlines()]

num_classes = len(class_names)

# Модель
model = efficientnet_b5(pretrained=False)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
model_path = os.path.join(base_dir, "model.pth")
model.load_state_dict(torch.load(model_path, map_location="cpu"))
model.eval()

# Преобразование
transform = transforms.Compose([
    transforms.Resize((512, 512)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# Загрузка изображения
image = Image.open(image_path).convert("RGB")
input_tensor = transform(image).unsqueeze(0)  # Добавляем batch dim

# Предсказание
with torch.no_grad():
    outputs = model(input_tensor)
    probabilities = torch.softmax(outputs, dim=1)
    top_prob, pred = torch.max(probabilities, 1)
    predicted_class = class_names[pred.item()]
    confidence = top_prob.item() * 100

# Вывод
filename = os.path.basename(image_path)
print(f"{filename}: {predicted_class} - {confidence:.1f}%")

