# 목표 달성 예상 시스템 (Goal Projection System)

## 개요
체중과 체지방률을 추적하고, 3일 Moving Average를 기반으로 목표 달성 예상일을 계산하는 시스템입니다.

## 주요 기능

### 1. 체중/체지방률 기록
- **일별 체중 기록**: 날짜별로 체중(kg)과 체지방률(%)을 기록
- **메모 기능**: 각 기록에 메모 추가 가능
- **자동 업데이트**: 같은 날짜에 재입력하면 자동으로 업데이트

### 2. 3일 Moving Average 계산
- 최근 3일간의 데이터를 평균하여 일일 변동성을 제거
- 더 정확한 추세 파악 가능
- 수분 섭취량, 소금 섭취 등으로 인한 일시적 체중 변화 보정

### 3. 일일 변화율 계산
```
일일 체중 변화율 = (최근 7일간 체중 변화) / 7
일일 칼로리 deficit = analytics에서 계산된 평균 deficit
```

### 4. 목표 달성 예상 계산 (개선된 과학적 모델)

#### Method 1: 실제 체중 변화 기반
- 최근 7일간의 실제 체중 변화율을 사용
- 측정된 추세가 목표 방향과 일치하는 경우만 계산

#### Method 2: 개선된 칼로리 Deficit 기반 (Forbes + Hall Model)
```
과학적 공식 (개선됨):

1. 체지방률 기반 에너지 밀도 (Forbes Equation):
   Energy Density = 1020 / (1 - (체지방률 / 100))
   
   예시:
   - 체지방률 25%: 1,360 kcal/kg
   - 체지방률 15%: 1,200 kcal/kg
   - 없으면 기본값: 7,700 kcal/kg

2. 대사 적응 (Hall Model):
   - 첫 4주: 적응 없음 (100%)
   - 4-12주: 점진적 적응 (100% → 90%)
   - 12주 이후: 최대 10% 대사율 감소
   
   Adaptation Factor = 1.0 - (min(days_over_28 / 56, 1.0) * 0.10)

3. 조정된 예측:
   Adjusted Deficit = Daily Deficit × Adaptation Factor
   Daily kg Change = Adjusted Deficit / Energy Density
   
   예상 달성일 = 현재 + (목표까지 kg / Daily kg Change)
```

**왜 개선되었나?**
- ✅ 체지방률 고려: 체지방이 많을수록 더 많은 칼로리 필요
- ✅ 대사 적응 반영: 장기 다이어트 시 대사율 감소
- ✅ 개인화: 각자의 신체 구성에 맞는 예측
- ✅ 과학적 근거: NIH/Lancet 연구 기반

### 5. 시각화

#### Historical Data (실제 기록)
- **파란색 선**: 실제 체중
- **보라색 선**: 3일 Moving Average
- **초록색 점선**: 목표 체중 (Reference Line)

#### Projection Data (미래 예측)
- **주황색 점선**: 예상 체중
- 현재 추세가 계속된다고 가정
- 최대 180일까지 표시

## 데이터베이스 스키마

### weight_logs 테이블
```sql
CREATE TABLE weight_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    date DATE NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL,
    body_fat_percentage DECIMAL(4,1),
    notes TEXT,
    created_at TIMESTAMP,
    UNIQUE(user_id, date)
);
```

### user_profiles 추가 필드
```sql
ALTER TABLE user_profiles ADD COLUMN:
- target_weight_kg DECIMAL(5,2)
- target_body_fat_percentage DECIMAL(4,1)
```

## API 엔드포인트

### Weight Tracking
```
POST   /api/weight/log              - 체중 기록 생성/업데이트
GET    /api/weight/logs?days=30     - 체중 기록 조회
PATCH  /api/weight/log/{id}         - 체중 기록 수정
DELETE /api/weight/log/{id}         - 체중 기록 삭제
PATCH  /api/weight/goals            - 목표 설정/수정
GET    /api/weight/projection       - 목표 달성 예상 조회
```

### Response Example: Projection
```json
{
  "current_weight": 75.2,
  "current_body_fat": 18.5,
  "target_weight": 70.0,
  "target_body_fat": 15.0,
  "moving_avg_weight": 75.1,
  "moving_avg_body_fat": 18.4,
  "daily_weight_change": -0.15,
  "daily_body_fat_change": -0.05,
  "avg_daily_deficit": 450.0,
  "estimated_days_to_goal": 34,
  "estimated_goal_date": "2026-03-20",
  "historical_data": [...],
  "projection_data": [...],
  "on_track": true,
  "message": "Keep up the good work!"
}
```

## 프론트엔드 컴포넌트

### 1. GoalProjectionChart
- 체중 추세 및 예상 그래프
- Historical + Projection 통합 시각화
- Recharts 사용

### 2. WeightLogForm
- 체중 기록 입력 폼
- 날짜, 체중, 체지방률, 메모

### 3. GoalSettingForm
- 목표 설정 폼
- 목표 체중, 목표 체지방률

### 4. Progress Page (`/progress`)
- 전체 시스템을 통합한 페이지
- 체중 기록 버튼
- 목표 설정 버튼
- GoalProjectionChart 표시

