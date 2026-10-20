# Отчёт о ките: tracker-jira-server 1.6.0

- Дата: 2026-10-20
- Кит: `.` (worktree запуска `improve/tracker-jira-server`, ветка
  `lado/kit-tracker-jira-server/improve-tracker-jira-server`), путь задан
- Коммит: ee2dc59 (`kit.yaml` `version: 1.6.0`). Визит 1 оценивал 6f175cf (отчёт 66d8918).
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.5.0-2026-10-20.md`
  (85d77cb, оценивал ceddd32); база — ceddd32, коммит, который план называет для своего
  отчёта. План — артефакт `plan`, сборка — `build-report`.
- Визит 2, после гейта выпуска (решение человека: исправить F12.1, F3.1, F5.1, F5.2,
  F12.2, F5.3, F3.2; F9.1 оставить; вопрос 1 — exit 3). С визита 1 (6f175cf → ee2dc59)
  изменились 3 файла, +87 −55: fae3326 (SKILL.md, jira.py, тесты: 149), 14a1a78 и ee2dc59
  (BLUEPRINT R1, R8, R11).
- Проходы визита 2: три по правкам 6f175cf..ee2dc59 и их окружению, по 12 критериям и
  известным дырам: мой (дифф целиком против SKILL.md и BLUEPRINT), субагент A (jira.py:
  `find_repository` на настоящих `git worktree add` — внутри и вне основной копии,
  относительный gitdir, симлинки, подмодуль; `_comment_failed` по каждому коду в
  `transition` и `attach`; тип поля; OSError в `download`), субагент B (BLUEPRINT R1, R7,
  R8, R11 и раздел 5 против кода, SKILL.md, tracker-yougile 94a29f5; проверка вырезанных
  правил по `git diff --word-diff`). Затем полный проход субагентом по всем трём файлам
  правки (BLUEPRINT.md, SKILL.md, jira.py) целиком. Пробы — против фейковой Jira на
  localhost и заглушки, без `JIRA_*`. Однопроходных находок отброшено: 2 (значение
  `field`, начинающееся с `-`, — exit 2 от argparse без подсказки о `--`: вреда нет,
  команда не выполнена; строка 2 таблицы говорит «inside the repository» без основной
  копии — действие агента то же); оставлено как подтверждённые: 1 (F12.3).
- Проходы визита 1: три независимых субагента по изменённому тексту ceddd32..6f175cf и
  полный проход по пяти файлам; однопроходных находок отброшено 1, оставлено как
  подтверждённые 1 (подробно — в версии отчёта 66d8918).

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; жёлтых и красных мер нет |
| a. Потоки | 0 нарисовано: потоков нет (R2); в BLUEPRINT.md скелетов нет |
| b. Рубрика | визит 2: 3 открытых находки в изменённом тексте (0 high, 1 medium, 2 low: F5.3, F5.4, F12.3 — новые) и F9.1 [low], оставленная человеком; 7 находок визита 1 и обе «Пропущено ранее» RESOLVED; все 6 находок 85d77cb RESOLVED; 9 из 12 критериев без открытых находок |
| Охват | повторная оценка изменённого текста (визит 1 — 5 файлов дифа ceddd32..6f175cf; визит 2 — 3 файла 6f175cf..ee2dc59) с полным проходом по файлам правки; тесты: 149, OK |
| Правило остановки | не выполнено: 0 high, 1 medium (F5.3, только BLUEPRINT.md) — совет для гейта выпуска, не блок |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
expects commands: uv
```

Expects: `expects commands: uv`. Предупреждения `expects.commands needs LADO 0.30 or newer`
нет: `dependencies.lado: ">=0.30"`.

Read-only: строки `read-only roles: …` нет — ролей нет; `dependencies.lado: ">=0.30"`.

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.6.0

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

```
$ flow_diagram.py . --compare BLUEPRINT.md
no flows in . or BLUEPRINT.md: nothing to do (exit status 0)
```

### Тесты и следы проекта

```
$ uv run --no-project python -m unittest discover -s tests
Ran 149 tests in 9.465s

OK
```
`grep -rniE "waiting|LAD-[0-9]|polygon|lado\b" skills README.md kit.yaml tests BACKLOG.md`
(визит 1) находит только пути `.lado/`, имя инструмента LADO, `LADO_AGENT`, метку
`[LADO: …]`, `lado kits`/`lado start` и `dependencies.lado`; правки визита 2 следов не
добавили (полный проход: в jira.py и SKILL.md `LAD-`, `waiting`, `polygon` нет).

