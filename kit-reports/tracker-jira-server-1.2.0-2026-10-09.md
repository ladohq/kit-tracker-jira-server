# Отчёт о ките: tracker-jira-server 1.2.0

- Дата: 2026-10-09
- Кит: `.` (worktree запуска `improve/tracker-jira-server-whoami`), путь задан
- Коммит: 0a71e86 (`kit.yaml` `version: 1.2.0`). Визит 2 оценивал 8aeda44 (отчёт cf31728),
  визит 1 — 65946fd (отчёт d6590ef).
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.1.0-2026-10-09.md`
  (полная оценка, b3e0aec). База — b3e0aec, её называет план. Дифф
  `git diff b3e0aec -- kit.yaml README.md BLUEPRINT.md agents flows skills` затрагивает
  5 файлов: BLUEPRINT.md, README.md, kit.yaml, skills/tracker/SKILL.md,
  skills/tracker/jira.py.
- Визит 3 шага `evaluate`, после второго отклонения на гейте выпуска («исправить F5.5,
  F3.3, F3.4»). С визита 2 (8aeda44 → 0a71e86) изменились:
  - SKILL.md: трассировка Python отделена от сообщений uv;
  - `jira.py`: 404 при снятии исполнителя — код 7; совет «fix the text the line names»;
  - BLUEPRINT: R8 и строка журнала 1.2.0;
  - тесты: 88.
- Проходы визита 3. Изменение — около 30 строк, три прохода я сделал сам, по 12 критериям
  и известным дырам:
  1. абзац SKILL.md «When the script fails» против `main` и таблицы кодов;
  2. `cmd_assign` и `cmd_transition` против таблицы кодов;
  3. R8 и журнал против кода.

  Новых находок эти проходы не дали. Затем был полный проход (Re-evaluation 5) по всем
  пяти файлам целиком. Его сделал отдельный субагент без `kit-reports/` и без `JIRA_*`,
  только против фейковой Jira. Он дал 2 находки low (F3.5, F6.1), обе я подтвердил по
  файлам. Однопроходных находок отброшено: 0.
- Проходы визитов 1–2: см. историю этого файла в git (d6590ef, cf31728).

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений; `expects commands: uv` |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано: потоков нет (R2), скелетов в BLUEPRINT.md нет |
| b. Рубрика | 2 открытые находки (0 high, 0 medium, 2 low); все 3 находки визита 2 RESOLVED; 10 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста и полный проход по 5 файлам, которых касается дифф (kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py); тесты: 88, OK |
| Правило остановки | выполнено: 0 high, 0 medium в изменённом тексте |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
expects commands: uv
```

Expects: `expects commands: uv`. Предупреждения `expects.commands needs LADO 0.30 or newer`
нет: `dependencies.lado: ">=0.30"`.

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.2.0

| Measure | Where | Value | Green / yellow up to | Zone |
|---|---|---|---|---|
| Worker roles (not supervisor) | kit | 0 | 3 / 5 | green |
| Work steps in a flow | no flows | 0 | 5 / 8 | green |
| Gates in a flow | no flows | 0 | 2 / 3 | green |
| Words in a role prompt | no roles | 0 | 800 / 1500 | green |
| Words in the lead's prompt | no lead role | 0 | 1000 / 1500 | green |
| Own skills | kit | 1 | 5 / 10 | green |
| MCP servers | kit | 0 | 2 / 4 | green |

## Similar paragraphs (one rule, one place; 55% similar or more)

none

Overall: green
```

### Потоки

У кита нет потоков (R2) и нет скелетов, поэтому сравнивать нечего. Скрипт потоков такой кит
не обрабатывает. Причина вне кита (см. «Found on the way»), так что на решение это не
влияет:

```
$ uv run --script flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Исправить сначала

Блокирующих и средних находок нет. По желанию, обе по одной строке:

