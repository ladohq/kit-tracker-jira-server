# Отчёт о ките: tracker-jira-server 1.3.0

- Дата: 2026-10-12
- Кит: `.` (worktree запуска `improve/tracker-jira-server-1-3-0`), путь задан
- Коммит: e857643 (`kit.yaml` `version: 1.3.0`)
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.2.0-2026-10-09.md`
  (6efeefc, оценивал 0a71e86; на шаге `assess` взят как оценка, текст кита с тех пор не
  менялся). База — 6efeefc, её называет план. Дифф
  `git diff 6efeefc -- kit.yaml README.md BLUEPRINT.md agents flows skills` затрагивает
  5 файлов: BLUEPRINT.md, README.md, kit.yaml, skills/tracker/SKILL.md,
  skills/tracker/jira.py. Визит 1 шага `evaluate`.
- Проходы: изменение около 100 строк. Три прохода по изменённому тексту я сделал сам, по 12
  критериям и известным дырам, с разных начал: 1) kit.yaml, README и BLUEPRINT R3/R8/R9/R11/R12;
  2) `cmd_edit`, `remark`, `_read_issue`/`_print_issue` против таблицы кодов SKILL.md;
  3) SKILL.md (описание, область записи, строка и пункт **edit**, «Writing in Jira»).
  Они дали одну находку (F6.2, 3/3). Затем полный проход (Re-evaluation 5) по всем пяти
  файлам целиком. Его сделал отдельный субагент без `kit-reports/` и без `JIRA_*`, с пробами
  только против фейковой Jira из тестов. Он повторил F6.2 и дал F9.2, которую я подтвердил
  пробой регулярного выражения. Однопроходных находок отброшено: 0, оставлено как
  подтверждённые: 1 (F9.2).

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений; `expects commands: uv` |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано: потоков нет (R2), скелетов в BLUEPRINT.md нет |
| b. Рубрика | 2 находки (0 high, 0 medium, 2 low); обе находки отчёта 1.2.0 (F3.5, F6.1) RESOLVED; 10 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста и полный проход по 5 файлам, которых касается дифф (kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py); тесты: 97, OK |
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

Read-only: строки `read-only roles: …` нет (ролей нет); `dependencies.lado: ">=0.30"`.

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.3.0

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
no flows in . or BLUEPRINT.md: nothing to do (exit status 0)
```

## Исправить сначала

Блокирующих находок нет. По желанию, обе low:

1. Назвать `edit` в описании кита в `kit.yaml` (F6.2).
2. Сузить `LEADING_MARK` до формы метки или сказать в SKILL.md «a leading mark» (F9.2).

## Находки

### 1. Границы ролей

Не применимо: ролей нет. Область записи для `edit` — SKILL.md:28-29 «Edit only when the
human or your step asks for it, since `edit` rewrites text a person may have written», как
R11 и README.

### 2. Передачи между шагами

Не применимо: потоков нет. Выход `edit` задан: «It prints the task's new state, as `get`
does» (SKILL.md:61-62), код печатает через общий `_print_issue`.

### 3. Готовность и исходы

Успех и «уже так» определены: «when nothing changes it says so: that is success»
(SKILL.md:60-61). Каждый отказ `edit` попадает в строку таблицы кодов: 2 (нет флага,
пустой текст), 7 (404, без PUT), 11 (поле не на экране, отказ значения), 12 (5xx, «may have
been applied»). Ошибка чтения после PUT — «changed, but reading the task back failed (do not
run it again)», как у `label`. F3.5 закрыта (см. «Прежние находки»).

### 4. Независимая проверка

Не применимо: потоков нет. R10 (BLUEPRINT.md:241-245): проба на тестовой Jira перед
одобрением релиза, когда она доступна.

### 5. Противоречия

SKILL.md, README, BLUEPRINT R3/R8/R9/R11/R12 и код согласны во флагах `edit`, метке,
области записи и кодах выхода; `edit --help` совпадает со строкой таблицы действий.
Неточность «replaces the description's old one» — F9.2.

### 6. Дублирование

- **F6.2** [low] `kit.yaml:4`
  > The tracker skill for Jira Server / Data Center 8.4 or newer: find, read, create, move, comment
  Описание кита (строки 4-7) перечисляет действия 1.2.0 без `edit`. README.md:4 («creates,
  edits (summary and description), moves,») и описание SKILL.md его называют, так что копии
  уже расходятся. Тот, кто выбирает кит по `lado kits show`/`list`, не увидит, что кит
  переписывает название и описание. Автор сам отметил это в `build-report`; план для
  `kit.yaml` называл только версию.
  Fix: дописать в описание «edit (summary and description)». Passes: 3/3 и полный проход.

### 7. Когда звать человека

`edit` — только по слову человека или шага; отказ сообщается по SKILL.md «To **report** a
failure: as a worker, send the supervisor that line and the command with `send_message`;
as the lead, tell the human».

### 8. Повторные визиты

Не применимо: потоков нет. `edit` идемпотентен: «A field already so is not sent, so an edit
run twice changes nothing the second time» (jira.py:700).

### 9. Краткость и «почему»

