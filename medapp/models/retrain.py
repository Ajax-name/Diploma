import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import efficientnet_b5
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import os

# === Кастомный датасет, который работает только с существующими классами ===
class MedicalImageDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.classes = []
        self.class_to_idx = {}
        self.samples = []
        
        # Сканируем папку и находим только существующие классы с изображениями
        for class_name in os.listdir(root_dir):
            class_dir = os.path.join(root_dir, class_name)
            if os.path.isdir(class_dir):
                images = [f for f in os.listdir(class_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'))]
                if images:
                    if class_name not in self.class_to_idx:
                        self.class_to_idx[class_name] = len(self.classes)
                        self.classes.append(class_name)
                    for img_name in images:
                        self.samples.append((os.path.join(class_dir, img_name), self.class_to_idx[class_name]))
        
        if not self.samples:
            raise RuntimeError(f"❌ В директории {root_dir} не найдено ни одного изображения.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        img = Image.open(img_path).convert('RGB')
        
        if self.transform:
            img = self.transform(img)
            
        return img, label

# === Настройки ===
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
num_epochs = 5
batch_size = 1
lr = 0.0005

# === Путь к текущему каталогу ===
base_dir = os.path.dirname(os.path.abspath(__file__))

# === Пути к папкам и файлам ===
dataset_train_path = os.path.join(base_dir, "dataset/train")
dataset_val_path = os.path.join(base_dir, "dataset/val")
model_path = os.path.join(base_dir, "model.pth")
class_file_path = os.path.join(base_dir, "class_names.txt")

# === Загрузка полного списка классов ===
with open(class_file_path, "r") as f:
    class_names = [line.strip() for line in f.readlines()]
num_classes = len(class_names)

# === Трансформации ===
transform = transforms.Compose([
    transforms.Resize((512, 512)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# === Создание датасетов ===
try:
    train_dataset = MedicalImageDataset(dataset_train_path, transform=transform)
    val_dataset = MedicalImageDataset(dataset_val_path, transform=transform)
except Exception as e:
    print(e)
    exit(1)

print(f"✔ Найдено классов в train: {train_dataset.classes}")
print(f"✔ Найдено классов в val: {val_dataset.classes}")
print(f"✔ Всего изображений в train: {len(train_dataset)}")
print(f"✔ Всего изображений в val: {len(val_dataset)}")

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

# === Загрузка модели ===
model = efficientnet_b5(pretrained=False)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)

if os.path.exists(model_path):
    try:
        model.load_state_dict(torch.load(model_path, map_location=device))
        print("✔ Модель успешно загружена")
    except Exception as e:
        print(f"⚠ Ошибка при загрузке модели: {e}")
        print("⚠ Будет создана новая модель")
else:
    print("⚠ Файл модели не найден, будет создана новая модель")

model = model.to(device)

# === Заморозка всех слоёв ===
for param in model.parameters():
    param.requires_grad = False

# === Разморозка последних 2 блоков ===
for name, param in model.features[-2:].named_parameters():
    param.requires_grad = True

# === Повторная установка классификатора ===
model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
model = model.to(device)

# === Оптимизатор и функция потерь ===
optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr)
criterion = nn.CrossEntropyLoss()

# === Обучение ===
for epoch in range(num_epochs):
    model.train()
    total_loss = 0.0
    correct = 0

    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()

    acc = 100 * correct / len(train_dataset)
    print(f"Epoch {epoch+1}/{num_epochs} - Train Loss: {total_loss:.4f}, Train Acc: {acc:.2f}%")

    # === Валидация ===
    model.eval()
    val_loss, correct = 0.0, 0

    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            val_loss += loss.item()
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()

    val_acc = 100 * correct / len(val_dataset)
    print(f"Validation Acc: {val_acc:.2f}%, Validation Loss: {val_loss:.4f}")

# === Сохранение модели ===
torch.save(model.state_dict(), model_path)
print("✅ Модель дообучена и сохранена:", model_path)
