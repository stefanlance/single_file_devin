def calculate_total(prices, quantities, discounts, tax_rate):
    subtotal = sum(price * quantity * (1 - discount) 
                   for price, quantity, discount 
                   in zip(prices, quantities, discounts))
    tax = subtotal * tax_rate
    total = subtotal + tax
    return total

def main():
    prices = [10.0, 25.0, 15.0] 
    quantities = [2, 1, 3]
    discounts = [0.1, 0.0, 0.2]
    tax_rate = 0.08

    total_cost = calculate_total(prices, quantities, discounts, tax_rate)
    print(f"Total cost: ${total_cost:.2f}")

if __name__ == "__main__":
    main()