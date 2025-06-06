"""
Loan re-engagement agent tools module.

This module contains all the function tools used by the loan re-engagement agent
for customer interaction, loan calculations, and data retrieval.
"""

from typing import Dict, Any, Optional
import streamlit as st
from agents import function_tool
from util.utils import format_currency, format_percentage, logger


@function_tool
def get_customer_details(detail_type: str = "all") -> str:
    """
    Get specific customer details.

    Args:
        detail_type: Type of detail to retrieve (all, loan_offer, interest_rate, emi, etc.)

    Returns:
        Formatted customer details
    """
    try:
        # Access customer data from the global context or pass it differently
        # For now, we'll need to modify this to work with the SDK pattern
        customer_data = st.session_state.get('customer_data', {})

        if detail_type == "all":
            return f"""
Name: {customer_data.get('name', '')}
Loan Offer: {format_currency(customer_data.get('loan_offer', 0))}
Interest Rate: {format_percentage(customer_data.get('interest_rate', 0))}
Tenure: {customer_data.get('tenure', '')} months
Monthly EMI: {format_currency(customer_data.get('emi_amount', 0))}
Processing Fee: {format_currency(customer_data.get('processing_fee', 0))}
Foreclosure Charges: {format_currency(customer_data.get('foreclosure_charges', 0))}
Offer Expiry: {customer_data.get('offer_expiry', '')}
Purpose: {customer_data.get('purpose', '')}
Application Link: {customer_data.get('application_link', '')}
"""
        elif detail_type == "loan_offer":
            return f"Your pre-approved loan offer: {format_currency(customer_data.get('loan_offer', 0))}"
        elif detail_type == "interest_rate":
            return f"Interest rate: {format_percentage(customer_data.get('interest_rate', 0))}"
        elif detail_type == "emi":
            return f"Monthly EMI: {format_currency(customer_data.get('emi_amount', 0))}"
        elif detail_type == "expiry":
            return f"Offer expires on: {customer_data.get('offer_expiry', 'Not specified')}"
        else:
            return f"{detail_type}: {customer_data.get(detail_type, 'Information not available')}"
    except Exception as e:
        logger.error(f"Error getting customer details: {str(e)}")
        return "Unable to retrieve customer details at the moment."


@function_tool
def calculate_emi(loan_amount: float, interest_rate: float, tenure_months: int) -> str:
    """
    Calculate EMI for given loan parameters.

    Args:
        loan_amount: Loan amount in rupees
        interest_rate: Annual interest rate as percentage
        tenure_months: Loan tenure in months

    Returns:
        Calculated EMI and breakdown
    """
    try:
        monthly_rate = (interest_rate / 100) / 12
        emi = (loan_amount * monthly_rate * (1 + monthly_rate) ** tenure_months) / (
                (1 + monthly_rate) ** tenure_months - 1)
        total_amount = emi * tenure_months
        total_interest = total_amount - loan_amount

        return f"""
EMI Calculation:
- Loan Amount: {format_currency(loan_amount)}
- Interest Rate: {format_percentage(interest_rate)}
- Tenure: {tenure_months} months
- Monthly EMI: {format_currency(emi)}
- Total Amount: {format_currency(total_amount)}
- Total Interest: {format_currency(total_interest)}
"""
    except Exception as e:
        logger.error(f"Error calculating EMI: {str(e)}")
        return "Unable to calculate EMI. Please check the input parameters."


# @function_tool
# def check_loan_eligibility() -> str:
#     """
#     Check current loan eligibility status.
#
#     Returns:
#         Current eligibility status and details
#     """
#     try:
#         customer_data = st.session_state.get('customer_data', {})
#         eligibility_status = "Eligible"  # Placeholder
#         return f"""
# Loan Eligibility Status: {eligibility_status}
# Pre-approved Amount: {format_currency(customer_data.get('loan_offer', 0))}
# Interest Rate: {format_percentage(customer_data.get('interest_rate', 0))}
# Maximum Tenure: {customer_data.get('tenure', 'Not specified')} months
# """
#     except Exception as e:
#         logger.error(f"Error checking eligibility: {str(e)}")
#         return "Unable to check eligibility at the moment."


