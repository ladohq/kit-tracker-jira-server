# Отчёт о ките: tracker-jira-server 1.0.1

- Дата: 2026-10-09
- Кит: `.` (worktree запуска `improve/tracker-jira-server-markdown`), путь задан
- Коммит: a0b8837 (`kit.yaml` `version: 1.0.1`)
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно версии 1d512d7/66a3ecf этого отчёта (коммит
  16909d7), база — 16909d7 (её называет план),
  `git diff 16909d7 -- kit.yaml README.md BLUEPRINT.md agents flows skills`: 3 файла
  (`jira.py`, `SKILL.md`, `BLUEPRINT.md`). Второй визит `evaluate`. Предыдущая версия
  (визит 1, 16909d7 против 1240f8d): `approved`, 5 находок (0 high, 2 medium, 3 low).
- Проходы (этот визит): изменение — около 50 строк. Три прохода я сделал сам, без
  субагентов. Проход 1: `jira.py` (`held`, `_same_list`, `_item`, `CODE_ESCAPE`, `LINK`)
  с запусками конвертера на 13 входах. Проход 2: две новые фразы SKILL.md против
  поведения скрипта. Проход 3: строка 1.0.1 журнала BLUEPRINT против плана и файлов.
  Затем полный проход по всем трём файлам, которых касается дифф (Re-evaluation 5): новых
  находок нет. Однопроходных находок отброшено: 0; оставлено как подтверждённые: 0.
  Проходы визита 1 описаны в версии 1d512d7.
- Оговорка: вывод конвертера подтверждён запусками. Как Jira Server 8.13 его покажет, я не
  проверял: это проверка на тестовой Jira 8.13.19 (R10). В неё входят F5.1, а также `\-`,
  `\|`, `\_` внутри `{{…}}` (F5.3).

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано (у кита нет потоков, R2); скелетов в BLUEPRINT.md нет |
| b. Рубрика | 1 открытая находка (0 high, 1 medium — F5.1, оставлена планом, 0 low); F5.2–F5.5 RESOLVED; новых находок нет; 11 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста, с полным проходом по 3 файлам, которых касается дифф (skills/tracker/jira.py, skills/tracker/SKILL.md, BLUEPRINT.md); тесты: 60, OK |
| Правило остановки | выполнено: в изменённом тексте 0 high, 0 medium; F5.1 (medium) оставлен планом до пробы на тестовой Jira |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
```

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.0.1

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

У кита нет потоков (R2), скелетов нет; сравнивать нечего. Скрипт потоков этого случая
по-прежнему не знает (см. «Found on the way»):

```
$ uv run --script flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Исправить сначала

1. F5.1 — оставлена планом: решается по итогам пробы на тестовой Jira 8.13.19 (см.
   «Left by the plan»).

## Находки

### 1. Границы ролей

Не применимо: ролей нет (R2). Право на запись в Jira не изменилось: SKILL.md:25-26 «only
when your role, / your step or the human asks for it».

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

Не применимо: потоков нет. Сбой конвертера — не новый код выхода: `to_wiki` возвращает
исходный текст (`jira.py` `except Exception: return text`), так что таблица кодов
SKILL.md не меняется.

### 4. Независимая проверка

Не применимо: потоков нет. Исправления покрыты тестами:
`test_blank_lines_inside_a_list_are_dropped` (F5.2), `test_emphasis_and_code` (F5.3),
`test_links` (F5.4). Всего 60 тестов, OK.

### 5. Противоречия

Открыта одна находка визита 1, её оставил план (STILL OPEN):

- **F5.1** [medium] `skills/tracker/jira.py:396`
  > `            out.append("{code:%s}" % match.group(2) if match.group(2) else "{code}")`
  Любое слово после ```` ``` ```` уходит в `{code:<слово>}`. Для языка вне списка Jira
  8.x над блоком появляется «Unable to find source-code formatter for language: …», а
  SKILL.md:68 обещает «fenced code blocks (with their language)».
  Fix: короткий список языков Jira 8.13 с синонимами, остальное — `{code}`; список
  проверить на тестовой Jira 8.13.19. Passes: 3/3 (визит 1)

Исправления визита 1 проверены запусками:

```
'1. one\n\n2. two\n'                      -> '# one\n# two\n'
'1. a\n\n   - b\n\n2. c'                  -> '# a\n#* b\n# c'
'- e\n\n1. f'                             -> '* e\n\n# f'
'1. a\n\nPara\n\n2. b'                    -> '# a\n\nPara\n\n# b'
'- a\n\n\n- b\n'                          -> '* a\n* b\n'
'1. a\n\n'                                -> '# a\n\n'
'- a\n\n```\ncode\n```'                   -> '* a\n\n{code}\ncode\n{code}'
'use `--force` and `a|b` and `x_y`'       -> 'use {{\-\-force}} and {{a\|b}} and {{x\_y}}'
'![alt](http://x/y.png) and [t](http://u)' -> '![alt](http://x/y.png) and [t|http://u]'
```

Новых противоречий нет. Новая фраза SKILL.md:73-74 («A code block inside a numbered list
ends the list in Jira») совпадает с поведением конвертера: `'1. run:\n   ```bash\n   ls\n
```\n2. done'` → `'# run:\n{code:bash}\n   ls\n{code}\n# done'`.