1. R8: «(4, 5, 6, 7, 10, 429)», как в журнале и коде (F6.1).
2. Строка 7 таблицы: после `assign … none` ключ верен, сообщить, а не проверять ключ
   (F3.5).

## Находки

Нумерация продолжает визиты 1–2; их находки закрыты (см. «Previous findings»). Новые —
F3.5 и F6.1.

### 1. Границы ролей

Не применимо: ролей нет. Область записи SKILL.md:26-28 не менялась; `--reassign` — только
«when the human or your step says to take it from them» (SKILL.md:71).

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

- **F3.5** [low] `skills/tracker/SKILL.md:141`
  > | 7 | task or project not found | check the key; report it if the key came from someone else |
  С 0a71e86 сюда попадает и 404 при снятии исполнителя. Но GET перед этим только что нашёл
  задачу, так что ключ верен и «check the key» — лишний шаг. Если ключ агент получил в
  своём же шаге, строка не велит и сообщить. Тест показывает, что автор хотел обратного:
  `tests/test_jira.py:828` `self.assertNotIn("check the key", err)`.
  Fix: в строку 7 дописать «(after `assign … none`: the key was found a moment before;
  report it)».
  Passes: full pass, confirmed — `jira.py:820`
  `raise Failure(NOT_FOUND, "Jira refused to unassign %s: the task is gone or "`. Сама
  строка таблицы не менялась, в неё ведёт правка F3.3.

### 4. Независимая проверка

Не применимо: потоков нет. 88 тестов, OK. Пробы на тестовой Jira для 1.2.0 ещё не было
(вопрос 1).

### 5. Противоречия

Абзац «When the script fails» (SKILL.md:122-127) отделяет трассировку («A Python traceback
(`Traceback …`) is the script crashing: exit 1, and a write may have been applied») от
сообщений uv и Python до запуска скрипта. Полный проход проверил это пробами: путь, которого
нет, — `can't open file`, код 2; падение — `Traceback …`, код 1. Совет при отвергнутом
комментарии (`jira.py:753`) согласован со строкой 11. Нарушения нет.

### 6. Дублирование

- **F6.1** [low] `BLUEPRINT.md:118`
  > other failure (5, 6, 7, 10, 429), report it and send the comment only when told to.
  В списке R8 нет кода 4, а в строке журнала 1.2.0 он есть («report first after 4, 5, 6,
  7, 10 and 429», BLUEPRINT.md:247). Код тоже включает его: ветка `else` в
  `jira.py:754-755` ловит и код 4. Две копии одного правила уже расходятся.
  Fix: в R8 «(4, 5, 6, 7, 10, 429)».
  Passes: full pass, confirmed — grep обеих строк.

Правило assign в SKILL.md:68-71 и в строке 11 требует R8, копии совпадают.

### 7. Когда звать человека

Без изменений: SKILL.md:128-131; при коде 5 скрипт велит остановить всех агентов.

### 8. Циклы на повторном визите

Не применимо: потоков нет.

### 9. Краткость и «почему»

Новые фразы несут причину: «a write may have been applied», «nothing reached Jira».
Нарушения нет.

### 10. Описания навыков

Без изменений: описание называет `whoami` по смыслу; `uv` в `expects.commands`.

### 11. Нейтральность к провайдеру

Без изменений: `${SKILL_DIR}` с запасным путём; абсолютных путей нет.

### 12. Безопасность и границы

Без изменений с визита 2: чужую задачу без `--reassign` не взять; http только на
localhost; TLS не отключается.

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Не применимо: потоков нет. Сообщения uv и Python до запуска (ничего не ушло в Jira) отделены от падения скрипта (SKILL.md:122-127). |
| 2. Work outside a flow, merge without a gate | Git-работы нет. Чужую задачу можно забрать только с `--reassign` по слову человека или шага (SKILL.md:71). |
| 3. Path outside the run's worktree | `${SKILL_DIR}`; `.lado/tracker.yaml` ищется до первого `.git`. |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: ни `dependencies.skills`, ни ролей. |
| 6. Commands out of step with `expects.commands` | (a) `uv` — единственная команда, которую кит запускает всегда: `expects commands: uv`, README:21 требует только его. (b) `uv` нужен на любом проекте. (c) `dependencies.lado: ">=0.30"`, у `lado kits check` нет предупреждения. |

