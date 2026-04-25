export async function selfAsk(question, askFn, answerFn) {
  const subQuestions = await askFn(`Break into sub-questions:\n${question}`);
  const subAnswers = [];
  for (const sq of subQuestions) {
    subAnswers.push({ subQuestion: sq, answer: await answerFn(sq) });
  }
  const final = await answerFn(
    `Synthesize answer from:\n${subAnswers.map(a => `- ${a.subQuestion}: ${a.answer}`).join("\n")}`
  );
  return { subQuestions, subAnswers, final };
}
