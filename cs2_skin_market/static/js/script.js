document.getElementById('recharge-button').addEventListener('click', function() {
    document.getElementById('recharge-modal').style.display = 'flex';
});

// 关闭弹窗
document.querySelector('.close-modal').addEventListener('click', function() {
    document.getElementById('recharge-modal').style.display = 'none';
});

// 充值提交逻辑
document.getElementById('recharge-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const cardNumber = document.getElementById('card-number').value;
    const amount = parseFloat(document.getElementById('amount').value);

    if (!cardNumber || amount <= 0) {
        alert("Please enter a valid card number and amount.");
        return;
    }

    // 发送数据到后端
    fetch('/recharge/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Django CSRF 保护
        },
        body: JSON.stringify({ card_number: cardNumber, amount: amount })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('wallet-balance').textContent = `¥${data.new_balance.toFixed(2)}`;
            alert(`Recharged ¥${amount} successfully!`);
            document.getElementById('recharge-modal').style.display = 'none';
        } else {
            alert(data.error || "Recharge failed.");
        }
    })
    .catch(error => console.error('Error:', error));
});

// 获取 CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
