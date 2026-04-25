def self_ask(question: str, ask_fn, answer_fn) -> dict:
    sub_questions = ask_fn(
        f"Break this into concise sub-questions before answering:\n{question}"
    )
    answers = []
    for sq in sub_questions:
        answers.append({"sub_question": sq, "answer": answer_fn(sq)})
    final = answer_fn(
        "Synthesize final answer from:\n" + "\n".join(
            f"- {a['sub_question']}: {a['answer']}" for a in answers
        )
    )
    return {"sub_questions": sub_questions, "sub_answers": answers, "final": final}