# @function_tool
# def get_application_status() -> str:
#     """
#     Get status of any existing loan applications.
#
#     Returns:
#         Application status information
#     """
#     try:
#         customer_data = st.session_state.get('customer_data', {})
#         return f"""
# Application Status: No pending applications
# Available Offer: {format_currency(customer_data.get('loan_offer', 0))}
# Offer Validity: {customer_data.get('offer_expiry', 'Please check with bank')}
# Application Link: {customer_data.get('application_link', 'Contact bank for application process')}
# """
#     except Exception as e:
#         logger.error(f"Error getting application status: {str(e)}")
#         return "Unable to retrieve application status."


# @function_tool
# def provide_loan_comparison(compare_with: str = "market_rates") -> str:
#     """
#     Provide loan comparison with market rates or other options.
#
#     Args:
#         compare_with: What to compare with (market_rates, other_banks, etc.)
#
#     Returns:
#         Comparison details
#     """
#     try:
#         customer_data = st.session_state.get('customer_data', {})
#         current_rate = customer_data.get('interest_rate', 0)
#
#         if compare_with == "market_rates":
#             return f"""
# Your Offer vs Market:
# - Your Rate: {format_percentage(current_rate)} (Pre-approved)
# - Market Rate: {format_percentage(current_rate + 1.5)} - {format_percentage(current_rate + 3)} (Typical range)
# - Your Advantage: Lower rate + No additional documentation
# - Processing Fee: {format_currency(customer_data.get('processing_fee', 0))}
# """
#         else:
#             return f"""
# Your current offer: {format_percentage(current_rate)}
# This is a competitive pre-approved rate with minimal documentation required.
# """
#     except Exception as e:
#         logger.error(f"Error providing comparison: {str(e)}")
#         return "Unable to provide comparison at the moment."


# @function_tool
# def get_loan_documents_required() -> str:
#     """
#     Get list of documents required for loan application.
#
#     Returns:
#         Document requirements information
#     """
#     try:
#         customer_data = st.session_state.get('customer_data', {})
#         loan_amount = customer_data.get('loan_offer', 0)
#
#         # Basic documents for pre-approved loans
#         basic_docs = [
#             "PAN Card",
#             "Aadhaar Card",
#             "Recent salary slips (last 3 months)",
#             "Bank statements (last 6 months)",
#             "Employment certificate"
#         ]
#
#         # Additional documents for higher amounts
#         if loan_amount > 1000000:  # Above 10 lakhs
#             basic_docs.extend([
#                 "Form 16 or ITR (last 2 years)",
#                 "Property documents (if applicable)",
#                 "Recent passport size photographs"
#             ])
#
#         return f"""
# Documents Required for Your Loan:
# {chr(10).join(f"• {doc}" for doc in basic_docs)}
#
# Note: Since this is a pre-approved offer, minimal documentation is required.
# Your relationship with the bank helps expedite the process.
# """
#     except Exception as e:
#         logger.error(f"Error getting document requirements: {str(e)}")
#         return "Unable to retrieve document requirements at the moment."


