# Отчёт о ките: tracker-jira-server 1.0.0

- Дата: 2026-10-08
- Кит: `.` (worktree запуска `improve/tracker-jira-server`), путь задан
- Коммит: f24cd29 (`kit.yaml` `version: 1.0.0`)
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-0.1.1-2026-10-08.md`
  (артефакт `assessment`), база — 37181e0 (её называет план),
  `git diff 37181e0 -- kit.yaml README.md BLUEPRINT.md agents flows skills`: 5 файлов.
  Второй визит `evaluate`: прошлая версия этого отчёта — 043988f (e81d06a, `changes`);
  с тех пор e750d69 (автор) и f24cd29 (супервизор, BLUEPRINT).
- Проходы: изменение после 043988f маленькое (4 файла, около 40 строк), три прохода я
  сделал сам, без субагентов. Проход 1: jira.py (`WAIT`, `STOP_ALL`, строки вложенных
  ключей) с запусками. Проход 2: SKILL.md и README против сообщений скрипта. Проход 3:
  BLUEPRINT R6, R8, R10, раздел 3 против файлов. Затем полный проход по всем пяти файлам,
  которых касается дифф от 37181e0 (Re-evaluation 5). Однопроходных находок отброшено: 0;
  оставлено как подтверждённые: 0. Новых находок нет.

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано (у кита нет потоков, R2); скелетов в BLUEPRINT.md нет |
| b. Рубрика | 0 находок; 12 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста, с полным проходом по 5 файлам, которых касается дифф (kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py); тесты: 50, OK |
| Правило остановки | выполнено: 0 high, 0 medium |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
```

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.0.0

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

У кита нет потоков (R2), скелетов нет; сравнивать нечего. Скрипт потоков этого случая не
знает (см. «Found on the way»):

