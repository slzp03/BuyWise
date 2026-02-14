"""
OpenAI API 서비스 모듈

후회 점수 기반 AI 소비 심리 분석 및 조언 생성
"""

import os
from typing import Dict, List, Optional
import json
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class OpenAIService:
    """OpenAI API 서비스 클래스"""

    def __init__(self):
        """초기화 및 API 키 확인"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '800'))

        if not self.api_key:
            raise ValueError(
                "❌ OPENAI_API_KEY가 설정되지 않았습니다.\n"
                ".env 파일에 OPENAI_API_KEY를 추가하거나\n"
                "환경 변수로 설정해주세요."
            )

        # OpenAI 클라이언트 초기화
        self.client = OpenAI(api_key=self.api_key)

    def is_api_key_valid(self) -> bool:
        """API 키 유효성 검사"""
        return bool(self.api_key and self.api_key.startswith('sk-'))

    def build_analysis_prompt(
        self,
        overall_score: float,
        total_purchases: int,
        total_amount: float,
        regret_ratio: float,
        main_cause: str,
        top_regret_items: List[Dict],
        category_breakdown: Dict,
        language: str = 'ko'
    ) -> str:
        """
        AI 분석용 프롬프트 생성

        Args:
            overall_score: 전체 후회 점수 (0-100)
            total_purchases: 총 구매 건수
            total_amount: 총 지출 금액
            regret_ratio: 후회 구매 비율 (%)
            main_cause: 주요 후회 원인
            top_regret_items: 상위 후회 구매 목록
            category_breakdown: 카테고리별 통계

        Returns:
            프롬프트 문자열
        """

        # 카테고리별 정보 포맷팅
        category_info = ""
        if category_breakdown:
            category_info = "\n".join([
                f"  - {cat}: {info['count']}건, 총 {info['amount']:,}원"
                for cat, info in list(category_breakdown.items())[:5]
            ])

        # 상위 후회 항목 포맷팅
        regret_items_info = ""
        if top_regret_items:
            regret_items_info = "\n".join([
                f"  {i+1}. {item['category']} - {item['product']} ({item['amount']:,}원, 후회점수: {item['score']:.1f})"
                for i, item in enumerate(top_regret_items[:5])
            ])

        prompt = f"""당신은 20년 경력의 소비 심리 전문가이자 재무 상담가입니다.
사용자의 구매 데이터를 분석하여 따뜻하고 공감적이면서도 전문적인 조언을 제공합니다.

# 분석 데이터

## 전체 개요
- **후회 점수**: {overall_score:.1f}/100
- **총 구매 건수**: {total_purchases}건
- **총 지출 금액**: ₩{total_amount:,.0f}
- **후회 구매 비율**: {regret_ratio:.1f}%
- **주요 후회 원인**: {main_cause}

## 카테고리별 분석
{category_info if category_info else "데이터 없음"}

## 후회 점수 높은 구매 TOP 5
{regret_items_info if regret_items_info else "데이터 없음"}

# 응답 형식

다음 형식으로 친근하고 공감적인 톤으로 응답하세요. 이모지를 적절히 사용하되 과하지 않게:

## 📊 당신의 소비 패턴 한눈에 보기
(2-3문장으로 전체적인 소비 패턴을 요약합니다. 비난하지 않고 팩트를 전달합니다.)

## 🔍 후회 구매의 주요 원인 3가지
1. **[원인 1 제목]**: [구체적인 설명과 패턴 분석]
2. **[원인 2 제목]**: [구체적인 설명과 패턴 분석]
3. **[원인 3 제목]**: [구체적인 설명과 패턴 분석]

## 💡 지금 바로 실천 가능한 개선 방안
1. **[방안 1 제목]**: [즉시 실천 가능한 구체적인 팁]
2. **[방안 2 제목]**: [습관 개선 제안]
3. **[방안 3 제목]**: [심리적 접근 방법]

## 🎯 이번 달 도전 과제
**목표**: [SMART 기준의 구체적이고 측정 가능한 목표 1개]
**실천 방법**: [목표 달성을 위한 3가지 작은 액션 아이템]

# 작성 가이드라인

