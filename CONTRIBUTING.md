# Guide de contribution — BookShop ETL Pipeline

Merci d'envisager de contribuer à ce projet ! Voici quelques directives pour faciliter les choses.

## Code de conduite

Soyez respectueux et constructif dans vos interactions. Ce projet suit les principes de transparence et d'inclusivité.

## Comment contribuer

### Signaler un bug
- Vérifiez que le bug n'existe pas déjà dans les issues
- Décrivez clairement les étapes pour reproduire le problème
- Précisez votre environnement (OS, versions Python, Docker, etc.)

### Proposer une amélioration
- Ouvrez une issue pour discuter de l'amélioration avant de coder
- Explicitez le problème que cela résout ou la valeur ajoutée

### Soumettre un code

1. **Fork** le dépôt
2. **Créer une branche** avec un nom descriptif : `fix/issue-123` ou `feature/new-dashboard`
3. **Commiter** avec des messages clairs et concis
4. **Pusher** vers votre fork
5. **Ouvrir une Pull Request** avec une description détaillée

### Exigences pour les PR

- ✓ Code testé localement avec `docker compose`
- ✓ Pas de secrets ni credentials dans le code ou `.env`
- ✓ Messages de commit explicites
- ✓ Documentation mise à jour si nécessaire (README, docstrings)
- ✓ Dépendances ajoutées documentées dans le bon `requirements.txt`

## Développement local

```bash
# Copier le template .env
cp .env.example .env

# Renseigner vos credentials Snowflake et PostgreSQL
# Puis démarrer les services
docker compose up -d --build

# Vérifier les logs
docker compose logs -f airflow-webserver
```

## Tests

### Valider les modèles dbt
```bash
docker compose exec dbt dbt test
```

### Vérifier le DAG Airflow
```bash
docker compose exec airflow-webserver airflow dags test bookshop_pipeline
```

### Tester le dashboard Streamlit
```bash
# L'app s'exécute sur http://localhost:8501
```

## Conventions de code

- **Python** : suivre PEP8 (utilisez `black` ou `flake8`)
- **dbt** : respecter les conventions du projet (noms `stg_*`, `dim_*`, `fact_*`)
- **SQL** : indentation lisible, commentaires pour les jointures complexes
- **Commits** : messages en français, clairs et courts

## Questions ?

Ouvrez une issue pour discuter de votre question. Nous répondrons dès que possible.

---

Merci pour votre contribution ! 🙏
