const dropArea = document.getElementById("drop-area");
const fileInput = document.getElementById("fileElem");
const previewContainer = document.getElementById("preview-container");
const processBtn = document.getElementById("process-btn");
const deleteBtn = document.getElementById("delete-btn");
const resultBlock = document.getElementById("result-block");
const resultText = document.getElementById("result-text");
const loadingSpinner = document.getElementById("loading-spinner");
const backLink = document.getElementById("retrain-link");

let uploadedFiles = [];

dropArea.addEventListener("click", () => {
    fileInput.click();
});

dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.classList.add("bg-gray-200");
});

dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("bg-gray-200");
});

dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.classList.remove("bg-gray-200");
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener("change", () => {
    handleFiles(fileInput.files);
});

function handleFiles(files) {
    const filesArray = Array.from(files);
    const newFiles = [...uploadedFiles, ...filesArray].slice(0, 3);
    uploadedFiles = newFiles;

    updatePreview();
    updateButtons();
}

function updatePreview() {
    previewContainer.innerHTML = "";
    uploadedFiles.forEach((file) => {
        const img = document.createElement("img");
        img.src = URL.createObjectURL(file);
        img.classList.add("h-32", "object-contain");
        previewContainer.appendChild(img);
    });
}

function updateButtons() {
    const visible = uploadedFiles.length > 0;
    processBtn.classList.toggle("hidden", !visible);
    deleteBtn.classList.toggle("hidden", !visible);
}

deleteBtn.addEventListener("click", () => {
    uploadedFiles.pop();
    updatePreview();
    updateButtons();
    resultBlock.classList.add("hidden");
});

processBtn.addEventListener("click", () => {
    backLink.classList.add("text-gray-400", "pointer-events-none"); // блокировка перехода

    const formData = new FormData();
    uploadedFiles.forEach((file) => formData.append("files", file));

    // Показать спиннер, скрыть блок с результатом и очистить его
    resultBlock.classList.add("hidden");
    resultText.innerHTML = "";
    loadingSpinner.classList.remove("hidden");

    console.log("Отправка запроса...");

    fetch("/api/analysis", {
        method: "POST",
        body: formData
    })
        .then((res) => {
            if (!res.ok) throw new Error("Ошибка ответа от сервера");
            return res.json();
        })
        .then((data) => {
            console.log("Ответ сервера:", data);

            const result = JSON.stringify(data.result);
            const resultArray = result.slice(1, result.length - 1).split(';');

            for (let picture of resultArray) {
                resultText.insertAdjacentHTML("beforeend", `<div>${picture}</div>`);
            }

            loadingSpinner.classList.add("hidden");
            resultBlock.classList.remove("hidden");
        })
        .catch((err) => {
            console.error("Ошибка:", err);
            resultText.textContent = "Произошла ошибка при анализе.";
            loadingSpinner.classList.add("hidden");
            resultBlock.classList.remove("hidden");
        })
        .finally(() => {
                backLink.classList.remove("text-gray-400", "pointer-events-none"); // вернуть активность
            });
});

