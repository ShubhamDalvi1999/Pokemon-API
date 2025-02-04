// Initialize Select2 for better dropdown experience
$(document).ready(function() {
    $('.pokemon-select').select2({
        placeholder: "Select a Pokemon",
        allowClear: true
    });
});

function showResult(elementId, data) {
    const element = document.getElementById(elementId);
    element.textContent = JSON.stringify(data, null, 2);
    element.classList.remove('d-none');
}

function showPokemonImages(data) {
    const container = document.getElementById('pokemonImages');
    container.innerHTML = ''; // Clear previous images
    
    if (data.sprites) {
        const sprites = data.sprites;
        container.classList.remove('d-none');
        
        // Add front default sprite
        if (sprites.front_default) {
            addImageToContainer(container, sprites.front_default, 'Front Default');
        }
        
        // Add back default sprite
        if (sprites.back_default) {
            addImageToContainer(container, sprites.back_default, 'Back Default');
        }
        
        // Add shiny sprites
        if (sprites.front_shiny) {
            addImageToContainer(container, sprites.front_shiny, 'Front Shiny');
        }
        if (sprites.back_shiny) {
            addImageToContainer(container, sprites.back_shiny, 'Back Shiny');
        }

        // Add official artwork if available
        if (sprites.other && sprites.other['official-artwork'] && sprites.other['official-artwork'].front_default) {
            addImageToContainer(container, sprites.other['official-artwork'].front_default, 'Official Artwork');
        }
    }
}

function addImageToContainer(container, url, label) {
    const div = document.createElement('div');
    div.className = 'pokemon-image-box';
    
    const img = document.createElement('img');
    img.src = url;
    img.alt = label;
    img.className = 'pokemon-image';
    
    const labelDiv = document.createElement('div');
    labelDiv.className = 'image-label';
    labelDiv.textContent = label;
    
    div.appendChild(img);
    div.appendChild(labelDiv);
    container.appendChild(div);
}

async function fetchData(url) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        return { error: error.message };
    }
}

async function fetchPokemon() {
    const name = document.getElementById('pokemonName').value;
    if (!name) return;
    const data = await fetchData(`/pokemon/${name}`);
    showPokemonImages(data);
    showResult('pokemonResult', data);
}

async function fetchPokemonList() {
    const data = await fetchData('/pokemon/list');
    showResult('listResult', data);
}

async function fetchPokemonByType() {
    const type = document.getElementById('pokemonType').value;
    if (!type) return;
    const data = await fetchData(`/pokemon/type/${type}`);
    showResult('typeResult', data);
}

async function fetchPokemonAbilities() {
    const name = document.getElementById('abilityPokemon').value;
    if (!name) return;
    const data = await fetchData(`/pokemon/${name}/abilities`);
    showResult('abilityResult', data);
}

async function fetchEvolutionChain() {
    const name = document.getElementById('evolutionPokemon').value;
    if (!name) return;
    const data = await fetchData(`/pokemon/species/${name}/evolution`);
    showResult('evolutionResult', data);
}

async function fetchFromDatabase() {
    const name = document.getElementById('dbPokemon').value;
    const db = document.getElementById('dbType').value;
    if (!name || !db) return;
    const data = await fetchData(`/pokemon/${name}/from/${db}`);
    showResult('dbResult', data);
} 