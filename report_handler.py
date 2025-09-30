from openai_llm import get_completion

def summarize_report(report_text):
    prompt = f"""
    You are a highly experienced medical doctor.
    Analyze and summarize the following medical report:

    {report_text}

    Then extract and list the following details:
    1. **Diagnosis**
    2. **Medications**
    3. **Do's** (positive actions the patient should take)
    4. **Don'ts** (actions the patient should avoid)
    5. **Lifestyle Changes** (diet, exercise, sleep, etc.)

    Provide the output in a clear structured format.
    """
    return get_completion(prompt)


