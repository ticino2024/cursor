# Docker 실행 가이드 (Korean)

## 문제 해결됨! ✅

Docker 실행 시 발생했던 Alembic 마이그레이션 오류가 모두 수정되었습니다.

### 수정된 문제들

1. ✅ **Alembic async 드라이버 오류** - 동기 마이그레이션으로 변경
2. ✅ **SECRET_KEY 경고** - 기본값 추가 (프로덕션에서는 변경 필요)
3. ✅ **초기 마이그레이션 생성** - users 테이블 스키마 포함
4. ✅ **Docker 설정** - .env 파일 자동 생성

## 빠른 시작

### 1. 서비스 시작
```bash
# 모든 서비스 시작 (PostgreSQL, Redis, API)
docker-compose up -d

# 로그 확인
docker-compose logs -f api
```

### 2. 샘플 데이터 생성 (선택사항)
```bash
# 샘플 유저 생성 (admin, user, moderator)
docker-compose exec api python scripts/init_db.py
```

### 3. API 접속
- **Swagger 문서**: http://localhost:8000/api/docs
- **API 엔드포인트**: http://localhost:8000/api/v1/

### 4. 테스트

#### 헬스 체크
```bash
curl http://localhost:8000/api/v1/health
```

#### 사용자 등록
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "홍길동",
    "password": "Secure123!@#"
  }'
```

#### 로그인
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "Secure123!@#"
  }'
```

## 샘플 계정 (init_db 실행 후)

- **관리자**: admin@example.com / Admin123!@#
- **일반사용자**: user@example.com / User123!@#
- **모더레이터**: moderator@example.com / Mod123!@#

## 주요 명령어

```bash
# 서비스 시작
docker-compose up -d

# 서비스 중지
docker-compose down

# 로그 보기
docker-compose logs -f api

# 서비스 재시작
docker-compose restart api

# 데이터베이스 접속
docker-compose exec postgres psql -U user -d userdb

# Redis 접속
docker-compose exec redis redis-cli

# 마이그레이션 실행
docker-compose exec api alembic upgrade head
```

## 문제 해결

### 서비스가 시작되지 않는 경우
```bash
# 로그 확인
docker-compose logs -f

# 서비스 재시작
docker-compose restart

# 완전히 재시작 (모든 데이터 삭제)
docker-compose down -v
docker-compose up -d
```

### 포트 충돌
```bash
# 사용 중인 포트 확인
lsof -i :8000  # API
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# docker-compose.yml에서 포트 변경
# 예: "8000:8000" → "8001:8000"
```

## 프로덕션 배포 전 체크리스트

- [ ] SECRET_KEY 변경
  ```bash
  docker-compose exec api python scripts/generate_secret.py
  # 생성된 키를 .env 파일에 업데이트
  ```

- [ ] 환경 변수 설정
  ```env
  ENV=production
  DEBUG=False
  ```

- [ ] CORS 오리진 설정
  ```env
  ALLOWED_ORIGINS=https://yourdomain.com
  ```

- [ ] SSL/TLS 인증서 설정
- [ ] 데이터베이스 백업 전략 수립
- [ ] 모니터링 및 로깅 설정

## 기술 스택

- **FastAPI** - 웹 프레임워크
- **PostgreSQL** - 데이터베이스
- **Redis** - 캐싱 및 속도 제한
- **SQLAlchemy** - ORM
- **Alembic** - 데이터베이스 마이그레이션
- **JWT** - 인증
- **Docker** - 컨테이너화

## 추가 문서

- **README.md** - 전체 문서 (영문)
- **QUICKSTART.md** - 빠른 시작 가이드
- **TROUBLESHOOTING.md** - 문제 해결 가이드
- **FIXES_APPLIED.md** - 적용된 수정사항
- **QUICK_REFERENCE.md** - 빠른 참조

## 지원

문제가 발생하면 **TROUBLESHOOTING.md** 문서를 참조하세요.
