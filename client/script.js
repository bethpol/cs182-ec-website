document.addEventListener('DOMContentLoaded', () => {
    const contentDiv = document.getElementById('content');
    const loadingP = document.getElementById('loading');

    fetch('data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            loadingP.style.display = 'none';
            // Simple display for now - can be enhanced later
            const pre = document.createElement('pre');
            pre.textContent = JSON.stringify(data, null, 2);
            contentDiv.appendChild(pre);
        })
        .catch(error => {
            console.error('Error loading data:', error);
            loadingP.textContent = 'Error loading data. Have you run the scraper?';
            loadingP.classList.add('error');
        });
});
