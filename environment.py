"""管理一个卖家和两个买家的连续竞价与确定性规则。"""

from agent import BargainingAgent
from protocol import BargainAction, BargainObservation


class BargainingEnvironment:
    """环境管理竞价流程和公共状态，不替 Agent 做主观决策。"""

    def __init__(
        self,
        seller: BargainingAgent,
        buyers: list[BargainingAgent],
        product_name: str = "二手自行车",
        max_rounds: int = 5,
    ) -> None:
        if len(buyers) != 2:
            raise ValueError("Step1 需要且只需要两个买家")

        self.seller = seller
        self.buyers = buyers
        self.product_name = product_name
        self.max_rounds = max_rounds
        self.current_price: float | None = None
        self.offered_by: str | None = None
        self.history: list[str] = []

    def run(self) -> None:
        """依次执行挂牌、买家竞价和卖家决策。"""

        print(
            f"开始三 Agent 竞价：商品为{self.product_name}，"
            f"最多 {self.max_rounds} 轮。"
        )

        if not self._run_listing():
            return

        for round_number in range(1, self.max_rounds + 1):
            print(f"\n──────────── 竞价第 {round_number} 轮 ────────────")

            for buyer in self.buyers:
                observation = self._create_observation(
                    phase="竞价",
                    round_number=round_number,
                    allowed_actions=["出价", "放弃"],
                )
                action = self._request_valid_action(buyer, observation)
                self._show_action(buyer, action)

                if action.action_type == "出价":
                    self.current_price = action.price
                    self.offered_by = buyer.name

                self.history.append(
                    self._history_text(round_number, buyer, action)
                )

            if self._run_seller_decision(round_number):
                return

        print("\n竞价结束：达到最大轮数，卖家未接受报价，本次未成交。")

    def _run_listing(self) -> bool:
        """让卖家自主确定挂牌价格。"""

        print("\n──────────── 卖家挂牌 ────────────")
        observation = self._create_observation(
            phase="挂牌",
            round_number=0,
            allowed_actions=["挂牌", "退出"],
        )
        action = self._request_valid_action(self.seller, observation)
        self._show_action(self.seller, action)

        if action.action_type == "退出":
            print("\n竞价结束：卖家取消挂牌，本次未成交。")
            return False

        self.current_price = action.price
        self.offered_by = None
        self.history.append(
            f"卖家 {self.seller.name} 将{self.product_name}以 "
            f"{self._format_price(action.price)} 元挂牌："
            f"{action.message}"
        )
        return True

    def _run_seller_decision(self, round_number: int) -> bool:
        """让卖家决定接受最高报价、继续竞价或退出。"""

        has_buyer_bid = self.offered_by is not None
        if round_number == self.max_rounds:
            allowed_actions = ["接受", "退出"] if has_buyer_bid else ["退出"]
        else:
            allowed_actions = (
                ["接受", "继续", "退出"]
                if has_buyer_bid
                else ["降价", "继续", "退出"]
            )

        observation = self._create_observation(
            phase="卖家决策",
            round_number=round_number,
            allowed_actions=allowed_actions,
        )
        action = self._request_valid_action(self.seller, observation)
        self._show_action(self.seller, action)
        self.history.append(
            self._history_text(round_number, self.seller, action)
        )

        if action.action_type == "接受":
            print(
                f"\n竞价结束：{self.offered_by} 以 "
                f"{self._format_price(self.current_price)} 元"
                f"竞得{self.product_name}。"
            )
            return True

        if action.action_type == "退出":
            print("\n竞价结束：卖家拒绝当前报价，本次未成交。")
            return True

        if action.action_type == "降价":
            self.current_price = action.price
            print(
                f"卖家将挂牌价调整为 {self._format_price(action.price)} 元，"
                "竞价继续。"
            )
            return False

        print("卖家暂不接受当前最高报价，竞价继续。")
        return False

    def _create_observation(
        self,
        phase: str,
        round_number: int,
        allowed_actions: list[str],
    ) -> BargainObservation:
        """将环境当前公共状态封装成 Observation。"""

        return BargainObservation(
            product_name=self.product_name,
            phase=phase,
            round_number=round_number,
            max_rounds=self.max_rounds,
            current_price=self.current_price,
            offered_by=self.offered_by,
            allowed_actions=allowed_actions,
            history=self.history.copy(),
        )

    def _request_valid_action(
        self,
        actor: BargainingAgent,
        observation: BargainObservation,
    ) -> BargainAction:
        """动作不符合环境规则时，反馈原因并让同一 Agent 重试一次。"""

        for attempt in range(2):
            action = actor.decide(observation)
            try:
                self._require_valid(actor, action, observation)
                return action
            except ValueError as error:
                if attempt == 1:
                    raise
                print(f"【环境校验】{error}，正在请求 {actor.name} 重新决策。")
                observation = observation.model_copy(
                    update={
                        "history": [
                            *observation.history,
                            f"环境校验反馈：上一次动作无效，原因是“{error}”。"
                            "请严格按照当前最高价和允许动作重新决策。",
                        ]
                    }
                )

        raise RuntimeError("未能取得有效动作")

    def _require_valid(
        self,
        actor: BargainingAgent,
        action: BargainAction,
        observation: BargainObservation,
    ) -> None:
        """校验动作是否合法，但不评价价格是否划算。"""

        if action.action_type not in observation.allowed_actions:
            raise ValueError(
                f"{actor.name} 在{observation.phase}阶段不能执行{action.action_type}"
            )
        if action.action_type == "出价" and (
            self.current_price is None or action.price <= self.current_price
        ):
            raise ValueError(
                f"{actor.name} 的出价必须严格高于当前最高价 "
                f"{self._format_price(self.current_price)}"
            )
        if action.action_type == "降价" and (
            self.offered_by is not None
            or self.current_price is None
            or action.price >= self.current_price
        ):
            raise ValueError(
                f"{actor.name} 只能在没有买家出价时降低挂牌价，"
                f"新价格必须低于 {self._format_price(self.current_price)}"
            )

    @staticmethod
    def _format_price(price: float) -> str:
        """以普通数字显示价格，避免大额价格变成科学计数法。"""

        return f"{price:,.2f}".rstrip("0").rstrip(".")

    @staticmethod
    def _history_text(
        round_number: int,
        actor: BargainingAgent,
        action: BargainAction,
    ) -> str:
        """把结构化动作转换成所有 Agent 可见的公开记录。"""

        price_text = (
            f" {BargainingEnvironment._format_price(action.price)} 元"
            if action.price is not None
            else ""
        )
        return (
            f"第 {round_number} 轮，{actor.name}{action.action_type}{price_text}："
            f"{action.message}"
        )

    @staticmethod
    def _show_action(actor: BargainingAgent, action: BargainAction) -> None:
        """打印本次结构化动作。"""

        print(f"【{actor.name}｜{actor.role}｜{action.action_type}】")
        if action.price is not None:
            print(f"价格：{BargainingEnvironment._format_price(action.price)}")
        print(f"发言：{action.message}")