## Исправить сначала

Блокирующих нет. Если править до выпуска — две строки BLUEPRINT.md:

1. R7 описывает старую проверку типа `field`, которая пропускала системные поля, — привести
   к R8 и коду (F5.3).
2. Строка журнала 1.6.0 пишет «R8: `field`'s exit 11» и не называет правок гейта (F5.4).

## Находки

Визит 2: только находки в изменённом тексте, открытые сейчас. Находки визита 1 — в
«Прежние находки».

### 1. Границы ролей

Не применимо: ролей нет. Правило записи — одно, SKILL.md:30-31.

### 2. Передачи между шагами

Не применимо: потоков нет. Вывод `field` и `download` не менялся.

### 3. Готовность и исходы

Каждый перенесённый или новый код ведёт к действию: строка 3 — поле не того типа «report
it; the user fixes the file», строка 11 — «a `field` not on the edit screen: report it,
Jira's admin adds the field to the screen», строка 1 — «the script crashed, or `download`
could not write a file | report its last line» (F3.1 и F3.2 визита 1 RESOLVED).

### 4. Независимая проверка

Не применимо: потоков нет. Проба `field` на тестовой Jira 8.13.19 (R10) ещё не сделана;
где её проводить, решает человек на гейте. Это шаг запуска, не находка текста.

### 5. Противоречия

- **F5.3** [medium] `BLUEPRINT.md:176` (R7)
  > `  field's type checked first in `/rest/api/2/field` (`schema.type == "string"`, not a`
  R7 по-прежнему описывает проверку типа до гейта — ту, что пропускала системные
  строковые поля (`summary`, `description`), то есть F12.1 визита 1. R8
  (BLUEPRINT.md:230-232 «a field in `fields` that is not a custom single-line text field
  (`customfield_*` of type textfield; a system field such as `description` included) is a
  settings error, exit 3») и код (jira.py:1130 `if schema.get("custom") != TEXT_FIELD:`)
  говорят обратное. Текст пришёл в этом запуске (2b2a5a1), ee2dc59 правил R8, не тронув
  R7. Агенты BLUEPRINT не читают, но следующий автор, собирая по R7, вернёт перезапись
  описания без метки. Проходы дали low (мой, A, B) и medium (полный); взят medium.
  Fix: в R7 — «(`schema.custom` is `…customfieldtypes:textfield`; a system, multi-line or
  option field is refused, R8)». Passes: 3/3, и полный проход

- **F5.4** [low] `BLUEPRINT.md:387` (журнал, строка 1.6.0)
  > `R8: `field`'s exit 11`
  Единственная строка 1.6.0 говорит, что поле не того типа — exit 11, а `download --to` —
  только «inside the repository»; правок гейта (отчёт 66d8918: F12.1, F3.1, F5.1, F5.2,
  F12.2, F5.3, F3.2) журнал не называет, они есть лишь в R1, R8, R11. Тот, кто проследит
  1.6.0 по журналу, получит старый код. (Цитата — часть одной длинной строки таблицы.)
  Fix: в строке «R8: `field`'s wrong type exit 3, not on the screen 11», «or the main
  checkout»; добавить строку 1.6.0 «release gate, report 66d8918: …» с ответом человека.
  Passes: 3/3, и полный проход

Остальное согласовано: `attach` и `transition` теперь делят один `_comment_failed`, и
совет после 401 больше не противоречит строке 5; поле не того типа — exit 3, как у
tracker-yougile 94a29f5 («or has states, is exit 3, nothing written»).

### 6. Дублирование

Совет после неудачного комментария — в одном месте (`_comment_failed`, jira.py:957-975),
R8 ссылается на него одной фразой; правило записи — одно (SKILL.md:30-31).

### 7. Когда звать человека

Каждый новый или перенесённый код говорит «report it» и кто исправляет: пользователь —
файл, администратор Jira — экран.

### 8. Повторные визиты

Не применимо: потоков нет; повтор `field` по-прежнему даёт «nothing changed».

### 9. Краткость и «почему»

Новые правила несут причину: jira.py:1128 «a system field (description, summary) would be
rewritten without the mark and outside edit's rule»; exit 1 — «nothing to fix in the
command». F9.1 визита 1 оставлен человеком («Оставлено планом»).

