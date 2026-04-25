import OpenAI from 'openai';

const client = new OpenAI();

const QUALITY_DIMENSIONS = {
  ACCURACY: 'accuracy',
  RELEVANCE: 'relevance', 
  COHERENCE: 'coherence',
  HELPFULNESS: 'helpfulness',
  SAFETY: 'safety'
};

async function judgeOutput(output, criteria, context = null, model = 'gpt-4o') {
  const prompt = `You are an expert evaluator judging AI system outputs.

## Output to Evaluate:
${output}

## Evaluation Context:
${context || 'No additional context provided.'}

## Evaluation Criteria:
${criteria}

Before scoring, provide step-by-step reasoning for your evaluation.

## Scoring Rubric:
- 1-3: Poor - Significant issues present
- 4-6: Average - Some issues, acceptable quality
- 7-8: Good - Minor issues, solid quality
- 9-10: Excellent - No significant issues

## Output Format:
Provide your evaluation in this JSON format:
{
  "overall_score": <number>,
  "dimension_scores": [
    {"dimension": "<dimension>", "score": <number>, "reasoning": "<reasoning>"}
  ],
  "summary": "<brief summary>",
  "improvement_suggestions": ["<suggestion1>", "<suggestion2>"]
}

Ensure scores are integers between 1 and 10.`;

  const response = await client.chat.completions.create({
    model,
    messages: [{ role: 'user', content: prompt }],
    response_format: { type: 'json_object' },
    temperature: 0,
    max_tokens: 2000
  });

  return JSON.parse(response.choices[0].message.content);
}

async function selfJudgeWithRetry(generateFn, judgeCriteria, maxRetries = 2) {
  let bestOutput = await generateFn();
  let bestScore = await judgeOutput(bestOutput, judgeCriteria);
  
  for (let i = 0; i < maxRetries; i++) {
    if (bestScore.overall_score >= 7) break;
    
    const improvementPrompt = `
      Previous output received score ${bestScore.overall_score}/10.
      Issues: ${bestScore.summary}
      Suggestions: ${bestScore.improvement_suggestions.join(', ')}
      
      Please regenerate with improvements.
    `;
    
    bestOutput = await generateFn(improvementPrompt);
    bestScore = await judgeOutput(bestOutput, judgeCriteria);
  }
  
  return { output: bestOutput, score: bestScore };
}