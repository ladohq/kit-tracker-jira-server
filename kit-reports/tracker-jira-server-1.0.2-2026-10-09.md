# Отчёт о ките: tracker-jira-server 1.0.2

- Дата: 2026-10-09
- Кит: `.` (worktree запуска `improve/tracker-jira-server-1-0-2`), путь задан
- Коммит: e9000a2 (`kit.yaml` `version: 1.0.2`); визит 1 оценивал f20af91
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно отчёта
  `kit-reports/tracker-jira-server-1.0.1-2026-10-09.md` (a0b8837, `assessment`). База —
  a0b8837: её называет план. `git diff a0b8837 -- kit.yaml README.md BLUEPRINT.md agents
  flows skills` затрагивает 4 файла: BLUEPRINT.md +10/−4, kit.yaml, SKILL.md +4/−5,
  jira.py +41/−8. Визит 2 `evaluate`: после гейта выпуска, где человек сказал «исправить
  F5.6 и сразу проверить». С визита 1 (19383cc) изменились `jira.py` +5/−1 (5eca454), тесты
  и BLUEPRINT.md +3/−2 (e9000a2: R3 и строка журнала 1.0.2).
- Проходы визита 2: изменение — 8 строк. Три прохода я сделал сам: ветка «already in»
  `cmd_transition` и её сбои; R3 и журнал против плана; тесты против плана. Затем
  полный проход по `cmd_transition` и BLUEPRINT R3. Новых находок нет; однопроходных
  отброшено 0, оставлено 0.
- Проходы визита 1: изменение — около 60 строк. Три прохода я сделал сам, без субагентов.
  Проход 1: `jira.py` (`CODE_LANGUAGES`, `_language`, `mark`, `cmd_transition`,
  `_add_comment`) с запусками конвертера на 9 входах. Проход 2: SKILL.md (раздел
  «Writing in Jira» и таблица кодов выхода) против поведения `cmd_transition`.
  Проход 3: R3, R9, R12 и журнал BLUEPRINT против плана и файлов. Затем полный проход по
  четырём файлам, которых касается дифф (Re-evaluation 5). Он дал одну находку в
  неизменённых строках (F5.6, «Missed earlier»), подтверждённую запуском.
  Однопроходных находок отброшено: 0; оставлено как подтверждённые: 1 (F5.6).
- Оговорка: вывод скрипта подтверждён тестами и запусками. Как Jira 8.13 покажет
  `{code:none}` и `\[LADO: …\]`, проверено в пробе `trial-1.0.1` на ручных примерах.
  Ветка `transition` с полем `comment` на экране проверена только на поддельной Jira:
  на тестовой Jira у всех переходов `fields: {}`. Пункты 1–3 подтверждены на живой Jira
  (`trial-1.0.2`). Ту же ветку и F5.6 там не проверяли; план назначает пробу F5.6
  перед гейтом выпуска.

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано (у кита нет потоков, R2); скелетов в BLUEPRINT.md нет |
| b. Рубрика | 0 открытых находок; F5.1 и F5.6 RESOLVED; пункты плана RESOLVED; 12 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста, с полным проходом по 4 файлам, которых касается дифф (kit.yaml, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py); тесты: 64, OK |
| Правило остановки | выполнено: в изменённом тексте 0 high, 0 medium |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
```

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.0.2

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

У кита нет потоков (R2) и нет скелетов, поэтому сравнивать нечего. Скрипт потоков
по-прежнему не обрабатывает такой кит (см. «Found on the way»):

```
$ uv run --script flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Исправить сначала

Ничего: открытых находок нет.

## Находки

### 1. Границы ролей

Не применимо: ролей нет (R2). Право на запись в Jira не менялось: SKILL.md:25-26 «only
when your role, / your step or the human asks for it». Отдельный POST комментария
выполняет то, о чём агент уже попросил через `--comment`, и новой записи не добавляет.

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

Не применимо: потоков нет. Новый частичный исход (переход сделан, комментарий нет)
выдаёт одну строку с кодом самого сбоя комментария, `jira.py:704`
`"%s done, but the comment was not added (do not "`. Строка говорит агенту, что делать.
Таблица кодов SKILL.md остаётся верной: при 9 и 12 к строке добавляется `APPLIED`
(«check with get»).

