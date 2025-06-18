"""
Main loan re-engagement agent module.

This module contains the main agent creation and runner logic,
with tools imported from the separate tools module.
"""
import asyncio
from typing import Dict, Any, Optional, Tuple
from agents import Agent, Runner
import streamlit as st
from config.config import OPENAI_MODEL
from util.utils import load_customer_data, format_currency, format_percentage, logger
from tools.loan_tools import LOAN_TOOLS


def _load_customer_data(customer_id: Optional[str] = None) -> Dict[str, Any]:
    """Load customer data with error handling."""
    try:
        return load_customer_data(customer_id)
    except Exception as e:
        logger.error(f"Failed to load customer data: {str(e)}")
        raise


def create_loan_reengagement_agent(customer_data: Dict[str, Any]) -> Agent:

    # Format customer context
    customer_context = f"""
Name: {customer_data.get('name', '')}
Loan Offer: {format_currency(customer_data.get('loan_offer', 0))}
Interest Rate: {format_percentage(customer_data.get('interest_rate', 0))}
minimumTenure: {customer_data.get('minimumtenure', '')} months
maximumTenure: {customer_data.get('maximumtenure', '')} months
Monthly EMI: {format_currency(customer_data.get('emi_amount', 0))}
Processing Fee: {format_currency(customer_data.get('processing_fee', 0))}
Foreclosure Charges: {format_currency(customer_data.get('foreclosure_charges', 0))}
APR: {customer_data.get('apr', '')}
Application Link: {customer_data.get('application_link', '')}
"""

    instructions = f"""You are a Professional and empathetic assistant from a bank, helping existing customers understand and explore their personal loan offers.

## Objective:
Gently nudge eligible customers to consider taking a loan. If they show interest, help them with details like amount, interest rate, minimum and maximum tenure, and process or terms related to loans. If they have concerns, listen patiently and resolve them. Also please only answer about questions related to Kotak peresonal loan if any other question is asked simply reply in a gently way that i am only trained to answer personal loan related questions.

## Tone:
- Calm, relatable, and helpful — like a trusted bank advisor or friend.
- Reply in a language which customer is questioning
- Encourage questions, resolve doubts.

## Behavioral Guidelines:
- Use the provided tools to access customer information and perform calculations.
- Answer all questions related to personal loan
- Do not hard-sell — focus on resolving confusion or hesitation.
- Avoid commands or salesy language.
- Keep replies conversational and end with a question when appropriate.
- Don't use emojis
- Always use tools to get accurate, up-to-date information.
- Maintain context from previous conversations in the session.

## Customer Context:
{customer_context}

## Available Tools:
- get_customer_details: Get detailed customer information
- calculate_emi: Calculate EMI for different loan amounts and tenures
- calculate_dynamic_pricing: Reduce loan interest and offer better loan
- calculate_loan_savings: Calculate savings with prepayment or different tenure
"""

    logger.info(f"Available customer context: {customer_context}")
    # Create the agent using the correct SDK pattern with imported tools
    agent = Agent(
        name="Loan Re-engagement Agent",
        instructions=instructions,
        model=OPENAI_MODEL,
        tools=LOAN_TOOLS
    )

    return agent


def _get_timestamp() -> str:
    """Get current timestamp."""
    from datetime import datetime
    return datetime.now().isoformat()


def get_conversation_summary(session_history: Dict[str, Any]) -> str:
    """
    Generate a summary of the conversation for analytics or handoff.

    Args:
        session_history: Session history dictionary

    Returns:
        Conversation summary
    """
    try:
        messages = session_history.get('messages', [])
        interaction_count = session_history.get('interaction_count', 0)
        preferences = session_history.get('customer_preferences', {})

        summary = f"""
Conversation Summary:
- Total Interactions: {interaction_count}
- Customer Preferences: {preferences}
- Last Interaction: {session_history.get('last_interaction', 'N/A')}
- Message Count: {len(messages)}
"""
        return summary

    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return "Unable to generate conversation summary."


def run_with_event_loop(coro):
    """
    Safely run async coroutine in Streamlit environment.

    Args:
        coro: Coroutine to run

    Returns:
        Result of the coroutine
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If there's a running loop, we need to run in a thread
            import concurrent.futures
            import threading

            def run_in_thread():
                # Create a new event loop for this thread
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


class StreamlitLoanReengagementRunner:
    """Custom runner for the loan re-engagement agent with Streamlit integration."""

    def __init__(self, customer_id: Optional[str] = None):
        """Initialize with loan re-engagement agent."""
        self.customer_data = _load_customer_data(customer_id)
        self.agent = create_loan_reengagement_agent(self.customer_data)
        logger.info("Agentic Loan Re-engagement Bot initialized for Streamlit")

    async def _process_async(self, user_message: str, session_history: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Internal async processing method."""
        try:
            # Store customer data in session state for tools to access
            if hasattr(st, 'session_state'):
                st.session_state.customer_data = self.customer_data

            # Build conversation input from session history
            conversation_input = []

            # Add previous messages to conversation context
            for msg in session_history.get('messages', []):
                if msg.get('role') == 'user':
                    conversation_input.append({"role": "user", "content": msg['content']})
                elif msg.get('role') == 'assistant':
                    conversation_input.append({"role": "assistant", "content": msg['content']})

            if conversation_input:
                conversation_input.append({"role": "user", "content": user_message})
                result = await Runner.run(self.agent, conversation_input)
            else:
                # First message, use string input
                result = await Runner.run(self.agent, user_message)

            # Extract the response text
            response_text = str(result.final_output)

            # Update session history
            session_history['messages'].extend([
                {'role': 'user', 'content': user_message, 'timestamp': _get_timestamp()},
                {'role': 'assistant', 'content': response_text, 'timestamp': _get_timestamp()}
            ])

            # Update interaction metadata
            session_history['interaction_count'] = session_history.get('interaction_count', 0) + 1
            session_history['last_interaction'] = _get_timestamp()

            # Extract preferences from user message
            # _update_customer_preferences(user_message, session_history)

            return response_text, session_history

        except Exception as e:
            logger.error(f"Error in async processing: {str(e)}")
            raise

    def process_with_history(self,
                             user_message: str,
                             session_history: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Process user message with session history for Streamlit integration (sync version).

        Args:
            user_message: Current user message
            session_history: Dictionary containing conversation history from Streamlit session

        Returns:
            Tuple of (response_message, updated_session_history)
        """
        try:
            # Initialize session history if None
            if session_history is None:
                session_history = {
                    'messages': [],
                    'customer_preferences': {},
                    'interaction_count': 0,
                    'last_interaction': None,
                    'session_start': _get_timestamp(),
                    'tools_used': [],
                    'conversation_topics': []
                }

            # Run the async processing with proper event loop handling
            response_text, updated_history = run_with_event_loop(
                self._process_async(user_message, session_history)
            )

            return response_text, updated_history

        except Exception as e:
            logger.error(f"Error processing message with history: {str(e)}")
            error_response = "I apologize, but I'm having trouble processing your request right now. Please try again."

            # Still update session history even on error
            if session_history:
                session_history['messages'].extend([
                    {'role': 'user', 'content': user_message, 'timestamp': _get_timestamp()},
                    {'role': 'assistant', 'content': error_response, 'timestamp': _get_timestamp(), 'error': True}
                ])

            return error_response, session_history