- **F9.2** [low] `skills/tracker/jira.py:514`
  > LEADING_MARK = re.compile(r"\A\s*\\?\[LADO:[^\n]*?\\?\]\s*")
  Выражение ловит любой текст от `[LADO:` до первой `]` в начале описания, а не только
  форму метки, и только в самом начале. В итоге (а) ссылка в начале текста, чьё имя
  начинается с «LADO:», теряется, и (б) если человек написал текст над старой меткой,
  после `edit` из текста `get` меток станет две. SKILL.md:62 при этом обещает без
  оговорок: «Your mark replaces the description's old one.» Оба случая редки и задевают
  только саму метку.
  Fix: ловить только форму метки (`\\?\[LADO: [^\]\n|]*\\?\]`), или написать в SKILL.md:62
  «a leading mark».
  Passes: 1/3 (полный проход), confirmed. Проба:
  `R.sub('', '[LADO: x](http://e/a) hello', count=1)` → `'(http://e/a) hello'`;
  `R.sub('', 'a\n\\[LADO: analyst\\]\n\nb2', count=1)` → без изменений, затем `mark`
  добавляет вторую метку.

### 10. Описания навыков

Описание SKILL.md называет `edit` («change a task's summary or description») и когда его
использовать; навык один, зависимых и ожидаемых навыков нет.

### 11. Нейтральность к провайдеру

Скрипт вызывается через `${SKILL_DIR}/jira.py`, для CLI без подстановки есть запасной путь
(«If your CLI does not expand `${SKILL_DIR}`, use the folder this SKILL.md is in»).
Имён инструментов отдельных CLI нет.

### 12. Безопасность и границы

`edit` строже прочих записей (R11, SKILL.md:28-29); удаления нет; учётные данные не
печатаются; пишутся только отличающиеся поля. Переписанное описание остаётся в истории
задачи в Jira.

## Известные дыры

| Известная дыра | Находка, или как кит её закрывает |
|---|---|
| 1. Красная проверка возвращается без учёта среды | Не применимо: потоков нет. SKILL.md отличает сообщения `uv`/Python от сообщений скрипта («Any other message that does not start with `jira.py` … comes from `uv` or Python before the script ran») |
| 2. Работа вне потока, слияние без гейта | Не применимо: ролей и потоков нет; `edit` — только по слову человека или шага |
| 3. Путь вне worktree запуска | Нет: `${SKILL_DIR}/jira.py`; путь в README — для ручной проверки человеком |
| 4. Вердикт без порога серьёзности | Не применимо: ревьюеров нет |
| 5. Зависимый навык пишет или спрашивает, где роли нельзя | Не применимо: зависимых навыков нет |
| 6. Команды не в ладу с `expects.commands` | Закрыта: `expects commands: uv`, `dependencies.lado: ">=0.30"`; скрипт запускает только `uv` |
| 7. Read-only роли не в ладу с делом | Не применимо: ролей нет |

## Не прослежено

Ничего. `edit` прослежен в R3, R8, R9, R11, R12 и разделе 3 («commands `get`, `search`,
`create`, `edit`, …»); журнал раздела 5 имеет строку 1.3.0; бюджет зелёный (раздел 4
«Output of the kit-budget script on the built kit (1.3.0)» совпадает с выводом выше).
Скелетов потоков нет: потоков нет (R2).

## Прежние находки

| Находка | Статус | Доказательство |
|---|---|---|
| F3.5 [low] строка 7: «check the key» после 404 на `assign … none` | RESOLVED | SKILL.md:149 «check the key; report it if the key came from someone else (after `assign … none`: report it)» |
| F6.1 [low] R8 без кода 4 | RESOLVED | BLUEPRINT.md:125 «other failure (4, 5, 6, 7, 10, 429), report it and send the comment only when told to»; `jira.py:813` ветка `else` — «report it; send the comment with comment once you are told to» |

Изменения плана: `edit` (jira.py, SKILL.md, тесты), README, `kit.yaml` 1.3.0, BLUEPRINT —
сделаны, как в списке `build-report`; проверено по файлам и тестам (97, OK). Проба на
тестовой Jira (R10) — не дело автора, её проводит supervisor перед одобрением релиза.

## Вырезанные правила

| Удалённое правило (файл:строка в базе) | Где оно теперь |
|---|---|
| SKILL.md:23 «every comment and every new task's description with `[LADO: …]`» | SKILL.md:24 «every comment and every description it writes» (шире, правило сохранено) |
| SKILL.md:27-28 «…and only on the tasks named; your process kit's roles and steps may allow more.» | SKILL.md:28-30, оба правила на месте |
| README.md:78-81 метка и область записи | README.md:78-84, оба правила на месте, дополнены `edit` |
| BLUEPRINT.md R8, R9, R11, R12 (переписанные строки) | те же требования; только дополнения |
| jira.py `cmd_get` (тело) | `_read_issue` + `_print_issue`, поведение то же (тесты `get` проходят) |

Ни одно правило не потеряно.

## Пропущено ранее

Нет. Полный проход не нашёл находок в тексте, которого не касается дифф.

## Оставлено планом

Ничего: «Leave: none».

## Вопросы к человеку

Нет.
