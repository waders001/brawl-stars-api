// Player search functionality with real backend API
const searchBtn = document.getElementById('searchPlayerBtn');
const playerTagInput = document.getElementById('playerTag');
const playerResult = document.getElementById('playerResult');

// Helper function to parse Brawl Stars custom date format (e.g., "20260519T021340.000Z")
function parseBrawlStarsDate(dateStr) {
    if (!dateStr) return null;
    const match = dateStr.match(/^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})\.(\d{3})Z$/);
    if (match) {
        const [, year, month, day, hour, minute, second, ms] = match;
        return new Date(Date.UTC(
            parseInt(year),
            parseInt(month) - 1,
            parseInt(day),
            parseInt(hour),
            parseInt(minute),
            parseInt(second),
            parseInt(ms)
        ));
    }
    const fallback = new Date(dateStr);
    return isNaN(fallback.getTime()) ? null : fallback;
}

// Format mode name: "hotZone" -> "Hot Zone", "heist" -> "Heist"
function formatModeName(mode) {
    if (!mode) return 'Unknown';
    let formatted = mode.replace(/([A-Z])/g, ' $1').trim();
    formatted = formatted.replace(/\b\w/g, c => c.toUpperCase());
    const special = {
        'Hot Zone': 'Hot Zone',
        'Gem Grab': 'Gem Grab',
        'Bounty': 'Bounty',
        'Heist': 'Heist',
        'Siege': 'Siege',
        'Brawl Ball': 'Brawl Ball',
        'Knockout': 'Knockout',
        'Duels': 'Duels',
        'Showdown': 'Showdown',
        'Duo Showdown': 'Duo Showdown'
    };
    return special[formatted] || formatted;
}

// Format result: "victory" -> "Victory", "defeat" -> "Defeat"
function formatResult(result) {
    if (!result) return 'Unknown';
    return result.charAt(0).toUpperCase() + result.slice(1).toLowerCase();
}

async function searchPlayer() {
    let tag = playerTagInput.value.trim();
    
    if (!tag) {
        playerResult.innerHTML = '<div class="player-card">Please enter a player tag</div>';
        return;
    }
    
    if (tag.startsWith('#')) {
        tag = tag.substring(1);
    }
    
    if (tag.length < 2 || tag.length > 9) {
        playerResult.innerHTML = '<div class="player-card">⚠️ Invalid player tag. Tags are usually 2-9 characters (e.g., 2PPU9VUR)</div>';
        return;
    }
    
    playerResult.innerHTML = '<div class="loading">🔍 Searching for player...</div>';
    
    try {
        const response = await fetch(`/players/${tag}`);
        
        if (!response.ok) {
            if (response.status === 404) throw new Error('Player not found');
            if (response.status === 429) throw new Error('Rate limit exceeded. Try again later.');
            throw new Error(`Error ${response.status}: Could not fetch player`);
        }
        
        const player = await response.json();
        displayPlayer(player);
        await fetchBattleLog(tag);
        
    } catch (error) {
        playerResult.innerHTML = `<div class="player-card" style="color: #e74c3c;">
            <h3>❌ Error</h3>
            <p>${error.message}</p>
            <p style="font-size:0.9rem;">💡 Tip: Use a valid player tag without spaces.</p>
        </div>`;
    }
}

