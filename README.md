# Loan Re-engagement Bot

This application uses OpenAI's GPT model to create an intelligent loan re-engagement system that helps banks interact with customers about their pre-approved loan offers.

## Features

- Reads customer data from Excel files
- Uses OpenAI's GPT model for natural conversations
- Maintains a friendly and empathetic tone
- Supports Hinglish (Hindi in English script) conversations
- Provides personalized responses based on customer data

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Prepare your customer data Excel file with the following columns:
- name
- loan_offer
- interest_rate
- tenure
- emi_amount
- processing_fee
- foreclosure_charges
- offer_expiry
- purpose
- application_link

## Usage

1. Place your customer data Excel file in the project directory
2. Update the `excel_path` in `loan_reengagement.py` to point to your Excel file
3. Run the application:
```bash
python loan_reengagement.py
```

4. Start interacting with the bot. Type 'quit' to exit the conversation.

## Example Conversation

```
Customer: Hi, I received a loan offer but I'm not sure if I should take it.
Bot: Hi! I understand your hesitation. Would you like to know more about the benefits and terms of your pre-approved loan? 😊

Customer: Yes, please tell me more about the EMI.
Bot: Your monthly EMI would be ₹23,000, which is quite manageable. Would you like to know how we calculated this? 🤔
```

## Notes

- The bot is designed to be non-pushy and focuses on resolving customer concerns
- Responses are kept short and conversational
- The system uses customer context to provide personalized responses
- Emojis are used to add warmth to the conversation# Anaya
