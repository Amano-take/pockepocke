document.addEventListener('DOMContentLoaded', () => {
    const matchButton = document.getElementById('match-button');
    const deckButton = document.getElementById('deck-button');
    const deckListButton = document.getElementById('deck-list-button');

    matchButton.addEventListener('click', () => {
        window.location.href = '/play';
        console.log('マッチングページに遷移します');
    });

    deckButton.addEventListener('click', () => {
        window.location.href = '/deck-builder';
    });

    deckListButton.addEventListener('click', () => {
        window.location.href = '/decks';

    });
});
