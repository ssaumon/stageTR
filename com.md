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



l'application crée des VM de deux types : Edge et IoT. une fois que ces VM sont créées, elles doivent communiquer entre elles

il faut que sur les VM Edge que je crée je mette K3S en mode master et sur les VM IoT 


création d'un executable qui verifie les dépendances de l'appllication et qui lance flask


ansible
vagrantfile regarder pour automatiser la création de vm




