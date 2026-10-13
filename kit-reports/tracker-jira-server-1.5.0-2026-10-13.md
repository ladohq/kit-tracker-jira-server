# Отчёт о ките: tracker-jira-server 1.5.0

- Дата: 2026-10-13
- Кит: `.` (ветка `lad-46-fixes` репозитория кита; визит 1 — `main`), путь задан
- Коммит: 071e637 (`kit.yaml` `version: 1.5.0`). Визит 1 оценивал 867defa (изменение —
  коммиты 8dc07d2 и 867defa; отчёт c5e6529).
- Оценил: независимый критик (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.4.0-2026-10-12.md`
  (f460312, оценивал 07b1cd7, открытых находок нет). База — f460312, выпущенная 1.4.0. Дифф
  `git diff f460312 867defa` затрагивает 6 файлов: BLUEPRINT.md, README.md, kit.yaml,
  skills/tracker/SKILL.md, skills/tracker/jira.py, tests/test_jira.py. Требования — задача
  Yougile LAD-46 (J1–J9), в пересказе supervisor'а.
- Визит 2, после гейта выпуска («Исправить все 4, затем тег и push»). С визита 1
  (867defa → 071e637) изменились 4 файла, 77 строк добавлено, 15 удалено: `text_arg` —
  отказ 11 для имён с `!`, `|`, `]` (F3.2); `cmd_attach` — «may have been uploaded» после 9
  и 5xx (F3.1); `cmd_download` — 3xx на `content` даёт 11 (F12.1); SKILL.md:113-114, :117,
  :143, строка 11 таблицы кодов; BLUEPRINT R8, R12 и строка журнала; три новых теста и
  переделанный `test_attach_partial_failure_names_both_sides` (тестов 133).
- Проходы визита 2. Два прохода я сделал сам, по 12 критериям и известным дырам: 1) дифф
  `jira.py` против `Failure`, `_http_failure`, `to_wiki` и всех вызовов `text_arg`
  (`create`, `edit`, `transition`, `comment`, `attach` — во всех проверка до первого
  запроса); 2) SKILL.md и BLUEPRINT против кода. Затем семь проб против фейковой Jira из
  тестов (без `JIRA_*` из окружения, к настоящей Jira не обращался): тайм-аут на первом из
  двух файлов `attach`, 500 на единственном файле с `--comment`, `create` с
  `attachment:x!y.png`, `attach x!y.png`, имя с `[`, 301 на `content`, 302 на REST API.
  Новая находка одна: F3.3 (low). Однопроходных находок отброшено: 1 (имя с `[` проходит
  проверку и даёт `[t|^a[b.txt]`; ломает ли это разметку Jira, без Jira не проверить, и
  находка визита 1 этот символ не называла).
- Проходы визита 1: изменение — около 450 строк текста кита и 300 строк тестов. Я сделал
  два прохода сам, по 12 критериям и известным дырам: 1) дифф `jira.py` (`Jira.call`/`send`,
  `same_server`, `ATTACHMENT`, `_check_files`, `cmd_attach`, `cmd_download`, правки
  `create`/`edit`/`comment`/`transition`, `_print_issue`) против `_http_failure`,
  `_network_failure` и требований J1–J5; 2) SKILL.md, BLUEPRINT R3/R7/R8/R10/R11/R12, README и
  kit.yaml против кода и J6–J7. Затем десять проб против фейковой Jira из тестов (без
  `JIRA_*` из окружения, к настоящей Jira не обращался): тайм-аут и 500 на загрузке, редирект
  на `content`, нечитаемый файл, `--to` без права записи, `attachment:` в блоке кода,
  `search`, имена с `|`, `!`, `]`, обрыв на втором файле `download`, имя с `"` и `\`,
  `transition` в тот же статус с неизвестным именем. Отдельного субагента не было.
  Однопроходных находок отброшено: 1 (кавычка и обратная косая черта в имени файла
  экранируются в `Content-Disposition` обратной косой чертой, а браузеры шлют `%22`; на Jira
  не проверено, вреда без такого имени нет). Оставлено как подтверждённые пробой: 4.

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений; `expects commands: uv` |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано: потоков нет (R2), скелетов в BLUEPRINT.md нет |
| b. Рубрика | 1 открытая находка (0 high, 0 medium, 1 low: F3.3, новая); F3.1, F3.2, F5.1, F12.1 визита 1 RESOLVED; 11 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста (6 файлов дифа f460312..867defa) по 12 критериям и J1–J9, пробы против фейковой Jira (визит 1); визит 2 — правки 867defa → 071e637 с окружением, семь проб; тесты: 133, OK |
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

Read-only: строки `read-only roles: …` нет, потому что ролей нет; `dependencies.lado: ">=0.30"`.

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.5.0

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
No flows in .: nothing to do (exit status 0)
```

### Тесты

```
$ uv run --no-project python -m unittest discover -s tests
Ran 133 tests in 7.942s

OK
```

## Исправить сначала

Ничего обязательного: открыта одна находка, low (F3.3, `\|` в строке 11 таблицы кодов
SKILL.md).

## Находки

### 1. Границы ролей

Не применимо: ролей нет. Границы записи — SKILL.md:29 «Create, transition, comment, assign,
label, link or attach only when your role, your step or the human asks for it», как R11.

### 2. Передачи между шагами

Не применимо: потоков нет. Выход новых действий задан и пригоден для следующего шага:
`attach` печатает строку `<id> <name> attachment:<имя в URL-кодировке>` на файл, готовую к
вставке в Markdown (тест `test_attach_one_file`), `download` — абсолютный путь на файл.

### 3. Готовность и исходы

Каждый отказ новых действий попадает в строку таблицы кодов: 2 (файл нет/папка/нечитаем —
проба: `cannot be read (Permission denied); nothing uploaded`, запросов 0; `--to` без права
записи — запросов 0; `attachment:` в `create`), 6 (403), 7 (файла нет, файлы задачи
перечислены), 11 (413, отключённые вложения, 404 на загрузке, чужой адрес, неизвестное имя в
`attachment:`), 12 (5xx). Проверка имён идёт до первой записи: проба `transition TEST-1 Open
--comment "[x](attachment:b.png)"` при задаче уже в Open — exit 11, комментарий не добавлен.

Правки визита 2: после тайм-аута или 5xx (кроме 429) `attach` называет упавший файл
отдельно — «may have been uploaded … (check with get before attaching it again)»
(`jira.py:1210-1218`); имя с `!`, `|` или `]` в `attachment:` — exit 11 до первого запроса
(`jira.py:542-555`, `text_arg`, во всех пяти командах вызывается до запросов). F3.1 и F3.2
визита 1 RESOLVED (см. «Прежние находки»). Проба: `create --description
"![](attachment:x!y.png)"` даёт теперь 11 («attach the file under another name»), а не 2,
как любая ссылка `attachment:` в `create`; запросов 0, R12 называет оба отказа, следующий
запуск без ссылки проходит — вреда нет.

- **F3.3** [low] `skills/tracker/SKILL.md:199` (новая, внесена правкой F3.2)
  > ``an `attachment:` name the task lacks or one with `!`, `|` or `]`, a file over Jira's``
  В строке 11 таблицы кодов `|` в спане кода не экранирован. В таблице GFM он всё равно
  делит ячейку: строка получает 4 ячейки при 3 в заголовке, колонка «What you do»
  показывает «` or `]`, a file over Jira's size limit …», а сам совет («read the line, fix
  the request once; … report it») при показе отбрасывается. Строки 45, 48 и 50 той же
  SKILL.md пишут `\|`, и строка журнала BLUEPRINT.md:337 тоже. Агент читает SKILL.md как
  текст, поэтому вред — в показе человеку (GitHub, просмотр в LADO), отсюда low.
  Fix: в SKILL.md:199 экранировать этот `|` как `\|`, как в строках 45, 48 и 50.
  Passes: 1/1, подтверждено подсчётом ячеек по правилу GFM («a pipe … inside other inline
  spans» делит ячейку, если не экранирован).