### 6. Дублирование

Подмножество Markdown названо в трёх местах: SKILL.md:67-70 (агенту), README.md:71-72
(человеку, коротко) и BLUEPRINT R12 (требование). У каждого из них свой читатель; копии
не расходятся. Нарушения нет.

### 7. Когда звать человека

Не применимо: ролей нет. Правило «report it» для кодов окружения не менялось.

### 8. Циклы на повторном визите

Не применимо: потоков нет.

### 9. Краткость и «почему»

Раздел SKILL.md:65-76 — 10 строк вместо 25 в 1.0.0 (SKILL.md: 1248 → 1242 слова). Обе
новые фразы этого визита несут причину: «Jira shows every line break», «so the numbering
after it starts again at 1».

### 10. Описания навыков

Описание `tracker` не менялось и по-прежнему говорит, что навык держит и когда его
звать; Markdown для описания не нужен. Внешних навыков нет.

### 11. Нейтральность к провайдеру

Нового пути к файлу нет; запуск по-прежнему `python3 ${SKILL_DIR}/jira.py`; только
стандартная библиотека (`import re`).

### 12. Безопасность и границы

Новых действий, которые трудно отменить, нет: конвертер меняет только текст, который и
раньше отправлялся по тем же правилам записи (R11). Метка R9 добавляется после
конвертации и через конвертер не проходит: `mark(text_arg(...))`, `jira.py:643`, `:653`.

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Коды разделяют окружение (4, 5, 9, 10, 12 — «report it») и ошибку запроса (2, 8, 11 — «fix»); сбой конвертера не даёт кода, текст уходит как есть. |
| 2. Work outside a flow, merge without a gate | Нет git-работы; запись в Jira — SKILL.md:25-26 «only when your role, / your step or the human asks for it». |
| 3. Path outside the run's worktree | Не изменилось: `.lado/tracker.yaml` «from the current directory up to the repository root». |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: `dependencies.skills` нет. |

## Not traced

Ничего: R12 называет `tracker`, `jira.py` и тесты (раздел 3 и обратная проверка), меры
бюджета green, потоков и скелетов нет (R2).

## Previous findings

Версия 1d512d7/66a3ecf этого отчёта (16909d7):

| Находка | Статус | Доказательство |
|---|---|---|
| F5.1 [medium] язык блока кода | STILL OPEN, оставлена планом | `jira.py:396` не менялся; план «Leave: F5.1 … decided from that trial» |
| F5.2 [medium] пустая строка / блок кода рвут нумерованный список | RESOLVED | `jira.py:412` `if lists and not line.strip():` (пустые строки придерживаются в `held`, `_same_list`); запуск `'1. one\n\n2. two\n'` → `'# one\n# two\n'`; блок кода — SKILL.md:73-74 «A code block inside a / numbered list ends the list in Jira»; `test_blank_lines_inside_a_list_are_dropped` |
| F5.3 [low] разметка внутри `{{…}}` | RESOLVED | `jira.py:362` `CODE_ESCAPE = re.compile(r"([*_\-+^~{}\[\]|])")`; запуск `` `--force` `` → `{{\-\-force}}`; `test_emphasis_and_code` |
| F5.4 [low] изображение → `![alt\|url]` | RESOLVED | `jira.py:357` `(?<!!)`; запуск без изменений; `test_links` |
| F5.5 [low] строки абзаца, перенесённые по ширине | RESOLVED | SKILL.md:73 «Write each paragraph on one line: Jira shows every line break.» |

Отчёт 1.0.0 (1240f8d, `assessment`) находок не имел; пункты плана визита 1 — RESOLVED
(таблица в версии 1d512d7). Build-report сверен с файлами: совпадает.

## Cut rules

| Удалённое правило (файл:строка в базе 16909d7) | Где теперь |
|---|---|
| `jira.py:357` `LINK` без `(?<!!)` | Тот же шаблон, сужен (F5.4) |
| `jira.py:372` `{{%s}}` без экранирования | `jira.py` с `CODE_ESCAPE` (F5.3) |
| `jira.py:401-402` вычисление `indent`, `kind` | `_item()`, вызывается там же |
| BLUEPRINT.md, строка журнала 1.0.1 | Та же строка, дополнена исправлениями и ответом на гейте |

Правил не потеряно. Удалённая строка комментария `_inline` дополнена, а не сокращена.

## Missed earlier

Нет: полный проход по трём файлам новых находок вне изменённого текста не дал.

## Left by the plan

- F5.1 [medium] — языки блоков кода. Причина плана: «the human wants to fix F5.2–F5.5
  first and then test; which languages Jira 8.13 accepts is checked on the test Jira
  8.13.19, and F5.1 is decided from that trial».

## Questions for the human

Нет.

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не знает кита без
  `flows/`: `error: kit.yaml: states must be a non-empty mapping` (код 2). Всё ещё открыто.
- `[kit-builder]` Скрипты `kit-budget` требуют `uv run --script` (PyYAML): при запуске
  через `python3` они падают с `ModuleNotFoundError: No module named 'yaml'`. Скилл это
  говорит («Run it»); заметка только для тех, кто запускает их иначе.
