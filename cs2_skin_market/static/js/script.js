document.getElementById('recharge-button').addEventListener('click', function() {
    document.getElementById('recharge-modal').style.display = 'flex';
});

// Close popup
function closeModal() {
    document.getElementById('recharge-modal').style.display = 'none';
}

// Recharge submission logic
function submitRecharge() {
    const amount = document.getElementById('rechargeAmount').value;
    if (!amount || isNaN(amount) || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }

    const data = {
        amount: parseFloat(amount)
    };

    // Send data to backend
    fetch('/accounts/recharge/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Django CSRF protection
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Recharge successful!');
            closeModal();
            // Refresh the page to update balance
            location.reload();
        } else {
            alert('Recharge failed: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during recharge');
    });
}

// Get CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
