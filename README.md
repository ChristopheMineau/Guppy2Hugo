# Guppy2Hugo
Some Tooling to translate a Guppy CMS site to a Hugo static site
___
Des outils pour convertir un site web [Guppy CMS](https://www.freeguppy.org/) en un site statique [Hugo](https://gohugo.io/).

# Documentation
Je poursuis cette documentation uniquement en français, je pense que la majorité des utilisateurs de Guppy sont de langue française.  
In case you need an English translation, please try an automated translator, and you can also post an issue here, in English, I will answer you.

# Pourquoi ce projet
Ce projet est un travail personnel qui n'a pas vocation à être universel et traiter tous les cas de figures d'un site Guppy.
J'ai développé cet outil pour convertir mon site datant déjà d'une 12aine d'années et qui devenait vieillissant. La taille grossissante du site, le nombre de photos et documents qu'il contenait amenait de forts ralentissements au chargement des pages.
Dernièrement, j'avais un peu délaissé les mises à jour de mon site, faute de temps car à vrai dire, la rédaction d'un article bien documenté avec des photos commentées, des vidéos, et en deux langues, prenait sous Guppy un certain temps.


J'ai cherché assez longtemps vers quelle solution je pouvais me tourner et j'ai opté pour la soltion d'un site statique -c'est à dire sans php ni base de donnée- ce qui procure une excellente réactivité.
[Hugo](https://gohugo.io/) est une solution qui a atteint une bonne maturité et qui possède une communauté déjà assez vaste pour trouver de l'aide et de la documentation sans problème.
Les deux grandes qualités que j'y trouve sont :
- organisation des données en répertoires correspondant à l'organisation arborescente des menus, avec un répertoire par article dans lequel on peut mettre tous les documents et médias associés à l'article.
Les données sont stockées avec l'article dans un seul répertoire, aucune gestion supplémentaire n'est nécessaire.
- Génération des articles au format MD. Ce format est simplissime et permet de rédiger très rapidement et très simplement des contenus sans aucun souci de mise en page (comme le présent texte par exemple). Un fichier par langue.

Ainsi, la rédaction d'un nouvel article sous Hugo se limite aux choses extêmement simples suivantes :
- ```hugo new chemin/chemin/mon article/_index.md```
- coller les photos et documents dans le répertoire chemin/chemin/mon article/
- ouvrir _index.md et taper son code md
- et c'est tout !
- mieux encore, on démarre le serveur local de hugo : hugo serveur -D
et on peut visualiser en direct tous les changement apportés, à chaque fois que l'on sauvegarde son travail.

Par contre, le choix d'une solution statique limite les fonctionnalités utilisables, si l'on veut comparer à Guppy. Il n'est pas possible d'implémenter avec Hugo un forum par exemple.
# Fonctionalités
Voici les fonctionalités que j'utilisais sous Guppy et qui ont toutes étées portées sous Hugo :
- Articles : Les articles deviennent des pages Hugo. L'arborescence des articles dans Hugo est calquée sur l'arborescence des menus dans Guppy.
Tous les fichiers utilisés par l'article sont déplacés dans le répertoire de l'article.
- News : Elles sont placées de même sous la catégorie Blog
- Téléchargements : Sont créés sous forme d'articles. Les fichiers sont déplacés dans le répertoire de l'article.
- Galleries : toutes les galleries Guppy sont transportées sans un répertoire Galleries navigable. Les fonctionalités des galleries guppy, avec commentaires, vignettes optionnelles, sont rendures.
- Vidéos : le code des vidéos embarquées est détecté et adapté au format md de Hugo.
- Audio : de même, les balises audio sont adaptées
- Liens internes : tous les liens internes pointant vers un article ou une news Guppy sont transformés vers l'url pointant sur le même article dans Hugo.
- Commentaires utilisateur : Les commentaires utilisateurs sont récupérés et ajoutés en fin de chaque article. 
- Livre d'or : le livre d'or est récupéré et transformé en commentaire que l'on peut insérer où on le veut, en bas de la page home ou dans la page about par exemple ou dans une nouvelle page livre d'or si on préfère.
- Les noms de répertoires principaux sont transformés en catégories associées aux articles et news. Les tags sont récupérés et ajoutés comme tags aux pages Hugo.
La navigation par catégorie / tag / ou autre taxonomies (voir doc Hugo) est un concept très moderne et bien valorisé par la pluspart des thèmes Hugo.
- URL rewriting : le script génère les directives d'url rewriting à insérer dans le .htaccess du nouveau site de manière à faire pointer les anciennes URL Guppy vers les nouvelles Hugo (pour les articles seulement).

# Comment faire
- Il vous faut une installation récente de Python 3
- au préalable, lire la doc, regarder les vidéos, essayer de bien maîtriser Hugo avant de commencer, c'est indispensable. Choisir un thème qui convienne à vos besoin. J'ai choisi "Future-imperfect-slim" personnellement.
- créer un répertoire de travail et y ramener les répertoires essentiels de Guppy qui contiennent les données et images nécessaires pour la recopie.
- cloner ce repo dans ce répertoire travail. L'organisation doit ressembler à :
* travail
  * file
  * data
  * img
  * inc
  * pages
  * photos
  * skins
  * Guppy2Hugo/gyppy2hugo.py


- Dans un terminal dans ce répertoire, simplement lancer :  
``` python Guppy2Hugo/guppy2hugo.py```

Le script va créer le répertoire content avec l'arborescence nécessaire et déplacer toutes les ressources utiles vers ce répertoire content.

Le script affiche en résultat un récapitulatif au format CSV des articles, news, galleries, téléchargements crées. On peu aisément conserver ces données dans un tableur ce qui donne une cartographie du site très pratique pour tester les différentes pages et fonctionalités.
La dernière partie des informations affichées représente le code du livre d'or, à conserver et insérer dans une page à sa convenance, home par exemple.

Le répertoire content sera ensuite à intégrer dans votre site Hugo, voir la doc Hugo pour comprendre ce qu'est le répertoire content.
Le script génère du code en utilisant des shortcodes spécifiques, ceux ci se trouvent dans le répertoire layouts fourni avec ce projet, ainsi que quelques styles nécessaires dans le répertoire static.

Enfin, le script génère une section à insérer dans votre fichier .htaccess et qui permet de faire pointer les anciennes URL Guppy vers les nouvelles url correspondantes du site Hugo. Ainsi, vous ne perdrez pas votre référencement Google et toutes les adresses que vous avez pu partager dans les réseaux sociaux ou forums restent valides.

# Limitations du support
Il va de soit que je partage ici un travail personnel qui m'a permis de convertir mon site [La Belle Note](https://www.labellenote.fr) et que vos besoins sont sans doute différents des miens.
Je vous laisse libre de forker ce projet et de le faire évoluer à votre guise.
Il est bien sûr nécessaire d'avoir une bonne connaissance du développement en Python, et du développement web en général, ainsi que de Hugo et Guppy.
Je serai ravi de répondre à vos questions, mais je n'apporterai pas de support à vos projets de conversion, faute de temps.

Bon courage !






