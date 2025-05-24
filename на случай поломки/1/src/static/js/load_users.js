document.getElementById('loadUsersForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const count = document.getElementById('count').value;
    
    try {
        const response = await fetch('/load-users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `count=${count}`
        });
        
        if (response.ok) {
            const result = await response.json();
            alert(result.message);
            window.location.reload();
        } else {
            const error = await response.json();
            alert(error.detail || 'Error loading users');
        }
    } catch (err) {
        alert('Network error: ' + err.message);
    }
});