
# TD1

`pandoc -s --toc README.md --css=./github-pandoc.css -o README.html`





## lscpu

```
coller ici les infos *utiles* de lscpu. 
```

*Des infos utiles s'y trouvent : nb core, taille de cache*



## Produit matrice-matrice



### Permutation des boucles

*Expliquer comment est compilé le code (ligne de make ou de gcc) : on aura besoin de savoir l'optim, les paramètres, etc. Par exemple :*

`make TestProduct.exe && ./TestProduct.exe 1024`


  ordre           | time    | MFlops  | MFlops(n=2048) 
------------------|---------|---------|----------------
i,j,k (origine)   | 4.26461 | 503.559 |   417.032             
j,i,k             | 4.38949 | 489.233 |   382.603 
i,k,j             | 18.0008 | 119.3   |   110.579 
k,i,j             | 17.9526 | 119.619 |   108.452 
j,k,i             | 0.34417 | 6239.48 |   4511.57 
k,j,i             | 0.35614 | 6029.91 |   3722.19 


*Discussion des résultats*
La matrice est stockée en mémoire selon une certaine structure, dans ce cas-ci, par colonnes. Ainsi, une colonne représente une zone contiguë dans la mémoire RAM. Il est donc intéressant de parcourir autant de cycles que possible dans la direction de la colonne, car les lignes de cache stockent des mots de mémoire et sont accessibles de manière plus efficace. À chaque changement de colonne, il est nécessaire de recharger les lignes de cache pour rendre les données facilement accessibles. L'ordre j, k, i maximise l'utilisation des lignes de cache en se déplaçant de manière efficace à travers les colonnes, ce qui réduit le besoin de rechargement fréquent des lignes de cache. En revanche, les ordres i, k, j et k, i, j montrent des performances inférieures en raison d'une utilisation moins optimale des lignes de cache.


### OMP sur la meilleure boucle 

`make TestProduct.exe && OMP_NUM_THREADS=8 ./TestProduct.exe 1024`

  OMP_NUM         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------
1                 | 6282.41 |     4537.47    |    6202.61     |  4300.13
2                 | 5607.94 |     4858.8     |    5988.95     |  4256.72
3                 | 6264.07 |     4823.82    |    6193.08     |  4300.45
4                 | 6205.64 |     4464.51    |    6081.97     |  4080.79 
5                 | 6209.69 |     4822.64    |    5997.13     |  4180.64
6                 | 6175.06 |     4364.19    |    6112.08     |  4140.16
7                 | 6072.91 |     4400.89    |    5659.76     |  4315.25
8                 | 6092.66 |     4673.72    |    5849.07     |  3771.72




### Produit par blocs

`make TestProduct.exe && ./TestProduct.exe 1024`

  szBlock         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
origine (=max)    | 6230.24 |    4780.94     |    5998.09     |    4193.38
32                | 4300.61 |    4575.19     |    4553.19     |    4589.33
64                | 4713.88 |    4754.99     |    4654.22     |    4762.48
128               | 4615.6  |    4786.78     |    4587.3      |    4717.46
256               | 5235.73 |    5426.15     |    5208.26     |    5367.89
512               | 5675.55 |    5806.68     |    5689.2      |    5720.3
1024              | 6042.94 |    6183.97     |    5626.84     |    6036.12

*Discussion*
La multiplication par blocks faire gagner plus de performance en tant que les matrices sont grandes. Tandis que pour matrices petites, le méthode ne offre pas un gain de performance.

### Bloc + OMP
`make TestProduct.exe && OMP_NUM_THREADS=8 ./TestProduct.exe 1024`

  szBlock      | OMP_NUM | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)|
---------------|---------|---------|-------------------------------------------------|
#A.nbCols#     |  1      | 5650.92 |     5740.25    |     5665.85    |    5751.09    |
512            |  8      | 5677.53 |     5763.59    |     5693.31    |    5726.5     |
---------------|---------|---------|-------------------------------------------------|
Speed-up       |         |         |                |                |               |
---------------|---------|---------|-------------------------------------------------|

Les nouveaux cores n'ont pas produit une grande amélioration de la performance, en fait, elle est presque la même dans le deux cas. 


### Comparaison with BLAS
L'algorithme BLAS produit des résultats similaires à ceux de notre algorithme lorsque la taille des blocs est optimisée pour la taille des matrices. Cela garantit que les opérations de multiplication matricielle sont effectuées de manière efficace, en exploitant au mieux les caractéristiques des caches mémoire et en minimisant les accès à la mémoire principale. 

# Tips 

```
	env 
	OMP_NUM_THREADS=4 ./produitMatriceMatrice.exe
```

```
    $ for i in $(seq 1 4); do elap=$(OMP_NUM_THREADS=$i ./TestProductOmp.exe|grep "Temps CPU"|cut -d " " -f 7); echo -e "$i\t$elap"; done > timers.out
```