### 4. Независимая проверка

Не применимо: потоков нет. Изменения покрыты тестами:
`test_code_block_language_is_one_jira_knows`, `test_transition_comment_on_its_screen`,
`test_transition_without_comment_field_posts_the_comment_after`,
`test_transition_done_but_comment_failed_says_so`; метку проверяют 8 утверждений.
`test_transition_already_there_still_posts_the_comment` (F5.6). Всего 64 теста, OK. Ветку «поле `comment` на экране» Jira 8.13 не проверяли (см. оговорку).

### 5. Противоречия

Новых противоречий в изменённом тексте нет. Языки проверены запусками:

```
'```\nx\n```'                     -> '{code:none}\nx\n{code}'
'```Python\nx\n```'               -> '{code:python}\nx\n{code}'
'```c++\nx\n```'                  -> '{code:c++}\nx\n{code}'
'```c#\nx\n```'                   -> '{code:c#}\nx\n{code}'
'```ts\nx\n```'                   -> '{code:javascript}\nx\n{code}'
'```rust\nx\n```'                 -> '{code:none}\nx\n{code}'
'~~~ sh\nx\n~~~'                  -> '{code:sh}\nx\n{code}'
'1. a\n\n   ```bash\n   x\n   ```\n2. b' -> '# a\n\n{code:bash}\n   x\n{code}\n# b'
```

SKILL.md:68-69 «fenced code blocks (a language Jira lacks / becomes plain code)»
совпадает с `_language` (`jira.py:435`). SKILL.md:22-23 по-прежнему пишет метку как
`[LADO: <your agent name>]`. Так её видит человек, хотя отправляется `\[LADO: …\]`
(`jira.py:490`). Агент не ищет метку в выводе `get`, так что расхождения на деле нет.

### 6. Дублирование

Список языков записан в двух местах: в `jira.py` (`CODE_LANGUAGES`) и в BLUEPRINT R12.
В R12 только правило и синонимы, без самого списка, поэтому копии не расходятся.
Нарушения нет.

### 7. Когда звать человека

Не применимо: ролей нет. Правило «report it» для кодов окружения не менялось.

### 8. Циклы на повторном визите

Не применимо: потоков нет.

### 9. Краткость и «почему»

У каждого нового правила в коде есть причина в комментарии:
`# Jira drops update.comment of a transition with no comment field on its screen.`,
`# Escaped: a bare [LADO: x] is a link in Jira, shown red as a broken one.`,
`# The languages Jira 8.13 highlights; any other gets {code:none}: a bare {code} is Java.`
Раздел SKILL.md стал на одну фразу короче. Строка SKILL.md:70 после правки длиннее
соседних. Это вид исходника, а не правило, поэтому находкой не считается.

### 10. Описания навыков

Описание `tracker` не менялось. Внешних навыков нет.

### 11. Нейтральность к провайдеру

Новых путей и зависимостей нет; запуск по-прежнему `python3 ${SKILL_DIR}/jira.py`.

### 12. Безопасность и границы

Новый POST `issue/{key}/comment` уходит только при `--comment` и только после
успешного перехода. Если он не прошёл, строка запрещает повторять переход:
«do not run the transition again; send the comment with comment». Так задача не получит
второй переход. В ветке «already in» (F5.6) уходит только комментарий,
без перехода: тест проверяет, что `POST issue/TEST-1/transitions` не отправлялся.

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Коды разделяют окружение (4, 5, 9, 10, 12 — «report it») и ошибку запроса (2, 8, 11 — «fix»). Сбой комментария после перехода сохраняет код своего сбоя (`jira.py:704`). |
| 2. Work outside a flow, merge without a gate | Нет git-работы. Запись в Jira разрешена только так: SKILL.md:25-26 «only when your role, / your step or the human asks for it». |
| 3. Path outside the run's worktree | Не изменилось: `.lado/tracker.yaml` «from the current directory up to the repository root». |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: `dependencies.skills` нет. |

## Not traced

