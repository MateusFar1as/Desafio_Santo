A tecnologia utilizada no desafio foi o python3.11.3 com os packages no requirements.txt, Containers Docker e o mysqlworkbench.

Primeiro, criei o banco de dados no MySQL Workbench com os dados do CSV. Após isso, identifiquei quais pacotes seriam necessários para completar o desafio.
Conectei o Python com o banco de dados utilizando o SQLAlchemy e, em seguida, parti para a criação das rotas utilizando o FastAPI. 
Criei a estrutura das rotas e as preenchi com as tarefas propostas. Após terminar as rotas, comecei a criação dos testes com o pytest, utilizando o TestClient fornecido pelo próprio FastAPI. Quando completado, utilizei o pytest --cov para mostrar a porcentagem de cobertura de testes. Como o FastAPI já possui um Swagger pronto em /docs, não precisei me preocupar com essa parte. 
Em seguida, exportei o esquema do MySQL e comecei a configurar o Dockerfile tanto para o Python quanto para o MySQL. Então, fiz o docker-compose para utilizar os dois containers em conjunto.

Para subir a API será usado o comando: docker-compose up
Após o container estar levantado o swagger da API estara no http://localhost:8000/docs
No terminal irá aparecer o porcentual da cobertura de testes