### 4. Независимая проверка

Не применимо: потоков нет. Файлы опробованы на тестовой Jira 8.13.19 до выпуска (R10,
BLUEPRINT.md:306-309, артефакт `lad-46-probe`); найденный там ответ 404 с текстом на файл
сверх лимита закреплён тестом `test_attach_refusals` («Jira 8.13.19's answer to a file over
jira.attachment.size»).

### 5. Противоречия

SKILL.md:116-117 «into a new temporary folder outside the repository, or into an existing
folder outside the repository given with `--to`» совпадает с R11 «kept outside the
repository». F5.1 визита 1 RESOLVED.

### 6. Дублирование

Повторов нет. Правило `attachment:` описано в одном месте («Writing in Jira: Markdown»,
SKILL.md:134-142), пункт **attach** и строки 2/11 таблицы кодов ссылаются на него, не
повторяя. Описание kit.yaml, README и SKILL.md называют файлы одинаково.

### 7. Когда звать человека

Отказы, которые агент не исправит сам, ведут к «report it»: файл сверх лимита, вложения
отключены, чужой адрес (SKILL.md, строка 11 таблицы). Чужой адрес назван с причиной: «Jira's
base URL differs from JIRA_URL; report it».

### 8. Повторные визиты

Не применимо: потоков нет. `download` повторно не перезаписывает (`-1`, `-2`, открытие с
`"xb"`); `attach` повторно добавляет копию, о чём SKILL.md предупреждает; файл, который
мог загрузиться, назван отдельно (SKILL.md:113-114).

