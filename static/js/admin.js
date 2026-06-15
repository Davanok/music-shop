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
            e.preventDefault();
            const url = row.getAttribute('data-href');
            loadEntry(url);
        });
    });

    // Handle forms
    document.querySelectorAll('.embedded-admin-form').forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            submitForm(form);
        });
    });
}

async function loadSection(url) {
    try {
        const response = await fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!response.ok) throw new Error('Network response was not ok');
        
        const html = await response.text();
        document.querySelector('.admin-list-panel').innerHTML = html;
        
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
        document.querySelector('.admin-list-panel').innerHTML = doc.querySelector('.admin-list-panel').innerHTML;
        document.querySelector('.admin-form-panel').innerHTML = doc.querySelector('.admin-form-panel').innerHTML;
        
        window.history.pushState({}, '', url);
        initSPA();
    } catch (error) {
        console.error('Error loading entry:', error);
        window.location.href = url;
    }
}

async function submitForm(form) {
    const formData = new FormData(form);
    const url = form.getAttribute('action');
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        if (response.redirected) {
            // Для SPA - загружаем секцию из URL редиректа
            const redirectUrl = new URL(response.url);
            const section = redirectUrl.searchParams.get('section') || 'products';
            loadSection(`${redirectUrl.pathname}?section=${section}`);
        } else {
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Проверяем, есть ли сообщение об ошибке
            const errorMsg = doc.querySelector('.flash-message.error, .alert.error');
            if (errorMsg) {
                // Показываем ошибку в форме
                const formPanel = document.querySelector('.admin-form-panel');
                if (formPanel) {
                    formPanel.innerHTML = doc.querySelector('.admin-form-panel').innerHTML;
                }
            } else {
                // Успех - перезагружаем список
                const currentUrl = new URL(window.location.href);
                const section = currentUrl.searchParams.get('section') || 'products';
                loadSection(`${currentUrl.pathname}?section=${section}`);
            }
            initSPA();
        }
    } catch (error) {
        console.error('Error submitting form:', error);
        form.submit(); // Fallback
    }
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

// Добавьте эту функцию для отображения уведомлений
function showNotification(message, type = 'success') {
    const existingNotifications = document.querySelectorAll('.admin-notification');
    existingNotifications.forEach(n => n.remove());

    const notification = document.createElement('div');
    notification.className = `admin-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;

    document.querySelector('.admin-workspace').prepend(notification);

    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Обновите loadSection для обработки флеш-сообщений
async function loadSection(url) {
    try {
        const response = await fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!response.ok) throw new Error('Network response was not ok');

        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        document.querySelector('.admin-list-panel').innerHTML = doc.querySelector('.admin-list-panel').innerHTML;

        // Обновляем форму, если есть
        const newFormPanel = doc.querySelector('.admin-form-panel');
        if (newFormPanel) {
            document.querySelector('.admin-form-panel').innerHTML = newFormPanel.innerHTML;
        } else {
            // Если форма не загрузилась, показываем пустое состояние
            document.querySelector('.admin-form-panel').innerHTML = `
                <div class="empty-state admin-form-empty">
                    <h2>Форма записи</h2>
                    <p>Выберите запись в таблице или нажмите «Добавить», чтобы открыть форму справа.</p>
                </div>
            `;
        }

        // Проверяем флеш-сообщения
        const flashMessage = doc.querySelector('.flash-message, .alert');
        if (flashMessage) {
            const message = flashMessage.textContent;
            const type = flashMessage.classList.contains('success') ? 'success' : 'error';
            showNotification(message, type);
        }

        window.history.pushState({}, '', url);
        initSPA();

        // Обновляем активное состояние в sidebar
        const urlParams = new URLSearchParams(url.split('?')[1]);
        const section = urlParams.get('section') || 'products';
        document.querySelectorAll('.admin-section-link').forEach(link => {
            const linkUrl = new URL(link.href, window.location.origin);
            const linkSection = linkUrl.searchParams.get('section') || 'products';
            link.classList.toggle('active', linkSection === section);
        });
    } catch (error) {
        console.error('Error loading section:', error);
        window.location.href = url;
    }
}