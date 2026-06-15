document.addEventListener('DOMContentLoaded', () => {
    initSPA();
});

function initSPA() {
    // Handle navigation links
    document.querySelectorAll('.admin-section-link, [data-spa-link]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const url = link.getAttribute('href');
            loadSection(url);
        });
    });

    // Handle table row clicks
    document.querySelectorAll('[data-spa-row]').forEach(row => {
        row.addEventListener('click', (e) => {
            // Не реагируем на клики по кнопкам внутри строки
            if (e.target.closest('button, a, input, .button')) return;
            e.preventDefault();
            const url = row.getAttribute('data-href');
            if (url) loadEntry(url);
        });
    });

    // Handle forms - ИСПРАВЛЕНО: проверяем что элемент действительно форма
    document.querySelectorAll('.embedded-admin-form').forEach(formElement => {
        // Убеждаемся что это именно HTMLFormElement
        if (formElement && formElement.tagName === 'FORM') {
            // Удаляем старый обработчик, если есть
            formElement.removeEventListener('submit', formSubmitHandler);
            // Добавляем новый
            formElement.addEventListener('submit', formSubmitHandler);
        }
    });
}

// Отдельная функция-обработчик для форм
function formSubmitHandler(e) {
    e.preventDefault();
    const form = e.currentTarget; // Это точно HTMLFormElement
    if (form && form.tagName === 'FORM') {
        submitForm(form);
    } else {
        console.error('Submit handler called on non-form element:', form);
    }
}

async function loadSection(url) {
    try {
        const response = await fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!response.ok) throw new Error('Network response was not ok');

        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        const listPanel = document.querySelector('.admin-list-panel');
        const newListContent = doc.querySelector('.admin-list-panel');
        if (listPanel && newListContent) {
            listPanel.innerHTML = newListContent.innerHTML;
        } else if (listPanel) {
            listPanel.innerHTML = html;
        }

        // Обновляем форму, если есть
        const formPanel = document.querySelector('.admin-form-panel');
        const newFormContent = doc.querySelector('.admin-form-panel');
        if (formPanel && newFormContent) {
            formPanel.innerHTML = newFormContent.innerHTML;
        }

        // Update URL in browser
        window.history.pushState({}, '', url);

        // Re-initialize listeners for the new content
        initSPA();

        // Update active state in sidebar
        const urlParams = new URLSearchParams(url.split('?')[1]);
        const section = urlParams.get('section') || 'products';
        document.querySelectorAll('.admin-section-link').forEach(link => {
            const linkUrl = new URL(link.href, window.location.origin);
            const linkSection = linkUrl.searchParams.get('section') || 'products';
            link.classList.toggle('active', linkSection === section);
        });
    } catch (error) {
        console.error('Error loading section:', error);
        window.location.href = url; // Fallback to full reload
    }
}

async function loadEntry(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Network response was not ok');

        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Update both list and form panels
        const listPanel = document.querySelector('.admin-list-panel');
        const newListContent = doc.querySelector('.admin-list-panel');
        if (listPanel && newListContent) {
            listPanel.innerHTML = newListContent.innerHTML;
        }

        const formPanel = document.querySelector('.admin-form-panel');
        const newFormContent = doc.querySelector('.admin-form-panel');
        if (formPanel && newFormContent) {
            formPanel.innerHTML = newFormContent.innerHTML;
        }

        window.history.pushState({}, '', url);
        initSPA();
    } catch (error) {
        console.error('Error loading entry:', error);
        window.location.href = url;
    }
}

async function submitForm(form) {
    // Дополнительная проверка
    if (!form || form.tagName !== 'FORM') {
        console.error('submitForm called with invalid form element:', form);
        return;
    }

    const formData = new FormData(form);
    const url = form.getAttribute('action');

    if (!url) {
        console.error('Form has no action attribute');
        return;
    }

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });

        if (response.redirected) {
            // Для SPA - загружаем секцию из URL редиректа
            const redirectUrl = new URL(response.url);
            const section = redirectUrl.searchParams.get('section') || 'products';
            await loadSection(`${redirectUrl.pathname}?section=${section}`);
        } else {
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Проверяем, есть ли сообщение об ошибке
            const errorMsg = doc.querySelector('.flash-message.error, .alert.error');
            const formPanel = document.querySelector('.admin-form-panel');

            if (errorMsg && formPanel) {
                // Показываем ошибку в форме
                const newFormContent = doc.querySelector('.admin-form-panel');
                if (newFormContent) {
                    formPanel.innerHTML = newFormContent.innerHTML;
                }
                showNotification(errorMsg.textContent, 'error');
            } else if (formPanel) {
                // Успех - перезагружаем список
                const currentUrl = new URL(window.location.href);
                const section = currentUrl.searchParams.get('section') || 'products';
                await loadSection(`${currentUrl.pathname}?section=${section}`);
            }
            initSPA();
        }
    } catch (error) {
        console.error('Error submitting form:', error);
        // Fallback - отправляем форму обычным способом
        form.submit();
    }
}

function showNotification(message, type = 'success') {
    // Удаляем старые уведомления
    const existingNotifications = document.querySelectorAll('.admin-notification');
    existingNotifications.forEach(n => n.remove());

    const notification = document.createElement('div');
    notification.className = `admin-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${escapeHtml(message)}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;

    const workspace = document.querySelector('.admin-workspace');
    if (workspace) {
        workspace.prepend(notification);
    } else {
        document.body.prepend(notification);
    }

    const closeBtn = notification.querySelector('.notification-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => notification.remove());
    }

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function filterTable(tableClass, query) {
    const rows = document.querySelectorAll(`.${tableClass} tbody tr`);
    const q = query.toLowerCase();
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(q) ? '' : 'none';
    });
}

// Global filter function for the search input
window.filterTable = filterTable;