document.addEventListener('DOMContentLoaded', () => {
    const matchButton = document.getElementById('match-button');
    const deckButton = document.getElementById('deck-button');
    const deckListButton = document.getElementById('deck-list-button');

    matchButton.addEventListener('click', () => {
        // WebSocketの接続を開始
        const clientId = generateClientId();
        const ws = new WebSocket(`ws://${window.location.host}/ws/${clientId}`);

        ws.onopen = () => {
            console.log('WebSocket接続が確立されました');
            // マッチング要求を送信
            ws.send(JSON.stringify({
                type: 'match_request'
            }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };

        ws.onerror = (error) => {
            console.error('WebSocket エラー:', error);
            alert('接続エラーが発生しました');
        };

        ws.onclose = () => {
            console.log('WebSocket 接続が閉じられました');
        };
    });

    deckButton.addEventListener('click', () => {
        window.location.href = '/deck-builder';
    });

    deckListButton.addEventListener('click', () => {
        window.location.href = '/decks';
    });

    // クライアントIDをCookieに保存
    function generateClientId() {
        let clientId = getCookie('client_id');
        if (!clientId) {
            clientId = 'client_' + Math.random().toString(36).substr(2, 9);
            setCookie('client_id', clientId, 7); // 7日間有効
        }
        return clientId;
    }
});

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'waiting':
            showMessage(data.message);
            break;
        case 'game_start':
            console.log('ゲームが開始されました');
            window.location.href = `/game/${data.game_id}`;
            break;
        case 'error':
            showMessage(data.message, true);
            break;
        default:
            console.log('未知のメッセージタイプ:', data.type);
    }
}

function showMessage(message, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isError ? 'error' : 'info'}`;
    messageDiv.textContent = message;

    const container = document.querySelector('.container');
    container.insertBefore(messageDiv, container.firstChild);

    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Cookie操作のユーティリティ関数
function setCookie(name, value, days) {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}
