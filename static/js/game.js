document.addEventListener('DOMContentLoaded', () => {
    const gameId = window.location.pathname.split('/').pop();
    const clientId = getCookie('client_id');

    if (!clientId) {
        window.location.href = '/';
        return;
    }

    // WebSocket接続
    const ws = new WebSocket(`ws://${window.location.host}/ws/${clientId}`);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleGameState(data);
    };

    ws.onerror = (error) => {
        console.error('WebSocket エラー:', error);
        showMessage('接続エラーが発生しました', true);
    };

    ws.onclose = () => {
        console.log('WebSocket 接続が閉じられました');
        showMessage('接続が切断されました', true);
    };
});

function handleGameState(data) {
    if (data.type === 'state_update') {
        updateGameState(data.state);
    } else if (data.type === 'action_request') {
        handleActionRequest(data.data.selections);
    }
}

function updateGameState(state) {
    // プレイヤーフィールドの更新
    updatePlayerField(state.your_info);
    // 相手フィールドの更新
    updateOpponentField(state.opponent_info);
}

function updatePlayerField(playerInfo) {
    const playerField = document.getElementById('player-field');
    updateField(playerField, playerInfo);
}

function updateOpponentField(opponentInfo) {
    const opponentField = document.getElementById('opponent-field');
    updateField(opponentField, opponentInfo);
}

function updateField(fieldElement, info) {
    // アクティブポケモンの更新
    const activeArea = fieldElement.querySelector('.active-area');
    activeArea.innerHTML = '';
    if (info.active_pokemon) {
        activeArea.appendChild(createPokemonElement(info.active_pokemon));
    }

    // ベンチの更新
    const benchArea = fieldElement.querySelector('.bench-area');
    benchArea.innerHTML = '';
    info.bench.forEach(pokemon => {
        benchArea.appendChild(createPokemonElement(pokemon));
    });

    // 手札の更新（枚数のみ表示）
    const handArea = fieldElement.querySelector('.hand-area');
    handArea.textContent = `手札: ${info.hand_size}枚`;
}

function createPokemonElement(pokemon) {
    const element = document.createElement('div');
    element.className = 'pokemon-card';
    element.innerHTML = `
        <div class="pokemon-name">${pokemon.name}</div>
        <div class="pokemon-hp">HP: ${pokemon.hp}/${pokemon.max_hp}</div>
        <div class="pokemon-energy">
            ${pokemon.energies.map(energy => `<span class="energy ${energy}">${energy}</span>`).join('')}
        </div>
    `;
    return element;
}

function handleActionRequest(selections) {
    const messageArea = document.getElementById('game-message');
    messageArea.innerHTML = '';

    const selectionContainer = document.createElement('div');
    selectionContainer.className = 'selection-container';

    Object.entries(selections).forEach(([index, text]) => {
        const button = document.createElement('button');
        button.className = 'selection-button';
        button.textContent = text;
        button.onclick = () => sendActionResponse(parseInt(index));
        selectionContainer.appendChild(button);
    });

    messageArea.appendChild(selectionContainer);
}

function sendActionResponse(selectedIndex) {
    const ws = new WebSocket(`ws://${window.location.host}/ws/${getCookie('client_id')}`);
    ws.onopen = () => {
        ws.send(JSON.stringify({
            type: 'action_response',
            selected_index: selectedIndex
        }));
    };
}

function showMessage(message, isError = false) {
    const messageArea = document.getElementById('game-message');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${isError ? 'error' : 'info'}`;
    messageElement.textContent = message;
    messageArea.appendChild(messageElement);

    setTimeout(() => {
        messageElement.remove();
    }, 5000);
}

// Cookie取得用のユーティリティ関数
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}
