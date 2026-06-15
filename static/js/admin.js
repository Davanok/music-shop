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
            loadSection(response.url);
        } else {
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            document.querySelector('.admin-form-panel').innerHTML = doc.querySelector('.admin-form-panel').innerHTML;
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

