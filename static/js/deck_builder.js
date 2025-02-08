let selectedCards = [];
const MAX_DECK_SIZE = 20;
const MAX_SAME_CARD = 2;

document.addEventListener('DOMContentLoaded', () => {
    // カード一覧を取得して表示
    fetchAvailableCards();

    // エナジー選択の変更を監視
    document.getElementById('energy-type').addEventListener('change', validateDeck);

    // 次へボタンのクリックイベント
    document.getElementById('next-button').addEventListener('click', saveDeck);
});

async function fetchAvailableCards() {
    try {
        const response = await fetch('/api/cards');
        const cards = await response.json();
        displayAvailableCards(cards);
    } catch (error) {
        console.error('カード一覧の取得に失敗しました:', error);
    }
}

function displayAvailableCards(cards) {
    const container = document.getElementById('available-cards');
    container.innerHTML = '';

    cards.forEach(card => {
        const cardElement = createCardElement(card);
        container.appendChild(cardElement);
    });
}

function createCardElement(card, count = 0) {
    const div = document.createElement('div');
    div.className = 'card';
    div.dataset.cardId = card.id;
    div.dataset.cardType = card.type;

    let cardContent = `
        <h3>${card.name}${count > 0 ? ` *${count}` : ''}</h3>
        <p>カテゴリー: ${
            card.category === 'pokemon'
                ? (card.type === 'basic_pokemon' ? '種ポケモン' : '進化ポケモン')
                : (card.category === 'goods' ? 'グッズ' : 'トレーナー')
        }</p>
    `;

    if (card.category === 'pokemon') {
        cardContent += `
            <p>HP: ${card.hp}</p>
            ${card.pokemon_type ? `<p>タイプ：${card.pokemon_type}タイプ</p>` : ''}
        `;
    }

    div.innerHTML = cardContent;
    div.addEventListener('click', () => handleCardClick(card, div));
    return div;
}

function handleCardClick(card, element) {
    const cardCount = selectedCards.filter(c => c.name === card.name).length;

    if (element.parentElement.id === 'selected-cards') {
        // 現在のデッキフィールドのカードをクリックした場合、1枚減らす
        const index = selectedCards.findIndex(c => c.name === card.name);
        if (index !== -1) {
            selectedCards.splice(index, 1);
        }
    } else {
        // カード一覧からクリックした場合
        if (cardCount >= MAX_SAME_CARD) {
            alert(`同じカードは${MAX_SAME_CARD}枚までしか入れられません。`);
            return;
        }
        if (selectedCards.length >= MAX_DECK_SIZE) {
            alert(`デッキは${MAX_DECK_SIZE}枚までです。`);
            return;
        }
        selectedCards.push(card);
    }

    updateDeckDisplay();
    validateDeck();
}

function updateDeckDisplay() {
    const container = document.getElementById('selected-cards');
    const deckCount = document.getElementById('deck-count');

    container.innerHTML = '';

    // カードをグループ化して表示
    const cardGroups = {};
    selectedCards.forEach(card => {
        if (!cardGroups[card.name]) {
            cardGroups[card.name] = {
                card: card,
                count: 1
            };
        } else {
            cardGroups[card.name].count++;
        }
    });

    Object.values(cardGroups).forEach(group => {
        const cardElement = createCardElement(group.card, group.count);
        cardElement.classList.add('selected');
        container.appendChild(cardElement);
    });

    deckCount.textContent = selectedCards.length;
}

function validateDeck() {
    const nextButton = document.getElementById('next-button');
    const energyType = document.getElementById('energy-type').value;

    // デッキのバリデーション
    const hasBasicPokemon = selectedCards.some(card => card.type === 'basic_pokemon');
    const isDeckSizeValid = selectedCards.length === MAX_DECK_SIZE;

    nextButton.disabled = !(hasBasicPokemon && isDeckSizeValid && energyType);

    if (nextButton.disabled) {
        nextButton.title = getValidationMessage(hasBasicPokemon, isDeckSizeValid, energyType);
    } else {
        nextButton.title = '';
    }
}

function getValidationMessage(hasBasicPokemon, isDeckSizeValid, energyType) {
    const messages = [];
    if (!hasBasicPokemon) messages.push('種ポケモンが必要です');
    if (!isDeckSizeValid) messages.push(`デッキは${MAX_DECK_SIZE}枚である必要があります`);
    if (!energyType) messages.push('エナジーを選択してください');
    return messages.join('\n');
}

async function saveDeck() {
    const energyType = document.getElementById('energy-type').value;
    const deckData = {
        cards: selectedCards.map(card => card.name),
        energy: energyType
    };

    try {
        const response = await fetch('/api/save-deck', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(deckData)
        });

        if (response.ok) {
            alert('デッキを保存しました！対戦を始めましょう！');
            window.location.href = '/'; // メイン画面に戻る
        } else {
            const error = await response.json();
            alert(`デッキを保存できません：${error.error}`);
        }
    } catch (error) {
        console.error('デッキの保存中にエラーが発生しました:', error);
        alert('デッキの保存中にエラーが発生しました。もう一度お試しください。');
    }
}
