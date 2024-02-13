
Exercise 1.3.1


  N de taches  |    1    |    2    |    4    |    8    | |
---------------|---------|---------|---------------------|
Temp total     | 1.8798  | 0.72010 | 0.40512 | 0.28743 | |
---------------|---------|---------|---------------------|
Speed-up       |         |  2.60   |   4.64  |   6.54  | |
---------------|---------|---------|---------------------|

Nous pouvons constater que la parallélisation est très efficace pour ce problème. En permettant à chaque processus de générer des parties de l'image en parallèle, il est possible de réduire jusqu'à six fois le temps total de la tâche.

Exercise 1.3.2

  N de taches  |    1    |    2    |    4    |    8    | |
---------------|---------|---------|---------------------|
Temp total     | 1.8798  | 1.3233  | 1.3523  | 1.31828 | |
---------------|---------|---------|---------------------|
Speed-up       |         |  1,42   |   1,39  |   1,43  | |
---------------|---------|---------|---------------------|

Dans ce cas, le speedup n'est pas aussi élevé que dans le cas précédent, mais il reste néanmoins significatif. Cela peut s'expliquer par le fait que nous avons un cœur de moins effectuant le travail de génération de l'image (le maître). Cependant, cette stratégie peut encore être optimisée en modifiant la taille de l'image sur laquelle chaque cœur doit travailler, ce qui permettrait d'obtenir de meilleurs résultats que dans le cas précédent.