## Not traced

Ничего:
- правки 8aeda44 и 0a71e86 записаны в R8 (BLUEPRINT.md:104-131) и в строке журнала 1.2.0
  со ссылками на d6590ef, cf31728 и решение на гейте;
- `uv` — «command (expects)»;
- бюджет green, раздел 4 совпадает с выводом скрипта;
- потоков и скелетов нет (R2).

Одна неточность R8 — F6.1.

## Previous findings

Находки визита 2 (cf31728). Находки визита 1 и полной оценки b3e0aec закрыты раньше и с
тех пор не менялись.

| Находка | Статус | Доказательство |
|---|---|---|
| F5.5 [medium] трассировка как «nothing reached Jira» | RESOLVED | SKILL.md:122-124 «A Python traceback (`Traceback …`) is the script crashing: exit 1, and a write may have been applied (row 1»; «nothing reached Jira» — только для «`uv` or Python before the script ran» |
| F3.3 [low] 404 при снятии без причины | RESOLVED | `jira.py:820` «Jira refused to unassign %s: the task is gone or not visible to you (404)», код 7. Ведёт в строку 7 — F3.5 |
| F3.4 [low] совет без «fix» при коде 11 | RESOLVED | `jira.py:753` `advice = "fix the text the line names, then send the comment with comment"`; тест `tests/test_jira.py:512` |
| Not traced: журнал и R8 без правок 8aeda44 | RESOLVED | BLUEPRINT R8 «after a refused comment (11), fix the text the line names»; журнал 1.2.0 «From the re-evaluations of the build: …» (код 4 в R8 — F6.1) |

Список «fixed / not fixed» в build-report сверен с файлами и совпадает.

## Cut rules

Удалённые строки визита 3 (`git diff cf31728`):

| Удалённое правило (файл:строка в cf31728) | Где теперь |
|---|---|
| SKILL.md:122-126 «comes from `uv` or Python … nothing reached Jira … treat it as exit 1 and report all of it» | SKILL.md:122-127: то же для сообщений до запуска скрипта («report all of it as exit 1»), трассировка отдельно |
| `jira.py` «send the comment with comment» при коде 11 | `jira.py:753`, с «fix the text the line names» |
| `jira.py` снятие при 404 → REFUSED «404» | `jira.py:819-821`, NOT_FOUND с причиной |
| BLUEPRINT R8 «after 429, report it and send the comment only when told to» | BLUEPRINT.md:118 «any other failure (5, 6, 7, 10, 429)» |

Правил не потеряно. Удалённые правила визитов 1–2 — см. d6590ef и cf31728.

## Missed earlier

Нет. Полный проход не нашёл находок в тексте, которого не касается дифф.

## Left by the plan

Нет: план ничего не оставляет («Leave: none»).

## Questions for the human

1. Проба на тестовой Jira 8.13 до выпуска: `whoami` (`/rest/api/2/myself`), отказ
   `assign`, запуск через `uv` в сессии LADO. Рекомендую сделать: пробы 1.2.0 на живой
   Jira ещё не было.
2. F3.5 и F6.1 (low) — по одной строке. Рекомендую исправить при выпуске или в следующей
   версии, на ваш выбор: выпуск они не блокируют.

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не обрабатывает кит без
  `flows/`: `error: kit.yaml: states must be a non-empty mapping` (код 2). Всё ещё открыто.
- На визите 1 один субагент-проход сделал одно чтение `whoami` к настоящей Jira. На
  визитах 2–3 пробы шли без `JIRA_*`, только против фейковой Jira.
