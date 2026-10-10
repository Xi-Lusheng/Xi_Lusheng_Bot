#!/usr/bin/env bash
# ============================================================================
# Xi_Lusheng Bot 服务器端自动更新脚本
#
# 流程：
#   1. git fetch 检查 origin/master 是否有新提交（没有就静默退出）
#   2. git reset --hard 切换到新提交
#   3. requirements.txt 有变化则同步依赖（uv）
#   4. 自检：compileall 全量语法检查 + nonebot 插件加载测试
#   5. systemctl restart 机器人服务，并确认端口 9090 已监听
#
#   第 2~5 步任何一步失败 -> git reset --hard 回滚到旧提交 -> 重新自检/重启
#                          -> 写 .update_status.json 失败标记
#                          -> bot 启动后读取该文件并私聊管理员
#
# 正常无更新时什么都不做，直接 exit 0。
# 可通过环境变量覆盖：UPDATE_BRANCH / BOT_SERVICE / UV_BIN / UPDATE_LOG / HEALTH_PORT
# ============================================================================

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

[ -n "$UPDATE_BRANCH" ] || UPDATE_BRANCH=master
[ -n "$BOT_SERVICE" ] || BOT_SERVICE=xilusheng-bot
[ -n "$UV_BIN" ] || UV_BIN=/root/ncd/tools/uv/uv
[ -n "$UPDATE_LOG" ] || UPDATE_LOG=/var/log/xilusheng-autoupdate.log
[ -n "$HEALTH_PORT" ] || HEALTH_PORT=9090

VENV_PY="$REPO_DIR/.venv/bin/python"
REQ_FILE="$REPO_DIR/requirements.txt"
STATUS_FILE="$REPO_DIR/.update_status.json"
LOCK_FILE="/tmp/xilusheng-autoupdate.lock"
WAIT_SECONDS=25

# 仓库里版本化的 systemd 单元；服务器上安装的就是它
UNIT_SRC="$REPO_DIR/scripts/systemd/xilusheng-bot.service"
UNIT_DST="/etc/systemd/system/xilusheng-bot.service"
UNIT_BACKUP="/tmp/xilusheng-bot.service.bak.$$"

log() {
    local line="[$(date '+%F %T')] $*"
    echo "$line" >> "$UPDATE_LOG"
    echo "$line"
}

# 写失败标记。bot 启动后会读取它并私聊管理员，发送成功后自动删除。
mark_failed() {
    jq -n --arg t "$(date '+%F %T')" --arg m "$1" --arg d "$2" \
       '{time:$t, status:"failed", message:$m, detail:$d}' > "$STATUS_FILE"
    log "已写入失败标记：$STATUS_FILE"
}

install_deps() {
    if [ -x "$UV_BIN" ]; then
        "$UV_BIN" pip install -q -r "$REQ_FILE" --python "$VENV_PY"
    else
        "$VENV_PY" -m pip install -q -r "$REQ_FILE"
    fi
}

deps_changed() {
    ! git -C "$REPO_DIR" diff --quiet "$1" "$2" -- requirements.txt
}

# 把仓库里的 systemd 单元同步到系统（MemoryMax / LOG_LEVEL 都在里面）。
# 首次改动前先备份原单元，回滚时还原。
sync_systemd_unit() {
    [ -f "$UNIT_SRC" ] || return 0
    if [ -f "$UNIT_DST" ] && [ ! -f "$UNIT_BACKUP" ]; then
        cp -a "$UNIT_DST" "$UNIT_BACKUP"
    fi
    if cmp -s "$UNIT_SRC" "$UNIT_DST"; then
        return 0
    fi
    install -m 644 "$UNIT_SRC" "$UNIT_DST" || return 1
    systemctl daemon-reload || return 1
    log "已同步 systemd 单元：$UNIT_DST"
    return 0
}

restore_systemd_unit() {
    [ -f "$UNIT_BACKUP" ] || return 0
    install -m 644 "$UNIT_BACKUP" "$UNIT_DST" || return 1
    systemctl daemon-reload || return 1
    log "已还原 systemd 单元：$UNIT_DST"
    return 0
}

