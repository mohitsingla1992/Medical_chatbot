import re
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import openai
# Initialize the LLM
llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")

def answer_medical_query(query):
    """Generate a detailed medical answer using LLM"""
    try:
        prompt = PromptTemplate(
            input_variables=["question"],
            template="You are a helpful and knowledgeable medical assistant. Answer the following question in detail:\n\n{question}"
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        answer = chain.run(question=query).strip()
        return answer
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "Sorry, I couldn't process your request."

def generate_followup_questions(question, answer):
    """Generate 5 follow-up questions based on original Q&A"""
    try:
        prompt = f"""
        Based on the following question and answer, generate exactly 5 relevant follow-up questions.
        Format strictly as a numbered list (1. ..., 2. ..., etc.) with no additional explanation.

        Question: {question}
        Answer: {answer}

        Follow-up Questions:
        1. """
        response = llm.invoke(prompt)
        content = response.content

        questions = []
        for line in content.split('\n'):
            match = re.match(r'^\d+\.\s+(.*?\?)', line.strip())
            if match:
                questions.append(match.group(1).strip())
        return questions[:5]
    except Exception as e:
        print(f"Error generating follow-ups: {e}")
        return [
            "What are the main symptoms?",
            "How is this condition diagnosed?",
            "What treatment options are available?",
            "Are there prevention strategies?",
            "What are the long-term effects?"
        ]

def chatbot_interaction(user_query):
    """Handles one round of question-answering and follow-up generation"""
    answer = answer_medical_query(user_query)
    followups = generate_followup_questions(user_query, answer)
    return {
        "answer": answer,
        "followup_questions": followups
    }

from openai import OpenAI

client = OpenAI()  # Automatically picks up API key from environment variable OPENAI_API_KEY

def ask_medical_question(query):
    response = client.chat.completions.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a helpful and accurate medical assistant."},
            {"role": "user", "content": query}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

import streamlit as st
from openai import OpenAI

# Initialize OpenAI client (make sure OPENAI_API_KEY is set in env)
client = OpenAI()

def get_medication_info(medication_name: str) -> str:
    prompt = f"""
You are a knowledgeable medical assistant.

Provide a detailed explanation about the medication named "{medication_name}". Include:

- What it is used for
- Typical dosage
- Common side effects
- Precautions and warnings
- Any other important information patients should know

Answer in clear, simple language suitable for patients.
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful and accurate medical assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# Streamlit UI for Medication Info tab
def get_medication_info(medication_name: str) -> dict:
    prompt = f"""
You are a medical assistant. Give detailed and structured information for the medication named "{medication_name}".

Respond in the following structured format:

1. **Purpose:** What is it used for?
2. **Dosage:** Typical dosage for adults and children.
3. **Side Effects:** Common and serious side effects.
4. **Precautions:** Any warnings or precautions.
5. **Other Information:** Storage, interactions, and additional guidance.

Be clear, concise, and easy to understand for patients.
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful and structured medical assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


# Example usage within your multi-tab app
# with tabs[4]:  # If you have a fifth tab, or add it as you like
#     medication_info_tab()

# Example usage
if __name__ == "__main__":
    user_question = "What are the symptoms of gestational diabetes?"
    result = chatbot_interaction(user_question)
    
    print("Answer:\n", result["answer"])
    print("\nFollow-up Questions:")
    for q in result["followup_questions"]:
        print("-", q)
