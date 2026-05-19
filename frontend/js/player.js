// Player search functionality (to be implemented with backend)
const searchBtn = document.getElementById('searchPlayerBtn');
const playerTagInput = document.getElementById('playerTag');
const playerResult = document.getElementById('playerResult');

searchBtn.addEventListener('click', async () => {
    let tag = playerTagInput.value.trim();
    if (!tag) {
        playerResult.innerHTML = '<div class="player-card">Please enter a player tag</div>';
        return;
    }
    
    // Remove # if present and add it back properly for API
    tag = tag.replace('#', '');
    
    playerResult.innerHTML = '<div class="loading">Searching for player...</div>';
    
    // TODO: Connect to backend endpoint when ready
    // For now, show placeholder
    setTimeout(() => {
        playerResult.innerHTML = `
            <div class="player-card">
                <h2 class="player-name">Player: ${tag}</h2>
                <p>Player search will be available once the backend endpoint is implemented.</p>
                <p>Check back soon!</p>
            </div>
        `;
    }, 500);
});

playerTagInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchBtn.click();
    }
});