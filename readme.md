Nom de la branche : CodeIA

Description :
Cette branche sert à développer le code de l'ia

Objectif : 
Pour créer notre IA, nous avons utiliser une classe qui permet de définir notre IA, avec les différentes méthodes qu'il peut avoir, dans notre cas, nous avons :
- initialisation de l'ia, il faut juste lui mettre sa couleur dans notre cas, on mis la couleur ennemi, 
- le déplacement de l'ia qui permet de déplacer ses unités,
- l'attaque de l'ia qui permet d'attaquer les unités joueurs,
- le tour de l'ia qui permet de gérer son tour

Explication méthodes : 
- tour_ia :
 Cette méthode gère le tour de l'IA. Elle regarde toutes les unités contrôlées par l'IA (les ennemis dans notre cas) et les unités de l'IA attaque si c'est possible,
puis déplace les unités si elles n'ont pas encore bougé ou attaqué durant ce tour.

- attaque_ia :
Cette méthode recherche des unités joueur à portée et attaque la première unité joueur rencontrer si l'unité de l'IA n'a pas déjà attaqué durant ce tour.

- mouvement_ia :
Cette méthode fait déplacer les unités contrôler par l'IA vers une case adjacente (déplacement horizontale, verticale, et diagonale) si l'unité n'est pas sur un objectif majeur ou mineur. La méthode choisit aléatoirement parmi les cases adjacentes non occupées par d'autres unités.

Auteur : Noah BELLO