### 9. Краткость и «почему»

Причины названы там, где агент мог бы спросить: `create` без `attachment:` — «the task has
no files yet»; «`!NAME!`» — «a link follows the name, so after a newer file of that name is
attached, older links show the newer file; give a version you mean to keep its own name»
(SKILL.md:137-139, по пробе на Jira).

### 10. Описания навыков

Описание навыка называет новые действия и поводы: «attach files to a task and download its
files (screenshots, logs, documents)», «"attach the screenshot", "look at the file in the
task"» (SKILL.md:7-11). kit.yaml и README согласованы с ним; строк в таблице действий две
(SKILL.md:49-50).

### 11. Нейтральность к провайдеру

Нового пути и имён CLI нет; скрипт по-прежнему через `${SKILL_DIR}/jira.py`. Папка по
умолчанию — `tempfile.mkdtemp(prefix="lado-jira-")`, без привязки к ОС.

### 12. Безопасность и границы

Учётные данные уходят только на `content` URL с той же схемой, хостом и портом, что у
`JIRA_URL` (`same_server`, jira.py:304), проверка всех выбранных файлов — до первого
скачивания; тест `test_download_from_another_server_sends_no_credentials` проверяет, что
другой сервер не получил ни одного запроса. Имя чистится (`_safe_name`: base name, без
управляющих символов, `.`/`..` заменены), тест с `../evil\x01.txt`. `attach` — запись по
правилу SKILL.md:29, без секретов (SKILL.md:109-111).

Редирект на `content` не следуется и теперь даёт exit 11 со своей строкой «Jira answered
file a.txt with a redirect (302), not followed: the credentials go only to JIRA_URL; report
it» (`jira.py:1284-1287`); тест `test_download_redirect_is_not_followed` проверяет, что
другой сервер получил 0 запросов. Редирект на REST API по-прежнему 4 (проба: `get` → 302 —
`exit 4 … JIRA_URL is not Jira's base address`). F12.1 визита 1 RESOLVED.

## Известные дыры

| Известная дыра | Находка, или как кит её закрывает |
|---|---|
| 1. Красная проверка возвращается без учёта среды | Не применимо: потоков нет. Сообщения `uv`/Python SKILL.md по-прежнему отличает от сообщений скрипта |
| 2. Работа вне потока, слияние без гейта | Не применимо: ролей и потоков нет; `attach` — только по просьбе роли, шага или человека (SKILL.md:29) |
| 3. Путь вне worktree запуска | Нет для скрипта: `${SKILL_DIR}/jira.py`. Скачанные файлы — во временной папке вне репозитория или в `--to` «outside the repository» (SKILL.md:117, R11) |
| 4. Вердикт без порога серьёзности | Не применимо: ревьюеров нет |
| 5. Зависимый навык пишет или спрашивает, где роли нельзя | Не применимо: зависимых навыков нет |
| 6. Команды не в ладу с `expects.commands` | Закрыта: `expects commands: uv`, `dependencies.lado: ">=0.30"`; новых команд нет (`tempfile`, `multipart` — стандартная библиотека) |
| 7. Read-only роли не в ладу с делом | Не применимо: ролей нет |

## Не прослежено

Ничего. Файлы задачи прослежены в R3 (три действия, «no attachments» убрано), R7 (ресурсы
вложений), R8 (коды файлов), R10 (проба `lad-46-probe`), R11 (`attach` — запись, без секретов,
скачанное — данные) и R12 (`attachment:`); раздел 3 называет `attach` и `download`; журнал
раздела 5 имеет строку 1.5.0 с источниками. Раздел 4 «Output of the kit-budget script on the
built kit (1.4.0; 1.5.0 adds no role, flow, skill or MCP server, so the values hold)»
совпадает с выводом выше. README говорит, что делает кит и где опробован («Where it was
tried», README.md:92). Скелетов потоков нет: потоков нет (R2).