1. **톤**: 친구 같은 상담사 톤. "~해요", "~이에요" 사용. 반말은 피함.
2. **비난 금지**: "잘못", "실수" 같은 부정적 단어 피함. "개선", "성장" 강조.
3. **구체성**: "조금만 줄이세요"가 아니라 "한 달에 2번 → 1번으로 줄여보세요" 같이 구체적.
4. **긍정적 강화**: 잘한 점이 있다면 먼저 칭찬.
5. **실천 가능성**: 거창한 목표보다 작고 구체적인 액션.
6. **공감**: 사용자의 감정을 이해하고 공감 표현 포함.
7. **길이**: 전체 500자 이내로 간결하게.

이제 위 데이터를 바탕으로 분석을 시작해주세요.
{chr(10) + "重要: 日本語で回答してください。~です、~ます体を使ってください。" if language == "ja" else ""}"""

        return prompt

    def generate_ai_feedback(
        self,
        overall_score: float,
        total_purchases: int,
        total_amount: float,
        regret_ratio: float,
        main_cause: str,
        top_regret_items: List[Dict] = None,
        category_breakdown: Dict = None,
        language: str = 'ko'
    ) -> Dict[str, str]:
        """
        AI 기반 소비 심리 분석 및 조언 생성

        Args:
            overall_score: 전체 후회 점수
            total_purchases: 총 구매 건수
            total_amount: 총 지출 금액
            regret_ratio: 후회 구매 비율
            main_cause: 주요 후회 원인
            top_regret_items: 상위 후회 구매 목록
            category_breakdown: 카테고리별 통계

        Returns:
            {
                'success': True/False,
                'feedback': AI 생성 피드백 텍스트,
                'error': 에러 메시지 (실패 시)
            }
        """

        if not self.is_api_key_valid():
            return {
                'success': False,
                'feedback': '',
                'error': 'OPENAI_API_KEY가 유효하지 않습니다. .env 파일을 확인해주세요.'
            }

        try:
            # 프롬프트 생성
            prompt = self.build_analysis_prompt(
                overall_score=overall_score,
                total_purchases=total_purchases,
                total_amount=total_amount,
                regret_ratio=regret_ratio,
                main_cause=main_cause,
                top_regret_items=top_regret_items or [],
                category_breakdown=category_breakdown or {},
                language=language
            )

            # 시스템 메시지 (언어별)
            if language == 'ja':
                system_msg = ("あなたは20年のキャリアを持つ消費心理の専門家であり、"
                              "ファイナンシャルアドバイザーです。"
                              "ユーザーに温かく共感的で実践可能なアドバイスを提供します。"
                              "日本語で回答してください。")
            else:
                system_msg = ("당신은 20년 경력의 소비 심리 전문가이자 재무 상담가입니다. "
                              "사용자에게 따뜻하고 공감적이면서도 실천 가능한 조언을 제공합니다.")

            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_msg
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1.0,
                frequency_penalty=0.3,
                presence_penalty=0.3
            )

            # 응답 추출
            feedback = response.choices[0].message.content.strip()

            # 토큰 사용량 로깅 (선택사항)
            usage = response.usage
            print(f"[OpenAI] API 호출 성공!")
            print(f"   - 모델: {self.model}")
            print(f"   - 입력 토큰: {usage.prompt_tokens}")
            print(f"   - 출력 토큰: {usage.completion_tokens}")
            print(f"   - 총 토큰: {usage.total_tokens}")

            return {
                'success': True,
                'feedback': feedback,
                'error': None,
                'usage': {
                    'prompt_tokens': usage.prompt_tokens,
                    'completion_tokens': usage.completion_tokens,
                    'total_tokens': usage.total_tokens
                }
            }

        except Exception as e:
            error_message = str(e)
            print(f"[OpenAI ERROR] API 호출 실패: {error_message}")

            return {
                'success': False,
                'feedback': '',
                'error': f"AI 분석 생성 중 오류 발생: {error_message}"
            }

    def build_smart_insights_prompt(
        self,
        overall_score: float,
        total_purchases: int,
        total_amount: float,
        target_items: list,
        category_spending: dict,
        category_breakdown: dict,
        language: str = 'ko'
    ) -> str:
        """스마트 인사이트 프롬프트 생성"""

        # 분석 대상 항목 포맷
        items_text = ""
        for i, item in enumerate(target_items, 1):
            items_text += (
                f"{i}. [{item['category']}] {item['product']} "
                f"- ₩{item['amount']:,} "
                f"(후회점수: {item['score']:.0f}, "
                f"필요도: {item['necessity']}, 사용빈도: {item['usage']})\n"
            )

        # 카테고리별 지출 포맷
        category_text = ""
        for cat, amount in category_spending.items():
            count = category_breakdown.get(cat, {}).get('count', 0)
            category_text += f"- {cat}: ₩{amount:,.0f} ({count}건)\n"

        prompt = f"""당신은 소비 데이터 분석 전문가입니다. 사용자의 구매 데이터를 기반으로 스마트 인사이트를 생성합니다.

