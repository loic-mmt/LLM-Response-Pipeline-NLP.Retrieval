# LLM-powered-meme-responder (v2)

Pipeline modulaire pour analyser un prompt, décider d'une reaction humaine, generer une reponse, puis selectionner un template de meme adaptee. La v2 est concue pour etre explicable, stable, et facile a faire evoluer.

## Vue d'ensemble

Entrer un prompt libre, obtenir:
- des tags semantiques (ModuleA)
- un plan de reaction (ModuleB)
- une reponse texte contrainte (ModuleC)
- un template de meme classe (ModuleD)

## Architecture (v2)

```
Prompt
  -> ModuleA: Classification (prompt -> tags)
  -> ModuleB: Policy engine (tags prompt -> plan de reaction)
  -> ModuleC: Generation (plan -> texte)
  -> ModuleD: Retrieval (tags prompt + tags reponse -> template meme)
```

## Modules

### ModuleA - Classifier
Fichier: `v2/ModuleA/classifier.py`

Responsabilites:
- Charger un dictionnaire de tags (ex: `tags.jsonl`)
- Normaliser les prompts
- Entrainement multi-label (TF-IDF+LR ou DistilBERT)
- Prediction et filtrage des tags

Sorties attendues:
- `TagPrediction(tag, score)`
- Liste de tags filtres selon un seuil ou top-k

### ModuleB - Policy Engine
Fichier: `v2/ModuleB/policy_engine.py`

Responsabilites:
- Charger des regles de mapping (JSON/YAML)
- Scorer les regles en fonction des tags prompt
- Deriver un plan de reaction humain
- Convertir le plan en tags de reponse

Sortie attendue:
- `ReactionPlan(tone, acts, intensity, format)`

### ModuleC - Generator
Fichier: `v2/ModuleC/generator.py`

Responsabilites:
- Charger des templates de reponse
- Rendre un texte a partir d'un template + plan de reaction
- Appliquer des contraintes (longueur, pas de mentions/hashtags)
- Generer la reponse finale

Sortie attendue:
- Texte final conforme aux contraintes

### ModuleD - Retrieval
Fichier: `v2/ModuleD/retrieval.py`

Responsabilites:
- Charger un catalogue de memes (metadata.jsonl)
- Scorer chaque template par rapport aux tags
- Classer et selectionner le meilleur template

Sorties attendues:
- `MemeTemplate(meme_id, tags, constraints)`
- `MemeCandidate(template, score)`

## Donnees attendues

- `tags.jsonl`: dictionnaire de tags (ton, actes, intensite, format)
- `metadata.jsonl`: catalogue de memes avec tags et contraintes
- Templates de reponse: liste ou fichier texte/JSON
- Regles de policy: JSON/YAML pour le mapping prompt -> reaction

## Exemple d'utilisation (pipeline)

```python
from v2.ModuleA.classifier import load_tag_dictionary, predict_tags, filter_tags
from v2.ModuleB.policy_engine import load_policy_rules, derive_reaction_plan, reaction_plan_to_tags
from v2.ModuleC.generator import load_templates, generate_response
from v2.ModuleD.retrieval import load_meme_catalog, rank_templates, select_template

prompt = "Je me suis encore plante en public..."

tag_dict = load_tag_dictionary("tags.jsonl")
prompt_predictions = predict_tags(prompt, model="classifier", tag_dictionary=tag_dict, threshold=0.4)
prompt_tags = [p.tag for p in filter_tags(prompt_predictions, top_k=6)]

rules = load_policy_rules("policy_rules.json")
reaction_plan = derive_reaction_plan(prompt_tags, rules)
response_tags = reaction_plan_to_tags(reaction_plan)

templates = load_templates("response_templates.json")
response_text = generate_response(prompt, reaction_plan, templates)

catalog = load_meme_catalog("metadata.jsonl")
candidates = rank_templates(catalog, prompt_tags, response_tags, top_k=5)
selected_template = select_template(candidates)
```

## Notes d'implementation

- Le flux est deterministe et explicable (tags + regles).
- Les modules peuvent etre remplaces progressivement par des modeles ML.
- Les contraintes de generation sont appliquees en dernier pour garantir la conformite.

## Etat du projet

La v2 decrit l'architecture et les interfaces; les fonctions sont concues pour etre completes mais l'implementation reste a finaliser.
