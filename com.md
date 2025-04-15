# Commandes

  

## kubectl :

`
kubectl create deployment <nom du deploy> --image=<nom de l'image>
` 		**crée un deployment**

`
kubectl expose deployment <nom du deploy> --type=<type du service (mettre NodePort)> --port=<port sur lequel est exposé le service>
`		**expose un service**

possibilité d'ajouté le paramètre ` -f <nom du fichier>` pour créer un service ou déployé un deploy à partir d'un fichier

`kubectl get deployment` listes les deploy
`kubectl get pods` listes les pods
`kubectl get services` listes les services

## minikube :

`minikube start` lance un cluster
`minikube dashboard` affiche le dashboard des services

`kubectl get services` listes les services
