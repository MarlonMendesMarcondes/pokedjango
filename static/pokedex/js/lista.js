document.addEventListener('DOMContentLoaded', function () {
    let page = 1;
    let loading = false;
    let hasNext = true;

    function loadMorePokemons() {
        if (loading || !hasNext) return;
        loading = true;

        const params = new URLSearchParams(window.location.search);
        params.set('page', page + 1);
        params.set('format', 'json');
        const url = `?${params.toString()}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                page++;
                hasNext = data.has_next;
                const pokemonContainer = document.querySelector('.row.row-cols-1.row-cols-sm-2.row-cols-md-3.g-4');
                data.pokemons.forEach(pokemon => {
                    const pokemonCard = `
                        <a href="/pokemons/${pokemon.id}/" class="col d-flex justify-content-center text-decoration-none text-dark">
                            <div class="card shadow rounded-4 text-center card-background" style="${pokemon.card_style}">

                                <div class="position-relative mb-5">
                                    <span class="badge bg-light text-dark position-absolute top-0 end-0 m-2">${pokemon.hp} HP</span>
                                </div>
                
                                <img src="${pokemon.image_url}" class="pokemon-img mx-auto d-block mt-3" alt="${pokemon.name}">
                                
                                <div class="card-body">
                                    <h5 class="pokemon-name text-capitalize m-3">${pokemon.name}</h5>
                                    
                                    ${pokemon.primary_type ? `<span class="pokemon-type badge rounded-pill px-3 py-2 tipo-${pokemon.primary_type}">${pokemon.primary_type}</span>` : ''}
                                    ${pokemon.secondary_type ? `<span class="pokemon-type badge rounded-pill px-3 py-2 tipo-${pokemon.secondary_type}">${pokemon.secondary_type}</span>` : ''}

                                    <div class="stats d-flex justify-content-around mt-4">
                                        <div class="text-center bg-white rounded-4 shadow-sm px-3 py-2 shadow-sm">
                                          <div class="fw-bold text-uppercase small text-muted">ATK</div>
                                          <div class="fs-5 fw-semibold text-dark">${pokemon.attack || '--'}</div>
                                        </div>
                                        <div class="text-center bg-white rounded-4 shadow-sm px-3 py-2 shadow-sm">
                                          <div class="fw-bold text-uppercase small text-muted">DEF</div>
                                          <div class="fs-5 fw-semibold text-dark">${pokemon.defense || '--'}</div>
                                        </div>
                                        <div class="text-center bg-white rounded-4 shadow-sm px-3 py-2 shadow-sm">
                                          <div class="fw-bold text-uppercase small text-muted">SPD</div>
                                          <div class="fs-5 fw-semibold text-dark">${pokemon.speed || '--'}</div>
                                        </div>
                                    </div>
                                    
                                </div>
                
                            </div>
                        </a>
                    `;
                    pokemonContainer.innerHTML += pokemonCard;
                });
                loading = false;
            })
            .catch(error => {
                console.error('Error loading more pokemons:', error);
                loading = false;
            });
    }

    window.addEventListener('scroll', () => {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
            loadMorePokemons();
        }
    });
});
