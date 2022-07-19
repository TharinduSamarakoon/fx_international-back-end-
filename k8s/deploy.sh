gcloud builds submit --project first-fuze-348014 --tag gcr.io/first-fuze-348014/fi-api:latest ../

gcloud container clusters get-credentials forex-international --region us-central1 --project first-fuze-348014

kubectl delete deployment --ignore-not-found=true fi-api

kubectl apply -f deployment.yml