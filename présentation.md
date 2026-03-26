# 1 - Présentation Globale Du Projet
## Naissance de l’idée :  
Nous sommes tous les deux anciens monteurs vidéo. L’idée est venue en voulant retrouver un outil simple et rapide pour faire des cuts, sans passer par des logiciels trop lourds. On voulait quelque chose de clair et direct, qui permette de se concentrer sur la coupe et le rythme, et surtout de bien comprendre ce qui se passe quand on édite une vidéo.

## Problématique initiale : 
Le problème de départ était la complexité. Beaucoup d’outils de montage sont complets, mais trop chargés pour un besoin simple. Notre objectif était d’avoir un logiciel léger pour couper et organiser des clips, avec une interface lisible et un flux de travail rapide.

## Objectifs : 
Faire notre premier projet sérieux et participer à un concours. Proposer un outil simple pour monter une vidéo, avec une timeline claire, un outil de coupe efficace et la possibilité d’ajouter du texte.

# 2 - Organisation Du Travail
## Présentation de l’équipe :
Kilen Millot et Tarek Aref, deux élèves de terminale (spé maths et spé NSI) au lycée Talma.

## Rôle de chacun et chacune :  
Kilen : structure du logiciel, interface, toolbox, affichage vidéo, texte avec OpenCV, glisser‑déposer et intégration timeline.  
Tarek : timeline complète, fonctions utiles (cut, supprimer, dupliquer), lien timeline‑séquence, sauvegarde JSON.

## Répartition des tâches :
On a séparé le travail entre l’interface et la logique métier. Kilen s’est concentré sur l’UI et l’affichage, Tarek sur la timeline et la gestion des clips. On a ensuite fait des points réguliers pour intégrer les deux parties et corriger les bugs ensemble.

## Temps passé sur le projet : 
Entre 80h et 100h de travail cumulé. Le plus gros du temps est parti dans la timeline, l’import/export vidéo et les tests.

# 3 - Présentation Des Étapes Du Projet
## De l’idée jusqu’à la réalisation du projet : 
On a d’abord posé les besoins (faire des cuts rapidement, gérer plusieurs clips, ajouter du texte). Ensuite on a défini une interface simple, puis créé un prototype de timeline. Une fois la base fonctionnelle, on a ajouté l’import des médias, l’outil coupe, la gestion du texte, puis l’export vidéo. Enfin, on a intégré tout ça et fait des tests pour stabiliser le projet.

# 4 - Validation De L’Opérationnalité Du Projet / De Son Fonctionnement
## État d’avancement du projet au moment du dépôt :
Environ 50% du projet était terminé. Les fonctions principales sont là, mais il reste des améliorations et des optimisations.

## Approches mises en œuvre pour vérifier l’absence de bugs : 
Tests sous plusieurs versions de Python. Tests complets avec différentes vidéos et différents formats. Tests sous Linux Fedora. Essais répétés des fonctions principales (coupe, import, export, texte, glisser‑déposer).

## Difficultés rencontrées et solutions apportées :
On a eu des soucis de synchro audio/vidéo, de FPS différents entre clips et de glisser‑déposer instable. On a réglé ça avec un recalcul audio par frame, un FPS de référence dans la timeline, et une gestion explicite des événements de drag. On a aussi dû ajuster le rendu texte pour éviter qu’il sorte de l’écran et rendre l’export plus fiable.

# 5 - Ouverture
## Idées d’amélioration du projet : 
Ajouter des effets (fond vert, correction couleur, flou), superposer des vidéos, ajouter des raccourcis clavier configurables et améliorer la gestion des médias.

## Analyse critique :
Le projet avance bien mais reste incomplet. Certaines parties sont longues et pas optimisées, et on observe encore des ralentissements au début de la lecture. L’architecture peut aussi être simplifiée.
Le raccord son / vidéo est aussi très mal réglé mais pas terminé par manque de temps.
Beaucoups de fonctions mérite d'être raccourci.
Au lieu d'utilise un dictionnaire pour stocker et afficher les vidéos il faudrait peut etre utiliser un tableau pour pouvoir ensuite pouvoir superposer plusieurs vidéos.
On a beaucoups de fonction qui servent de 'gardes-fou' pour essayer de minimiser les bugs de son / vidéo.
Sur la timeline, la barre diparait une fois qu'elle est arrivée au bout et ne continue pas sur le bloc média rendant difficile la navigation.



## Compétences personnelles développées : 
Lecture et compréhension de documentation, logique mathématique appliquée à la programmation, patience, organisation et recherche de solutions.

## Démarche d’inclusion :  
Interface simple avec boutons clairs, couleurs contrastées, et tests sous Linux pour éviter la dépendance à un seul OS.

# Utilisation De L’IA
On a utilisé l’IA ponctuellement pour reformuler des idées, clarifier la rédaction et débloquer quelques points techniques. Ça nous a aussi aidés à résumer certaines documentations (OpenCV, MoviePy) et à nous assister sur la dernière semaine avant le rendu, car nous étions en période d’examens (bac blanc).

Toute la logique de programmation a été faite par nous‑mêmes, et chaque changement a été relu, testé et corrigé par nous‑mêmes.