## 사용 방법

### 1. 데이터베이스 마이그레이션
```bash
# Supabase SQL Editor에서 실행
ADD_WEIGHT_TRACKING_AND_GOALS.sql
```

### 2. 백엔드 시작
```bash
cd backend
uvicorn app.main:app --reload
```

### 3. 프론트엔드 시작
```bash
cd frontend
npm run dev
```

### 4. 사용 시나리오

#### Step 1: 목표 설정
1. `/progress` 페이지 방문
2. "🎯 목표 설정" 버튼 클릭
3. 목표 체중 입력 (예: 70kg)
4. 목표 체지방률 입력 (선택사항, 예: 15%)

#### Step 2: 체중 기록
1. "⚖️ 체중 기록" 버튼 클릭
2. 날짜 선택 (기본값: 오늘)
3. 체중 입력 (예: 75.2kg)
4. 체지방률 입력 (선택사항, 예: 18.5%)
5. 메모 추가 (선택사항)

#### Step 3: 추세 확인
- 최소 3일 이상 기록하면 Moving Average 계산 시작
- 7일 이상 기록하면 더 정확한 예측 가능
- 그래프에서 현재 추세와 목표 달성 예상일 확인

#### Step 4: 칼로리 관리
- `/home` 페이지에서 일일 칼로리 수지 확인
- Deficit이 목표 방향과 일치하는지 확인
- 필요시 칼로리 섭취량 조정

## 계산 정확도 향상 팁

### 1. 측정 시간 일관성
- **추천**: 매일 아침, 화장실 다녀온 후, 식사 전
- 같은 시간에 측정하면 수분 변동 최소화

### 2. 측정 빈도
- **최소**: 주 3회 (Moving Average 계산을 위해)
- **권장**: 매일 (더 정확한 추세 파악)

### 3. 충분한 데이터
- 최소 7일 데이터 필요 (일일 변화율 계산)
- 14-30일 데이터 권장 (더 신뢰성 있는 예측)

### 4. 칼로리 기록의 정확성
- 음식 섭취량 정확히 기록
- 운동 칼로리 소모 기록
- 일일 TDEE가 정확해야 예측도 정확

## 과학적 근거

### 1. 7700 kcal = 1kg 공식
- 지방 1g = 9 kcal
- 체지방 1kg = 약 7700 kcal (수분 포함)
- 국제적으로 인정된 표준

### 2. Moving Average
- 단기 변동성 제거
- 추세 파악 용이
- 3일 = 단기 수분 변동 보정
- 7일 = 주간 패턴 반영

### 3. BMR & TDEE
- Mifflin-St Jeor 방정식 사용
- 성별, 나이, 키, 몸무게, 활동 레벨 고려
- 의학적으로 검증된 공식

## 주의사항

### 1. 예측의 한계
- 현재 추세가 계속된다고 가정
- 실제로는 대사율 변화, 운동량 변화 등으로 변동 가능
- **참고용으로만 사용**, 절대적 기준 아님

### 2. 건강 우선
- 급격한 체중 감량(주 1kg 이상)은 건강에 해로움
- 권장: 주 0.5kg 감량 (일일 500 kcal deficit)
- 의학적 조언은 전문의 상담

### 3. 데이터 품질
- "Garbage In, Garbage Out"
- 정확한 측정과 기록이 정확한 예측의 전제

## 향후 개선 계획

### Phase 2
- [ ] 체중 기록 리스트 뷰 (편집/삭제 가능)
- [ ] 주간/월간 리포트 생성
- [ ] 체지방률 변화 그래프 추가

### Phase 3
- [ ] 목표 달성 알림 (푸시 알림)
- [ ] 주간 진행 상황 이메일 리포트
- [ ] AI 기반 조언 (목표 달성을 위한 추천)

### Phase 4
- [ ] 체중 외 다른 지표 추적 (근육량, 골격근량 등)
- [ ] Inbody 데이터 연동
- [ ] 스마트 체중계 연동 (Bluetooth)

## 문제 해결

### Q: "Not enough data to project" 메시지가 나옵니다.
A: 최소 3일 이상의 체중 기록이 필요합니다. 체중을 더 기록해주세요.

### Q: 예상 날짜가 비현실적으로 나옵니다.
A: 최근 7일간의 칼로리 기록을 확인하세요. Deficit이 너무 크거나 작을 수 있습니다.

### Q: "Moving away from goal" 메시지가 나옵니다.
A: 현재 추세가 목표와 반대 방향입니다. 칼로리 섭취/소비를 조정하세요.

### Q: 그래프가 표시되지 않습니다.
A: 
1. 백엔드가 실행 중인지 확인
2. SQL 마이그레이션이 완료되었는지 확인
3. 브라우저 콘솔에서 에러 확인

## 참고 자료
- [Mifflin-St Jeor Equation](https://en.wikipedia.org/wiki/Basal_metabolic_rate)
- [7700 kcal per kg rule](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3302369/)
- [Moving Average](https://en.wikipedia.org/wiki/Moving_average)