# 只做静态自检，不启动服务：语法编译 + 真实加载一遍全部插件，
# 并要求 src/plugins 下每个插件目录都加载成功（缺依赖 / 语法之外的错误都会被抓出来）。
self_check() {
    cd "$REPO_DIR" || return 1
    "$VENV_PY" -m compileall -q src utils bot.py || return 1

    local out
    out="$(ENVIRONMENT=prod timeout 90 "$VENV_PY" -c '
import sys
from pathlib import Path
import nonebot

nonebot.init()
nonebot.load_from_toml("pyproject.toml")

loaded = {p.name for p in nonebot.get_loaded_plugins()}
plugins_dir = Path("src/plugins")
expected = {
    d.name for d in plugins_dir.iterdir()
    if d.is_dir() and not d.name.startswith("_") and (d / "__init__.py").exists()
}
missing = sorted(expected - loaded)
if missing:
    print("SELFCHECK_FAIL 以下插件未能加载: " + ", ".join(missing))
    sys.exit(1)
print("SELFCHECK_OK loaded=" + str(len(loaded)) + " / expected=" + str(len(expected)))
' 2>&1)" || { echo "$out" | tail -n 20; return 1; }

    echo "$out" | grep -q '^SELFCHECK_OK' || { echo "$out" | tail -n 20; return 1; }
    echo "$out" | tail -n 1
    return 0
}

restart_and_check() {
    systemctl restart "$BOT_SERVICE" || return 1
    local i=0
    while [ "$i" -lt "$WAIT_SECONDS" ]; do
        sleep 1
        i=$((i + 1))
        systemctl is-active --quiet "$BOT_SERVICE" || continue
        if ss -ltn | grep -q "127.0.0.1:$HEALTH_PORT"; then
            sleep 3
            systemctl is-active --quiet "$BOT_SERVICE" || return 1
            return 0
        fi
    done
    log "健康检查超时：服务未在 $WAIT_SECONDS 秒内监听 $HEALTH_PORT"
    return 1
}

# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

exec 9>"$LOCK_FILE"
flock -n 9 || { log "已有更新任务在运行，本次跳过"; exit 0; }

cd "$REPO_DIR" || exit 1

OLD_SHA="$(git rev-parse HEAD 2>/dev/null)" || { log "无法读取 HEAD，跳过"; exit 0; }

if ! git fetch --quiet origin "$UPDATE_BRANCH"; then
    log "git fetch 失败（网络或仓库问题），本次跳过"
    exit 0
fi

NEW_SHA="$(git rev-parse "origin/$UPDATE_BRANCH" 2>/dev/null)" || exit 0

if [ "$OLD_SHA" = "$NEW_SHA" ]; then
    exit 0
fi

log "检测到新提交：$OLD_SHA -> $NEW_SHA"

DEPS_CHANGED=""

rollback() {
    local reason="$1"
    log "开始回滚：$reason"
    git reset --hard --quiet "$OLD_SHA" || log "警告：git reset 回滚失败"
    if [ -n "$DEPS_CHANGED" ]; then
        install_deps || log "警告：回滚后依赖恢复失败"
    fi
    restore_systemd_unit || log "警告：回滚后 systemd 单元还原失败"
    if restart_and_check; then
        log "回滚完成，服务已恢复到 $OLD_SHA"
    else
        log "严重：回滚后服务仍不健康，请人工介入"
    fi
    mark_failed "自动更新失败，已回滚到 $OLD_SHA" "$reason"
}

# 1. 切换代码
git checkout --quiet "$UPDATE_BRANCH" 2>/dev/null
if ! git reset --hard --quiet "$NEW_SHA"; then
    rollback "git reset 到 $NEW_SHA 失败"
    exit 1
fi

# 2. 依赖
if deps_changed "$OLD_SHA" "$NEW_SHA"; then
    DEPS_CHANGED="yes"
    log "requirements.txt 有变化，同步依赖中"
    if ! install_deps; then
        rollback "依赖安装失败"
        exit 1
    fi
fi

# 2.5 同步 systemd 单元（MemoryMax=700M 与 LOG_LEVEL=INFO 都在里面）
if ! sync_systemd_unit; then
    rollback "systemd 单元同步失败"
    exit 1
fi

# 3. 自检
CHECK_OUT=""
if ! CHECK_OUT="$(self_check 2>&1)"; then
    rollback "代码自检未通过：$(echo "$CHECK_OUT" | tail -n 5)"
    exit 1
fi
log "自检通过"

# 4. 重启 + 健康检查
if ! restart_and_check; then
    rollback "服务重启后健康检查未通过"
    exit 1
fi

log "更新成功，当前运行 $NEW_SHA"
exit 0
