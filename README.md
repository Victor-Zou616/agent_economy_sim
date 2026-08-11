# Step0：最小双 Agent 讨价还价

这个项目只包含三个核心模块：

- `agent.py`：使用 LangChain 1.x 创建卖家和买家 Agent。
- `protocol.py`：定义 `Observation` 和 `Action`。
- `environment.py`：管理轮次、公开状态和成交条件。

通信方向：

```text
Agent（左侧） ⇄ Protocol（中间） ⇄ Environment（右侧）
```

## 安装

```bash
cd /Users/boyuzou/step0
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

将 `.env.example` 复制为 `.env`，并填写 DeepSeek 配置。

## 运行

```bash
python environment.py --rounds 10
```
