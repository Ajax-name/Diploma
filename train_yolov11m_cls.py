import os
import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import cycle
from ultralytics import YOLO
from torch.utils.tensorboard import SummaryWriter
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    roc_curve,
    auc,
    classification_report
)
from sklearn.preprocessing import label_binarize

# === Конфигурация ===
DATA_ROOT       = 'dataset'
MODEL_WEIGHTS   = 'yolo11m-cls.pt'
PROJECT_DIR     = 'runs_cls'
EXPERIMENT_NAME = 'yolo11m_cls_run'
EPOCHS          = 40
IMGSZ           = 224
BATCH           = 16
LR0             = 0.0003
PATIENCE        = 5
DEVICE          = 'cuda' if torch.cuda.is_available() and torch.cuda.device_count() > 0 else 'cpu'

# === Аугментации ===
AUG_PARAMS = dict(
    fliplr     = 0.5,
    flipud     = 0.0,
    degrees    = 15.0,
    translate  = 0.05,
    scale      = 0.05,
    hsv_h      = 0.1,
    hsv_s      = 0.1,
    hsv_v      = 0.1,
    copy_paste = 0.0,
    mosaic     = 1.0,
    mixup      = 0.0,
)

# === Метрики ===
def calculate_specificity(cm):
    spec = []
    for i in range(len(cm)):
        tn = cm.sum() - (cm[i, :].sum() + cm[:, i].sum() - cm[i, i])
        fp = cm[:, i].sum() - cm[i, i]
        spec.append(tn / (tn + fp) if (tn + fp) > 0 else 0.0)
    return spec

def plot_and_log_metrics(y_true, y_scores_arr, class_names, writer, epoch):
    y_pred = np.argmax(y_scores_arr, axis=1)
    prec = precision_score(y_true, y_pred, average='macro', zero_division=0)
    rec  = recall_score(y_true, y_pred, average='macro', zero_division=0)

    cm = confusion_matrix(y_true, y_pred, labels=range(len(class_names)))
    spec_list = calculate_specificity(cm)
    spec_avg  = np.mean(spec_list)

    # Логируем скаляры
    writer.add_scalar('Metrics/Precision', prec, epoch)
    writer.add_scalar('Metrics/Recall',    rec,  epoch)
    writer.add_scalar('Metrics/Specificity', spec_avg, epoch)

    print(f"\n=== Epoch {epoch+1} Metrics ===")
    print(classification_report(y_true, y_pred, target_names=class_names))

    # Матрица ошибок
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.title(f'Confusion Matrix (Epoch {epoch+1})')
    plt.ylabel('True label'); plt.xlabel('Predicted label')
    writer.add_figure('Confusion Matrix', plt.gcf(), epoch)
    plt.close()

    # ROC-кривые
    y_true_bin = label_binarize(y_true, classes=range(len(class_names)))
    fpr, tpr, roc_auc = {}, {}, {}
    for i in range(len(class_names)):
        fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_scores_arr[:, i])
        roc_auc[i]     = auc(fpr[i], tpr[i])

    plt.figure(figsize=(8, 6))
    colors = cycle(['aqua','darkorange','cornflowerblue','red','green','purple','cyan','magenta','yellow'])
    for i, color in zip(range(len(class_names)), colors):
        plt.plot(fpr[i], tpr[i], color=color,
                 label=f'{class_names[i]} (AUC = {roc_auc[i]:.2f})')
    plt.plot([0,1], [0,1], 'k--', lw=1)
    plt.xlim([0.0,1.0]); plt.ylim([0.0,1.05])
    plt.xlabel('False Positive Rate'); plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curves (Epoch {epoch+1})')
    plt.legend(loc='lower right')
    writer.add_figure('ROC Curves', plt.gcf(), epoch)
    plt.close()

# === Основной цикл ===
def main():
    writer = SummaryWriter(log_dir=os.path.join(PROJECT_DIR, EXPERIMENT_NAME))
    print("Device:", DEVICE)
    model = YOLO(MODEL_WEIGHTS)

    class_names = sorted(os.listdir(os.path.join(DATA_ROOT, 'train')))

    # По-эпохный цикл
    for epoch in range(EPOCHS):
        print(f"\n--- Training epoch {epoch+1}/{EPOCHS} ---")
        # Тренируем ровно одну эпоху
        model.train(
            data=DATA_ROOT,
            epochs=1,
            imgsz=IMGSZ,
            batch=BATCH,
            lr0=LR0,
            patience=PATIENCE,
            device=DEVICE,           
            project=PROJECT_DIR,
            name=EXPERIMENT_NAME,
            exist_ok=True,
            resume=False,          
            plots=False,
            **AUG_PARAMS
        )

        # Validation
        y_true_list, y_scores_list = [], []
        val_root = os.path.join(DATA_ROOT, 'val')
        for idx, cls in enumerate(class_names):
            cls_dir = os.path.join(val_root, cls)
            for img_name in os.listdir(cls_dir):
                img_path = os.path.join(cls_dir, img_name)
                res = model.predict(img_path, imgsz=IMGSZ, device=DEVICE, verbose=False)[0]
                if res.probs is None:
                    continue
                probs_np = res.probs.data.cpu().numpy()
                y_scores_list.append(probs_np)
                y_true_list.append(idx)

        y_true_arr   = np.array(y_true_list)
        y_scores_arr = np.stack(y_scores_list, axis=0)
        plot_and_log_metrics(y_true_arr, y_scores_arr, class_names, writer, epoch)

    writer.close()

if __name__ == '__main__':
    main()

