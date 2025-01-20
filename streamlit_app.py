import streamlit as st

# Constants
STANDARD_DEDUCTION = {
    "single": 13850,
    "married_jointly": 27700,
    "head_of_household": 20800,
    "married_separately": 13850,
}
TAX_BRACKETS = [
    (0, 11000, 0.10),
    (11001, 44725, 0.12),
    (44726, 95375, 0.22),
    (95376, 182100, 0.24),
    (182101, 231250, 0.32),
    (231251, 578125, 0.35),
    (578126, float('inf'), 0.37)
]
SALT_DEDUCTION_CAP = 10000  # SALT deduction cap


# Function to calculate federal tax liability
def calculate_federal_tax(taxable_income, brackets):
    tax = 0
    for lower, upper, rate in brackets:
        if taxable_income > lower:
            income_in_bracket = min(taxable_income, upper) - lower
            tax += income_in_bracket * rate
        if taxable_income <= upper:
            break
    return tax


# Function to estimate taxes
def estimate_tax(
    wages,
    federal_tax_withheld,
    state_tax_withheld,
    filing_status="single",
    itemized_deductions=None,
):
    # Get standard deduction
    standard_deduction = STANDARD_DEDUCTION.get(filing_status, STANDARD_DEDUCTION["single"])

    # Calculate itemized deductions if provided
    itemized_deduction_total = 0
    if itemized_deductions:
        state_local_taxes = min(itemized_deductions.get("state_and_local_taxes", 0), SALT_DEDUCTION_CAP)
        mortgage_interest = itemized_deductions.get("mortgage_interest", 0)
        charitable_donations = itemized_deductions.get("charitable_donations", 0)
        medical_expenses = itemized_deductions.get("medical_expenses", 0)
        itemized_deduction_total = state_local_taxes + mortgage_interest + charitable_donations + medical_expenses

    # Use the larger of standard or itemized deduction
    total_deductions = max(standard_deduction, itemized_deduction_total)
    taxable_income = wages - total_deductions

    # Calculate federal tax liability
    federal_tax_liability = calculate_federal_tax(taxable_income, TAX_BRACKETS)

    # Calculate refund or amount owed
    federal_refund = federal_tax_withheld - federal_tax_liability

    return {
        "Taxable Income": round(taxable_income, 2),
        "Federal Tax Liability": round(federal_tax_liability, 2),
        "Federal Tax Withheld": federal_tax_withheld,
        "Federal Refund or Amount Owed": round(federal_refund, 2),
        "Deductions Used": "Standard" if total_deductions == standard_deduction else "Itemized",
        "Total Deductions": round(total_deductions, 2),
    }


# Streamlit App
st.title("Federal Tax Estimator")

# User inputs
st.header("Enter Your W-2 Details")
wages = st.number_input("Wages (Box 1 of W-2):", min_value=0.0, format="%0.2f")
federal_tax_withheld = st.number_input("Federal Tax Withheld (Box 2 of W-2):", min_value=0.0, format="%0.2f")
state_tax_withheld = st.number_input("State Tax Withheld (Box 17 of W-2):", min_value=0.0, format="%0.2f")
filing_status = st.selectbox("Filing Status:", options=["single", "married_jointly", "head_of_household", "married_separately"])

# Itemized deductions
use_itemized = st.checkbox("Use Itemized Deductions?")
itemized_deductions = None
if use_itemized:
    st.subheader("Enter Itemized Deductions")
    state_and_local_taxes = st.number_input("  State and Local Taxes:", min_value=0.0, format="%0.2f")
    mortgage_interest = st.number_input("  Mortgage Interest:", min_value=0.0, format="%0.2f")
    charitable_donations = st.number_input("  Charitable Donations:", min_value=0.0, format="%0.2f")
    medical_expenses = st.number_input("  Medical Expenses:", min_value=0.0, format="%0.2f")

    itemized_deductions = {
        "state_and_local_taxes": state_and_local_taxes,
        "mortgage_interest": mortgage_interest,
        "charitable_donations": charitable_donations,
        "medical_expenses": medical_expenses,
    }

# Calculate tax
if st.button("Calculate"):
    if wages > 0 and federal_tax_withheld >= 0:
        results = estimate_tax(
            wages=wages,
            federal_tax_withheld=federal_tax_withheld,
            state_tax_withheld=state_tax_withheld,
            filing_status=filing_status,
            itemized_deductions=itemized_deductions,
        )

        # Display results
        st.subheader("Tax Calculation Results")
        for key, value in results.items():
            st.write(f"{key}: {value}")
    else:
        st.error("Please enter valid values for wages and tax withheld.")
