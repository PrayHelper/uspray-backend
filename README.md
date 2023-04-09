# prayhelper-backend

## 🌿 With 
```
Flask
PostgreSQL
Swagger
Docker
```
<br />

## ❓ How to run server
```
docker compose -f docker-compose.dev.yml up --build
docker compose -f docker-compose.prod.yml up --build
```
에러가 난다? 
```
export DOCKER_DEFAULT_PLATFORM=linux/amd64
``` 


<br /><br />
## ❗️ 유의할 점
- [ ] 애플리케이션 팩토리 사용하기
- [ ] config 패키지화 하기
- [X] 뷰 데코레이터 사용하기 
- [X] 에러핸들러 사용하기
- [ ] TDD 도입하기
- [ ] Type int 사용하기
- [ ] DTO & DAO 사용하기

<br /><br />
## ❗️ 변수명 작성 방법
클래스나 메소드명은 파스칼 표기법을 따른다.(모든 단어에서 첫 문자는 대문자 나머지는 소문자)
> ex) HelloWordl, NameViva

변수, 파라미터 등은 카멜 표기법을 따른다.
> ex) helloWorld, nameViva

메서드 이름은 동사/전치사로 시작한다.
> ex) countNumber, withUserId

상수는 대문자로 작성하고 복합어인 경우 '_'를 사용하여 단어를 구분한다.
> ex) public final int SPECIAL_NUMBER = 1;

<br /><br />
## requirement txt upload
pip freeze > requirements.txt

<br /><br />

## 배포 환경에서 migration 방법
새 터미널 열고 가상환경 켜기 
```
config/development.py의  host='db:5432'를  host='localhost:5432'로 바꾸기
export DOCKER_DEFAULT_PLATFORM=linux/amd64하기 
flask db migrate
flask db upgrade하기 
```
