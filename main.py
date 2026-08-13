"""创建三个 Agent，并启动竞价环境。"""

import argparse

from agent import BargainingAgent
from environment import BargainingEnvironment


def main() -> None:
    """读取命令行参数，组装并运行三 Agent 竞价系统。"""

    parser = argparse.ArgumentParser(description="最小三 Agent 商品竞价示例")
    parser.add_argument("--rounds", type=int, default=5, help="最大竞价轮数")
    parser.add_argument("--product", default="二手自行车", help="竞价商品")
    args = parser.parse_args()

    seller = BargainingAgent(
        name="Alice",
        role="卖家",
        goal="自主确定挂牌价格，并判断是否接受当前最高报价。",
    )
    buyer_one = BargainingAgent(
        name="Bob",
        role="买家",
        goal="在与另一位买家的竞争中，尽量以较低价格竞得商品。",
    )
    buyer_two = BargainingAgent(
        name="Charlie",
        role="买家",
        goal="在与另一位买家的竞争中，尽量以较低价格竞得商品。",
    )

    environment = BargainingEnvironment(
        seller=seller,
        buyers=[buyer_one, buyer_two],
        product_name=args.product,
        max_rounds=args.rounds,
    )
    environment.run()


if __name__ == "__main__":
    main()
