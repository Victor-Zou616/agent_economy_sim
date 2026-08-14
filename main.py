"""创建三个 Agent，并启动竞价环境。"""

import argparse

from agent import BargainingAgent
from environment import BargainingEnvironment
from tools import ProductInspectionService


def main() -> None:
    """读取命令行参数，组装并运行三 Agent 竞价系统。"""

    parser = argparse.ArgumentParser(description="最小三 Agent 商品竞价示例")
    parser.add_argument("--rounds", type=int, default=5, help="最大竞价轮数")
    parser.add_argument("--product", default="二手自行车", help="竞价商品")
    parser.add_argument(
        "--inspections",
        type=int,
        default=2,
        help="每位买家最多可以检查的不同商品方面数量",
    )
    args = parser.parse_args()

    inspection_service = ProductInspectionService(
        max_inspections_per_buyer=args.inspections
    )

    seller = BargainingAgent(
        name="Alice",
        role="卖家",
        goal="自主确定挂牌价格，并判断是否接受当前最高报价。",
    )
    buyer_one = BargainingAgent(
        name="Bob",
        role="买家",
        goal="在与另一位买家的竞争中，尽量以较低价格竞得商品。",
        tools=[inspection_service.create_tool("Bob")],
    )
    buyer_two = BargainingAgent(
        name="Charlie",
        role="买家",
        goal="在与另一位买家的竞争中，尽量以较低价格竞得商品。",
        tools=[inspection_service.create_tool("Charlie")],
    )

    environment = BargainingEnvironment(
        seller=seller,
        buyers=[buyer_one, buyer_two],
        inspection_service=inspection_service,
        product_name=args.product,
        max_rounds=args.rounds,
    )
    environment.run()


if __name__ == "__main__":
    main()
