# Step1：最小三 Agent 竞价

Step1 在 Step0 的三个模块基础上做最小升级：一个卖家、两个买家围绕固定商品进行竞价。

- `agent.py`：使用同一个通用类创建一个卖家和两个买家 Agent。
- `protocol.py`：定义 `Observation` 和 `Action`。
- `environment.py`：管理挂牌、买家依次出价、卖家决策、降价和成交条件。
- `main.py`：读取命令行参数，创建 Agent、组装 Environment 并启动程序。

通信方向：

```text
Agent（左侧） ⇄ Protocol（中间） ⇄ Environment（右侧）
```

## 安装

```bash
cd /Users/boyuzou/step1
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

将 `.env.example` 复制为 `.env`，并填写 DeepSeek 配置。

## 运行

```bash
python main.py --rounds 5 --product "二手自行车"
```

每轮流程：

```text
Bob 出价或放弃 → Charlie 出价或放弃 → Alice 接受、降价、继续或退出
```
