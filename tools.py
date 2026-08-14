"""提供买家可自主调用的独立商品检查工具。"""

from typing import Literal

from langchain_core.tools import BaseTool, tool

from protocol import ProductProfile


InspectionAspect = Literal[
    "整体状况",
    "使用历史",
    "维护或保存情况",
    "缺陷与风险",
    "来源与真实性",
]


class ProductInspectionService:
    """保存隐藏商品档案，并分别记录每个买家的私有检查结果。"""

    def __init__(self, max_inspections_per_buyer: int = 2) -> None:
        if max_inspections_per_buyer < 1:
            raise ValueError("每位买家的检查次数必须至少为一次")

        self.max_inspections_per_buyer = max_inspections_per_buyer
        self._profile: ProductProfile | None = None
        self._results: dict[str, dict[str, str]] = {}

    def set_profile(self, profile: ProductProfile) -> None:
        """由 Environment 在开拍前设置一次隐藏商品档案。"""

        if self._profile is not None:
            raise ValueError("商品档案已经设置，竞价过程中不能修改")
        self._profile = profile

    def create_tool(self, buyer_name: str) -> BaseTool:
        """创建绑定到指定买家的私有检查工具。"""

        service = self

        @tool("inspect_product")
        def inspect_product(aspect: InspectionAspect) -> str:
            """独立检查商品的一个方面；检查次数上限由系统配置。"""

            return service.inspect(buyer_name, aspect)

        return inspect_product

    def inspect(self, buyer_name: str, aspect: InspectionAspect) -> str:
        """返回一个方面的检查结果，并执行次数限制。"""

        if self._profile is None:
            return "检查失败：Environment 尚未建立商品档案。"

        buyer_results = self._results.setdefault(buyer_name, {})
        if aspect in buyer_results:
            result = buyer_results[aspect]
            print(f"【工具调用｜{buyer_name}】重复查询：{aspect}")
            print(f"【私有工具结果｜仅 {buyer_name} 可见】{result}")
            return result

        if len(buyer_results) >= self.max_inspections_per_buyer:
            result = (
                f"检查失败：你最多只能检查 {self.max_inspections_per_buyer} 个不同方面，"
                "当前次数已经用完。"
            )
            print(f"【工具调用｜{buyer_name}】检查：{aspect}")
            print(f"【私有工具结果｜仅 {buyer_name} 可见】{result}")
            return result

        profile_fields = {
            "整体状况": self._profile.overall_condition,
            "使用历史": self._profile.usage_history,
            "维护或保存情况": self._profile.maintenance_or_storage,
            "缺陷与风险": self._profile.defects_and_risks,
            "来源与真实性": self._profile.authenticity_and_source,
        }
        result = f"独立检查结果｜{aspect}：{profile_fields[aspect]}"
        buyer_results[aspect] = result

        print(f"【工具调用｜{buyer_name}】检查：{aspect}")
        print(f"【私有工具结果｜仅 {buyer_name} 可见】{result}")
        return result

    def private_results_for(self, buyer_name: str) -> list[str]:
        """返回指定买家过去获得的全部私有检查结果。"""

        return list(self._results.get(buyer_name, {}).values())
