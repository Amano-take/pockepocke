document.addEventListener('DOMContentLoaded', () => {
    // クライアントIDの確認と生成
    let clientId = document.cookie.split('; ').find(row => row.startsWith('client_id='));
    if (!clientId) {
        clientId = 'client_' + Math.random().toString(36).substr(2, 9);
        const expires = new Date();
        expires.setTime(expires.getTime() + 7 * 24 * 60 * 60 * 1000); // 7日間有効
        document.cookie = `client_id=${clientId};expires=${expires.toUTCString()};path=/`;
        console.log('新しいクライアントIDを生成しました:', clientId);
    } else {
        console.log('既存のクライアントID:', clientId.split('=')[1]);
    }

    // デッキ一覧を取得して表示
    fetchDecks();

    // 新しいデッキ作成ボタンのイベントリスナー
    document.getElementById('create-deck-button').addEventListener('click', () => {
        window.location.href = '/deck-builder';
    });

    // 戻るボタンのイベントリスナー
    document.getElementById('back-button').addEventListener('click', () => {
        window.location.href = '/';
    });
});

async function fetchDecks() {
    try {
        console.log('デッキ一覧を取得中...');
        const response = await fetch('/api/decks');
        console.log('レスポンスステータス:', response.status);
        if (!response.ok) {
            const errorData = await response.json();
            console.error('エラーレスポンス:', errorData);
            throw new Error('デッキ一覧の取得に失敗しました');
        }
        const decks = await response.json();
        console.log('取得したデッキ:', decks);
        displayDecks(decks);
    } catch (error) {
        console.error('デッキ一覧の取得に失敗しました:', error);
        showMessage('デッキ一覧の取得に失敗しました。もう一度お試しください。', true);
    }
}

function displayDecks(decks) {
    const container = document.getElementById('decks-container');
    container.innerHTML = '';

    if (decks.length === 0) {
        container.innerHTML = '<p class="no-decks">デッキがありません。新しいデッキを作成してください。</p>';
        return;
    }

    decks.forEach(deck => {
        const deckElement = createDeckElement(deck);
        container.appendChild(deckElement);
    });
}

function createDeckElement(deck) {
    const deckElement = document.createElement('div');
    deckElement.className = 'deck-item';

    const ratingColor = getRatingColor(deck.rating);

    deckElement.innerHTML = `
        <div class="deck-header">
            <h3>${deck.name}</h3>
            <div class="deck-rating" style="color: ${ratingColor}">
                レーティング: ${Math.round(deck.rating)}
            </div>
            <div class="deck-stats">
                戦績: ${deck.wins}勝${deck.games_played - deck.wins}敗
            </div>
        </div>
        <div class="deck-actions">
            <button onclick="useDeck(${deck.id})">使用</button>
            <button onclick="deleteDeck(${deck.id})">削除</button>
        </div>
    `;

    return deckElement;
}

function getEnergyTypeJa(energyType) {
    const energyMapping = {
        'grass': 'くさ',
        'fire': 'ほのお',
        'water': 'みず',
        'lightning': 'でんき',
        'psychic': 'エスパー',
        'fighting': 'かくとう'
    };
    return energyMapping[energyType] || energyType;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return `${date.getFullYear()}/${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getDate().toString().padStart(2, '0')}`;
}

function calculateDisplayScore(rating) {
    const minRating = 1000;
    const maxRating = 2000;
    const normalized = (rating - minRating) / (maxRating - minRating);
    return Math.max(0, Math.min(100, normalized * 100));
}

function getRatingColor(score) {
    // 赤から青のグラデーション
    const red = Math.min(255, Math.round((100 - score) * 2.55));
    const blue = Math.min(255, Math.round(score * 2.55));
    return `rgb(${red}, 0, ${blue})`;
}

async function editDeck(deckId) {
    window.location.href = `/deck-builder?deck_id=${deckId}`;
}

async function useDeck(deckId) {
    try {
        const response = await fetch(`/api/decks/${deckId}/use`, {
            method: 'POST'
        });

        if (response.ok) {
            window.location.href = '/'; // メイン画面に戻る
        } else {
            const error = await response.json();
            showMessage(`デッキの使用に失敗しました：${error.error}`, true);
        }
    } catch (error) {
        console.error('デッキの使用中にエラーが発生しました:', error);
        showMessage('デッキの使用中にエラーが発生しました。もう一度お試しください。', true);
    }
}

async function deleteDeck(deckId) {
    if (!confirm('このデッキを削除してもよろしいですか？')) {
        return;
    }

    try {
        const response = await fetch(`/api/decks/${deckId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            fetchDecks(); // デッキ一覧を再取得
            showMessage('デッキを削除しました。', false);
        } else {
            const error = await response.json();
            showMessage(`デッキの削除に失敗しました：${error.error}`, true);
        }
    } catch (error) {
        console.error('デッキの削除中にエラーが発生しました:', error);
        showMessage('デッキの削除中にエラーが発生しました。もう一度お試しください。', true);
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
