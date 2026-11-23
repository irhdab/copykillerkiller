# copykillerkiller

**과제 제출을 앞두고 카피킬러 AI 생성률이 높게 나왔다면, 어느 문단부터 다시 봐야 할까요?**

`copykillerkiller`는 AI 생성률을 낮추기 위해 과제 원고를 다시 살펴보는 대학생을 위한 스킬입니다. 카피킬러 상세 보고서의 표시를 Word 원고와 연결하고, 해당 문단에 출처나 설명이 빠진 곳을 짚어줍니다. 원고와 보고서의 판본도 대조해서 예전 초고의 검사 결과를 보며 현재 원고를 검토할 때 생기는 혼동을 줄입니다.

특정 대화 도구에 종속되지 않습니다. 문서는 `SKILL.md`와 `references/`로, 자동화는 표준 라이브러리만 쓰는 Python 스크립트로 되어 있어서, 파일을 읽고 셸을 실행할 수 있는 에이전트면 같은 판단 절차를 그대로 씁니다. 실행 환경이 부족하면 [등급별 절차](copykillerkiller/references/capabilities.md)로 내려갑니다.

## 이렇게 써보세요

Word 원고와 카피킬러 상세 보고서를 대화에 넘기고 검토를 요청합니다. 호출 문법만 도구마다 다릅니다.

```text
Codex:          $copykillerkiller
Claude Code:    /copykillerkiller
Hermes, Cursor: 스킬을 지정하거나 요청 문장에 검토 대상과 목적을 적기
```

> 상세 보고서와 지금 과제 원고를 대조해줘. 표시된 문단마다 내가 확인할 출처나 보완할 근거를 짚고, 원본을 보존한 Word 주석 사본으로 만들어줘.

수정본이 여럿이면 지금 쓰는 원고를 지정하고, 분량이나 AI 활용에 관한 수업 지침이 있다면 함께 알려주세요.

가상의 과제에서 초안에 다음과 같이 적었다고 해보죠.

> 복습 기록을 쓰면 학생들의 성적이 오른다.

갖고 있는 자료가 수강생 12명 중 9명이 복습 기록을 제출했다는 기록이라면, 그 자료로 설명할 수 있는 것은 제출 결과입니다. 스킬은 해당 문단에 성적 변화까지 말하려면 어떤 자료가 더 필요한지 주석으로 남깁니다.

과제 지침이 AI 문장 수정을 제한하면 직접 고칠 수 있도록 확인 질문과 검토 의견을 제공합니다. 점수 변화를 보려면 수정한 판본을 같은 설정으로 검사하고 새 상세 보고서에서 확인하세요.

보고서 없이도 쓸 수 있습니다. 예를 들어 `이 수업 메모로 보고서 개요를 잡아줘. 내가 확인할 출처와 수치는 따로 표시해줘.`처럼 요청하세요. 업무 보고, 제안서, 이메일 등 다른 문서 유형도 [작성 가이드](copykillerkiller/references/writing-playbook.md)에서 다룹니다.

## 설치

Git이 설치된 터미널에서 내려받고, 설치 스크립트에 대상 에이전트를 지정합니다. GitHub 로그인 없이 설치할 수 있습니다.

```sh
git clone https://github.com/hyscodebase/copykillerkiller.git
cd copykillerkiller
sh install.sh --agent codex
```

| `--agent` | 설치 위치 |
|---|---|
| `codex` | `${CODEX_HOME:-$HOME/.codex}/skills/` |
| `claude` | `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/` |
| `hermes` | `${HERMES_HOME:-$HOME/.hermes}/skills/` |
| `cursor` | `./.cursor/skills/` (프로젝트 폴더 기준) |
| `project` | `./.agents/skills/` (프로젝트 폴더 기준) |
| `auto` | 위 경로 중 존재하는 첫 번째, 없으면 `project` |

에이전트별 스킬 경로는 판이 바뀌면 달라질 수 있습니다. `sh install.sh --list`로 이 스크립트가 쓰는 경로를 확인하고, 다르면 `--dir`로 직접 지정하세요.

```sh
sh install.sh --dir ~/my-agent/skills
```

