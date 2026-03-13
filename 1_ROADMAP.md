 Plan de finalisation de Creatakis (avant le 20)

Objectif: rendre l'application **fiable, utilisable en démo, et crédible en production légère**.

> Ce plan est orienté exécution: quoi faire, dans quel ordre, et quand considérer que c'est terminé.

## 0) Vision “version prête”

Une version prête avant le 20 doit permettre:
1. d'importer des médias sans bug,
2. de monter rapidement (couper, déplacer, texte, audio de base),
3. d'exporter en MP4 avec paramètres simples,
4. de rouvrir un projet sans perte.

---

## 1) Priorités critiques (P0) — à livrer en premier

## 1.1 Dialogues fichiers 100% Qt (fin du mix tkinter/PyQt)
**Problème actuel**: `utils.py` utilise `tkinter` dans une app PyQt → risques de focus, fenêtres bloquées, UX incohérente.

**À implémenter précisément**:
- Remplacer `import_video()`, `save_as_path()`, `load_save()` par `QFileDialog`.
- Forcer filtres explicites:
  - import: `*.mp4 *.mov *.avi *.mkv`
  - projet: `*.creatakis.json`
  - export: `*.mp4`
- Sauvegarder le dernier dossier utilisé (settings utilisateur).

**Critères d'acceptation**:
- Aucun import/sauvegarde n'ouvre de fenêtre tkinter.
- Tous les dialogues sont non bloquants pour l'UI principale.
- Le dernier chemin est réutilisé entre deux ouvertures.

---

## 1.2 Timeline éditable (sélection, suppression, déplacement)
**Problème actuel**: `remove_selected_clip()` vide, pas de workflow édition minimal.

**À implémenter précisément**:
- État `selected_clip_id` dans la timeline.
- Rendu visuel clair (bordure + couleur) pour le clip sélectionné.
- Action `Supprimer`:
  - touche `Delete`
  - bouton dans UI
  - entrée menu Édition
- Déplacement simple d'un clip (drag horizontal, snap frame par frame).

**Critères d'acceptation**:
- Un clip peut être sélectionné/désélectionné.
- Supprimer retire le clip visuellement et du modèle de données.
- Déplacer met à jour `start_frame/end_frame` correctement.

---

## 1.3 Sauvegarde/chargement de projet robuste (sans `eval`)
**Problème actuel**: sérialisation en `str`, rechargement fragile, `eval` dangereux.

**À implémenter précisément**:
- Nouveau format de projet versionné:
```json
{
  "project_version": 1,
  "meta": {"created_at": "...", "app_version": "..."},
  "sources": [{"id": "src_1", "path": "...", "duration": 120.0}],
  "timeline": {
    "fps": 30,
    "tracks": [
      {"id": "video_1", "type": "video", "clips": [...]},
      {"id": "text_1", "type": "text", "clips": [...]},
      {"id": "audio_1", "type": "audio", "clips": [...]}
    ]
  },
  "export": {"codec": "h264", "container": "mp4"}
}
```
- Pas de `eval`, jamais.
- Validation de schéma avant chargement (minimum: champs obligatoires + types).
- Gestion des médias manquants (dialog “relocaliser le fichier”).

**Critères d'acceptation**:
- Ouvrir/sauver un projet ne perd pas les clips timeline.
- Charger un fichier invalide affiche une erreur propre.
- Aucun warning sécurité lié à `eval`.

---

## 1.4 Texte piloté par la timeline (et non global)
**Problème actuel**: `text_to_display` est global et non indexé par le temps.

**À implémenter précisément**:
- Chaque clip texte possède:
  - `start_frame`, `end_frame`
  - `content`, `font`, `size`, `color`, `position`, `align`
  - optionnel: `background_color`, `stroke`
- Au rendu: récupérer les clips texte actifs pour la frame courante.
- Gérer superposition de plusieurs textes (ordre piste + z-index).

**Critères d'acceptation**:
- Le texte apparaît uniquement pendant son intervalle.
- Deux textes peuvent coexister sur des plages différentes (ou superposées).
- Modifier un clip texte met à jour l'aperçu immédiatement.

---

## 2) Effets à ajouter (priorisés)

## 2.1 Effets vidéo essentiels (P1)
- **Luminosité / Contraste / Saturation** (sliders).
- **Température couleur** (chaud/froid).
- **Netteté légère**.
- **Vignette** simple.
- **Noir et blanc / Sépia** (presets rapides).

**Implémentation conseillée**:
- Effets non destructifs stockés dans les propriétés du clip.
- Pipeline: frame brute → stack d'effets → overlay texte.

---

## 2.2 Transitions (P1)
- **Fondu en entrée / sortie** (audio + vidéo).
- **Crossfade** entre deux clips.
- **Cut** (transition instantanée) par défaut.

**Minimum viable**:
- Durée transition (0.2s à 2s).
- Prévisualisation basique en lecture.

---

## 2.3 Effets texte (P1)
- Ombre portée.
- Contour (stroke).
- Fond semi-transparent.
- Animations simples: fade in / fade out / slide up.

---

## 2.4 Audio (P1-P2)
- Gain clip audio (+/- dB).
- Fade in/out audio.
- Mute piste.
- Normalisation simple (option “uniformiser volume”).

---

