"""定义 Agent 与 Environment 之间唯一允许传递的数据结构。"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class BargainObservation(BaseModel):
    """Environment 发给 Agent 的公开观察。"""

    round_number: int = Field(description="当前轮数")
    max_rounds: int = Field(description="最大轮数")
    current_price: float | None = Field(description="当前报价；尚未报价时为空")
    offered_by: str | None = Field(description="当前报价者；尚未报价时为空")
    history: list[str] = Field(description="双方都能看到的谈判记录")


class BargainAction(BaseModel):
    """Agent 返回给 Environment 的结构化动作。"""

    action_type: Literal["报价", "接受", "退出"] = Field(
        description="本轮选择报价、接受或者退出"
    )
    price: float | None = Field(
        default=None,
        description="选择报价时填写正数；接受或退出时为空",
    )
    message: str = Field(description="说给对方听的中文发言")

    @model_validator(mode="after")
    def validate_price(self) -> "BargainAction":
        """保证报价动作一定带有合法价格。"""

        if self.action_type == "报价" and (self.price is None or self.price <= 0):
            raise ValueError("报价动作必须包含大于零的价格")
        if self.action_type != "报价":
            self.price = None
        return self
