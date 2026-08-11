"""用一个通用类创建卖家 Agent 和买家 Agent。"""

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from protocol import BargainAction, BargainObservation


class BargainingAgent:
    """接收环境观察，调用大模型，并返回一个结构化动作。"""

    def __init__(self, name: str, role: str, goal: str) -> None:
        self.name = name
        self.role = role

        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("缺少 DEEPSEEK_API_KEY，请在 .env 文件中配置")

        model = init_chat_model(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro"),
            model_provider="openai",
            api_key=api_key,
            base_url="https://api.deepseek.com",
            temperature=0,
            extra_body={"thinking": {"type": "disabled"}},
        )

        system_prompt = f"""
        你是{name}，身份是{role}，正在与另一个人进行一件商品的价格谈判。
        你的目标是：{goal}
        
        你可以执行三种动作：报价、接受、退出。
        没有当前报价时不能接受；不能接受自己提出的报价。
        报价时必须填写大于零的价格；接受或退出时不要填写价格。
        你可以根据当前报价、剩余轮数和谈判历史自主决定，不要求一定成交。
        所有对外发言必须使用简洁、自然的中文。
        """.strip()

        # data = [("system", """
        # 你是{name}，身份是{role}，正在与另一个人进行一件商品的价格谈判。
        # 你的目标是：{goal}
        # 你可以执行三种动作：报价、接受、退出。
        # 没有当前报价时不能接受；不能接受自己提出的报价。
        # 报价时必须填写大于零的价格；接受或退出时不要填写价格。
        # 你可以根据当前报价、剩余轮数和谈判历史自主决定，不要求一定成交。
        # 所有对外发言必须使用简洁、自然的中文。
        # """.strip())]
        #
        # system_prompt= ChatPromptTemplate.from_messages(data)





        self._agent = create_agent(
            model=model,
            tools=[],
            system_prompt=system_prompt,
            response_format=ToolStrategy(BargainAction),
        )

    def decide(self, observation: BargainObservation) -> BargainAction:
        """把环境观察交给 LangChain Agent，并取回结构化动作。"""

        prompt = f"""
当前轮数：{observation.round_number}/{observation.max_rounds}
当前报价：{observation.current_price if observation.current_price is not None else "暂无"}
当前报价者：{observation.offered_by or "暂无"}
公开谈判历史：
{chr(10).join(observation.history) if observation.history else "暂无"}

请做出本轮决策。
""".strip()

        result = self._agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]}
        )
        return result["structured_response"]
