import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import config
import commands.enter as enter_module
from commands.enter import enter_command


def make_ctx(username="testuser"):
    ctx = MagicMock()
    ctx.author.name = username
    ctx.reply = AsyncMock()
    return ctx


@pytest.fixture(autouse=True)
def reset_cooldowns():
    enter_module._cooldowns.clear()
    yield
    enter_module._cooldowns.clear()


async def test_success_replies_in_chat():
    ctx = make_ctx("testuser")
    with patch("commands.enter.get_latest_battleroom", new_callable=AsyncMock, return_value={"id": 1}), \
         patch("commands.enter.battleroom_enter", new_callable=AsyncMock, return_value={"status": 200, "body": {}}):
        await enter_command(ctx)
    ctx.reply.assert_awaited_once()
    assert "testuser" in ctx.reply.call_args[0][0]


async def test_no_room_replies_in_chat():
    ctx = make_ctx("testuser")
    with patch("commands.enter.get_latest_battleroom", new_callable=AsyncMock, return_value=None):
        await enter_command(ctx)
    ctx.reply.assert_awaited_once()
    assert "Aucune battleroom" in ctx.reply.call_args[0][0]


async def test_already_registered_no_chat_reply():
    ctx = make_ctx("testuser")
    with patch("commands.enter.get_latest_battleroom", new_callable=AsyncMock, return_value={"id": 1}), \
         patch("commands.enter.battleroom_enter", new_callable=AsyncMock, return_value={"status": 409, "body": {}}):
        await enter_command(ctx)
    ctx.reply.assert_not_awaited()


async def test_network_error_no_chat_reply():
    ctx = make_ctx("testuser")
    with patch("commands.enter.get_latest_battleroom", new_callable=AsyncMock, return_value={"id": 1}), \
         patch("commands.enter.battleroom_enter", new_callable=AsyncMock, return_value=None):
        await enter_command(ctx)
    ctx.reply.assert_not_awaited()


async def test_unexpected_status_no_chat_reply():
    ctx = make_ctx("testuser")
    with patch("commands.enter.get_latest_battleroom", new_callable=AsyncMock, return_value={"id": 1}), \
         patch("commands.enter.battleroom_enter", new_callable=AsyncMock, return_value={"status": 500, "body": {}}):
        await enter_command(ctx)
    ctx.reply.assert_not_awaited()


async def test_cooldown_blocks_second_call():
    ctx = make_ctx("testuser")
    with patch("commands.enter.get_latest_battleroom", new_callable=AsyncMock, return_value={"id": 1}), \
         patch("commands.enter.battleroom_enter", new_callable=AsyncMock, return_value={"status": 200, "body": {}}), \
         patch.object(config, "COOLDOWN_SECONDS", 30):
        await enter_command(ctx)
        await enter_command(ctx)
    assert ctx.reply.await_count == 1


async def test_cooldown_applied_even_without_active_room():
    ctx = make_ctx("testuser")
    with patch("commands.enter.get_latest_battleroom", new_callable=AsyncMock, return_value=None), \
         patch.object(config, "COOLDOWN_SECONDS", 30):
        await enter_command(ctx)
        await enter_command(ctx)
    assert ctx.reply.await_count == 1


async def test_different_users_have_independent_cooldowns():
    ctx_a = make_ctx("alice")
    ctx_b = make_ctx("bob")
    with patch("commands.enter.get_latest_battleroom", new_callable=AsyncMock, return_value={"id": 1}), \
         patch("commands.enter.battleroom_enter", new_callable=AsyncMock, return_value={"status": 200, "body": {}}), \
         patch.object(config, "COOLDOWN_SECONDS", 30):
        await enter_command(ctx_a)
        await enter_command(ctx_b)
    ctx_a.reply.assert_awaited_once()
    ctx_b.reply.assert_awaited_once()