Ничего. R3 называет отдельный комментарий перехода и комментарий к задаче, уже стоящей в целевом статусе (BLUEPRINT.md:29-32), R9 —
экранированную метку, R12 — языки. Меры бюджета green. Потоков и скелетов нет (R2).
Заголовок раздела 4 BLUEPRINT обновлён до «(1.0.2)», значения совпадают с выводом скрипта
выше.

## Previous findings

Отчёт 1.0.1 (a0b8837, `assessment`) и пункты плана:

| Находка / пункт | Статус | Доказательство |
|---|---|---|
| F5.1 [medium] язык блока кода | RESOLVED | `jira.py:435` `out.append("{code:%s}" % _language(match.group(2)))`; список Jira 8.13 и синонимы — `CODE_LANGUAGES`, `CODE_SYNONYMS`; запуски выше; `test_code_block_language_is_one_jira_knows` |
| Проба 2: комментарий перехода теряется | RESOLVED | `jira.py:691` `inline = comment is not None and "comment" in (transition.get("fields") or {})`; иначе `_add_comment` после перехода; три теста `test_transition_*comment*` |
| Проба 3: метка красная | RESOLVED | `jira.py:490` `label = "\\[LADO: %s\\]" % agent`; тесты, например `tests/test_jira.py:338` |
| Проба 4: ложная фраза SKILL.md | RESOLVED | `grep -n "ends the list" skills/tracker/SKILL.md` ничего не находит |
| `kit.yaml` 1.0.2 | RESOLVED | `kit.yaml:2` `version: 1.0.2` |
| F5.6 [medium] комментарий теряется, если задача уже в целевом статусе (визит 1, «Missed earlier») | RESOLVED | `jira.py:664` `there += ", comment %s added" % _add_comment(jira, args.key, comment)`; `test_transition_already_there_still_posts_the_comment`; BLUEPRINT.md:31 «on a task already in the target status it is posted» |

Build-report сверен с файлами: совпадает. Раздел «Cut text: None» верен в том смысле,
что ни одно правило не сокращено. Единственное удалённое правило удалено по плану
(см. ниже).

## Cut rules

| Удалённое правило (файл:строка в базе a0b8837) | Где теперь |
|---|---|
| SKILL.md:68 «fenced code blocks (with their language)» | SKILL.md:68-69, уточнено: «a language Jira lacks becomes plain code» |
| SKILL.md:73-74 «A code block inside a numbered list ends the list in Jira, so the numbering after it starts again at 1.» | Удалено по плану (проба 4: фраза ложная) |
| `jira.py` `{code}` для блока без языка | `{code:none}` (F5.1, по плану) |
| `jira.py` `update.comment` при любом `--comment` | `jira.py:691-693`, только при поле `comment`; иначе — `_add_comment` |
| `jira.py` тело `cmd_comment` | `_add_comment`, вызывается там же |
| BLUEPRINT R12 «(with their language)», раздел 4 «(1.0.1)» | R12 уточнён (BLUEPRINT.md:92-94), раздел 4 — «(1.0.2)» |
| Визит 2: `jira.py` `print("%s is already in %s" …)` | `jira.py:661-665`, та же строка плюс комментарий при `--comment` (F5.6) |
| Визит 2: BLUEPRINT R3 «Jira silently drops it otherwise), comment» и строка журнала 1.0.2 | Те же места, дополнены F5.6 (BLUEPRINT.md:31-32, строка журнала 1.0.2) |

Правил не потеряно.

## Missed earlier

Нет. F5.6 из визита 1 закрыт (RESOLVED, см. «Previous findings»). Полный проход визита 2
по `cmd_transition` новых находок не дал.

## Left by the plan

- `{x}` внутри кода в тексте (`{{\{x\}}}` ломается) и картинки `![alt](url)` (`[alt]`
  краснеет). Причина плана: «the human chose items 1–4 only; they stay as they are».

## Questions for the human

Нет. Вопрос визита 1 о F5.6 человек решил на гейте: «исправить F5.6 и сразу проверить».

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не обрабатывает кит без
  `flows/`: `error: kit.yaml: states must be a non-empty mapping` (код 2). Всё ещё открыто.
