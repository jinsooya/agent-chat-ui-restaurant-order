# 한식당 주문 챗봇 (stand-alone 버전)
# Korean restaurant order chatbot (stand-alone version)
#
# 메뉴 도구를 사용하는 한식당 주문 챗봇을 LangGraph 서버(langgraph dev)에 올려
# Agent Chat UI(https://agentchat.vercel.app)에서 대화할 수 있도록 .py 파일 하나로 만든 것이다.
# a Korean restaurant order chatbot with a menu tool, written as a single .py file so that
# a LangGraph server (langgraph dev) can serve it to Agent Chat UI (https://agentchat.vercel.app)
#
# 실행 방법은 같은 폴더의 README.md를 참고한다.
# see README.md in the same folder for how to run it
#
# This file is provided for educational purpose and distributed for class use.
# Copyright (c) by Jinsoo Park, Seoul National University. All rights reserved.
#

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool

# 이 파일이 있는 폴더(또는 그 상위 폴더)의 .env 파일에서 API 키를 불러온다.
# load the API keys from the .env file in this folder (or one of its parent folders)
load_dotenv()

# (선택) LangSmith 추적을 켠 경우(.env의 LANGSMITH_TRACING=true), 실행 기록을 저장할 프로젝트 이름이다.
# 추적을 켜지 않았다면 아무 영향이 없다.
# (optional) the LangSmith project that receives the traces when tracing is on (LANGSMITH_TRACING=true in .env);
# it has no effect when tracing is off
os.environ['LANGSMITH_PROJECT'] = 'Agent Chat UI Apps - Restaurant Order'


# --- 도구 정의
# 메뉴를 시스템 프롬프트에 넣지 않고 도구로 제공한다. 메뉴가 바뀌면 이 도구만 수정하면 된다.
# the menu is served by a tool instead of the system prompt; when the menu changes, only this tool changes
@tool(
    'menu',
    # parse_docstring=True,
    description=(
        'Provide the latest updated restaurant menu including main dishes, '
        'additional options, and beverages. '
        'Use this tool whenever the user asks about available menu items, '
        'prices, or food and drink options.'
    )
)
def menu() -> str:
    """Provide the latest updated restaurant menu.
    It returns the currently available main dishes, add-on options, and beverages with prices.

    최신 업데이트된 식당 메뉴를 제공한다.
    이 함수는 현재 판매 중인 메인 메뉴, 추가 옵션, 음료 목록과 가격 정보를 반환한다.

    Returns:
        str: A formatted string containing menu categories and prices.
             메뉴 카테고리와 가격 정보를 포함한 형식화한 문자열
    """
    # NOTE: 이 코드는 하드코딩한 텍스트를 반환한다.
    # 실제 서비스에서는 데이터베이스 또는 외부 API와 연결해 동적 메뉴를 조회하도록 확장할 수 있다.
    # NOTE: This implementation returns hard-coded text.
    # It can be extended to retrieve dynamic menu data from a database or external api.
    return '''
[메인 메뉴]
- 불고기 15,000원
- 비빔밥 10,000원
- 김치찌개 8,000원
- 해물파전 12,000원
- 잡채 9,000원

[추가 옵션]
- 계란 1,000원
- 두부 1,500원
- 고기 3,000원
- 해산물 4,000원
- 고추장 500원
- 김치 1,000원

[음료]
- 식혜 3,000원
- 수정과 3,000원
- 콜라 2,000원
- 사이다 2,000원
- 생수 1,000원
'''


# --- 시스템 프롬프트
# 메뉴 확인, 주문 요약, 합계, 픽업 또는 배달, 결제까지 여러 턴에 걸쳐 진행하는 주문봇 페르소나
# an order-bot persona that runs menu check, order summary, total, pickup or delivery, and payment over several turns
INSTRUCTION = '''당신은 한식당을 위한 자동 주문봇입니다. 
메뉴와 가격은 **반드시** `menu` 도구를 호출하여 확인합니다. 메뉴와 가격을 추측하지 않습니다. 

고객으로부터 주문을 받으면 먼저 주문한 음식과 해당 음식의 가격이 메뉴에 있는지 **반드시** 확인합니다. 
메뉴에 없는 음식은 주문을 받을 수 없습니다. 
메뉴에 있는 음식이면, 주문 내역을 고객에게 요약하고, 고객이 추가로 주문할 것이 있는지 최종 확인합니다. 
메뉴에서 항목을 구별할 수 있도록 모든 옵션 및 추가 사항 등을 명확히 해야 합니다. 

최종 확인 시, 고객이 주문한 메뉴와 해당 메뉴의 가격을 **반드시 다시 확인**하여 오류가 없는지 검토하세요. 
메뉴 가격이나 최종 합계 계산이 틀렸다면 수정 후 총 합계를 고객에게 알려줍니다.

최종 주문을 확인 한 후 고객에게 픽업인지 배달인지 묻습니다.
배달인 경우 주소를 묻습니다. 마지막으로 결제를 진행합니다.
결제 방식으로는 현금 결제, 신용카드 결제, 모바일 결제가 있습니다.
이 중 고객이 원하는 결제 방식으로 결제를 처리합니다.
대화식이고 친근한 스타일로 간단하게 대답합니다.

[중요] 
- 대화의 첫 응답에서는 고객에게 인사하고, 주문 가능한 메뉴를 안내한 뒤 무엇을 주문할지 물어보세요. 
- 그 이후에는 **인사말을 다시 하거나 메뉴 전체를 다시 출력하지 마세요.** 고객이 메뉴를 다시 요청한 경우에만 메뉴를 보여 줍니다.

[참고] 일반 텍스트로만 출력해 주세요. 마크다운 문법은 사용하지 말아 주세요.
'''


# --- 모델 초기화
# 모델을 바꿔 테스트하려면 model 값을 바꾸고, 해당 모델 제공자(provider)의 API 키를 .env 파일에 넣는다.
# 아래 model 값은 예시이며, 도구 호출(tool calling)을 지원하는 채팅 모델이면 어느 것이든 사용할 수 있다.
model = init_chat_model(
    model='openai:gpt-6-luna'
)


# --- 다중 턴 기억 (multi-turn memory)
# (caution) 일반 파이썬 프로그램에서 에이전트를 직접 실행할 때는 아래 두 줄처럼 체크포인터를 만들어
#           에이전트에 넘겨야 다중 턴 기억이 동작한다.
#           여기서는 주석으로 남겨 두고 사용하지 않는다. LangGraph 서버(langgraph dev)가
#           스레드별 대화 기록을 직접 저장하고 관리하므로, 다중 턴 기억은 서버가 제공한다.
# from langgraph.checkpoint.memory import InMemorySaver
# memory = InMemorySaver()

# --- 에이전트 구성
# 모델, 메뉴 도구, 시스템 프롬프트로 에이전트를 구성한다. checkpointer=memory 줄은 주석으로 처리한다.
# thread_id도 직접 만들지 않는다. Agent Chat UI가 대화(스레드)마다 thread_id를 만들어 서버에 넘긴다.
agent = create_agent(
    model=model,
    tools=[menu],
    # checkpointer=memory,  # (caution) 서버가 대화 기록을 저장하므로 넘기지 않는다 / the server stores the history, so it is not passed
    system_prompt=INSTRUCTION
)
