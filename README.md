# 🤖 AI 데이터 분석 비서

> **자연어로 묻고, AI가 분석하고, 시각화로 답하다**

LangChain과 Gradio를 기반으로 한 지능형 데이터 분석 시스템입니다. 사용자는 자연어로 질문하면 AI가 데이터베이스를 조회하거나 Excel 파일을 분석하여 시각화된 결과를 제공합니다.

## 🎯 주요 기능

- 🗣️ **자연어 질의**: SQL 없이 일상 언어로 데이터 질문
- ⚡ **즉시 분석**: 5초 내 분석 결과 제공  
- 📊 **자동 시각화**: 데이터 특성에 맞는 차트 자동 생성
- 🔄 **대화형 UI**: 연속 질문으로 심화 분석

## 🏗️ 기술 스택

- **Frontend**: Gradio 4.0+, Plotly
- **AI Engine**: LangChain, OpenAI GPT-4
- **Data**: Pandas, SQLAlchemy
- **Database**: PostgreSQL, Redis
- **Deployment**: Docker, Gradio Cloud

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 리포지토리 클론
git clone <repository-url>
cd ai-data-analyst

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# 환경 변수 파일 생성
cp env.example .env

# .env 파일 편집하여 실제 값 설정
# - OPENAI_API_KEY: OpenAI API 키
# - DATABASE_URL: 데이터베이스 연결 문자열
# - 기타 필요한 설정들
```

### 3. 애플리케이션 실행

```bash
# 개발 서버 실행
python app/main.py
```

브라우저에서 `http://localhost:7860` 접속

## 📁 프로젝트 구조

```
ai-data-analyst/
├── app/                    # 메인 애플리케이션
│   ├── config/            # 설정 관리
│   ├── core/              # 핵심 비즈니스 로직
│   ├── services/          # 외부 서비스 연동
│   ├── models/            # 데이터 모델
│   ├── utils/             # 유틸리티 함수
│   ├── ui/                # UI 컴포넌트
│   └── main.py            # 애플리케이션 엔트리포인트
├── tests/                 # 테스트 코드
├── docs/                  # 문서
├── scripts/               # 유틸리티 스크립트
├── requirements.txt       # Python 의존성
└── README.md             # 프로젝트 설명
```

## 📋 개발 상태

현재 **Week 0 (개발 환경 구축)** 단계입니다.

### ✅ 완료된 작업
- [x] 프로젝트 구조 생성
- [x] 기본 설정 파일 작성
- [x] Gradio 기본 애플리케이션 구성

### 🚧 진행 예정
- [ ] Week 1: Gradio UI 기본 구성
- [ ] Week 2: LangChain 통합 및 AI 연동
- [ ] Week 3: SQL 데이터베이스 연동
- [ ] Week 4: Excel 파일 분석 구현
- [ ] Week 5: 시각화 엔진 구현
- [ ] Week 6: 성능 최적화 및 안정성
- [ ] Week 7: 테스트 및 문서화
- [ ] Week 8: 배포 및 MVP 런칭

## 📚 문서

- [📋 PRD (제품 요구사항)](./PRD_LLM_Data_Analysis_Service.md)
- [🏗️ 시스템 설계 문서](./System_Design_Document.md)
- [🎨 UI 와이어프레임](./gradio_ui_wireframe.svg)
- [✅ 개발 체크리스트](./Development_Checklist.md)

## 🤝 기여하기

1. 이슈를 확인하거나 새로운 이슈를 생성하세요
2. 기능 브랜치를 생성하세요 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋하세요 (`git commit -m 'feat: Add amazing feature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성하세요

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 👥 팀

**AI 데이터 분석 비서 개발팀**

---

*"데이터의 힘을 모든 사람에게"* 🌟