@function_tool
def calculate_loan_savings(prepayment_amount: float = 0) -> str:
    """
    Calculate potential savings with prepayment or different tenure options.

    Args:
        prepayment_amount: Amount for prepayment (optional)

    Returns:
        Savings calculation details
    """
    try:
        customer_data = st.session_state.get('customer_data', {})
        loan_amount = customer_data.get('loan_offer', 0)
        interest_rate = customer_data.get('interest_rate', 0)
        tenure = customer_data.get('tenure', 12)

        if not all([loan_amount, interest_rate, tenure]):
            return "Unable to calculate savings. Missing loan parameters."

        monthly_rate = (interest_rate / 100) / 12
        current_emi = (loan_amount * monthly_rate * (1 + monthly_rate) ** tenure) / (
                (1 + monthly_rate) ** tenure - 1)
        current_total = current_emi * tenure
        current_interest = current_total - loan_amount

        result = f"""
Current Loan Structure:
- EMI: {format_currency(current_emi)}
- Total Interest: {format_currency(current_interest)}
- Total Amount: {format_currency(current_total)}

"""

        if prepayment_amount > 0:
            remaining_principal = loan_amount - prepayment_amount
            if remaining_principal > 0:
                new_emi = (remaining_principal * monthly_rate * (1 + monthly_rate) ** tenure) / (
                        (1 + monthly_rate) ** tenure - 1)
                new_total = new_emi * tenure + prepayment_amount
                new_interest = new_total - loan_amount
                savings = current_interest - new_interest

                result += f"""
With Prepayment of {format_currency(prepayment_amount)}:
- New EMI: {format_currency(new_emi)}
- Total Interest Saved: {format_currency(savings)}
- New Total Amount: {format_currency(new_total)}
"""
        else:
            # Show different tenure options
            for new_tenure in [12, 24, 36, 60]:
                if new_tenure != tenure:
                    new_emi = (loan_amount * monthly_rate * (1 + monthly_rate) ** new_tenure) / (
                            (1 + monthly_rate) ** new_tenure - 1)
                    new_total = new_emi * new_tenure
                    new_interest = new_total - loan_amount
                    difference = current_interest - new_interest

                    result += f"""
{new_tenure} months tenure:
- EMI: {format_currency(new_emi)}
- Interest difference: {format_currency(difference)} {'(Save)' if difference > 0 else '(Extra)'}
"""

        return result

    except Exception as e:
        logger.error(f"Error calculating savings: {str(e)}")
        return "Unable to calculate loan savings at the moment."


