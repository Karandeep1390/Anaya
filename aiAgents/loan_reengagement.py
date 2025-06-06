import os
from openai import OpenAI
from typing import List, Dict, Any, Optional
from config.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE
)
from util.utils import load_customer_data, format_currency, format_percentage, logger
from agents import Agent,Runner


def _load_customer_data(customer_id: Optional[str] = None) -> Dict[str, Any]:
    """Load customer data with error handling."""
    try:
        return load_customer_data(customer_id)
    except Exception as e:
        logger.error(f"Failed to load customer data: {str(e)}")
        raise


def _get_system_prompt() -> str:
    """Get the system prompt with customer context."""
    return """You are a friendly and empathetic assistant from a bank, helping existing customers understand and explore their pre-approved loan offers.

## Objective:
Gently nudge eligible customers to consider taking a loan. If they show interest, help them with details like amount, interest rate, tenure, and process. If they have concerns, listen patiently and resolve them.

## Tone:
- Calm, relatable, and helpful — like a trusted bank advisor or friend.
- Use Hinglish (Hindi in English script) if the customer prefers it.
- Be emotionally intelligent; avoid pushiness.
- Encourage questions, resolve doubts.

## Behavioral Guidelines:
- Use customer context provided at runtime.
- Do not hard-sell — focus on resolving confusion or hesitation.
- Avoid commands or salesy language.
- Keep replies short (under 26 words) and end with a question when possible.
- Emojis are okay when adding emotional warmth.

## Customer Context:
{context}"""


class LoanReengagementAgent:
    def __init__(self, customer_id: Optional[str] = None):
        """
        Initialize the loan re-engagement agent.

        Args:
            customer_id: Optional customer ID to load specific customer data
        """
        super().__init__()
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.customer_data = _load_customer_data(customer_id)
        self.system_prompt = _get_system_prompt()

    def format_customer_context(self) -> str:
        """Format customer data for the prompt."""
        try:
            return f"""
Name: {self.customer_data.get('name', '')}
Loan Offer: {format_currency(self.customer_data.get('loan_offer', 0))}
Interest Rate: {format_percentage(self.customer_data.get('interest_rate', 0))}
Tenure: {self.customer_data.get('tenure', '')} months
Monthly EMI: {format_currency(self.customer_data.get('emi_amount', 0))}
Processing Fee: {format_currency(self.customer_data.get('processing_fee', 0))}
Foreclosure Charges: {format_currency(self.customer_data.get('foreclosure_charges', 0))}
Offer Expiry: {self.customer_data.get('offer_expiry', '')}
Purpose: {self.customer_data.get('purpose', '')}
Application Link: {self.customer_data.get('application_link', '')}
"""
        except Exception as e:
            logger.error(f"Error formatting customer context: {str(e)}")
            raise

    def process_message(self, message: str, messages: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Process incoming message and generate response.

        Args:
            message: User's message
            messages: Optional conversation history

        Returns:
            Generated response

        Raises:
            Exception: If there's an error processing the message
        """
        try:
            customer_context = self.format_customer_context()
            system_message = self.system_prompt.format(context=customer_context)

            # Prepare messages list with system message
            chat_messages = [{"role": "system", "content": system_message}]

            # Add conversation history if available
            if messages:
                chat_messages.extend(messages)

            # Add current message
            chat_messages.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=chat_messages,
                temperature=OPENAI_TEMPERATURE
            )

            return response.choices[0].message.content

        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            return "I apologize, but I'm having trouble processing your request right now. Please try again later."


def main():
    """Main function for command-line usage."""
    try:
        # Initialize the agent - Fixed typo in class name
        agent = LoanReengagementAgent()

        # Initialize the runner
        logger.info("Loan Re-engagement Bot initialized")
        print("Loan Re-engagement Bot initialized. Type 'quit' to exit.")

        # Example conversation loop
        while True:
            user_input = input("\nCustomer: ")
            if user_input.lower() == 'quit':
                break

            response = agent.process_message(user_input)
            print(f"\nBot: {response}")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print("An error occurred. Please check the logs for details.")


if __name__ == "__main__":
    main()