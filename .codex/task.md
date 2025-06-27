# 🔧 Задание: устранить ошибки в e2e-тесте и добавить FSM-проверку

## Цель

Привести `tests/e2e/test_fsm_conversation.py` в рабочее состояние:
- устранить предупреждение Ruff (F841)
- использовать объект `Update`
- реализовать тестирование FSM-хендлера

---

## Конкретно:

1. **Исправить F841**:
   - либо удалить переменную `update`, если она не используется
   - либо использовать её, передав в FSM-обработчик

2. **Добавить вызов FSM-хендлера**:
   - Найти `start_handler()` (или другой `/start`-обработчик) в проекте
   - Эмулировать `Message` и `FSMContext`
   - Вызвать обработчик вручную: `await start_handler(message, state=context)`

3. **Добавить проверки**:
   - Проверить, что состояние FSM действительно изменилось (`FSMContext.get_state()`)
   - Проверить ответ Telegram-бота, если реализована отправка через `bot.send_message`

4. **Обеспечить совместимость с `pytest`**:
   - Оставить `@pytest.mark.asyncio` и структуру `async def`

---

## Результат

Рабочий тест, не вызывающий ошибок Ruff, запускаемый в CI:

```python
async def test_fsm_start_handler():
    ...
    await start_handler(message, state=fsm_context)
    assert await fsm_context.get_state() == "SomeState"