## Прежние находки

Визит 1 (отчёт c5e6529, коммит 867defa):

| Находка | Статус | Доказательство |
|---|---|---|
| F3.1 [low] `jira.py:1199` файл, упавший на 9/12, назван «not uploaded» | RESOLVED | `jira.py:1210-1218` `unsure = failure.code == UNREACHABLE or (failure.code == SERVER_ERROR and failure.status != 429)`; пробы: тайм-аут на первом из двух — `exit 9 … uploaded none; may have been uploaded a.txt (check with get before attaching it again); not uploaded b.txt`; 500 на единственном — `exit 12 … may have been uploaded a.txt (…); not uploaded none; no comment added`; тест `test_attach_without_an_answer_names_the_file_that_may_be_there` (504, 429); SKILL.md:113-114, R8 (BLUEPRINT.md:154-156) |
| F3.2 [low] `jira.py:433-434` имена с `!`, `\|`, `]` ломают разметку | RESOLVED, с замечанием | `text_arg` (`jira.py:542-555`): `re.search(r"[!\|\]]", name)` → exit 11 до запросов; тест `test_names_wiki_markup_cannot_hold_are_refused_before_any_request` (три имени, `requests == []`); SKILL.md:143, строка 11; R12. Замечание: сам `attach x!y.png` по-прежнему загружает файл и печатает `5 x!y.png attachment:x%21y.png` (проба), ссылка из этой строки будет отклонена — агент узнает об этом при записи, совет «attach the file under another name» даёт вторую копию. Битая разметка в Jira больше не пишется, а это и было вредом находки |
| F5.1 [low] SKILL.md `--to` без «вне репозитория» | RESOLVED | SKILL.md:117 «or into an existing folder outside the repository given with `--to`»; код не тронут, как советовал Fix |
| F12.1 [low] нет теста на редирект `content`; неверный совет exit 4 | RESOLVED | `jira.py:1284-1287` 3xx → `REFUSED` «… not followed: the credentials go only to JIRA_URL; report it»; тест `test_download_redirect_is_not_followed` (другой сервер — 0 запросов, нет «JIRA_URL is not»); проба 301 — тоже 11; R8 (BLUEPRINT.md:154), строка 11 SKILL.md |

В отчёте 1.4.0 открытых находок не было. Требования LAD-46:

| Требование | Статус | Доказательство |
|---|---|---|
| J1 `get`: блок `Files: N` между Description и Comments, строка `<id> <name> (<size>, <author>, <date>)`, без файлов — без блока; `search` без изменений | RESOLVED | `_print_issue`; тесты `test_get_shows_files_between_description_and_comments`, `test_get_without_files_has_no_block`; проба: `search` просит `summary,status,issuetype,assignee` |
| J2 `attach`: multipart `file`, `X-Atlassian-Token: no-check`, все файлы до первой загрузки, строка на файл, `--comment` последним, имена комментария до загрузки, частичный отказ называет обе стороны | RESOLVED, с замечанием | `cmd_attach`, `Jira.call(upload=…)`; тесты `test_attach_*` (10); файл, упавший на 9/12, назван «may have been uploaded» (F3.1 RESOLVED) |
| J3 `download`: id, затем имя (новейший); данные только на схему, хост, порт `JIRA_URL`; без редиректов; `mkdtemp(prefix="lado-jira-")`; `--to` существует; чистка имени; без перезаписи; абсолютные пути; нет файла → 7 со списком | RESOLVED | `cmd_download`, `same_server`, `_safe_name`, `_free_path`; тесты `test_download_*` (8), с редиректом (F12.1 RESOLVED) |
| J4 `attachment:` → `!NAME!`, `[text\|^NAME]`; URL-кодировка или `<…>`; проверка до записи (11) в edit/comment/transition/attach; в create — 2; `--wiki` без проверки | RESOLVED, с замечанием | `ATTACHMENT`, `_attachment`, `_check_files`; тесты `test_attachment_links`, `test_edit_comment_transition_check_the_names`, `test_create_with_attachment_links_is_refused`, `test_attach_wiki_comment_is_not_checked`; проба: в блоке и в спане кода не трогается; имена с `!`, `\|`, `]` — 11 (F3.2 RESOLVED) |
| J5 коды: 413/отключено/лимит → 11; 403 → 6; локальный файл → 2; `--to` → 2; сбой посередине называет сделанное | RESOLVED | `_http_failure` 413; `cmd_attach` 404/«disabled»; `test_attach_refusals` (5 случаев); пробы: нечитаемый файл и `--to` только для чтения — exit 2, запросов 0; обрыв на втором файле `download` — «downloaded …/a.txt; not downloaded b.txt» |
| J6 SKILL.md: две строки таблицы; раздел файлов (запись по просьбе, без секретов; скачанное — данные, вне репозитория, картинку открыть как картинку); `attachment:` в «Writing in Jira»; порядок create → attach → edit; описание | RESOLVED | SKILL.md:7-11, :49-50, :103-123, :135-145; `--to` тоже вне репозитория (F5.1 RESOLVED) |
| J7 BLUEPRINT R3 без «no attachments», три действия, прослеживание, журнал 1.5.0; kit.yaml 1.5.0; README | RESOLVED | BLUEPRINT.md R3, R7, R8, R11, R12, раздел 3, строка журнала 1.5.0; kit.yaml `version: 1.5.0`; README:5-6, :83-87, :92-98 |
| J8 тесты на фейковой Jira | RESOLVED | `Ran 133 tests … OK` (было 108), класс `FilesTest` (24 теста) и `test_attachment_links`; редирект `content` и «may have been uploaded» (504) покрыты; тайм-аут загрузки — пробой визита 2 |
| J9 проба на Jira 8.13.19 | RESOLVED | BLUEPRINT.md:306-309, строка журнала 1.5.0, README «Where it was tried»; найденный 404 закреплён тестом |