### 10. Описания навыков

Не менялись в визите 2; описание называет все 13 действий.

### 11. Нейтральность к провайдеру

`find_repository` читает только файлы `.git` и `commondir`, `git` не запускает; имён CLI
нет.

### 12. Безопасность и границы

- **F12.3** [low] `skills/tracker/jira.py:244`
  > `            with open(os.path.join(gitdir, "commondir"), encoding="utf-8") as handle:`
  У файла `.git` подмодуля нет `commondir`, поэтому поиск кончается на подмодуле и
  содержащий его проект не входит в отказанные папки. Проба (субагент A): cwd
  `main/mods/sub`, `--to main/docs` — exit 0, файл записан в
  `/tmp/claude-1000/v2a/main/docs/a.txt`, среди файлов основной копии (известная дыра 3).
  Маловероятно: агенты работают из корня worktree. Для worktree LADO внутри основной копии
  отказ работает (пробы на `git worktree add`: внутри, вне, относительный gitdir,
  симлинки — везде exit 2).
  Fix: без `commondir` идти выше от `os.path.dirname(here)` и добавлять каждый найденный
  репозиторий; или назвать подмодуль в R11 как непроверяемый. Passes: 1/3, confirmed
  (вывод пробы выше)

## Известные дыры

| Известная дыра | Находка, или как кит её закрывает |
|---|---|
| 1. Красная проверка возвращается без учёта среды | Не применимо: потоков нет. Навык отличает среду (4, 5, 9, 10, 12; сообщения `uv`/Python) от запроса (2, 8, 11) |
| 2. Работа вне потока, слияние без гейта | Не применимо: ролей и слияний нет; запись — по SKILL.md:30-31 |
| 3. Путь вне worktree запуска | `--to` внутри репозитория и основной копии worktree — exit 2 (F12.2 RESOLVED); остаток — подмодуль (F12.3) |
| 4. Вердикт без порога серьёзности | Не применимо: ревьюеров нет |
| 5. Зависимый навык пишет или спрашивает, где роли нельзя | Не применимо: зависимых навыков нет |
| 6. Команды не в ладу с `expects.commands` | Закрыта: `expects commands: uv`, `dependencies.lado: ">=0.30"`; jira.py не запускает других CLI (`find_repository` читает файлы) |
| 7. Read-only роли не в ладу с делом | Не применимо: ролей нет |

## Не прослежено

Ничего блокирующего: правки гейта прослежены в R1, R8, R11 (14a1a78, ee2dc59); бюджет
green; потоков и скелетов нет. Расхождения внутри BLUEPRINT — F5.3 (R7) и F5.4 (журнал).
Exit 3 для id из `fields`, которого нет в Jira, по-прежнему не назван в R8 отдельной
фразой (визит 1, совет), но покрыт R6.

## Прежние находки

Визит 1 (отчёт 66d8918, коммит 6f175cf):

| Находка | Статус | Доказательство |
|---|---|---|
| F12.1 [medium] системные поля проходят проверку типа | RESOLVED | jira.py:1130 `if schema.get("custom") != TEXT_FIELD:`; проба: `fields: summ: summary`, `field TEST-1 summ x` — exit 3 «… is of type system field summary, not a custom single-line text field (textfield): report it, the user fixes the file», ничего не отправлено; тесты с `summary`, `description` |
| F3.1 [medium] строка 11 «fix the request once» для `field` | RESOLVED | поле не того типа — строка 3 (SKILL.md:206 «or its field missing in this Jira or not a custom single-line text field \| report it; the user fixes the file»), как у tracker-yougile; строка 11 (SKILL.md:214) «a `field` not on the edit screen: report it, Jira's admin adds the field to the screen» |
| F5.1 [low] «field» в правиле записи | RESOLVED | SKILL.md:30 «label, set a field, link» |
| F5.2 [medium] метку называет и роль | RESOLVED | SKILL.md:92 «Use the label your role, your step or the human names»; R1 (BLUEPRINT.md:19) так же |
| F9.1 [low] фраза для авторов процесс-китов | STILL OPEN, оставлена человеком | SKILL.md:93-94 без изменений («Оставлено планом») |
| F12.2 [low] `--to` в основную копию | RESOLVED | `find_repository` (jira.py:226-250) идёт `.git` → gitdir → `commondir`; пробы на настоящих worktree — exit 2; SKILL.md:130 «outside the repository and the checkout its worktree lies in»; тест `test_download_into_the_main_checkout_of_a_worktree_is_refused`. Остаток — F12.3 |
| F5.3 [medium, пропущено ранее] совет после комментария `attach` | RESOLVED | jira.py:1343 `_comment_failed(failure, "do not attach again")`; пробы: 401 → exit 5 «report it; send the comment with comment once you are told to», 502 → «may not have been added … check with get», обрыв → «once you are told Jira answers again»; тест `test_attach_comment_failure_keeps_its_rule`; R8 (BLUEPRINT.md:214-215) |
| F3.2 [low, пропущено ранее] OSError в `download` — exit 2 | RESOLVED | `getattr(failure, "code", CRASH)`; проба: exit 1 «cannot write: [Errno 2] …; report it»; строка 1 SKILL.md; тест `test_download_a_file_it_cannot_write_is_exit_1` |