## 2.5 Fonctionnalités “pro” à forte valeur (P2)
- **Vitesse clip** (0.5x, 1x, 1.5x, 2x).
- **Reverse clip**.
- **Freeze frame**.
- **Crop/zoom** (transform 2D position/scale).
- **Stabilisation légère** (si temps restant).

---

## 3) Fonctionnalités de montage à ajouter

## 3.1 Outils timeline indispensables
- Split au playhead (`Ctrl+K`).
- Ripple delete (optionnel mais puissant).
- Snap magnétique (playhead, bords de clips).
- Zoom timeline + mini-map.

## 3.2 Gestion pistes
- Ajouter/supprimer piste (video/text/audio).
- Lock piste.
- Mute/Solo piste audio.
- Renommer piste.

## 3.3 Bibliothèque médias
- Colonnes utiles: nom, type, durée, résolution, fps, taille.
- Vignettes vidéos.
- Recherche/filtre (texte + type).
- Détection doublons d'import.

## 3.4 Export
- Presets: YouTube 1080p30, TikTok 1080x1920, Proxy 720p.
- Choix bitrate (faible/moyen/élevé).
- Barre de progression + ETA.
- Rapport export (durée, taille finale, éventuels warnings).

---

## 4) UX / ergonomie (gains rapides)

- Désactiver les actions non disponibles (Play sans vidéo, Export sans timeline).
- Barre d'état contextuelle (frame, timecode, zoom, sélection).
- Raccourcis standard:
  - `Space`: Play/Pause
  - `Ctrl+S`: Save
  - `Ctrl+Shift+S`: Save As
  - `Ctrl+Z / Ctrl+Y`: Undo/Redo
  - `Delete`: supprimer clip
  - `Ctrl+D`: dupliquer clip
- Message d'erreur propre (QMessageBox) + logs techniques séparés.

---

## 5) Architecture et qualité (pour éviter de casser l'app)

## 5.1 Refactor structurel minimum
- Créer un `ProjectState` (dataclass) unique.
- Arrêter les variables globales mutables dispersées.
- Séparer modules:
  - `ui/`
  - `domain/` (timeline, clips, commandes)
  - `io/` (save/load/import/export)
  - `render/` (preview + export)

## 5.2 Undo/Redo
- Pattern Command:
  - `AddClipCommand`
  - `RemoveClipCommand`
  - `MoveClipCommand`
  - `TrimClipCommand`
  - `UpdateTextStyleCommand`

## 5.3 Tests minimaux à écrire
- tests modèle timeline (durées, overlap, move, trim)
- tests save/load (round-trip JSON)
- tests activation texte selon frame
- tests commandes undo/redo

Objectif: **>= 15 tests** automatisés avant le 20.

---

## 6) Plan d'exécution concret (jusqu'au 20)

## Jours 1-2 (socle)
- Dialogues `QFileDialog` + persistance chemins.
- Nouveau format projet JSON v1 + validateur + migration minimale.

## Jours 3-4 (montage de base)
- Sélection/suppression clips.
- Déplacement horizontal + snap.
- Texte lié timeline (multi-clips).

## Jours 5-6 (édition)
- Trim début/fin.
- Propriétés clip (texte + style).
- Raccourcis clavier critiques.

## Jours 7-8 (effets + robustesse)
- Effets vidéo essentiels (lum/contraste/sat + B&W).
- Fade in/out vidéo/audio.
- Undo/Redo des commandes cœur.

## Jours 9-10 (export + polish)
- Presets export + progress.
- Logs + messages d'erreur propres.
- Campagne de test + correction bugs bloquants.

---

## 7) Backlog “tickets prêts à coder” (ordre recommandé)

1. `IO-01` Remplacer tkinter par QFileDialog.
2. `PRJ-01` Définir schéma projet JSON v1.
3. `PRJ-02` Implémenter save/load + validation + migration.
4. `TL-01` Sélection clip + surbrillance.
5. `TL-02` Suppression clip (Delete + menu + bouton).
6. `TL-03` Déplacement clip horizontal.
7. `TXT-01` Clips texte temporels + rendu par frame.
8. `TXT-02` Éditeur style texte (couleur, taille, position).
9. `FX-01` Effets vidéo de base (lum/contrast/sat/B&W).
10. `AUD-01` Gain + fade audio.
11. `EXP-01` Presets export + progression.
12. `CORE-01` Undo/Redo commandes cœur.
13. `QA-01` Suite de tests auto + check manuel de non-régression.

---

## 8) Définition de “app complète au maximum” (checklist finale)

- [ ] Import média stable (video/audio/image).
- [ ] Timeline éditable (add/move/trim/delete/split).
- [ ] Texte complet (style + timing + animation simple).
- [ ] Effets vidéo essentiels fonctionnels.
- [ ] Audio de base exploitable (gain + fade + mute).
- [ ] Save/Load projet sans perte ni crash.
- [ ] Export MP4 presets + progression.
- [ ] Undo/Redo sur actions principales.
- [ ] 15+ tests auto verts.
- [ ] Démo 5 min sans bug bloquant.

---

Si tu veux, je peux maintenant te faire la suite directement: **un backlog détaillé ticket par ticket avec estimation (heures), dépendances, et ordre de commits pour livrer avant le 20**.