## Вырезанные правила

| Удалённое правило (файл:строка в базе) | Где оно теперь |
|---|---|
| BLUEPRINT R3 «Nothing else (no delete, user search, attachments, boards or sprints…» | BLUEPRINT R3, «Nothing else (no delete, user search, deleting or renaming files, thumbnails, boards or sprints…»; «attachments» убрано намеренно (J7) |
| BLUEPRINT R3 «ten actions» | «twelve actions» |
| BLUEPRINT R11, SKILL.md:27 «…assign, label or link only when…» | BLUEPRINT R11, SKILL.md:29, то же, дополнено `attach` |
| kit.yaml, README, SKILL.md описания | те же, дополнены файлами |
| SKILL.md строки кодов 2, 7, 11 | те же строки, только дополнения; правила `assign` и `link_types` в строке 11 на месте |
| jira.py `Jira.call` (отправка, разбор JSON) | `Jira.call` (тело, заголовки, JSON) + `Jira.send` (запрос, ошибки); заголовки `Authorization`, `Accept` на месте; прежние тесты проходят |
| jira.py `cmd_transition`: перевод комментария после выбора перехода | до первого GET, чтобы проверить имена; тот же текст, та же метка |
| jira.py `cmd_create`: перевод описания после `createmeta` | до запросов; поле `description` то же |
| (визит 2) jira.py `cmd_attach` «uploaded …; not uploaded …» | `jira.py:1213-1218`, та же строка; при 9 и 5xx упавший файл вынесен в «may have been uploaded»; при 2/6/7/11 и 429 без изменений |
| (визит 2) jira.py `text_arg`: `to_wiki(text, names)` | `jira.py:546-554`: имена собираются так же, `names` дополняется после проверки; `--wiki` не проверяется, как прежде |
| (визит 2) jira.py `cmd_download`: 404 → 7 | `jira.py:1282-1283`, на месте; добавлена ветка 3xx → 11 |
| (визит 2) тест `test_attach_partial_failure_names_both_sides` (500) | тот же тест на 413; 5xx — в `test_attach_without_an_answer_names_the_file_that_may_be_there` |
| (визит 2) SKILL.md:114-116, строка 11 таблицы кодов; BLUEPRINT R8, R12 | те же, только дополнения |

Ни одно правило не потеряно.

## Пропущено ранее

Нет.

## Оставлено планом

Ничего: план (LAD-46) не оставлял пунктов.

## Вопросы к человеку

1. F3.3 [low] — один символ (`\|`) в SKILL.md:199. Исправить до тега или следующим
   выпуском? Рекомендую до тега: правка в одну строку, кода не касается.
