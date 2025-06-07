// Определяем, где сейчас находится курсор
let currentEditor = null;

document.addEventListener("selectionchange", () => {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const editor = range.startContainer.closest(".editor");
        if (editor) {
            currentEditor = editor;
        }
    }
});

// document.addEventListener("DOMContentLoaded", () => {
//     loadSections();
// });

function addSection(content = "") {
    let sectionsContainer = document.getElementById("sections");

    let sectionWrapper = document.createElement("div");
    sectionWrapper.className = "section-wrapper";
    sectionWrapper.style.position = "relative";

    // Заголовок раздела
    let title = document.createElement("h2");
    title.className = "section-title";
    title.contentEditable = true;
    title.textContent = content ? content.split("\n")[0] : "Название раздела";

    // Основной контент
    let section = document.createElement("div");
    section.className = "editor";
    section.contentEditable = true;
    section.innerHTML = content ? content.split("\n").slice(1).join("\n") : "";

    // Следим за изменением заголовка и обновляем меню
    title.addEventListener("input", updateMenu);

    sectionWrapper.appendChild(title);
    sectionWrapper.appendChild(section);
    sectionsContainer.appendChild(sectionWrapper);

    updateMenu();
}

function deleteSection() {
    const selection = window.getSelection();
    const range = selection.getRangeAt(0);
    const currentSection = range.startContainer.closest('.editor');

    if (currentSection) {
        currentSection.remove();
        saveSections();  // Сохраняем изменения после удаления
    }
}

function updateMenu() {
    const menu = document.getElementById("menu");
    menu.innerHTML = ""; // Очищаем старое меню

    const sections = document.querySelectorAll(".section-wrapper");
    sections.forEach((wrapper, index) => {
        let title = wrapper.querySelector(".section-title").textContent.trim();
        if (!title) title = `Раздел ${index + 1}`;

        const menuItem = document.createElement("div");
        menuItem.classList.add("menu-item");
        menuItem.textContent = title;
        menuItem.onclick = () => wrapper.scrollIntoView({ behavior: "smooth" });

        menu.appendChild(menuItem);
    });
}

function showControlsOnSelect(event) {
    const selection = window.getSelection();
    if (selection.rangeCount > 0 && selection.toString().trim() !== "") {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        const controls = document.getElementById("controls");
        controls.style.display = "block";
        controls.style.top = `${rect.bottom + window.scrollY}px`;
        controls.style.left = `${rect.left + window.scrollX}px`;
    }
}

function applyCommand(command) {
    document.execCommand(command, false, null);
    saveSections();
}

function saveSections() {
    const sections = [];
    document.querySelectorAll(".section-wrapper").forEach(wrapper => {
        let title = wrapper.querySelector(".section-title").textContent.trim();
        let content = wrapper.querySelector(".editor").innerHTML;
        sections.push(`${title}\n${content}`);
    });
    localStorage.setItem("sections", JSON.stringify(sections));
    updateMenu();
}

function loadSections() {
    const savedSections = JSON.parse(localStorage.getItem("sections") || "[]");
    if (savedSections.length === 0) {
        addSection();
    } else {
        savedSections.forEach(content => addSection(content));
    }
}

function toggleMenu(event) {
    event.stopPropagation(); // Останавливаем всплытие события
    const menu = document.getElementById("menu");
    menu.style.display = (menu.style.display === "block") ? "none" : "block";
}

// Назначаем обработчик клика на кнопку меню
document.querySelector(".menu-button").addEventListener("click", (event) => {
    toggleMenu(event);
});

// Закрытие меню при клике вне его области
document.addEventListener("click", (event) => {
    const menu = document.getElementById("menu");
    const menuButton = document.querySelector(".menu-button");

    if (!menu.contains(event.target) && !menuButton.contains(event.target)) {
        menu.style.display = "none";
    }
});

document.addEventListener("click", function(event) {
    if (!event.target.closest(".controls")) {
        document.getElementById("controls").style.display = "none";
    }
});

document.addEventListener("contextmenu", function(event) {
    event.preventDefault();

    const selection = window.getSelection();
    const selectedText = selection.toString().trim();
    showControlsOnSelect(event);
});

function encodeImageToBase64(imgElement) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = imgElement.width;
    canvas.height = imgElement.height;
    ctx.drawImage(imgElement, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/png'); // Преобразуем в Base64
}

function saveContentWithImages() {
    const content = document.body.innerHTML; // Получаем весь HTML
    const images = document.querySelectorAll('img'); // Находим все изображения на странице

    images.forEach(img => {
        const base64Image = encodeImageToBase64(img); // Преобразуем изображение в Base64
        img.src = base64Image; // Заменяем исходный путь изображения на строку Base64
    });

    const htmlContent = document.body.innerHTML; // Получаем обновленный HTML с Base64 изображениями
    const blob = new Blob([htmlContent], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'base.html'; // Устанавливаем имя файла
    link.click();
}

function restoreImages() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        const base64String = img.src;
        if (base64String.startsWith('data:image/png;base64,')) {
            img.src = base64String; // Восстанавливаем изображение из Base64
        }
    });
}

function loadPageFromFile(file) {
    const reader = new FileReader();
    reader.onload = function(event) {
        document.body.innerHTML = event.target.result; // Вставляем загруженный HTML в тело страницы
        restoreImages(); // Восстанавливаем изображения
    };
    reader.readAsText(file);
}

document.getElementById('file-input').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        loadPageFromFile(file); // Загружаем файл
    }
});





// Функция для преобразования изображения в Base64
function encodeImageToBase64Async(img) {
    return new Promise((resolve, reject) => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const image = new Image();

        image.crossOrigin = 'Anonymous';
        image.src = img.src;

        image.onload = () => {
            canvas.width = image.width;
            canvas.height = image.height;
            ctx.drawImage(image, 0, 0);
            const dataURL = canvas.toDataURL('image/png');
            resolve(dataURL);
        };

        image.onerror = reject;
    });
}

async function postContentWithImages() {
    const contentDiv = document.getElementById('sections'); // Находим нужный div
    if (!contentDiv) {
        console.error('Content div not found');
        return;
    }

    const images = contentDiv.querySelectorAll('img'); // Находим все изображения внутри div

    // Преобразуем изображения в Base64
    for (let img of images) {
        const base64Image = await encodeImageToBase64Async(img);
        img.src = base64Image;
    }

    const htmlContent = contentDiv.innerHTML; // Получаем обновленный HTML с Base64 изображениями

    // Отправляем содержимое на эндпоинт
    const response = await fetch('/knowledgebase2/base/upload', {
        method: 'POST',
        headers: {
            'Content-Type': 'test/html',
            'X-Session-Id': localStorage.getItem('sessionId'),
            'X-Team-Id': document.getElementById('teamId').innerText
        },
        body: htmlContent
    });

    if (response.ok) {
        console.log('Content successfully uploaded');
    } else {
        console.error('Failed to upload content');
    }
}