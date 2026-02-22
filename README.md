# Redis로 보안성이 강화된 JWT 인증 서버
**Redis를 통해 Refresh Token Rotation과 Blacklist를 적용하여 토큰을 관리하고 공격에 대응하는 JWT 인증 서버 개발**

## 💻프로젝트 개요
### 프로젝트 목표
- Redis를 이용해 보안성이 높은 JWT 인증 기능 개발
- Refresh Token Rotation과 Blacklist 적용
### Tech Stack
- Language: Python 3.14
- Framework: FastAPI
- Database: MySQL 8.0
- In-memory Data Store: Redis 3.0.5
### Development & Testing
- Dependency Management: Poetry
- Testing: pytest

## 🛠️프로젝트 세팅 및 실행
1. 의존성 설치
   ```bash
   poetry install
   ```
2. 환경변수 파일 세팅
   `.env.example` 파일 참고하여 같은 위치에 `.env.dev` 파일 생성 (환경 별로 다른 환경 변수 파일 쓰고 싶은 경우 .env.* 패턴으로 만들기)
   ```bash
   # 실행 환경 설정 분기
   DEBUG_MODE=True

   # DB 설정
   DB_USERNAME=your_db_username
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=your_db_port
   DB_NAME=your_db_name

   # JWT 설정
   JWT_SECRET_KEY=your_jwt_secret_key
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7

   # Redis 설정
   REDIS_URL=your_redis_url
   REDIS_PORT=your_redis_port
   REDIS_DB=0
   ```
3. 실행 및 테스트
   - 서버 실행
     ```bash
     uvicorn app.main:app
     ```
     - 환경변수 ENV 지정하여 읽고 싶은 환경변수 파일 지정 가능
     - ENV 없는 경우 디폴트로 dev 설정으로 서버 실행
     - 만약 .env.test 파일을 읽고 싶은 경우 ENV=test 설정으로 실행
       ```bash
       // Mac, Linux
       ENV=test uvicorn main:app
       ```
    - 테스트 실행
      ```bash
      // 테스트 전체 실행
      pytest

      // 유닛 테스트만 실행
      pytest tests/unit

      // 통합 테스트만 실행
      pytest tests/integration
      ```