@function_tool
def calculate_dynamic_pricing(loan_amount: float = 0, requested_tenure: int = 0) -> str:
    """
    Calculate dynamic pricing based on customer profile and risk assessment.

    Args:
        loan_amount: Requested loan amount (0 to use customer default)
        requested_tenure: Requested tenure in months (0 to use customer default)

    Returns:
        Dynamic pricing details with adjusted rates and terms
    """
    try:
        # Get customer data from session state
        customer_data = st.session_state.get('customer_data', {})

        # Use provided parameters or fall back to customer data
        base_loan_amount = loan_amount if loan_amount > 0 else customer_data.get('loan_offer', 0)
        base_tenure = requested_tenure if requested_tenure > 0 else customer_data.get('tenure', 12)
        base_interest_rate = customer_data.get('interest_rate', 12.0)

        if not base_loan_amount or not base_interest_rate:
            return "Unable to calculate dynamic pricing. Missing essential customer data."

        # Initialize pricing factors
        rate_adjustment = 0.0  # Percentage points to add/subtract
        processing_fee_multiplier = 1.0  # Multiplier for processing fee
        max_loan_multiplier = 1.0  # Multiplier for maximum loan amount

        # --- CUSTOMER RELATIONSHIP FACTORS ---

        # Account age factor
        account_age_years = customer_data.get('account_age_years', 0)
        if account_age_years >= 5:
            rate_adjustment -= 0.5  # 0.5% discount for 5+ years
        elif account_age_years >= 2:
            rate_adjustment -= 0.25  # 0.25% discount for 2-5 years
        elif account_age_years < 1:
            rate_adjustment += 0.25  # 0.25% premium for new customers

        # Salary account relationship
        is_salary_account = customer_data.get('is_salary_account', False)
        if is_salary_account:
            rate_adjustment -= 0.3
            processing_fee_multiplier *= 0.8  # 20% processing fee discount

        # Banking relationship value
        avg_monthly_balance = customer_data.get('avg_monthly_balance', 0)
        if avg_monthly_balance >= 100000:  # 1 lakh+
            rate_adjustment -= 0.4
            max_loan_multiplier *= 1.2
        elif avg_monthly_balance >= 50000:  # 50k+
            rate_adjustment -= 0.2
            max_loan_multiplier *= 1.1
        elif avg_monthly_balance < 10000:  # Less than 10k
            rate_adjustment += 0.3

        # --- CREDIT PROFILE FACTORS ---

        # Credit score impact
        credit_score = customer_data.get('credit_score', 750)
        if credit_score >= 800:
            rate_adjustment -= 0.5
            max_loan_multiplier *= 1.3
        elif credit_score >= 750:
            rate_adjustment -= 0.25
        elif credit_score >= 700:
            rate_adjustment += 0.0  # No change
        elif credit_score >= 650:
            rate_adjustment += 0.5
        else:
            rate_adjustment += 1.0
            max_loan_multiplier *= 0.8

        # Existing loan performance
        loan_history_score = customer_data.get('loan_history_score', 'good')  # excellent, good, average, poor
        if loan_history_score == 'excellent':
            rate_adjustment -= 0.3
            processing_fee_multiplier *= 0.7
        elif loan_history_score == 'good':
            rate_adjustment -= 0.1
        elif loan_history_score == 'poor':
            rate_adjustment += 0.5

        # --- INCOME AND EMPLOYMENT FACTORS ---

        # Monthly income
        monthly_income = customer_data.get('monthly_income', 0)
        if monthly_income >= 100000:  # 1 lakh+
            rate_adjustment -= 0.2
            max_loan_multiplier *= 1.4
        elif monthly_income >= 75000:  # 75k+
            rate_adjustment -= 0.1
            max_loan_multiplier *= 1.2
        elif monthly_income < 30000:  # Less than 30k
            rate_adjustment += 0.3
            max_loan_multiplier *= 0.9

        # Employment type
        employment_type = customer_data.get('employment_type', 'salaried')
        if employment_type == 'government':
            rate_adjustment -= 0.4
        elif employment_type == 'mnc':
            rate_adjustment -= 0.2
        elif employment_type == 'self_employed':
            rate_adjustment += 0.3
        elif employment_type == 'business_owner':
            rate_adjustment += 0.2

        # Job stability (years in current job)
        job_stability_years = customer_data.get('job_stability_years', 2)
        if job_stability_years >= 3:
            rate_adjustment -= 0.1
        elif job_stability_years < 1:
            rate_adjustment += 0.2

        # --- LOAN AMOUNT AND TENURE FACTORS ---

        # Loan amount brackets
        if base_loan_amount >= 2000000:  # 20 lakh+
            rate_adjustment -= 0.25  # Volume discount
        elif base_loan_amount >= 1000000:  # 10 lakh+
            rate_adjustment -= 0.15
        elif base_loan_amount < 200000:  # Less than 2 lakh
            rate_adjustment += 0.2  # Small loan premium

        # Tenure optimization
        if base_tenure <= 12:  # Short tenure
            rate_adjustment -= 0.1
        elif base_tenure >= 60:  # Long tenure
            rate_adjustment += 0.2

        # --- MARKET AND SEASONAL FACTORS ---

        # Festive season discount (if applicable)
        is_festive_season = customer_data.get('is_festive_season', False)
        if is_festive_season:
            rate_adjustment -= 0.15
            processing_fee_multiplier *= 0.9

        # Customer acquisition vs retention
        has_existing_loans = customer_data.get('has_existing_loans', False)
        if not has_existing_loans:
            rate_adjustment -= 0.1  # New loan customer incentive

        # --- CALCULATE FINAL PRICING ---

        # Apply rate adjustment (with reasonable bounds)
        final_interest_rate = max(8.0, min(18.0, base_interest_rate + rate_adjustment))

        # Calculate adjusted loan amount
        max_eligible_amount = base_loan_amount * max_loan_multiplier

        # Calculate processing fee
        base_processing_fee = customer_data.get('processing_fee', base_loan_amount * 0.02)
        final_processing_fee = base_processing_fee * processing_fee_multiplier

        # Calculate EMI with new rate
        monthly_rate = (final_interest_rate / 100) / 12
        final_emi = (base_loan_amount * monthly_rate * (1 + monthly_rate) ** base_tenure) / (
                (1 + monthly_rate) ** base_tenure - 1)

        # Calculate savings/additional cost compared to base offer
        base_monthly_rate = (base_interest_rate / 100) / 12
        base_emi = (base_loan_amount * base_monthly_rate * (1 + base_monthly_rate) ** base_tenure) / (
                (1 + base_monthly_rate) ** base_tenure - 1)

        monthly_difference = final_emi - base_emi
        total_difference = monthly_difference * base_tenure

        # Generate pricing explanation
        explanation_factors = []
        if rate_adjustment < -0.1:
            explanation_factors.append("✅ Excellent banking relationship")
        if credit_score >= 750:
            explanation_factors.append("✅ Strong credit profile")
        if is_salary_account:
            explanation_factors.append("✅ Salary account holder")
        if monthly_income >= 75000:
            explanation_factors.append("✅ High income bracket")
        if rate_adjustment > 0.1:
            explanation_factors.append("⚠️ Risk factors considered")

        # Format response
        result = f"""
🎯 **PERSONALIZED PRICING ANALYSIS**

**Your Customized Offer:**
• Interest Rate: {format_percentage(final_interest_rate)} (Adjusted from {format_percentage(base_interest_rate)})
• Monthly EMI: {format_currency(final_emi)}
• Processing Fee: {format_currency(final_processing_fee)}
• Maximum Eligible: {format_currency(max_eligible_amount)}

**Rate Adjustment: {'+' if rate_adjustment > 0 else ''}{rate_adjustment:.2f}% points**

**Key Factors Considered:**
{chr(10).join(explanation_factors) if explanation_factors else "• Standard market factors applied"}

**Financial Impact:**
• Monthly difference: {'+' if monthly_difference > 0 else ''}{format_currency(abs(monthly_difference))} {'more' if monthly_difference > 0 else 'savings'}
• Total impact over {base_tenure} months: {'+' if total_difference > 0 else ''}{format_currency(abs(total_difference))} {'more' if total_difference > 0 else 'savings'}

**Why This Rate?**
Our dynamic pricing considers your relationship history, credit profile, income stability, and current market conditions to offer you the best possible rate.

**Special Benefits Available:**
"""

        # Add special benefits
        if processing_fee_multiplier < 1.0:
            discount_percent = (1 - processing_fee_multiplier) * 100
            result += f"• {discount_percent:.0f}% discount on processing fee\n"

        if max_loan_multiplier > 1.0:
            increase_percent = (max_loan_multiplier - 1) * 100
            result += f"• Up to {increase_percent:.0f}% higher loan eligibility\n"

        if is_salary_account:
            result += "• Priority processing for salary account holders\n"

        if is_festive_season:
            result += "• 🎉 Festive season special discount applied\n"

        result += f"\n💡 **Recommendation:** This rate is valid for the next 15 days. Your profile qualifies you for our premium customer segment."

        return result

    except Exception as e:
        logger.error(f"Error calculating dynamic pricing: {str(e)}")
        return "Unable to calculate personalized pricing at the moment. Please try again or contact our loan specialist."


