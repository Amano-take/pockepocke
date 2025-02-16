document.addEventListener('DOMContentLoaded', () => {
    const deckButton = document.getElementById('deck-button');
    const deckListButton = document.getElementById('deck-list-button');

    deckButton.addEventListener('click', () => {
        window.location.href = '/deck-builder';
    });

    deckListButton.addEventListener('click', () => {
        window.location.href = '/decks';
    });
});
