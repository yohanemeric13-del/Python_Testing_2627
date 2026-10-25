# Rapport de test de performance

## Environnement et scénario

- Date : 25 octobre 2026.
- Environnement : macOS, Python 3.14.6, Flask 3.1.3, Locust 2.47.0.
- Serveur testé : serveur de développement Flask local (`127.0.0.1:5001`).
- Charge : 10 utilisateurs virtuels, ajoutés à raison de 2 par seconde, pendant 1 minute.
- Parcours : page d’accueil, tableau des points, résumé du club et ouverture de la page de réservation.
- Les requêtes ne valident aucune réservation et ne modifient pas les fichiers JSON.

## Résultats

| Mesure | Résultat |
| --- | ---: |
| Requêtes terminées | 293 |
| Requêtes en échec | 0 (0 %) |
| Débit moyen | 4,96 requêtes/s |
| Latence moyenne agrégée | 4,35 ms |
| Latence médiane agrégée | 4 ms |
| 95e percentile agrégé | 7 ms |
| Latence maximale agrégée | 19,13 ms |

## Résultats par route

| Route | Requêtes | Échecs | Latence moyenne | 95e percentile |
| --- | ---: | ---: | ---: | ---: |
| `GET /` | 112 | 0 | 4,11 ms | 6 ms |
| `GET /points` | 78 | 0 | 3,98 ms | 6 ms |
| `POST /showSummary` | 43 | 0 | 5,03 ms | 7 ms |
| `POST /showSummary` (connexion initiale) | 10 | 0 | 8,30 ms | 19 ms |
| `GET /book/<competition>/<club>` | 50 | 0 | 4,11 ms | 6 ms |

## Fichiers de résultats

- `rapport.html` : rapport visuel Locust.
- `locust_stats.csv` : statistiques par route et agrégées.
- `locust_stats_history.csv` : évolution des statistiques pendant le test.
- `locust_failures.csv` et `locust_exceptions.csv` : détails des erreurs et exceptions.

Cette mesure décrit une charge légère sur un serveur local de développement. Elle ne représente pas les performances d’un déploiement de production ni une charge maximale.
