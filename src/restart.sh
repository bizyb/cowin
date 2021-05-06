docker-compose down -v
git pull origin master
docker-compose up --force-recreate --build -d