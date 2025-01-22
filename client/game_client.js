// WebSocket接続の設定
let ws = null;
const clientId = generateUUID();

// ゲームの状態
let gameState = null;

// 初期化
function init() {
    connectWebSocket();
}

// WebSocket接続
function connectWebSocket() {
    ws = new WebSocket(`ws://localhost:8080/ws/${clientId}`);

    ws.onopen = () => {
        updateStatus('サーバーに接続しました');
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleMessage(message);
    };

    ws.onclose = () => {
        updateStatus('サーバーとの接続が切断されました');
    };

    ws.onerror = (error) => {
        updateStatus('エラーが発生しました: ' + error.message);
    };
}

// メッセージ処理
function handleMessage(message) {
    switch (message.type) {
        case 'waiting':
            updateStatus(message.message);
            break;
        case 'game_start':
            updateStatus('ゲームが開始されました');
            break;
        case 'state_update':
            updateGameState(message.state);
            break;
        case 'action_request':
            showActionButtons(message.data.selections);
            break;
    }
}

// ゲーム状態の更新
function updateGameState(state) {
    gameState = state;

    // プレイヤー情報の更新
    const playerDetails = document.getElementById('player-details');
    playerDetails.innerHTML = `
        <p>手札: ${state.your_info.hand_size}枚</p>
        <p>デッキ残り: ${state.your_info.deck_size}枚</p>
        ${state.your_info.active_pokemon ?
            `<p>場のポケモン: ${state.your_info.active_pokemon.name}
             (HP: ${state.your_info.active_pokemon.hp}/${state.your_info.active_pokemon.max_hp})</p>
             <p>エネルギー: ${state.your_info.active_pokemon.energies.join(', ')}</p>`
            : '<p>場のポケモン: なし</p>'}
    `;

    // 対戦相手情報の更新
    const opponentDetails = document.getElementById('opponent-details');
    opponentDetails.innerHTML = `
        <p>手札: ${state.opponent_info.hand_size}枚</p>
        <p>デッキ残り: ${state.opponent_info.deck_size}枚</p>
        ${state.opponent_info.active_pokemon ?
            `<p>場のポケモン: ${state.opponent_info.active_pokemon.name}
             (HP: ${state.opponent_info.active_pokemon.hp}/${state.opponent_info.active_pokemon.max_hp})</p>
             <p>エネルギー: ${state.opponent_info.active_pokemon.energies.join(', ')}</p>`
            : '<p>場のポケモン: なし</p>'}
    `;

    // ターン情報の更新
    updateStatus(`ターン ${state.turn} - アクティブプレイヤー: ${state.active_player}`);
}

// アクションボタンの表示
function showActionButtons(selections) {
    const actionArea = document.getElementById('action-area');
    actionArea.innerHTML = '';

    Object.entries(selections).forEach(([index, description]) => {
        const button = document.createElement('button');
        button.className = 'action-button';
        button.textContent = description;
        button.onclick = () => sendAction(parseInt(index));
        actionArea.appendChild(button);
    });
}

// アクションの送信
function sendAction(selectedIndex) {
    const message = {
        type: 'action_response',
        data: { selected_index: selectedIndex }
    };
    ws.send(JSON.stringify(message));
}

// ステータス表示の更新
function updateStatus(message) {
    const statusElement = document.getElementById('status');
    statusElement.textContent = message;
}

// UUID生成
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0,
            v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// 初期化
init();
