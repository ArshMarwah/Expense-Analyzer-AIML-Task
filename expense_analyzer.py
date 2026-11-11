"""
Personal Expense Analyzer
-------------------------
Enter daily expenses, save them, and see where your money goes.
Libraries: Pandas (tables), NumPy (maths), Matplotlib (charts)
"""

import os
from datetime import date

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

FILE = "expenses.csv"  # all your data is saved in this file
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]


# ---------- 1. LOAD & SAVE DATA ----------
def load_data():
    """Read the CSV file. If it doesn't exist yet, return an empty table."""
    if os.path.exists(FILE):
        df = pd.read_csv(FILE, parse_dates=["Date"])
        return df
    return pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])


def save_data(df):
    df.to_csv(FILE, index=False)


# ---------- 2. ADD AN EXPENSE ----------
def add_expense(df):
    print("\nCategories:")
    for i, c in enumerate(CATEGORIES, start=1):
        print(f"  {i}. {c}")

    try:
        choice = int(input("Choose category number: "))
        category = CATEGORIES[choice - 1]
        amount = float(input("Amount spent: "))
        note = input("Note (optional): ")
    except (ValueError, IndexError):
        print("Invalid input. Expense not added.")
        return df

    day = input("Date (YYYY-MM-DD) or press Enter for today: ").strip()
    day = pd.to_datetime(day) if day else pd.to_datetime(date.today())

    new_row = pd.DataFrame(
        [{"Date": day, "Category": category, "Amount": amount, "Note": note}]
    )
    df = pd.concat([df, new_row], ignore_index=True)
    df["Date"] = pd.to_datetime(df["Date"])  # make sure Date is a real date
    save_data(df)
    print(f"Added: {category} - {amount:.2f}")
    return df


# ---------- 3. ANALYSIS ----------
def show_summary(df):
    """Total, average, biggest expense, and spending per category."""
    if df.empty:
        print("\nNo data yet. Add some expenses first.")
        return

    amounts = df["Amount"].to_numpy()  # Pandas column -> NumPy array

    print("\n===== OVERALL SUMMARY =====")
    print(f"Total spent      : {np.sum(amounts):.2f}")
    print(f"Average expense  : {np.mean(amounts):.2f}")
    print(f"Biggest expense  : {np.max(amounts):.2f}")
    print(f"Smallest expense : {np.min(amounts):.2f}")
    print(f"Number of entries: {len(amounts)}")

    by_cat = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    percent = (by_cat / by_cat.sum() * 100).round(1)

    print("\n===== SPENDING BY CATEGORY =====")
    for cat in by_cat.index:
        print(f"{cat:<15} {by_cat[cat]:>10.2f}   ({percent[cat]}%)")

    print(f"\nYou spend the most on: {by_cat.idxmax()}")


def monthly_report(df):
    """Total spending for each month + category breakdown."""
    if df.empty:
        print("\nNo data yet.")
        return

    df = df.copy()
    df["Month"] = df["Date"].dt.to_period("M")  # e.g. 2026-11

    monthly_total = df.groupby("Month")["Amount"].sum()
    print("\n===== MONTHLY REPORT =====")
    for month, total in monthly_total.items():
        print(f"{month}: {total:.2f}")

    print("\n----- Month x Category table -----")
    table = df.pivot_table(
        index="Month", columns="Category", values="Amount",
        aggfunc="sum", fill_value=0,
    )
    print(table.round(2))

    if len(monthly_total) >= 2:
        change = monthly_total.iloc[-1] - monthly_total.iloc[-2]
        word = "more" if change > 0 else "less"
        print(f"\nLatest month: you spent {abs(change):.2f} {word} than the month before (the latest month may be incomplete).")


# ---------- 4. CHARTS ----------
def show_charts(df):
    if df.empty:
        print("\nNo data yet.")
        return

    by_cat = df.groupby("Category")["Amount"].sum()
    monthly = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].pie(by_cat, labels=by_cat.index, autopct="%1.1f%%", startangle=90)
    axes[0].set_title("Where your money goes")

    axes[1].bar(monthly.index.astype(str), monthly.values, color="teal")
    axes[1].set_title("Monthly spending")
    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("Amount")

    plt.tight_layout()
    plt.savefig("expense_report.png")  # also saves the picture
    print("Chart saved as expense_report.png")
    plt.show()


# ---------- 5. SAMPLE DATA (to try the app quickly) ----------
def add_sample_data(df):
    np.random.seed(42)  # same "random" numbers every time
    rows = []
    for d in pd.date_range("2026-09-01", "2026-11-10", freq="2D"):
        cat = np.random.choice(CATEGORIES, p=[0.3, 0.2, 0.15, 0.1, 0.1, 0.05, 0.1])
        amt = round(float(np.random.uniform(50, 1500)), 2)
        rows.append({"Date": d, "Category": cat, "Amount": amt, "Note": "sample"})
    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
    df["Date"] = pd.to_datetime(df["Date"])  # make sure Date is a real date
    save_data(df)
    print(f"Added {len(rows)} sample expenses.")
    return df


# ---------- 6. MAIN MENU ----------
def main():
    df = load_data()
    while True:
        print("\n===== PERSONAL EXPENSE ANALYZER =====")
        print("1. Add expense")
        print("2. View all expenses")
        print("3. Summary & category analysis")
        print("4. Monthly report")
        print("5. Show charts")
        print("6. Load sample data (for practice)")
        print("7. Exit")
        choice = input("Choose (1-7): ").strip()

        if choice == "1":
            df = add_expense(df)
        elif choice == "2":
            print(df.to_string() if not df.empty else "No data yet.")
        elif choice == "3":
            show_summary(df)
        elif choice == "4":
            monthly_report(df)
        elif choice == "5":
            show_charts(df)
        elif choice == "6":
            df = add_sample_data(df)
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Please choose 1-7.")


if __name__ == "__main__":
    main()
