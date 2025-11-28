document.addEventListener('DOMContentLoaded', () => {
    console.log("🟢 Le script JS a démarré !"); // Mouchard 1

    const tbody = document.getElementById('classement-body');
    if (!tbody) {
        console.error("🔴 Erreur : Impossible de trouver le tableau dans le HTML (id='classement-body' introuvable)");
        return;
    }

    // Le chemin vers le fichier JSON
    const urlJson = '../data/classement_r3.json';
    console.log(`🔍 Tentative de chargement du fichier : ${urlJson}`); // Mouchard 2

    fetch(urlJson)
        .then(response => {
            console.log(`Reçu réponse du serveur : ${response.status}`); // Mouchard 3
            if (!response.ok) {
                throw new Error(`Fichier introuvable (Erreur ${response.status})`);
            }
            return response.json();
        })
        .then(data => {
            console.log("✅ Données JSON reçues :", data); // Mouchard 4 : Affiche les données brutes

            tbody.innerHTML = ''; // On vide le tableau

            data.forEach((row, index) => {
                const tr = document.createElement('tr');

                // Détection de l'équipe (ASESG / ECHIRE)
                const nomEquipe = row.equipe ? row.equipe.toUpperCase() : "";
                if (nomEquipe.includes('ECHIRE') || nomEquipe.includes('GELAIS') || nomEquipe.includes('ASESG')) {
                    tr.classList.add('my-team');
                }

                // ON NE MET QUE 4 CELLULES ICI :
                tr.innerHTML = `
                    <td>${row.pos || '-'}</td>
                    <td class="team-name">${row.equipe || 'Inconnu'}</td>
                    <td><strong>${row.pts || 0}</strong></td>
                    <td>${row.joues || 0}</td>
                `; 
                // J'ai supprimé la ligne <td>${row.dif}</td>

                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('❌ ERREUR FATALE :', error);
            tbody.innerHTML = `<tr><td colspan="4" style="color: red; text-align: center;">Erreur : ${error.message}</td></tr>`;
        });
});