Отчёт 85d77cb (полная оценка ceddd32): все 6 RESOLVED на визите 1 (F10.1, F5.1, F5.2,
F6.1, F9.1, F12.1), правки визита 2 их не трогали; F5.1 дополнена ролью (F5.2 визита 1).

План (артефакт `plan`): все пункты RESOLVED на визите 1, кроме проверки типа (была STILL
OPEN частично — теперь RESOLVED, F12.1); проба на тестовой Jira — открыта по плану, перед
гейтом выпуска.

## Вырезанные правила

| Удалённое правило (файл:строка в базе 6f175cf) | Где оно теперь |
|---|---|
| SKILL.md:101-102 «a field of another type … exit 11» | SKILL.md:101 и строка 3 — exit 3, намеренно (решение человека, вопрос 1) |
| SKILL.md:102 «one Jira does not let you set (not on the task's edit screen), exit 11» | SKILL.md:102-103, то же |
| SKILL.md:212, строка 11 «a `field` not a single-line text field» | строка 3 (SKILL.md:206) |
| SKILL.md:30 «label, field, link» | SKILL.md:30 «label, set a field, link»; чтение — не запись, намеренно |
| SKILL.md:92 «your step or the human names» | SKILL.md:92, с «your role» |
| SKILL.md:129 «outside the repository (one inside is exit 2)» | SKILL.md:130-131, расширено основной копией |
| строка 1 «the script crashed» | строка 1, расширено |
| jira.py `cmd_transition`: совет по коду после комментария | `_comment_failed` (jira.py:957-975), те же ветки, тот же текст и правило 429 |
| jira.py `cmd_attach`: «do not attach again; send it with comment» | «do not attach again» на месте; «send it with comment» — совет по коду (правка F5.3) |
| jira.py `cmd_download`: «cannot write: %s» | на месте, с «; report it», exit 1 |
| jira.py `cmd_field`: `schema.type == "string"` | заменено строже: `custom == textfield` (textfield всегда string) |
| BLUEPRINT R1 «its step or the human names» | R1, с «its role» |
| BLUEPRINT R8 «a field of another type … exit 11 with the type named» | R8 (BLUEPRINT.md:230-234), exit 3 с типом, намеренно |
| BLUEPRINT R11 «`--to` … inside the current repository is exit 2» | R11 (BLUEPRINT.md:250-252), расширено |

Ни одно правило не потеряно.

## Пропущено ранее

Визит 2: нет. Обе находки визита 1 (F5.3, F3.2) RESOLVED (см. «Прежние находки»).

## Оставлено планом

- **F9.1** [low] `skills/tracker/SKILL.md:93` — фраза «so a process kit that runs on both
  uses label words without spaces» оставлена по решению человека на гейте выпуска; план её
  и просил.

## Вопросы к человеку

1. F5.3 [medium] и F5.4 [low] — правки двух строк BLUEPRINT.md, кода и SKILL.md не
   касаются. Исправить до тега? Рекомендую да: R7 в нынешнем виде ведёт следующую сборку
   обратно к перезаписи описания.
2. F12.3 [low] (подмодуль) — оставить или исправить? Рекомендую оставить на потом
   (BACKLOG): агенты работают из корня worktree, LADO подмодули не создаёт.
3. Проба `field` на тестовой Jira 8.13.19 (R10) — где и когда её провести до тега.
