const dropArea = document.getElementById("drop-area");
const fileInput = document.getElementById("fileElem");
const previewContainer = document.getElementById("preview-container");
const classButtons = document.querySelectorAll(".class-btn");
const retrainBtn = document.getElementById("retrain-btn");
const deleteBtn = document.getElementById("delete-btn");
const statusMessage = document.getElementById("status-message");
const loader = document.getElementById("loader");
const backLink = document.getElementById("back-link");

let selectedClass = null;
let uploadedFile = null;

dropArea.addEventListener("click", () => fileInput.click());

dropArea.addEventListener("dragover", e => {
    e.preventDefault();
    dropArea.classList.add("bg-gray-200");
});

dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("bg-gray-200");
});

dropArea.addEventListener("drop", e => {
    e.preventDefault();
    dropArea.classList.remove("bg-gray-200");
    handleFile(e.dataTransfer.files[0]);
});

fileInput.addEventListener("change", () => handleFile(fileInput.files[0]));

function handleFile(file) {
    uploadedFile = file;
    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    img.classList.add("h-32", "object-contain");
    previewContainer.innerHTML = "";
    previewContainer.appendChild(img);
    deleteBtn.classList.remove("hidden");
    updateSubmitState();
}

classButtons.forEach(btn => {
    btn.classList.add("bg-white", "border", "rounded", "p-2", "hover:bg-gray-100");
    btn.addEventListener("click", () => {
        classButtons.forEach(b => b.classList.remove("bg-blue-100", "font-bold"));
        btn.classList.add("bg-blue-100", "font-bold");
        selectedClass = btn.textContent;
        updateSubmitState();
    });
});

deleteBtn.addEventListener("click", () => {
    uploadedFile = null;
    previewContainer.innerHTML = "";
    deleteBtn.classList.add("hidden");
    updateSubmitState();
});

function updateSubmitState() {
    const canSubmit = uploadedFile && selectedClass;
    retrainBtn.disabled = !canSubmit;
    retrainBtn.classList.toggle("opacity-50", !canSubmit);
    retrainBtn.classList.toggle("cursor-not-allowed", !canSubmit);
}

retrainBtn.addEventListener("click", () => {
    const formData = new FormData();
    formData.append("file", uploadedFile);
    formData.append("className", selectedClass);

    loader.classList.remove("hidden");
    statusMessage.classList.add("hidden");
    retrainBtn.disabled = true;
    backLink.classList.add("text-gray-400", "pointer-events-none");

    fetch("/api/retrain", {
        method: "POST",
        body: formData
    })
        .then(res => {
            if (!res.ok) throw new Error("Ошибка сервера");
            return res.text();
        })
        .then(() => {
            statusMessage.textContent = "Модель обучена!";
            statusMessage.classList.remove("hidden");
            statusMessage.classList.remove("text-red-500");
            statusMessage.classList.add("text-green-600");
        })
        .catch(() => {
            statusMessage.textContent = "Произошла ошибка при дообучении.";
            statusMessage.classList.remove("hidden");
            statusMessage.classList.remove("text-green-600");
            statusMessage.classList.add("text-red-500");
        })
        .finally(() => {
            loader.classList.add("hidden");
            retrainBtn.disabled = false;
            backLink.classList.remove("text-gray-400", "pointer-events-none");
        });
});
