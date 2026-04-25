import OpenAI from 'openai';

const client = new OpenAI();

const userProfileSchema = {
  type: "object",
  properties: {
    user_id: { type: "string", description: "Unique user identifier" },
    name: { type: "string", minLength: 1, maxLength: 100 },
    email: { type: "string", pattern: "^[\\w.-]+@[\\w.-]+\\.\\w+$" },
    roles: { type: "array", items: { type: "string" }, default: [] },
    active: { type: "boolean", default: true }
  },
  required: ["user_id", "name", "email"]
};

async function generateStructuredOutput(prompt, schema) {
  const systemPrompt = `You are a data extraction assistant.
Output ONLY valid JSON that matches this schema:
${JSON.stringify(schema, null, 2)}
Do not include any explanation or markdown. Only output valid JSON.`;

  const response = await client.chat.completions.create({
    model: "gpt-4o-2024-08-06",
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: prompt }
    ],
    response_format: { type: "json_object" },
    temperature: 0,
    max_tokens: 2000
  });

  try {
    return JSON.parse(response.choices[0].message.content);
  } catch (error) {
    throw new Error(`Failed to parse output: ${error.message}`);
  }
}

// Example: Using tool calling for guaranteed structure
async function generateWithToolCalling(userData) {
  const response = await client.chat.completions.create({
    model: "gpt-4o-2024-08-06",
    messages: [
      { 
        role: "system", 
        content: "Extract user information from the provided text." 
      },
      { 
        role: "user", 
        content: `Extract: ${userData}` 
      }
    ],
    tools: [{
      type: "function",
      function: {
        name: "extract_user",
        description: "Extract user profile information",
        parameters: userProfileSchema
      }
    }],
    tool_choice: { type: "function", function: { name: "extract_user" } }
  });

  const toolCall = response.choices[0].message.tool_calls[0];
  return JSON.parse(toolCall.function.arguments);
}