이미 설치되어 있으면 덮어쓰지 않고 멈춥니다. 교체하려면 `--force`를 붙이면 기존 폴더가 시각이 붙은 백업으로 옮겨집니다. 설치가 끝나면 실행 환경 등급을 함께 출력합니다.

## 실행 환경 등급

```sh
python3 "<스킬 폴더>/scripts/capability.py"
```

| 등급 | 조건 | 결과 |
|---|---|---|
| `full` | Python 3.9 이상, `pdftotext`, 쓰기 가능한 작업 폴더 | PDF 추출, 판본 대조, 주석 사본 생성, 구조 검증 |
| `reduced` | Python은 있으나 `pdftotext` 없음 | 대조와 사본 생성은 되고, PDF 텍스트는 에이전트가 읽어 넘김 |
| `manual` | 셸 실행이나 쓰기 권한 없음 | 스크립트를 돌리지 않고 위치별 검토 의견과 실행 명령을 제공 |

자동 전처리에는 Python 3.9 이상, PDF에서 텍스트를 추출하려면 Poppler의 `pdftotext`가 필요합니다. `python3 --version`, `pdftotext -v`로 확인할 수 있습니다.

### `pdftotext` (Poppler) 설치

| OS | 명령어 |
|---|---|
| macOS | `brew install poppler` |
| Ubuntu/Debian | `apt install poppler-utils` |
| Fedora | `dnf install poppler-utils` |
| Arch Linux | `pacman -S poppler` |

## 자동화 범위

| 단계 | 스킬이 하는 일 |
|---|---|
| 초안과 편집 | 학술 글, 업무·기술 보고, 제안서, 공지·이메일, 에세이의 독자와 목적에 맞춰 작성합니다. 제공한 자료로 뒷받침할 수 있는 범위를 지킵니다. |
| 검사본 대조 | 보고서의 표시를 원고 후보와 대조합니다. 검사 당시 원고와 현재 작업 대상은 따로 표시합니다. |
| 근거 검토 | 표시 구간의 경계를 PDF에서 확인하고, 위치·문제·확인할 자료를 정리합니다. |
| 수정 사본 검증 | 수정 요청이 있고 과제 규정이 허용되면 별도 사본을 만듭니다. 본문 텍스트 변화와 서식 차이를 비교해 주석 사본의 용도를 표시합니다. |

표시 범위의 정확한 끝, 페이지 사이 연결, 여러 판본의 공통 본문은 추가 확인이 필요합니다. 도구는 로컬에서 동작하며, 주석 사본을 만들 때는 지정된 작업 대상의 해시와 문단을 확인합니다.

저장소를 내려받은 폴더에서 직접 실행할 수도 있습니다.

```sh
python3 copykillerkiller/scripts/prepare_review.py --target-index 2 "상세 결과.pdf" "검사 당시 원고.docx" "현재 원고.docx"
python3 copykillerkiller/scripts/create_review_copy.py "현재 원고.docx" --expected-sha256 "<작업 대상 SHA-256>" --notes "주석.json" --out "검토용 사본.docx"
python3 copykillerkiller/scripts/verify_docx.py "원본.docx" "검토용 사본.docx"
```

자세한 작성 흐름과 결과 해석은 [문서 유형별 글쓰기](copykillerkiller/references/writing-playbook.md), [전처리 안내](copykillerkiller/references/preflight.md), [DOCX 검증 안내](copykillerkiller/references/docx-verification.md), [실행 환경 판정](copykillerkiller/references/capabilities.md)을 참고하세요.

## 통합 테스트

`python3 -B -m unittest discover -s tests`는 임시 폴더에 가상 보고서와 이름이 같은 과거·현재 DOCX를 만들고, 실행 환경 판정과 설치 스크립트까지 확인합니다. 과거 보고서가 있더라도 현재 원고로 주석 사본이 생성되는지, 원본과 문서 구조가 보존되는지 검증합니다.

`soffice`, `pdftotext`, `pdftoppm`을 사용할 수 있는 환경에서는 다음 한 줄로 본문 페이지의 픽셀 비교까지 실행할 수 있습니다.

```sh
COPYKILLER_RENDER_TEST=1 python3 -B -m unittest discover -s tests
```
