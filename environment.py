"""管理两个 Agent 的轮流谈判以及确定性的结束规则。"""

import argparse

from agent import BargainingAgent
from protocol import BargainAction, BargainObservation


class BargainingEnvironment:
    """环境只管理流程和公共状态，不替 Agent 做经济决策。"""

    def __init__(
        self,
        seller: BargainingAgent,
        buyer: BargainingAgent,
        max_rounds: int = 10,
    ) -> None:
        self.seller = seller
        self.buyer = buyer
        self.max_rounds = max_rounds
        self.current_price: float | None = None
        self.offered_by: str | None = None
        self.history: list[str] = []

    def run(self) -> None:
        """让卖家先行动，之后买卖双方交替行动。"""

        agents = [self.seller, self.buyer]
        print(f"开始讨价还价，最多 {self.max_rounds} 轮。")

        for round_number in range(1, self.max_rounds + 1):
            actor = agents[(round_number - 1) % 2]
            print(f"\n──────────── 第 {round_number} 轮 ────────────")

            observation = BargainObservation(
                round_number=round_number,
                max_rounds=self.max_rounds,
                current_price=self.current_price,
                offered_by=self.offered_by,
                history=self.history.copy(),
            )
            action = actor.decide(observation)

            if not self._is_valid(actor, action):
                raise ValueError(f"{actor.name} 返回了不符合当前状态的动作：{action}")

            self._show_action(actor, action)

            if action.action_type == "报价":
                self.current_price = action.price
                self.offered_by = actor.name
                self.history.append(
                    f"第 {round_number} 轮，{actor.name} 报价 {action.price:g}：{action.message}"
                )
                continue

            if action.action_type == "接受":
                print(f"\n谈判结束：双方以 {self.current_price:g} 的价格成交。")
                return

            print(f"\n谈判结束：{actor.name} 选择退出，本次未成交。")
            return

        print("\n谈判结束：达到最大轮数，本次未成交。")

    def _is_valid(
        self,
        actor: BargainingAgent,
        action: BargainAction,
    ) -> bool:
        """校验动作是否合法，但不评价报价是否划算。"""

        if action.action_type == "接受":
            return self.current_price is not None and self.offered_by != actor.name
        return True

    @staticmethod
    def _show_action(actor: BargainingAgent, action: BargainAction) -> None:
        """以适合学习和观察的格式打印本轮动作。"""

        print(f"【{actor.name}｜{actor.role}｜{action.action_type}】")
        if action.price is not None:
            print(f"价格：{action.price:g}")
        print(f"发言：{action.message}")


def main() -> None:
    """创建两个 Agent，并启动环境。"""

    parser = argparse.ArgumentParser(description="最小双 Agent 讨价还价示例")
    parser.add_argument("--rounds", type=int, default=10, help="最大谈判轮数")
    args = parser.parse_args()

    seller = BargainingAgent(
        name="Alice",
        role="卖家",
        goal="尽量以较高的价格卖出商品，同时自行判断是否接受买家的报价。",
    )
    buyer = BargainingAgent(
        name="Bob",
        role="买家",
        goal="尽量以较低的价格买到商品，同时自行判断是否接受卖家的报价。",
    )
    BargainingEnvironment(seller, buyer, max_rounds=args.rounds).run()


if __name__ == "__main__":
    main()