@function_tool
def get_rate_improvement_suggestions() -> str:
    """
    Provide suggestions on how customer can improve their loan rate.

    Returns:
        Actionable suggestions for better rates
    """
    try:
        customer_data = st.session_state.get('customer_data', {})
        current_rate = customer_data.get('interest_rate', 12.0)

        suggestions = []
        potential_savings = 0

        # Credit score improvement
        credit_score = customer_data.get('credit_score', 750)
        if credit_score < 800:
            target_score = min(850, credit_score + 50)
            potential_reduction = 0.5 if target_score >= 800 else 0.25
            potential_savings += potential_reduction
            suggestions.append(f"🎯 **Improve Credit Score to {target_score}+**")
            suggestions.append(f"   • Potential rate reduction: {potential_reduction}%")
            suggestions.append(f"   • Pay all bills on time, reduce credit utilization")

        # Salary account conversion
        is_salary_account = customer_data.get('is_salary_account', False)
        if not is_salary_account:
            potential_savings += 0.3
            suggestions.append(f"💰 **Convert to Salary Account**")
            suggestions.append(f"   • Potential rate reduction: 0.3%")
            suggestions.append(f"   • Additional processing fee discount: 20%")

        # Increase monthly balance
        avg_balance = customer_data.get('avg_monthly_balance', 0)
        if avg_balance < 50000:
            potential_savings += 0.2
            suggestions.append(f"💳 **Maintain Higher Account Balance**")
            suggestions.append(f"   • Target: ₹50,000+ average monthly balance")
            suggestions.append(f"   • Potential rate reduction: 0.2-0.4%")

        # Loan amount optimization
        loan_amount = customer_data.get('loan_offer', 0)
        if loan_amount < 1000000:
            suggestions.append(f"📈 **Consider Higher Loan Amount**")
            suggestions.append(f"   • ₹10+ lakh loans get volume discounts")
            suggestions.append(f"   • Rate reduction: 0.15-0.25%")

        # Tenure optimization
        tenure = customer_data.get('tenure', 12)
        if tenure > 36:
            suggestions.append(f"⏰ **Opt for Shorter Tenure**")
            suggestions.append(f"   • Current: {tenure} months")
            suggestions.append(f"   • Consider: 24-36 months for better rates")
            suggestions.append(f"   • Rate reduction: 0.1%")

        if not suggestions:
            return f"""
🌟 **Congratulations!** 

Your profile already qualifies for our best rates. You're getting:
• Interest Rate: {format_percentage(current_rate)}
• This is among our most competitive rates
• Your excellent banking relationship has optimized your pricing

💡 **Tip:** Maintain your current credit discipline and account relationship to continue enjoying premium rates.
"""

        # Calculate potential EMI savings
        if potential_savings > 0:
            new_rate = max(8.0, current_rate - potential_savings)
            monthly_rate_current = (current_rate / 100) / 12
            monthly_rate_new = (new_rate / 100) / 12

            current_emi = (loan_amount * monthly_rate_current * (1 + monthly_rate_current) ** tenure) / (
                    (1 + monthly_rate_current) ** tenure - 1)
            new_emi = (loan_amount * monthly_rate_new * (1 + monthly_rate_new) ** tenure) / (
                    (1 + monthly_rate_new) ** tenure - 1)

            monthly_savings = current_emi - new_emi
            total_savings = monthly_savings * tenure

            result = f"""
🚀 **RATE IMPROVEMENT ROADMAP**

**Current Rate:** {format_percentage(current_rate)}
**Potential Best Rate:** {format_percentage(new_rate)} (Save {potential_savings:.1f}%)

**Potential Savings:**
• Monthly EMI reduction: {format_currency(monthly_savings)}
• Total savings over {tenure} months: {format_currency(total_savings)}

**Action Items:**
{chr(10).join(suggestions)}

**Timeline:** Most improvements can be achieved within 3-6 months with consistent effort.

🎯 **Quick Win:** Start with salary account conversion for immediate 0.3% rate reduction!
"""
        else:
            result = f"""
**RATE IMPROVEMENT SUGGESTIONS**

{chr(10).join(suggestions)}

These improvements will enhance your overall banking relationship and may qualify you for better rates in future loan applications.
"""

        return result

    except Exception as e:
        logger.error(f"Error generating rate improvement suggestions: {str(e)}")
        return "Unable to generate rate improvement suggestions at the moment."


# List of all available tools for easy import
LOAN_TOOLS = [
    get_customer_details,
    calculate_emi,
    calculate_loan_savings,
    calculate_dynamic_pricing
]