function displayPlayer(player) {
    const playerName = player.name || 'Unknown';
    
    const clubInfo = (player.club && player.club.name) ? 
        `<p><strong>🏠 Club:</strong> ${player.club.name} (${player.club.tag || '??'})</p>` : 
        '<p><strong>🏠 Club:</strong> No club</p>';
    
    const cleanTag = player.tag ? '#' + player.tag.replace('#', '') : 'N/A';
    
    // Additional stats
    const totalWins = (player['3vs3Victories'] || 0) + (player.soloVictories || 0) + (player.duoVictories || 0);
    const totalPrestige = player.totalPrestigeLevel || 0;
    const rankedElo = player.rankedElo || 0;
    const highestRankedElo = player.highestAllTimeRankedElo || 0;
    
    playerResult.innerHTML = `
        <div class="player-card">
            <h2 class="player-name">${playerName}</h2>
            <p><strong>🏷️ Tag:</strong> ${cleanTag}</p>
            <p><strong>🏆 Trophies:</strong> ${player.trophies?.toLocaleString() || 0}</p>
            <p><strong>⭐ Highest Trophies:</strong> ${player.highestTrophies?.toLocaleString() || 0}</p>
            <p><strong>📈 Exp Level:</strong> ${player.expLevel || 0}</p>
            ${clubInfo}
            <div class="player-stats-grid">
                <div class="stat"><span class="stat-label">🎮 3v3 Wins:</span><span class="stat-value">${player['3vs3Victories']?.toLocaleString() || 0}</span></div>
                <div class="stat"><span class="stat-label">👤 Solo Wins:</span><span class="stat-value">${player.soloVictories?.toLocaleString() || 0}</span></div>
                <div class="stat"><span class="stat-label">👥 Duo Wins:</span><span class="stat-value">${player.duoVictories?.toLocaleString() || 0}</span></div>
            </div>
            <div class="player-stats-grid">
                <div class="stat"><span class="stat-label">🏅 Total Wins:</span><span class="stat-value">${totalWins.toLocaleString()}</span></div>
                <div class="stat"><span class="stat-label">✨ Total Prestige:</span><span class="stat-value">${totalPrestige.toLocaleString()}</span></div>
                <div class="stat"><span class="stat-label">🎯 Ranked Elo:</span><span class="stat-value">${rankedElo.toLocaleString()}</span></div>
                <div class="stat"><span class="stat-label">🏆 Highest Ranked Elo:</span><span class="stat-value">${highestRankedElo.toLocaleString()}</span></div>
            </div>
            <div style="margin-top:20px;"><p><strong>🤺 Brawlers Unlocked:</strong> ${player.brawlers?.length || 0}</p></div>
        </div>
    `;
}

async function fetchBattleLog(tag) {
    try {
        const response = await fetch(`/players/${tag}/battlelog?limit=5`);
        if (!response.ok) return;
        const battleLog = await response.json();
        if (battleLog.items && battleLog.items.length > 0) {
            displayBattleLog(battleLog.items);
        }
    } catch (error) {
        console.error('Battle log error:', error);
    }
}

function displayBattleLog(battles) {
    const battleSection = document.createElement('div');
    battleSection.className = 'player-card';
    battleSection.style.marginTop = '20px';
    let html = '<h3>📜 Recent Battles</h3><div style="overflow-x:auto;"><table style="width:100%; border-collapse:collapse;">';
    html += '<thead><tr style="border-bottom:1px solid rgba(255,255,255,0.1);"><th style="padding:10px;">Mode</th><th style="padding:10px;">Map</th><th style="padding:10px;">Result</th><th style="padding:10px;">Date</th></tr></thead><tbody>';
    
    for (const battle of battles) {
        const rawMode = battle.event?.mode || 'Unknown';
        const formattedMode = formatModeName(rawMode);
        const mapName = battle.event?.map || 'Unknown';
        const rawResult = battle.battle?.result || 'Unknown';
        const formattedResult = formatResult(rawResult);
        const resultColor = rawResult === 'victory' ? '#2ecc71' : (rawResult === 'defeat' ? '#e74c3c' : '#f39c12');
        
        let battleTime = 'Unknown';
        if (battle.battleTime) {
            const parsedDate = parseBrawlStarsDate(battle.battleTime);
            if (parsedDate) {
                battleTime = parsedDate.toLocaleDateString();
            }
        }
        
        html += `<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
            <td style="padding:8px;">${formattedMode}</td>
            <td style="padding:8px;">${mapName}</td>
            <td style="padding:8px; color:${resultColor};">${formattedResult}</td>
            <td style="padding:8px;">${battleTime}</td>
        </tr>`;
    }
    html += '</tbody></table></div>';
    battleSection.innerHTML = html;
    playerResult.appendChild(battleSection);
}

searchBtn.addEventListener('click', searchPlayer);
playerTagInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') searchPlayer(); });
playerTagInput.placeholder = "Enter player tag (e.g., 2PPU9VUR or #2PPU9VUR)";
