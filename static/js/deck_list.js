document.addEventListener('DOMContentLoaded', async () => {
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

    // カード一覧を取得
    try {
        const response = await fetch('/api/cards', {
            cache: 'no-store',  // キャッシュを使用しない
            headers: {
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            }
        });
        if (response.ok) {
            const cards = await response.json();
            // カードを種類ごとに分類
            window.POKEMON_CARDS = cards.filter(card => card.category === 'pokemon').map(card => card.name);
            window.GOODS_CARDS = cards.filter(card => card.category === 'goods').map(card => card.name);
            window.TRAINER_CARDS = cards.filter(card => card.category === 'trainer').map(card => card.name);
        }
    } catch (error) {
        console.error('カード一覧の取得に失敗しました:', error);
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
        const response = await fetch('/api/decks', {
            cache: 'no-store',  // キャッシュを使用しない
            headers: {
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            }
        });
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
    const isOwnDeck = deck.client_id === getCookie('client_id');

    deckElement.innerHTML = `
        <div class="deck-header">
            <h3>${deck.name}</h3>
            <div class="deck-creator">
                作成者: ${deck.client_id.substring(0, 8)}...
            </div>
            <div class="deck-rating" style="color: ${ratingColor}">
                レーティング: ${Math.round(deck.rating)}
            </div>
            <div class="deck-stats">
                戦績: ${deck.wins}勝${deck.games_played - deck.wins}敗
            </div>
        </div>
        <div class="deck-actions">
            <button onclick="showDeckDetails(${JSON.stringify(deck).replace(/"/g, '&quot;')})">詳細</button>
            <button onclick="useDeck(${deck.id})">使用</button>
            ${isOwnDeck ? `<button onclick="deleteDeck(${deck.id})">削除</button>` : ''}
        </div>
    `;

    return deckElement;
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
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
            method: 'POST',
            headers: {
                'Cache-Control': 'no-cache'
            }
        });

        if (response.ok) {
            // マッチング画面に遷移
            window.location.href = '/play';
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

function showDeckDetails(deck) {
    // モーダルを作成
    const modal = document.createElement('div');
    modal.className = 'modal';

    // カードをカテゴリごとに分類
    const cardsByCategory = categorizeCards(deck.cards);

    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>${deck.name}</h2>
                <span class="close">&times;</span>
            </div>
            <div class="modal-body">
                <div class="deck-info">
                    <p>エナジータイプ: ${getEnergyTypeJa(deck.energy)}</p>
                    <p>総カード枚数: ${deck.cards.length}枚</p>
                </div>
                <div class="cards-section">
                    <h3>ポケモン (${cardsByCategory.pokemon.length}枚)</h3>
                    <ul>${cardsByCategory.pokemon.map(card => `<li>${card}</li>`).join('')}</ul>

                    <h3>グッズ (${cardsByCategory.goods.length}枚)</h3>
                    <ul>${cardsByCategory.goods.map(card => `<li>${card}</li>`).join('')}</ul>

                    <h3>トレーナー (${cardsByCategory.trainer.length}枚)</h3>
                    <ul>${cardsByCategory.trainer.map(card => `<li>${card}</li>`).join('')}</ul>
                </div>
            </div>
        </div>
    `;

    // モーダルを閉じる処理
    const closeBtn = modal.querySelector('.close');
    closeBtn.onclick = () => modal.remove();

    // モーダル外をクリックしても閉じる
    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    };

    document.body.appendChild(modal);
}

function categorizeCards(cards) {
    const categories = {
        pokemon: [],
        goods: [],
        trainer: []
    };

    // カードの出現回数をカウント
    const cardCounts = {};
    cards.forEach(card => {
        cardCounts[card] = (cardCounts[card] || 0) + 1;
    });

    // 重複を除外してカードを分類
    [...new Set(cards)].forEach(card => {
        const count = cardCounts[card];
        const cardWithCount = count > 1 ? `${card} ×${count}` : card;

        if (window.POKEMON_CARDS.includes(card)) {
            categories.pokemon.push(cardWithCount);
        } else if (window.GOODS_CARDS.includes(card)) {
            categories.goods.push(cardWithCount);
        } else if (window.TRAINER_CARDS.includes(card)) {
            categories.trainer.push(cardWithCount);
        }
    });

    return categories;
}