# 분석 데이터

## 전체 개요
- 후회 점수: {overall_score:.1f}/100
- 총 구매 건수: {total_purchases}건
- 총 지출 금액: ₩{total_amount:,.0f}

## 분석 대상 구매 항목
{items_text}

## 카테고리별 지출
{category_text}

# 요청 사항

다음 4가지 인사이트를 정확히 아래 형식으로 작성하세요.

## 🏷️ 소비패턴 분류
각 항목의 소비 심리를 분류합니다.
- **[상품명]** (₩금액): [패턴 유형] - [한줄 설명]

패턴 유형 예시: 스트레스성 소비, 계획된 필수 소비, 충동적 보상 소비, 습관적 반복 소비, 사회적 압력 소비, 합리적 투자 소비

## 🔄 유사 사용자 재구매율
각 항목에 대해 유사 사용자의 추정 재구매율을 제시합니다.
- **[상품명]**: 재구매율 약 XX% → [한줄 해석]

필요도 대비 사용빈도가 낮으면 재구매율도 낮게 설정하세요. 현실적인 수치를 사용하세요.

## 💰 장기 저축 효과
카테고리별로 30% 지출 절감 시 연간 저축 효과를 제시합니다.
- **[카테고리]**: 월 평균 ₩XX → 30% 절감 시 연간 약 ₩XXX 저축 가능 + [한줄 코멘트]

## 🛒 추천 구매목록 TOP 5
소비 패턴과 실제 니즈를 분석하여 가치 있는 구매를 추천합니다.
반드시 실제 존재하는 브랜드와 모델명을 포함한 구체적인 상품을 추천하세요.

