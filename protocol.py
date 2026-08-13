"""定义 Agent 与 Environment 之间唯一允许传递的数据结构。"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class BargainObservation(BaseModel):
    """Environment 发给 Agent 的公开观察。"""

    product_name: str = Field(description="本次竞价的商品名称")
    phase: Literal["挂牌", "竞价", "卖家决策"] = Field(description="当前阶段")
    round_number: int = Field(description="当前轮数")
    max_rounds: int = Field(description="最大轮数")
    current_price: float | None = Field(description="当前最高价；尚未挂牌时为空")
    offered_by: str | None = Field(description="当前最高出价者；尚无买家出价时为空")
    allowed_actions: list[str] = Field(description="当前 Agent 可以选择的动作")
    history: list[str] = Field(description="所有 Agent 都能看到的竞价记录")


class BargainAction(BaseModel):
    """Agent 返回给 Environment 的结构化动作。"""

    action_type: Literal[
        "挂牌", "出价", "放弃", "接受", "继续", "降价", "退出"
    ] = Field(
        description="卖家可挂牌、接受、继续、降价或退出；买家可出价或放弃"
    )
    price: float | None = Field(
        default=None,
        description="挂牌、出价或降价时填写正数；其他动作时为空",
    )
    message: str = Field(description="说给对方听的中文发言")

    @model_validator(mode="after")
    def validate_price(self) -> "BargainAction":
        """保证挂牌、出价和降价动作一定带有合法价格。"""

        if self.action_type in {"挂牌", "出价", "降价"} and (
            self.price is None or self.price <= 0
        ):
            raise ValueError("挂牌、出价或降价动作必须包含大于零的价格")
        if self.action_type not in {"挂牌", "出价", "降价"}:
            self.price = None
        return self
