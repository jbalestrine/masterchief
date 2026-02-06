# (optional) pull to see errors
docker pull inspircd/inspircd-docker:latest

# run via feature
Invoke-RestMethod -Uri 'http://127.0.0.1:8080/feature/run/app_installer.feature_install_docker' -Method Post -Body '{"app":"inspircd","docker_image":"inspircd/inspircd-docker:latest","ports":["6667:6667"]}' -ContentType 'application/json'

# poll status
Invoke-RestMethod -Uri 'http://127.0.0.1:8080/feature/run/app_installer.feature_install_status' -Method Post -Body '{"app":"inspircd"}' -ContentType 'application/json'

# check container via Docker
docker ps -a
docker logs inspircd