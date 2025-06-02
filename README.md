# OPENCLASSROOMS - Parcours Data Scientist - Projet n°8
# Réalisez un dashboard et assurez une veille technique - 40 h

------------------------------
## Mission - Concevez un dashboard de credit scoring
------------------------------

Vous êtes Data Scientist au sein d'une société financière, nommée **"Prêt à dépenser"**, qui propose des crédits à la consommation pour des personnes ayant peu ou pas du tout d'historique de prêt.

Vous venez de mettre en œuvre un outil de “scoring crédit” pour calculer la probabilité qu’un client rembourse son crédit, et classifier la demande en crédit accordé ou refusé.  

Les chargés de relation client ont fait remonter le fait que les clients sont de plus en plus demandeurs de transparence vis-à-vis des décisions d’octroi de crédit. 

Prêt à dépenser décide donc de développer un **dashboard interactif** pour que les chargés de relation client puissent expliquer de façon la plus transparente possible les décisions d’octroi de crédit, lors de rendez-vous avec eux. Cette volonté de transparence va tout à fait dans le sens des valeurs que l’entreprise veut incarner.

Michaël vous a envoyé un mail pour vous préciser ses attentes et ses conseils.

*Bonjour,*

*Bravo pour la réalisation de l’outil de scoring et ta présentation à l’équipe. Tu as assuré !*

*Maintenant nous souhaitons utiliser l’API pour réaliser un dashboard à destination de nos chargés de relation client. Ils le réclament depuis longtemps afin de pouvoir mieux expliquer à leurs clients les décisions, et parfois les revoir si nécessaire.* 

*Voici les spécifications pour le **dashboard interactif** :* 
* *Permettre de visualiser le score, sa probabilité (est-il loin du seuil ?) et l’interprétation de ce score pour chaque client de façon intelligible pour une personne non experte en data science.*
* *Permettre de visualiser les principales informations descriptives relatives à un client.*
* *Permettre de comparer, à l’aide de graphiques, les principales informations descriptives relatives à un client à l’ensemble des clients ou à un groupe de clients similaires (via un système de filtre : par exemple, liste déroulante des principales variables).*
* *Prendre en compte le besoin des personnes en situation de handicap dans la réalisation des graphiques, en couvrant des critères d'accessibilité du WCAG.*
* *Déployer le dashboard sur une plateforme Cloud, afin qu'il soit accessible pour d'autres utilisateurs sur leur poste de travail.*
* *Optionnellement (si tu as le temps) : Permettre d’obtenir un score et une probabilité rafraîchis après avoir saisi une modification d’une ou plusieurs informations relatives à un client, ainsi que de saisir un nouveau dossier client pour en obtenir le score et la probabilité.*
 
*C’est une première itération que nous présenterons aux chargés de relation client pour nous assurer que nous répondons à leur besoin.*

*Je te propose d’utiliser Dash ou Bokeh ou Streamlit pour réaliser ce dashboard interactif. Ce dashboard appellera l’API de prédiction que tu as déjà réalisée pour déterminer la probabilité et la classe (accord ou refus) d’un client.*

*Bon courage !*

*Mickael*

------------------------------
## Mission - Réalisez une veille technique
------------------------------

Vous avez bien avancé dans la réalisation du dashboard, alors Michaël décide de vous confier une autre mission.

*Bonjour,*

*Merci encore pour tout ce que tu as fait jusqu’à maintenant ! J’ai vu que tu as travaillé sur de nombreux sujets chez nous en plus de celui-ci, en particulier sur des problématiques de données texte (NLP) et de données d’images.*

*Tu sais que nous sommes soucieux de mettre en œuvre les dernières techniques en data science sur ces deux thématiques. Pourrais-tu réaliser un état de l’art sur une technique récente de modélisation de données texte ou de données image, l’analyser, la tester et la comparer à une approche plus classique que tu as réalisée précédemment ?*

*Concrètement, voici ce que j’attends de ta part :*
* *L’état de l’art devra concerner une technique datant de moins de 5 ans, présentée dans un article.*
* *La technique doit être référencée sur des sites de recherche (Arxiv), des sites connus (par exemple fastml, machine learning mastery, kdnuggets, import AI, MIT tech review, MIT news ML) ou des newsletters de qualité comme data elixir et data science weekly.*
* *Tu réaliseras et nous présenteras une preuve de concept qui met en oeuvre cette nouvelle technique avec les données texte ou image que tu as déjà exploitées précédemment.*
* *Tu nous expliqueras rapidement les concepts et techniques dans une note méthodologique (modèle en pièce-jointe) et lors d’une présentation.*

*Je suis convaincu que ta curiosité nous permettra de découvrir de nouvelles techniques performantes.*

*Merci par avance !*

*Mickael*

------------------------------
## Source 
------------------------------

Les données sont disponibles à l’adresse suivante : 

[Lien](https://s3-eu-west-1.amazonaws.com/static.oc-static.com/prod/courses/files/Parcours_data_scientist/Projet+-+Impl%C3%A9menter+un+mod%C3%A8le+de+scoring/Projet+Mise+en+prod+-+home-credit-default-risk.zip)


------------------------------
## Objectifs pédagogiques
------------------------------

  * Réaliser la présentation orale d'une démarche de modélisation à un client interne/externe
  * Réaliser une veille sur les outils et tendances en data science et IA
  * Réaliser un tableau de bord afin de présenter son travail de modélisation à un public
  * Rédiger une note méthodologique afin de communiquer sa démarche de modélisation
