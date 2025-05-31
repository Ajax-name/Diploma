import torch
import torch.nn as nn
from torch.amp import autocast
from torch.cuda.amp import GradScaler
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from torchvision.models import densenet121, DenseNet121_Weights
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from sklearn.metrics import (confusion_matrix, precision_score, recall_score, roc_curve, auc)
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from itertools import cycle  # Добавлен недостающий импорт

# 1. Настройки
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
batch_size = 16
num_epochs = 30
num_classes = 9
lr = 0.0003
patience = 5
img_size = 224

# 2. Аугментации для медицинских изображений
train_transform = transforms.Compose([
    transforms.Resize((img_size, img_size)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.1, contrast=0.1),
    transforms.RandomAffine(degrees=5, translate=(0.05, 0.05)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((img_size, img_size)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# 3. Загрузка данных
train_dataset = datasets.ImageFolder('dataset/train', transform=train_transform)
val_dataset = datasets.ImageFolder('dataset/val', transform=val_transform)

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)

# 4. Инициализация модели ResNet50
model = densenet121(weights=DenseNet121_Weights.IMAGENET1K_V1)

# Замораживаем параметры
for param in model.parameters():
    param.requires_grad = False

# Размораживаем последний denseblock
for param in model.features.denseblock4.parameters():
    param.requires_grad = True

# Заменяем классификатор
num_features = model.classifier.in_features
model.classifier = nn.Sequential(
    nn.Dropout(0.5),
    nn.Linear(num_features, num_classes)
)
model = model.to(device)

# 5. Функции для метрик
def calculate_specificity(cm, class_idx):
    tn = cm.sum() - (cm[class_idx, :].sum() + cm[:, class_idx].sum() - cm[class_idx, class_idx])
    fp = cm[:, class_idx].sum() - cm[class_idx, class_idx]
    return tn / (tn + fp) if (tn + fp) > 0 else 0

def plot_roc_curve(y_true, y_probs, class_names, writer, phase, epoch):
    try:
        # Конвертация в one-hot encoding
        y_true_onehot = np.eye(len(class_names))[y_true]
        
        # Расчет ROC кривых
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        
        for i in range(len(class_names)):
            fpr[i], tpr[i], _ = roc_curve(y_true_onehot[:, i], y_probs[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])
        
        # Создаем общий график
        plt.figure(figsize=(10, 8))
        colors = cycle(['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'purple', 'orange'])
        
        for i, color in zip(range(len(class_names)), colors):
            plt.plot(fpr[i], tpr[i], color=color, lw=1.5,
                     label=f'{class_names[i]} (AUC = {roc_auc[i]:.2f})')
        
        plt.plot([0, 1], [0, 1], 'k--', lw=1.5)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'{phase} ROC Curves')
        plt.legend(loc="lower right")
        writer.add_figure(f'{phase}/ROC_Curves', plt.gcf(), epoch)
        plt.close()
        
        return roc_auc
    
    except Exception as e:
        print(f"Ошибка построения ROC-кривых: {e}")
        return {}

def log_metrics(writer, phase, cm, epoch, loss=None, y_true=None, y_probs=None, class_names=None):
    try:
        # Логирование основных метрик
        precision = precision_score(cm['true'], cm['pred'], average='macro', zero_division=0)
        recall = recall_score(cm['true'], cm['pred'], average='macro', zero_division=0)
        specificity = np.mean([calculate_specificity(cm['matrix'], i) for i in range(num_classes)])
        
        writer.add_scalar(f'{phase}/Precision', precision, epoch)
        writer.add_scalar(f'{phase}/Recall', recall, epoch)
        writer.add_scalar(f'{phase}/Specificity', specificity, epoch)
        
        if loss is not None:
            writer.add_scalar(f'{phase}/Loss', loss, epoch)
        
        # Матрица ошибок
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm['matrix'], annot=True, fmt='d', cmap='Blues', 
                    xticklabels=class_names, yticklabels=class_names)
        plt.title(f'{phase} Confusion Matrix')
        writer.add_figure(f'{phase}/Confusion_Matrix', plt.gcf(), epoch)
        plt.close()
        
        # ROC-AUC
        if y_true is not None and y_probs is not None:
            # Проверка вероятностей
            if not np.allclose(y_probs.sum(axis=1), 1.0, atol=1e-3):
                y_probs = y_probs / y_probs.sum(axis=1, keepdims=True)
            
            roc_auc = plot_roc_curve(y_true, y_probs, class_names, writer, phase, epoch)
            
            # Логирование AUC
            if roc_auc:
                writer.add_scalar(f'{phase}/AUC Macro', np.mean(list(roc_auc.values())), epoch)
                
    except Exception as e:
        print(f"Ошибка логирования метрик: {e}")

# 6. Процесс обучения
optimizer = torch.optim.AdamW(
    filter(lambda p: p.requires_grad, model.parameters()), 
    lr=lr,
    weight_decay=0.01
)

scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, 
    mode='max', 
    patience=2, 
    factor=0.5
)

criterion = nn.CrossEntropyLoss()
scaler = GradScaler()

# TensorBoard
log_dir = f"runs/densenet50_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
writer = SummaryWriter(log_dir)

best_val_accuracy = 0
early_stop_counter = 0

for epoch in range(num_epochs):
    # Train
    model.train()
    train_preds, train_labels, train_probs = [], [], []
    train_loss = 0.0
    
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        
        with autocast(device_type='cuda', dtype=torch.float16):
            outputs = model(inputs)
            loss = criterion(outputs, labels)
        
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        
        # Сохранение предсказаний и вероятностей
        probs = torch.softmax(outputs, dim=1)
        train_probs.extend(probs.detach().cpu().numpy())
        _, preds = torch.max(outputs, 1)
        train_preds.extend(preds.detach().cpu().numpy())
        train_labels.extend(labels.detach().cpu().numpy())
        train_loss += loss.item() * inputs.size(0)
    
    # Метрики обучения
    train_loss /= len(train_dataset)
    train_cm = confusion_matrix(train_labels, train_preds, labels=range(num_classes))
    log_metrics(writer, 'Train', 
               {'matrix': train_cm, 'true': train_labels, 'pred': train_preds}, 
               epoch, train_loss, 
               np.array(train_labels), np.array(train_probs), 
               train_dataset.classes)

    # Validation
    model.eval()
    val_preds, val_labels, val_probs = [], [], []
    val_loss = 0.0
    
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            with autocast(device_type='cuda', dtype=torch.float16):
                outputs = model(inputs)
                loss = criterion(outputs, labels)
            
            probs = torch.softmax(outputs, dim=1)
            val_probs.extend(probs.cpu().numpy())
            _, preds = torch.max(outputs, 1)
            val_preds.extend(preds.cpu().numpy())
            val_labels.extend(labels.cpu().numpy())
            val_loss += loss.item() * inputs.size(0)
    
    # Метрики валидации
    val_loss /= len(val_dataset)
    val_cm = confusion_matrix(val_labels, val_preds, labels=range(num_classes))
    val_accuracy = np.trace(val_cm) / np.sum(val_cm)
    
    log_metrics(writer, 'Val', 
               {'matrix': val_cm, 'true': val_labels, 'pred': val_preds}, 
               epoch, val_loss, 
               np.array(val_labels), np.array(val_probs), 
               train_dataset.classes)

    # Ранняя остановка
    if val_accuracy > best_val_accuracy:
        best_val_accuracy = val_accuracy
        early_stop_counter = 0
        torch.save(model.state_dict(), f'{log_dir}/best_model.pth')
    else:
        early_stop_counter += 1
        if early_stop_counter >= patience:
            print(f"Ранняя остановка на эпохе {epoch+1}")
            break
    
    scheduler.step(val_accuracy)
    print(f"Эпоха {epoch+1}: "
          f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
          f"Val Accuracy: {val_accuracy:.4f}")

writer.close()