```
$ flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Исправить сначала

Нечего: ни одной находки не открыто.

## Находки

### 1. Границы ролей

Ролей нет. Рассылку при коде 5 делает ведущий: `jira.py:40` `STOP_ALL = ("; the lead tells
every agent to stop using Jira until the human says it is "`; SKILL.md:127 «the lead tells
them»; README.md:12 «says the lead tells every agent to stop using Jira».

### 2. Передачи между шагами

Не применимо: потоков нет. Отчёт об ошибке — «that line and the command» (SKILL.md:117),
и строка теперь сама несёт правила кодов 5 и 9.

### 3. Готовность и исходы

У каждого кода одно действие (SKILL.md:121-134). Эпик: SKILL.md:48-49 «`--epic-name` when
the settings name `fields.epic_name`, otherwise the `--field` the script names (exit 8)» —
согласно с `jira.py:484-488`.

### 4. Независимая проверка

Не применимо к тексту кита; R10 ставит повтор пробы в песочнице до одобрения релиза
человеком (BLUEPRINT.md:91-92).

### 5. Противоречия

R8 «the script's message says so» теперь верно: запуск против закрытого порта —
`get`: `… are you on the VPN or the company network?; send Jira nothing more until you are
told it answers again` (код 9); `comment`: то же и `; the change may have been applied:
once Jira answers again, check with get or search before running it again`. SKILL.md:136
«After exit 1, 9 or a 5xx exit 12 on a write, once you are told Jira answers again» больше
не спорит с 429 и строкой 9. BLUEPRINT.md:128 и :142 согласны с новой R10.

### 6. Дублирование

Правило кода 5 — в сообщении скрипта, строке SKILL.md и README, намеренно (R8 «so a lead
without the skill learns it too»); формулировки совпадают. Правило кода 9 — в сообщении
(`WAIT`) и строке 9 SKILL.md, по той же причине. Не находка.

### 7. Когда звать человека

Работник → супервизор, ведущий → человек; «Then wait for the answer if your step cannot go
on without the tracker; otherwise go on with it.» (SKILL.md:118-119). Ведущий без навыка
получает правила кодов 5 и 9 из самой строки.

### 8. Циклы на повторном визите

Не применимо: потоков нет; код 11 — «fix the request once».

### 9. Краткость и «почему»

Строки R1 и R6 перенесены, «F5.5» — в *Source* R6 (BLUEPRINT.md:54). Ошибка вложенного
значения называет его строку: `… tracker.yaml line 4: 'statuses.done' must be one plain
value` (значение на строке 4; `jira.py:150`).

### 10. Описания навыков

`description` не менялся, говорит что и когда; `dependencies.skills` нет.

### 11. Нейтральность к провайдеру

Путь — `${SKILL_DIR}` с запасным правилом; инструментов CLI нет; `<kit>` в README — для
человека, с подсказкой «`lado kits show tracker-jira-server` prints it».

### 12. Безопасность и границы

Пароль не попадает в аргументы процессов: проверка входа — только `jira.py search`
(README.md:41-43). Переименование репозитория — «at the release step with the human's yes»
(R10); README.md:1 и :17 уже под новым именем — сверка с remote на шаге релиза (см.
«Questions for the human»).

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Коды разделяют окружение (4, 5, 9, 10, 12 — «report it») и ошибку запроса (2, 8, 11 — «fix»), SKILL.md:121-134. |
| 2. Work outside a flow, merge without a gate | Нет git-работы; запись в Jira — SKILL.md:25 «only when your role, your step or the human asks for it». |
| 3. Path outside the run's worktree | `.lado/tracker.yaml` «from the current directory up to the repository root»; `find_config` останавливается на первом `.git`. |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: `dependencies.skills` нет. |

## Not traced

Ничего: все элементы названы требованиями (раздел 3), меры бюджета green, потоков и
скелетов нет (R2); R8 и R10 согласны с файлами.

## Previous findings

Отчёт 043988f (e81d06a):

| Находка | Статус | Доказательство |
|---|---|---|
| F5.1 [high] R8: сообщение кода 9 | RESOLVED | `jira.py:42` `WAIT = "; send Jira nothing more until you are told it answers again"`, `:291` `after = WAIT + (APPLIED if method != "GET" else "")`; запуск выше; тесты `tests/test_jira.py:576`, `:585` |
| F3.1 [medium] SKILL.md:48 `--epic-name` | RESOLVED | SKILL.md:48-49 «`--epic-name` when the settings name `fields.epic_name`, otherwise the `--field` the script names (exit 8)» |
| F5.2 [low] `STOP_ALL` | RESOLVED | `jira.py:40` «the lead tells every agent…»; README.md:12 |
| F5.3 [low] SKILL.md:134 после 429 | RESOLVED | SKILL.md:136 «After exit 1, 9 or a 5xx exit 12 on a write, once you are told Jira answers again» |
| F5.4 [low] BLUEPRINT :126/:140 | RESOLVED | BLUEPRINT.md:128 «the trials run on a test Jira»; :142 «the release, the sandbox trial before it and the rename are» |
| F5.5 [low] BLUEPRINT:52 | RESOLVED | BLUEPRINT.md:53-54 «Q2 (the first project's facts are gathered at its first use)» |
| F9.1 [low] строка вложенного значения | RESOLVED | `jira.py:150` `lines[section + "." + key] = number`; запуск: «line 4» |
| F9.2 [low] строки R1/R6 | RESOLVED | BLUEPRINT.md:13-16, :46-54 перенесены; «report 37181e0, F5.5» в *Source* |
| F12.1 [low] curl с паролем | RESOLVED | README.md:41-43, вариант с curl убран |
| F12.2 [low] URL до переименования, заголовок | RESOLVED в тексте кита (README.md:1 `# lado-kit-tracker-jira-server`); сверка URL с remote — на шаге релиза, вопрос 1 | README.md:17 |

Отчёт 37181e0 (`assessment`): все 15 находок RESOLVED — подтверждено в версии 043988f
этого отчёта; остаточные замечания оттуда (F5.1, F3.1, F5.2–F5.5, F9.1, F12.1, F12.2)
закрыты выше. Список build-report (визит 3) сверен с файлами: совпадает.

## Cut rules

| Удалённое правило (файл:строка в базе) | Где теперь |
|---|---|
| SKILL.md:113 «and wait for its answer» | SKILL.md:118-119, условно — так велит план (F5.1 отчёта 37181e0) |
| SKILL.md:121 «The lead tells every agent to stop using Jira until the human says it is fixed» | SKILL.md:127 «the lead tells them»; `jira.py:40` `STOP_ALL` |
| SKILL.md:128 «whether your step can go on without the tracker is your step's decision» | SKILL.md:118-119 |
| SKILL.md:45 «An epic also needs `--epic-name`» | SKILL.md:48-49, с условием |
| SKILL.md:130 «After exit 1, 9 or 12 on a write, `get` or `search` before running it again» | SKILL.md:136-137, для 5xx и «once you are told Jira answers again» |
| README.md:24-25 «Jira Server before 8.14 has no personal access tokens, so the password is the user's own» | README.md:26-28 |
| README.md:38 проверка входа `curl -u "$JIRA_USER"` | README.md:41-43, `jira.py search … --max 1` |
| BLUEPRINT.md:75-78 R10 (проба на настоящей Jira) | R10 BLUEPRINT.md:88-97 — заменено решением триажа |
| BLUEPRINT.md:80-83 «Further limits for agents» | BLUEPRINT.md:99-101 |
| BLUEPRINT.md:84-85 «CRM3's facts … gathered by the human before the trial» | BLUEPRINT.md:53-54 «gathered at its first use» |

Правил не потеряно.

## Missed earlier

Нет: полный проход по пяти файлам новых находок не дал.

## Left by the plan

Нет: план «Leave: none».

## Questions for the human

1. На шаге релиза: README.md:17 уже указывает на `ladohq/lado-kit-tracker-jira-server`, а
   `git remote` — всё ещё `ladohq/kit-tracker-jira-server`. Совет: переименовать
   репозиторий на GitHub (R10, с вашего «да») до push и pull request в маркетплейс; если
   откажетесь — вернуть в README прежний URL и заголовок до тега.

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не знает кита без
  `flows/`: `error: kit.yaml: states must be a non-empty mapping` (код 2). Всё ещё открыто.