정확히 아래 형식으로 작성하세요 (줄바꿈 포함):
1. **[브랜드 + 구체적 상품명]** (예상 ₩가격): [추천 이유]
   → [쿠팡에서 보기](https://www.coupang.com/np/search?q=브랜드+상품명)

예시:
1. **소니 WH-1000XM5 헤드폰** (예상 ₩350,000): 기존 이어폰 대비 활용도 높음
   → [쿠팡에서 보기](https://www.coupang.com/np/search?q=소니+WH-1000XM5)
2. **샤오미 미밴드 8** (예상 ₩45,000): 저렴하면서 매일 착용 가능
   → [쿠팡에서 보기](https://www.coupang.com/np/search?q=샤오미+미밴드8)

추천 기준: 사용빈도가 높았던 카테고리의 업그레이드, 후회 구매를 대체할 대안, 충족되지 않은 니즈 해결
링크 작성 규칙: 쿠팡 검색 URL은 https://www.coupang.com/np/search?q= 뒤에 브랜드+상품명 검색어를 붙이세요. 공백은 +로 대체하세요.
중요: "고급 무선이어폰" 같은 일반적 표현 대신 "소니 WF-1000XM5" 처럼 실제 브랜드와 모델명을 사용하세요.

## 💡 절약 추천 TOP 5
후회 점수가 높은 구매 패턴을 분석하여, 불필요한 지출을 줄일 수 있는 구체적인 절약 방법을 추천합니다.
각 항목에 예상 월 절약 금액을 반드시 포함하세요.

형식:
1. **[절약 방법 제목]**: [구체적 실천 방안 1-2문장] → 예상 월 절약 ₩XX,XXX

예시:
1. **배달 앱 삭제 챌린지**: 주 3회 배달을 1회로 줄이고 간단한 자취 요리로 대체 → 예상 월 절약 ₩80,000
2. **충동구매 24시간 룰**: 5만원 이상 구매 시 24시간 대기 후 결정 → 예상 월 절약 ₩50,000

# 작성 가이드라인
- 톤: 친근하고 유용한 정보 전달
- 구체적 숫자와 근거 포함
- ~해요, ~이에요 체 사용
{("- 日本語で回答してください。~です、~ます体を使ってください。" + chr(10) + "- 쿠팡 링크 대신 Amazon.co.jp 검색 링크를 사용하세요: https://www.amazon.co.jp/s?k=검색어") if language == "ja" else "- 한국어로 작성"}"""

        return prompt

    def generate_smart_insights(
        self,
        overall_score: float,
        total_purchases: int,
        total_amount: float,
        target_items: list,
        category_spending: dict,
        category_breakdown: dict,
        language: str = 'ko'
    ) -> dict:
        """스마트 인사이트 생성 (API 호출)"""

        try:
            if not self.is_api_key_valid():
                return {
                    'success': False,
                    'insights': '',
                    'error': 'API 키가 유효하지 않습니다.'
                }

            prompt = self.build_smart_insights_prompt(
                overall_score, total_purchases, total_amount,
                target_items, category_spending, category_breakdown,
                language=language
            )

            if language == 'ja':
                system_msg = "あなたは消費データ分析の専門家です。購買データに基づいて実用的なインサイトを提供します。日本語で回答してください。"
            else:
                system_msg = "당신은 소비 데이터 분석 전문가입니다. 구매 데이터를 기반으로 실용적인 인사이트를 제공합니다."

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_msg
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=1500,
                frequency_penalty=0.3,
                presence_penalty=0.3
            )

            insights = response.choices[0].message.content

            usage = response.usage
            print(f"[Smart Insights] 토큰 사용량 - 입력: {usage.prompt_tokens}, "
                  f"출력: {usage.completion_tokens}, 총: {usage.total_tokens}")

            return {
                'success': True,
                'insights': insights,
                'error': None,
                'usage': {
                    'prompt_tokens': usage.prompt_tokens,
                    'completion_tokens': usage.completion_tokens,
                    'total_tokens': usage.total_tokens
                }
            }

        except Exception as e:
            error_message = str(e)
            print(f"[Smart Insights ERROR] API 호출 실패: {error_message}")

            return {
                'success': False,
                'insights': '',
                'error': f"스마트 인사이트 생성 중 오류 발생: {error_message}"
            }

    def generate_quick_tips(self, regret_score: float) -> List[str]:
        """
        후회 점수 기반 빠른 팁 생성 (API 호출 없이)

        Args:
            regret_score: 후회 점수

        Returns:
            팁 리스트
        """
        if regret_score <= 20:
            return [
                "✅ 훌륭한 소비 패턴을 유지하고 계세요!",
                "💡 이런 신중한 구매 습관을 계속 이어가세요.",
                "📊 다른 사람들과 구매 노하우를 공유해보는 건 어떨까요?"
            ]
        elif regret_score <= 35:
            return [
                "👍 대체로 합리적인 구매를 하고 계세요.",
                "💡 구매 전 24시간 고민 시간을 가져보세요.",
                "📝 구매 목록을 미리 작성하는 습관을 들여보세요."
            ]
        elif regret_score <= 50:
            return [
                "⚠️ 충동 구매를 줄일 필요가 있어요.",
                "💡 새벽/늦은 밤 시간대 쇼핑을 피해보세요.",
                "🛒 장바구니에 담고 3일 후 다시 확인하세요."
            ]
        elif regret_score <= 65:
            return [
                "🚨 구매 패턴 개선이 필요합니다.",
                "💡 한 달 소비 예산을 설정하고 추적해보세요.",
                "🤔 구매 전 '정말 필요한가?' 3번 자문하세요."
            ]
        else:
            return [
                "🔴 충동 구매 습관을 개선해야 합니다.",
                "💡 결제 수단을 물리적으로 멀리 두세요.",
                "👥 가족이나 친구에게 구매 전 의견을 구하세요.",
                "📱 쇼핑 앱 알림을 모두 끄세요."
            ]


# 싱글톤 인스턴스 (선택사항)
_openai_service = None


def get_openai_service() -> OpenAIService:
    """
    OpenAI 서비스 싱글톤 인스턴스 반환

    Returns:
        OpenAIService 인스턴스
    """
    global _openai_service

    if _openai_service is None:
        try:
            _openai_service = OpenAIService()
        except ValueError as e:
            # API 키가 없을 때 에러를 발생시키지 않고 None 반환
            print(f"[OpenAI WARNING] {str(e)}")
            return None

    return _openai_service


def check_api_key_available() -> tuple[bool, str]:
    """
    API 키 사용 가능 여부 확인

    Returns:
        (사용 가능 여부, 메시지)
    """
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        return False, "OPENAI_API_KEY 환경 변수가 설정되지 않았습니다."

    if not api_key.startswith('sk-'):
        return False, "OPENAI_API_KEY 형식이 올바르지 않습니다."

    return True, "API 키가 정상적으로 설정되었습니다."
