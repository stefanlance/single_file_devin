import typing

def calculate_total(
    prices: typing.Sequence[float],
    quantities: typing.Sequence[int],
    discounts: typing.Sequence[float],
    tax_rate: float,
) -> float:
    """
    Calculate the total cost of items with prices, quantities, discounts, and tax.

    Args:
        prices: A sequence of item prices.
        quantities: A sequence of item quantities.
        discounts: A sequence of item discount rates.
        tax_rate: The tax rate to apply.

    Returns:
        The total cost after applying discounts and tax.
    """
    subtotal = sum(
        price * quantity * (1 - discount)
        for price, quantity, discount in zip(prices, quantities, discounts)
    )
    tax = subtotal * tax_rate
    total = subtotal + tax
    return total


def main() -> None:
    prices = [10.0, 25.0, 15.0]
    quantities = [2, 1, 3]
    discounts = [0.1, 0.0, 0.2]
    tax_rate = 0.08

    total_cost = calculate_total(prices, quantities, discounts, tax_rate)
    print(f"Total cost: ${total_cost:.2f}")


if __name__ == "__main__":
    main()