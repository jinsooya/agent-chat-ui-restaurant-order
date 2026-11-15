# 한식당 주문 챗봇을 Agent Chat UI에서 실행하기

메뉴 도구(tool)를 사용하는 한식당 주문 챗봇을 내 컴퓨터에서 실행하고, 웹 채팅 화면인 Agent Chat UI(<https://agentchat.vercel.app>)에서 대화하는 방법을 설명한다. 챗봇은 메뉴 안내, 주문 접수, 합계 계산, 픽업 또는 배달 확인, 결제까지 여러 턴에 걸쳐 진행한다.

## 전체 구조

챗봇은 두 프로그램이 역할을 나누어 실행한다.

```text
[브라우저] Agent Chat UI  ──────►  [내 컴퓨터] LangGraph 서버  ──────►  [모델 제공자] LLM API
https://agentchat.vercel.app        http://localhost:2024
(채팅 화면)                          (restaurant_order_agent.py의 agent 실행)
```

- **LangGraph 서버**는 `restaurant_order_agent.py`의 `agent`를 내 컴퓨터에서 실행하고, 대화 기록을 스레드별로 저장한다.
- **Agent Chat UI**는 채팅 화면만 제공하는 웹 앱이다. 내 컴퓨터의 LangGraph 서버 주소를 알려 주면 그 서버의 에이전트와 대화한다.
- 에이전트와 API 키는 내 컴퓨터에만 있다. Agent Chat UI 사이트에는 코드와 API 키가 올라가지 않는다.

## 폴더 구성

이 저장소에는 아래 파일이 들어 있다.

| 파일 | 역할 |
|---|---|
| `restaurant_order_agent.py` | 한식당 주문 챗봇 에이전트와 메뉴 도구. 서버가 이 파일의 `agent` 변수를 불러온다. |
| `langgraph.json` | LangGraph 서버 설정. 어떤 파일의 어떤 변수를 어떤 이름(`agent`)으로 제공할지 지정한다. |
| `pyproject.toml` | 필요한 패키지 목록. `uv`가 이 파일을 읽고 패키지를 설치한다. |
| `uv.lock` | 패키지 버전 고정 파일. 모든 사람이 같은 버전의 패키지를 설치하도록 한다. |
| `.env.example` | API 키 파일의 견본. 복사하여 `.env`를 만든다. |
| `.gitignore` | `.env`(API 키)처럼 저장소에 올리지 않을 파일의 목록. |

## 준비물

- **uv**: 설치되어 있지 않으면 <https://docs.astral.sh/uv/getting-started/installation/>의 안내대로 설치한다. Python은 `uv`가 필요한 버전을 자동으로 준비한다.
- **LLM API 키**: 사용할 모델의 모델 제공자(provider) API 키가 필요하다. 코드에는 기본 모델로 OpenAI 모델을 지정해 두었으며, 다른 모델을 사용하려면 코드를 수정한다. 수정 방법은 아래 [코드 수정하기](#코드-수정하기)를 참고한다.
- **Chrome 브라우저**: Safari와 Brave는 웹 사이트가 내 컴퓨터(`localhost`)에 연결하는 것을 차단하므로 Chrome을 사용한다.

## 실행 순서

### 1. 저장소를 내려받고 폴더로 이동한다

터미널에서 아래 명령으로 저장소를 내려받는다.

```bash
git clone https://github.com/jinsooya/agent-chat-ui-restaurant-order.git
```

git이 없으면 저장소 페이지의 **Code** 버튼에서 **Download ZIP**을 눌러 내려받고 압축을 푼다. 이때 폴더 이름은 `agent-chat-ui-restaurant-order-main`이 되므로, 아래 `cd` 명령의 폴더 이름도 그에 맞게 바꾼다.

내려받은 폴더로 이동한다. 이후의 명령은 모두 이 폴더에서 실행한다.

```bash
cd agent-chat-ui-restaurant-order
```

### 2. API 키 파일(.env)을 만든다

`.env.example`을 복사하여 `.env` 파일을 만든다.

```bash
cp .env.example .env
```

Windows에서는 `copy .env.example .env`를 실행한다.

편집기로 `.env`를 열고, 사용할 모델의 모델 제공자(provider) API 키를 입력한 후 저장한다. 사용하지 않는 줄은 주석(`#`)으로 남겨 둔다.

```text
OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=
# GOOGLE_API_KEY=
```

`restaurant_order_agent.py`에는 기본 모델로 OpenAI 모델을 지정해 두었으므로, 코드를 그대로 실행하면 위의 예와 같이 `OPENAI_API_KEY`가 필요하다. 다른 모델을 사용하려면 코드의 `model` 값을 수정하고 그 모델 제공자의 키를 입력한다. 수정 방법과 모델 제공자별 키 이름은 [코드 수정하기](#코드-수정하기)를 참고한다.

> **(caution)** `.env` 파일에는 본인의 API 키가 들어 있으므로 다른 사람에게 공유하거나 GitHub에 올리지 않는다.

### 3. LangGraph 서버를 실행한다

```bash
uv run langgraph dev --no-browser
```

- 처음 실행할 때는 `uv`가 이 폴더 안에 `.venv` 폴더(가상 환경)를 만들고 패키지를 설치하므로 시간이 조금 걸린다. 두 번째부터는 바로 실행된다.
- 아래와 같은 주소가 출력되면 서버가 준비된 것이다. 이 터미널은 **닫지 말고 그대로 둔다**.

```text
- 🚀 API: http://127.0.0.1:2024
- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- 📚 API Docs: http://127.0.0.1:2024/docs
```

### 4. Agent Chat UI에 접속하여 서버 정보를 입력한다

Chrome에서 <https://agentchat.vercel.app>을 열고 아래 값을 입력한 후 **Continue**를 누른다.

| 입력란 | 입력할 값 | 설명 |
|---|---|---|
| Deployment URL | `http://localhost:2024` | 3단계에서 실행한 LangGraph 서버의 주소 |
| Assistant / Graph ID | `agent` | `langgraph.json`의 `graphs`에 적은 이름 |
| LangSmith API Key | (비워 둔다) | 클라우드에 배포한 서버에 연결할 때만 필요하다 |

Chrome이 주소창 아래에 **agentchat.vercel.app에서 다음 권한을 요청합니다**라는 창을 표시하면 **허용**을 누른다. 웹 사이트가 내 컴퓨터의 서버(`localhost`)에 연결하는 것을 허용하는 권한이다. 허용하지 않으면 메시지를 보내도 답이 나타나지 않고 대기 상태로 남는다.

### 5. 대화한다

화면 아래의 입력란에 메시지를 입력하고 Enter를 누른다. 아래 순서로 입력하면 도구 호출과 다중 턴 기억을 확인할 수 있다.

```text
안녕하세요.
비빔밥에 계란과 고추장을 추가할게요.
식혜도 하나 주세요.
주문은 이게 전부예요.
```

- 챗봇이 `menu` 도구를 호출하여 메뉴와 가격을 확인해야 한다. 도구 호출과 도구가 반환한 메뉴는 채팅 화면에 함께 표시된다. 화면 아래의 **Hide Tool Calls**를 켜면 도구 호출을 숨기고 대화만 볼 수 있다.
- 챗봇이 앞에서 주문한 내용을 기억하고, 주문 내역과 합계를 알려야 한다. 위의 주문은 비빔밥 10,000원, 계란 1,000원, 고추장 500원, 식혜 3,000원으로 합계가 14,500원이다.
- 이어서 챗봇이 픽업인지 배달인지 묻고, 결제 방식을 물어야 한다.
- 오른쪽 위의 **연필 아이콘**(New thread)을 누르면 새 대화가 시작된다. 새 대화에서는 앞의 주문 내용을 기억하지 못해야 한다.
- 왼쪽 위의 아이콘을 누르면 **Thread History**가 열리고, 이전 대화로 돌아가 이어서 대화할 수 있다.

### 6. 종료한다

서버를 실행한 터미널에서 `Ctrl + C`를 누른다. 서버를 종료하면 Agent Chat UI는 더 이상 응답하지 않는다.

## 코드 살펴보기

`restaurant_order_agent.py`는 네 부분으로 이루어져 있다.

| 부분 | 코드 | 설명 |
|---|---|---|
| 도구 | `@tool`을 붙인 `menu()` 함수 | 메뉴와 가격을 텍스트로 반환한다. 챗봇은 메뉴와 가격을 추측하지 않고 이 도구를 호출하여 확인한다 |
| 시스템 프롬프트 | `INSTRUCTION` | 주문봇의 역할과 주문 절차(메뉴 확인, 주문 요약, 합계, 픽업 또는 배달, 결제)를 정한다 |
| 모델 | `init_chat_model(...)` | 챗봇이 사용할 LLM을 지정한다 |
| 에이전트 | `create_agent(model=, tools=, system_prompt=)` | 모델, 도구, 시스템 프롬프트를 묶어 `agent`를 만든다. 서버가 이 `agent`를 불러온다 |

코드에는 `while True:`와 `input()` 같은 입력 루프가 없고, 대화 기록을 저장하는 체크포인터(`InMemorySaver`)도 주석으로만 남아 있다. 서버에서 실행할 때는 아래와 같이 다른 프로그램이 그 역할을 맡기 때문이다.

| 항목 | 일반 파이썬 프로그램으로 직접 실행할 때 | LangGraph 서버와 Agent Chat UI로 실행할 때 |
|---|---|---|
| 다중 턴 기억 | `checkpointer=InMemorySaver()`를 에이전트에 직접 넘긴다 | 넘기지 않는다. LangGraph 서버가 대화 기록을 저장한다 |
| `thread_id` | 직접 만들어 `config`에 넣는다 | Agent Chat UI가 대화마다 만들어 서버에 전달한다 |
| 입력과 출력 | `input()`과 `print()`로 직접 처리한다 | 채팅 화면이 메시지를 보내고 답을 표시한다 |

> 메뉴를 시스템 프롬프트에 넣지 않고 도구로 분리하면, 메뉴가 바뀔 때 도구만 수정하면 된다. 실제 서비스에서는 이 도구가 데이터베이스나 외부 API에서 그날의 메뉴와 재고를 조회하도록 만들 수 있다.

## 코드 수정하기

서버가 실행 중일 때 `restaurant_order_agent.py`를 수정하고 저장하면, 서버가 변경을 감지하여 자동으로 다시 불러온다. 서버를 다시 실행할 필요가 없다.

- **메뉴 변경**: `menu()` 함수가 반환하는 텍스트에서 품목이나 가격을 수정한다. 예를 들어 음료에 `- 매실차 3,000원`을 추가한 후, 새 대화(New thread)에서 매실차를 주문하여 확인한다.
- **주문 절차 변경**: `INSTRUCTION`을 수정한다. 예를 들어 결제 방식을 바꾸거나, 포장 여부를 묻는 단계를 추가한다.
- **모델 변경**: `init_chat_model`의 `model` 값을 바꾸고, 해당 모델 제공자(provider)의 API 키를 `.env`에 추가한 후 서버를 종료하고 다시 실행한다. `model` 값은 아래 표의 형식으로 작성하며, 도구 호출(tool calling)을 지원하는 채팅 모델이어야 한다. 챗봇이 `menu` 도구를 호출하기 때문이다.

| 모델 제공자 | `model` 값의 형식 | `.env`에 넣을 키 |
|---|---|---|
| OpenAI | `openai:모델 이름` | `OPENAI_API_KEY` |
| Anthropic | `anthropic:모델 이름` | `ANTHROPIC_API_KEY` |
| Google | `google_genai:모델 이름` | `GOOGLE_API_KEY` |

모델 이름은 각 모델 제공자의 문서에서 확인한다.

## (선택) LangSmith로 실행 기록 확인하기

`.env`에서 아래 두 줄의 주석(`#`)을 지우고 LangSmith API 키를 입력한 후 서버를 다시 실행한다.

```text
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_TRACING=true
```

대화할 때마다 실행 기록(trace)이 LangSmith(<https://smith.langchain.com>)의 **Agent Chat UI Apps - Restaurant Order** 프로젝트에 저장된다. 프로젝트 이름은 `restaurant_order_agent.py`의 `LANGSMITH_PROJECT`에서 지정한다.

## 문제 해결

| 증상 | 원인과 해결 방법 |
|---|---|
| 메시지를 보냈는데 답이 나타나지 않고 계속 대기한다 | Chrome의 로컬 네트워크 권한을 허용하지 않은 경우이다. 주소창 왼쪽의 사이트 설정 아이콘을 눌러 로컬 네트워크 접근을 허용한 후 새로 고침한다. |
| Safari나 Brave에서 연결되지 않는다 | Chrome을 사용한다. 또는 `uv run langgraph dev --tunnel`로 실행하고, 출력되는 `https://...trycloudflare.com` 주소를 Deployment URL에 입력한다. |
| 접속하자마자 연결 오류가 표시된다 | 서버가 실행 중인지, Deployment URL이 `http://localhost:2024`인지(`https`가 아니다) 확인한다. |
| 서버 터미널에 API 키 오류가 출력된다 | `.env` 파일이 `restaurant_order_agent.py`와 같은 폴더에 있는지, 키 이름과 값이 맞는지 확인한 후 서버를 다시 실행한다. |
| `address already in use` 오류로 서버가 시작되지 않는다 | 2024번 포트를 다른 프로그램이 사용 중이다. `uv run langgraph dev --no-browser --port 2025`로 실행하고 Deployment URL을 `http://localhost:2025`로 입력한다. |
| 서버 정보를 잘못 입력하여 다시 입력하고 싶다 | 주소창에 <https://agentchat.vercel.app>만 입력하여 다시 접속하면 입력 화면이 나타난다. |

## 참고 자료

- Agent Chat UI 저장소: <https://github.com/langchain-ai/agent-chat-ui>
- LangGraph 로컬 서버 안내: <https://docs.langchain.com/langsmith/local-server>
