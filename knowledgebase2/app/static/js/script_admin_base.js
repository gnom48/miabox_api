// Открытие проводника для выбора изображения
function openImageUploader() {
    const input = document.getElementById("image-input");
    input.value = ""; // Сбрасываем значение (чтобы выбрать тот же файл снова)
    input.click();
    input.onchange = (event) => insertImage(event.target.files[0]);
}

// Вставка изображения в текущий раздел
function insertImage(file) {
    if (!currentEditor) return;

    const reader = new FileReader();
    reader.onload = function (event) {
        const imgContainer = document.createElement("div");
        imgContainer.className = "image-container";

        const img = document.createElement("img");
        img.src = event.target.result;
        img.className = "inserted-image";

        // Устанавливаем изображение на 50% от оригинального размера
        img.onload = function () {
            img.style.width = "50%";
            img.style.height = "auto";
        };

        // Контейнер для кнопок
        const btnContainer = document.createElement("div");
        btnContainer.className = "image-btn-container";

        // Кнопка удаления
        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "Удалить";
        deleteBtn.className = "delete-image-btn";
        deleteBtn.onclick = () => imgContainer.remove(); // Полностью убираем контейнер с изображением

        // Кнопка замены
        const replaceBtn = document.createElement("button");
        replaceBtn.textContent = "Заменить";
        replaceBtn.className = "replace-image-btn";
        replaceBtn.onclick = () => openReplaceImage(img);

        btnContainer.appendChild(deleteBtn);
        btnContainer.appendChild(replaceBtn);

        imgContainer.appendChild(img);
        imgContainer.appendChild(btnContainer);

        // Добавляем изображение в редактор
        currentEditor.appendChild(imgContainer);

        // Создаём новый div для дальнейшего ввода текста
        const newTextDiv = document.createElement("div");
        newTextDiv.className = "editor-text";
        newTextDiv.contentEditable = "true";
        newTextDiv.setAttribute("placeholder", "Продолжайте писать...");

        currentEditor.appendChild(newTextDiv);
        newTextDiv.focus(); // Ставим курсор сразу в новый блок
    };
    reader.readAsDataURL(file);
}

// Замена изображения
function openReplaceImage(img) {
    const input = document.getElementById("image-input");
    input.value = "";
    input.click();
    input.onchange = (event) => {
        const reader = new FileReader();
        reader.onload = (e) => (img.src = e.target.result);
        reader.readAsDataURL(event.target.files[0]);
    };
}
