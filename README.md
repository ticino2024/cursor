# FastAPI Application

프로덕션 준비가 완료된 FastAPI 애플리케이션의 기본 구조입니다.

## 🚀 주요 기능

- **FastAPI 프레임워크**: 높은 성능과 자동 문서화
- **모듈화된 구조**: 확장 가능하고 유지보수가 쉬운 아키텍처
- **Pydantic 모델**: 타입 검증과 데이터 직렬화
- **CORS 지원**: 크로스 오리진 요청 처리
- **환경 변수 관리**: `.env` 파일을 통한 설정 관리
- **미들웨어**: 로깅, 요청 ID, 처리 시간 측정
- **RESTful API**: Users와 Items 엔드포인트 예제
- **서비스 레이어**: 비즈니스 로직 분리
- **자동 API 문서**: Swagger UI와 ReDoc

## 📁 프로젝트 구조

```
.
├── app/
│   ├── api/                  # API 엔드포인트
│   │   └── v1/
│   │       ├── endpoints/    # 각 리소스별 엔드포인트
│   │       │   ├── users.py
│   │       │   └── items.py
│   │       └── router.py     # API 라우터 결합
│   ├── core/                 # 핵심 설정 및 미들웨어
│   │   ├── config.py         # 애플리케이션 설정
│   │   └── middleware.py     # 커스텀 미들웨어
│   ├── models/               # 데이터 모델
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/              # Pydantic 스키마
│   │   ├── user.py
│   │   └── item.py
│   ├── services/             # 비즈니스 로직
│   │   ├── user_service.py
│   │   └── item_service.py
│   └── main.py              # FastAPI 애플리케이션 진입점
├── tests/                   # 테스트 코드
├── .env.example             # 환경 변수 예제
├── requirements.txt         # Python 의존성
└── README.md               # 프로젝트 문서
```

## 🛠️ 설치 방법

### 1. 저장소 클론
```bash
git clone <repository-url>
cd fastapi-app
```

### 2. 가상 환경 생성 및 활성화
```bash
# Python 가상 환경 생성
python -m venv venv

# 활성화 (Linux/Mac)
source venv/bin/activate

# 활성화 (Windows)
venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일을 열어 필요한 설정 수정
```

## 🚀 실행 방법

### 개발 서버 실행
```bash
# Uvicorn으로 실행 (자동 리로드 활성화)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 Python으로 직접 실행
python run.py
```

### 프로덕션 서버 실행
```bash
# Gunicorn + Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📖 API 문서

서버를 실행한 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 🔍 API 엔드포인트

### Users
- `GET /api/v1/users` - 사용자 목록 조회
- `GET /api/v1/users/{user_id}` - 특정 사용자 조회
- `POST /api/v1/users` - 새 사용자 생성
- `PUT /api/v1/users/{user_id}` - 사용자 정보 수정
- `DELETE /api/v1/users/{user_id}` - 사용자 삭제
- `POST /api/v1/users/login` - 사용자 로그인
- `GET /api/v1/users/me/profile` - 현재 사용자 프로필

### Items
- `GET /api/v1/items` - 아이템 목록 조회
- `GET /api/v1/items/{item_id}` - 특정 아이템 조회
- `POST /api/v1/items` - 새 아이템 생성
- `PUT /api/v1/items/{item_id}` - 아이템 정보 수정
- `DELETE /api/v1/items/{item_id}` - 아이템 삭제
- `GET /api/v1/items/search` - 아이템 검색
- `GET /api/v1/items/category/{category}` - 카테고리별 아이템 조회

## 🧪 테스트

```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=app tests/

# 특정 테스트 파일 실행
pytest tests/test_users.py
```

## 🔧 개발 도구

### 코드 포맷팅
```bash
# Black으로 코드 포맷팅
black app/

# isort로 import 정렬
isort app/
```

### 린팅
```bash
# Flake8로 코드 스타일 검사
flake8 app/

# MyPy로 타입 검사
mypy app/
```

## 📦 추가 기능 구현 가이드

### 데이터베이스 연결
1. `requirements.txt`에서 데이터베이스 드라이버 주석 해제
2. `.env` 파일에 `DATABASE_URL` 설정
3. SQLAlchemy 모델 생성
4. Alembic으로 마이그레이션 관리

### 인증/인가
1. JWT 라이브러리 설치 (requirements.txt 참조)
2. 인증 미들웨어 구현
3. 보호된 엔드포인트에 의존성 주입

### Redis 캐싱
1. Redis 라이브러리 설치
2. `.env`에 `REDIS_URL` 설정
3. 캐싱 데코레이터 구현

## 🐳 Docker 지원

### Dockerfile 예제
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose 예제
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env
```

## 📝 라이선스

MIT License

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 💬 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 Issue를 생성해주세요.