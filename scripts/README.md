# 自动更新说明（scripts/auto_update.sh）

## 一、它是怎么工作的

服务器上有一个 systemd timer，**每 2 分钟**执行一次 `scripts/auto_update.sh`：

| 步骤 | 做什么 | 失败会怎样 |
| --- | --- | --- |
| 1 | `git fetch` 检查 `origin/master` 有没有新提交 | 网络问题就静默跳过，不打扰你 |
| 2 | 没有新提交 → 直接退出（绝大多数时候走这里） | — |
| 3 | 有新提交 → `git reset --hard` 切到新代码 | 回滚 + 通知 |
| 4 | `requirements.txt` 变了就 `uv pip install` 同步依赖 | 回滚 + 通知 |
| 5 | **自检**：`compileall` 全量语法检查 + 真正 `load_from_toml` 加载一遍所有插件 | 回滚 + 通知 |
| 6 | 重启 `xilusheng-bot` 服务，确认 25 秒内 9090 端口已监听并且进程还活着 | 回滚 + 通知 |
| 7 | 全部通过 → 记录日志，结束 | — |

**回滚**就是 `git reset --hard` 回旧提交（依赖变了就再装回去），
然后重新自检 + 重启，最后写一个失败标记。

## 二、失败是怎么通知到你的

脚本**不直接调 QQ 接口**（那需要开 NapCat 的 HTTP API，重启容器会掉登录态）。
它只做一件事：在项目根目录写 `.update_status.json`。

项目里的插件 `src/plugins/autoupdate/__init__.py` 在 bot 启动后会起一个后台任务，
每 30 秒看一次这个文件；发现 `status = "failed"` 就用**已经连上 QQ 的机器人**
私聊 `SUPERUSERS`（也就是你的 428733650），发送成功后删除该文件。

    .update_status.json
    {
      "time": "2026-10-07 21:30:00",
      "status": "failed",
      "message": "自动更新失败，已回滚到 e1c328f",
      "detail": "代码自检未通过：...Traceback..."
    }

因为回滚后旧代码会正常启动，所以这条通知几乎总是能发出来。
万一连回滚都失败（bot 起不来），标记文件会留在那里，等下次服务恢复时自动补发。

## 三、服务器上的相关文件

| 路径 | 说明 |
| --- | --- |
| `/opt/Xi_Lusheng_Bot/scripts/auto_update.sh` | 更新脚本本体（跟着仓库一起更新） |
| `/etc/systemd/system/xilusheng-update.service` | 一次性执行的 systemd 服务 |
| `/etc/systemd/system/xilusheng-update.timer` | 每 2 分钟触发一次 |
| `/var/log/xilusheng-autoupdate.log` | 更新日志 |
| `/opt/Xi_Lusheng_Bot/.update_status.json` | 失败标记（仅失败时存在） |

常用命令：

    systemctl list-timers xilusheng-update.timer      # 看下次什么时候跑
    systemctl start xilusheng-update.service          # 手动立刻跑一次
    journalctl -u xilusheng-update -n 100 --no-pager  # 看最近一次的输出
    tail -f /var/log/xilusheng-autoupdate.log         # 看历史日志

可覆盖的环境变量（在 service 文件里加 `Environment=XXX=yyy`）：
`UPDATE_BRANCH`（默认 master）、`BOT_SERVICE`、`UV_BIN`、`UPDATE_LOG`、`HEALTH_PORT`。

## 四、分支约定

- `master`：**只有能上线的代码才进 master**。服务器定时器盯的就是它。
- `test`：**平时本地开发都在 test 分支上做**，随便改、随便提交。

上线流程：

    git checkout test
    # ...改代码、本地跑通...
    git commit -am "feat: xxx"
    git push server test        # 备份到服务器裸仓库

    git checkout master
    git merge test              # 合并
    git push server master      # 服务器 2 分钟内自动拉取 + 自检 + 重启

> 想临时换更新分支，把 service 里的 `UPDATE_BRANCH` 改成 test 即可，
> 但不建议长期这么干 —— test 分支随时可能是坏的。

## 五、为什么更新脚本自己能安全地更新自己

`auto_update.sh` 本身也在仓库里，会被 `git reset --hard` 覆盖。
但 bash 是拿着已打开的文件描述符按块读脚本的，git 换文件用的是
“新建再改名”，旧 inode 会保留到脚本执行结束，所以**不会读到半截的脚本**。
