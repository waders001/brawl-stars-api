// API Configuration
const API_URL = 'http://localhost:8000';

// State
let currentPage = 1;
let currentLimit = 20;
let currentClass = '';
let currentRarity = '';
let currentSearch = '';
let totalBrawlers = 0;

// DOM Elements
const brawlersGrid = document.getElementById('brawlersGrid');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const pageInfo = document.getElementById('pageInfo');
const brawlerCount = document.getElementById('brawlerCount');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const resetBtn = document.getElementById('resetBtn');
const classFilter = document.getElementById('classFilter');
const rarityFilter = document.getElementById('rarityFilter');
const searchHint = document.getElementById('searchHint');

// Fetch brawlers from API
async function fetchBrawlers() {
    showLoading();
    
    try {
        // If searching, use search endpoint
        if (currentSearch && currentSearch.length >= 2) {
            const searchUrl = `${API_URL}/brawlers/search/?q=${encodeURIComponent(currentSearch)}&limit=100`;
            const response = await fetch(searchUrl);
            const data = await response.json();
            
            totalBrawlers = data.total;
            
            if (data.total === 0) {
                brawlerCount.textContent = `🔍 No brawlers found matching "${currentSearch}"`;
                searchHint.innerHTML = `💡 Try a different search term. Examples: "el", "spike", "crow", "shelly"`;
                searchHint.style.color = '#ffaa00';
            } else {
                brawlerCount.textContent = `🔍 Found ${data.total} brawler(s) matching "${currentSearch}"`;
                searchHint.innerHTML = `✨ Showing ${data.total} result(s) for "${currentSearch}"`;
                searchHint.style.color = '#2ecc71';
            }
            
            renderBrawlers(data.brawlers);
            updatePagination(data.total);
            return;
        }
        
        // Clear search hint when not searching
        searchHint.innerHTML = '';
        
        // Otherwise use regular endpoint with filters
        let url = `${API_URL}/brawlers/?limit=${currentLimit}&offset=${(currentPage - 1) * currentLimit}`;
        
        if (currentClass) {
            url += `&class_filter=${encodeURIComponent(currentClass)}`;
        }
        if (currentRarity) {
            url += `&rarity_filter=${encodeURIComponent(currentRarity)}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        totalBrawlers = data.total;
        
        // Update stats bar with distribution hint
        let rarityHint = '';
        if (currentRarity === 'Ultra-Legendary') rarityHint = ' 👑 Rarest of the rare!';
        else if (currentRarity === 'Legendary') rarityHint = ' ⭐ Extremely rare';
        else if (currentRarity === 'Mythic') rarityHint = ' 🔮 Very rare';
        
        brawlerCount.textContent = `📊 ${totalBrawlers} Brawlers Found${rarityHint}`;
        renderBrawlers(data.brawlers);
        updatePagination(data.total);
        
    } catch (error) {
        console.error('Error fetching brawlers:', error);
        brawlersGrid.innerHTML = '<div class="loading">❌ Error loading brawlers. Make sure the API is running at http://localhost:8000</div>';
        searchHint.innerHTML = '⚠️ Cannot connect to API. Make sure the backend is running.';
        searchHint.style.color = '#e74c3c';
    }
}

// Get rarity color
function getRarityColor(rarity) {
    const colors = {
        'Ultra-Legendary': '#ff1493',
        'Legendary': '#ff4500',
        'Mythic': '#9b59b6',
        'Epic': '#e74c3c',
        'Super Rare': '#3498db',
        'Rare': '#2ecc71',
        'Common': '#95a5a6',
        'Starting Brawler': '#f39c12',
        'Trophy Road': '#1abc9c'
    };
    return colors[rarity] || '#aaa';
}

// Render brawlers to grid
function renderBrawlers(brawlers) {
    if (!brawlers || brawlers.length === 0) {
        brawlersGrid.innerHTML = '<div class="loading">No brawlers found</div>';
        return;
    }
    
    brawlersGrid.innerHTML = brawlers.map(brawler => {
        const rarityColor = getRarityColor(brawler.rarity);
        const isUltraLegendary = brawler.rarity === 'Ultra-Legendary';
        
        // Format stats with better null handling
        const health = brawler.base_health ? brawler.base_health.toLocaleString() : '?';
        const damage = brawler.base_attack_damage ? brawler.base_attack_damage.toLocaleString() : '?';
        const range = brawler.attack_range ? brawler.attack_range.toFixed(1) : '?';
        const speed = brawler.movement_speed || '?';
        
        return `
        <div class="brawler-card ${isUltraLegendary ? 'ultra-legendary-card' : ''}">
            <div class="brawler-name">${brawler.name}</div>
            <div class="brawler-class">${brawler.class || 'Unknown'}</div>
            <div class="brawler-stats">
                <div class="stat">
                    <span class="stat-label">❤️ Health</span>
                    <span class="stat-value">${health}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">💥 Damage</span>
                    <span class="stat-value">${damage}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">📏 Range</span>
                    <span class="stat-value">${range}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">⚡ Speed</span>
                    <span class="stat-value">${speed}</span>
                </div>
            </div>
            <div class="brawler-rarity" style="color: ${rarityColor}">
                ${isUltraLegendary ? '👑 ' : '✨ '}${brawler.rarity || 'Unknown'}
            </div>
        </div>
    `}).join('');
}

// Update pagination controls
function updatePagination(total) {
    const totalPages = Math.ceil(total / currentLimit);
    pageInfo.textContent = `Page ${currentPage} of ${totalPages || 1}`;
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage >= totalPages;
}

// Show loading state
function showLoading() {
    brawlersGrid.innerHTML = '<div class="loading">Loading brawlers...</div>';
}

// Reset all filters
function resetFilters() {
    currentPage = 1;
    currentClass = '';
    currentRarity = '';
    currentSearch = '';
    searchInput.value = '';
    classFilter.value = '';
    rarityFilter.value = '';
    searchHint.innerHTML = '';
    fetchBrawlers();
}

// Validate and execute search
function executeSearch() {
    let searchTerm = searchInput.value.trim();
    
    // Strip quotes from the search term
    searchTerm = searchTerm.replace(/['"]+/g, '');
    
    // Edge case: empty search
    if (searchTerm === '') {
        resetFilters();
        return;
    }
    
    // Edge case: too short
    if (searchTerm.length === 1) {
        searchHint.innerHTML = '⚠️ Please enter at least 2 characters to search. Try "el", "sp", "ca", etc.';
        searchHint.style.color = '#ffaa00';
        return;
    }
    
    // Clear any previous hint
    searchHint.innerHTML = '';
    
    // Execute search
    currentSearch = searchTerm;
    currentPage = 1;
    currentClass = '';
    currentRarity = '';
    classFilter.value = '';
    rarityFilter.value = '';
    fetchBrawlers();
}

// Event Listeners
searchBtn.addEventListener('click', executeSearch);

resetBtn.addEventListener('click', resetFilters);

classFilter.addEventListener('change', () => {
    currentClass = classFilter.value;
    currentPage = 1;
    currentSearch = '';
    searchInput.value = '';
    searchHint.innerHTML = '';
    fetchBrawlers();
});

rarityFilter.addEventListener('change', () => {
    currentRarity = rarityFilter.value;
    currentPage = 1;
    currentSearch = '';
    searchInput.value = '';
    searchHint.innerHTML = '';
    fetchBrawlers();
});

searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        executeSearch();
    }
});

// Add real-time hint as user types
searchInput.addEventListener('input', (e) => {
    let value = e.target.value.trim();
    // Strip quotes for the hint too
    value = value.replace(/['"]+/g, '');
    
    if (value.length === 1) {
        searchHint.innerHTML = '💡 Type at least 2 characters to search';
        searchHint.style.color = '#aaa';
    } else if (value.length >= 2) {
        searchHint.innerHTML = '⏎ Press Enter or click Search';
        searchHint.style.color = '#2ecc71';
    } else {
        searchHint.innerHTML = '';
    }
});

// Clear hint when input loses focus
searchInput.addEventListener('blur', () => {
    setTimeout(() => {
        if (!searchInput.value.trim()) {
            searchHint.innerHTML = '';
        }
    }, 200);
});

prevBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        fetchBrawlers();
    }
});

nextBtn.addEventListener('click', () => {
    currentPage++;
    fetchBrawlers();
});

// Initial load
fetchBrawlers();