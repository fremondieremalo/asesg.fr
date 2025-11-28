document.addEventListener('DOMContentLoaded', () => {
    const tbody = document.getElementById('classement-body');

    // 1. On va chercher le fichier JSON
    // ⚠️ Si ton HTML est dans un sous-dossier, le chemin vers assets doit être adapté
    // Si ca ne marche pas, essaie '../assets/data/classement_d2.json'
    fetch('../data/classement_d2.json') 
        .then(response => {
            if (!response.ok) {
                throw new Error("Impossible de trouver le fichier classement_d2.json");
            }
            return response.json();
        })
        .then(data => {
            // 2. On vide le message de chargement
            tbody.innerHTML = '';

            // 3. On boucle sur chaque équipe
            data.forEach(row => {
                const tr = document.createElement('tr');

                // 4. On détecte si c'est notre équipe (ASESG ou ECHIRE)
                // Adapte 'ECHIRE' selon comment la FFF écrit le nom exact de ton club dans le JSON
                const nomEquipe = row.equipe.toUpperCase();
                if (nomEquipe.includes('ECHIRE') || nomEquipe.includes('GELAIS') || nomEquipe.includes('ASESG')) {
                    tr.classList.add('my-team'); // On ajoute la classe CSS spéciale
                }

                // 5. On crée les cellules (HTML)
                tr.innerHTML = `
                    <td>${row.pos}</td>
                    <td class="team-name">${row.equipe}</td>
                    <td><strong>${row.pts}</strong></td>
                    <td>${row.joues}</td>
                `;

                // 6. On ajoute la ligne au tableau
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Erreur:', error);
            tbody.innerHTML = '<tr><td colspan="4" style="color:red;">Classement indisponible pour le moment.</td></tr>';
        });
});