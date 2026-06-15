document.addEventListener('DOMContentLoaded', () => {
    initSPA();
});

function initSPA() {
    // Handle navigation links
    document.querySelectorAll('.admin-section-link, [data-spa-link]').forEach(link => {
        link.removeEventListener('click', handleSectionClick);
        link.addEventListener('click', handleSectionClick);
    });

    // Handle table row clicks
    document.querySelectorAll('[data-spa-row]').forEach(row => {
        row.removeEventListener('click', handleRowClick);
        row.addEventListener('click', handleRowClick);
    });

    // Handle forms
    document.querySelectorAll('.embedded-admin-form').forEach(form => {
        form.removeEventListener('submit', handleFormSubmit);
        form.addEventListener('submit', handleFormSubmit);
    });
}

function handleSectionClick(e) {
    e.preventDefault();
    const url = this.getAttribute('href');
    loadSection(url);
}

function handleRowClick(e) {
    // Don't trigger if clicking on a button or link inside the row
    if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' ||
        e.target.closest('button') || e.target.closest('a')) {
        return;
    }
    e.preventDefault();
    const url = this.getAttribute('data-href');
    if (url) {
        loadEntry(url);
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    await submitForm(this);
}

async function loadSection(url) {
    try {
        showLoading();

        const response = await fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-SPA-Request': 'section'
            }
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Update list panel
        const newContent = doc.querySelector('#admin-list-panel');
        if (newContent) {
            document.querySelector('#admin-list-panel').innerHTML = newContent.innerHTML;
        }

        // Clear form panel
        const emptyForm = doc.querySelector('#admin-form-panel');
        if (emptyForm) {
            document.querySelector('#admin-form-panel').innerHTML = emptyForm.innerHTML;
        }

        // Update URL
        window.history.pushState({}, '', url);

        // Update active state in sidebar
        const urlParams = new URLSearchParams(url.split('?')[1]);
        const section = urlParams.get('section') || 'products';
        document.querySelectorAll('.admin-section-link').forEach(link => {
            const linkUrl = new URL(link.href, window.location.origin);
            const linkSection = linkUrl.searchParams.get('section') || 'products';
            link.classList.toggle('active', linkSection === section);
        });

        initSPA();
        hideLoading();
    } catch (error) {
        console.error('Error loading section:', error);
        hideLoading();
        window.location.href = url;
    }
}

async function loadEntry(url) {
    try {
        showLoading();

        const response = await fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-SPA-Request': 'entry'
            }
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Update list panel
        const newListPanel = doc.querySelector('#admin-list-panel');
        if (newListPanel) {
            document.querySelector('#admin-list-panel').innerHTML = newListPanel.innerHTML;
        }

        // Update form panel
        const newFormPanel = doc.querySelector('#admin-form-panel');
        if (newFormPanel) {
            document.querySelector('#admin-form-panel').innerHTML = newFormPanel.innerHTML;
        }

        window.history.pushState({}, '', url);
        initSPA();
        hideLoading();
    } catch (error) {
        console.error('Error loading entry:', error);
        hideLoading();
        window.location.href = url;
    }
}

async function submitForm(form) {
    const formData = new FormData(form);
    const url = form.getAttribute('action');

    showLoading();

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();

            // Update panels with returned HTML
            if (data.listPanel) {
                document.querySelector('#admin-list-panel').innerHTML = data.listPanel;
            }
            if (data.formPanel) {
                document.querySelector('#admin-form-panel').innerHTML = data.formPanel;
            }

            // Show flash message
            if (data.message) {
                showFlashMessage(data.message, data.success ? 'success' : 'error');
            }

            initSPA();
        } else if (response.redirected) {
            await loadSection(response.url);
        } else {
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Update form panel
            const newFormPanel = doc.querySelector('#admin-form-panel');
            if (newFormPanel) {
                document.querySelector('#admin-form-panel').innerHTML = newFormPanel.innerHTML;
            }

            // Update list panel if it came in response
            const newListPanel = doc.querySelector('#admin-list-panel');
            if (newListPanel) {
                document.querySelector('#admin-list-panel').innerHTML = newListPanel.innerHTML;
            }

            initSPA();
        }

        hideLoading();
    } catch (error) {
        console.error('Error submitting form:', error);
        hideLoading();
        form.submit();
    }
}

function showFlashMessage(message, type) {
    // Create flash message element
    const flashDiv = document.createElement('div');
    flashDiv.className = `flash-message ${type}`;
    flashDiv.innerHTML = `
        <span>${message}</span>
        <button class="flash-close">&times;</button>
    `;

    // Add to page
    const container = document.querySelector('.admin-page');
    if (container) {
        container.insertBefore(flashDiv, container.firstChild);

        // Auto remove after 3 seconds
        setTimeout(() => {
            flashDiv.remove();
        }, 3000);

        // Close button
        flashDiv.querySelector('.flash-close').addEventListener('click', () => {
            flashDiv.remove();
        });
    }
}

function showLoading() {
    const panels = document.querySelectorAll('.admin-list-panel, .admin-form-panel');
    panels.forEach(panel => {
        panel.style.opacity = '0.5';
        panel.style.pointerEvents = 'none';
    });
}

function hideLoading() {
    const panels = document.querySelectorAll('.admin-list-panel, .admin-form-panel');
    panels.forEach(panel => {
        panel.style.opacity = '';
        panel.style.pointerEvents = '';
    });
}

window.filterTable = function(tableClass, query) {
    const table = document.querySelector(`.${tableClass}`);
    if (!table) return;

    const rows = table.querySelectorAll('tbody tr');
    const q = query.toLowerCase();

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(q) ? '' : 'none';
    });
};

window.addEventListener('popstate', () => {
    loadSection(window.location.href);
});