import OpenAI from 'openai';

class OutputParser {
  constructor(schema) {
    this.schema = schema;
    this.client = new OpenAI();
  }

  extractJSON(text) {
    // Try to find JSON in code blocks or plain
    const patterns = [
      /```json\s*([\s\S]*?)\s*```/,
      /```\s*([\s\S]*?)\s*```/,
      /(\{[\s\S]*\})/
    ];

    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match) {
        try {
          return JSON.parse(match[1] || match[0]);
        } catch (e) {
          continue;
        }
      }
    }
    return null;
  }

  async parse(text) {
    // Try direct extraction first
    let data = this.extractJSON(text);
    if (data) {
      return { success: true, data, strategy: 'regex' };
    }

    // Try key-value parsing
    const kvPattern = /(\w+):\s*([^\n]+)/g;
    let match;
    const parsed = {};
    while ((match = kvPattern.exec(text)) !== null) {
      parsed[match[1].trim()] = match[2].trim();
    }
    if (Object.keys(parsed).length > 0) {
      return { success: true, data: parsed, strategy: 'kv' };
    }

    // Final fallback: LLM assisted
    const prompt = `Extract structured data from this output.
    
Output:
${text}

Schema:
${JSON.stringify(this.schema, null, 2)}

Return valid JSON matching the schema. If extraction fails, return:
{"error": "Could not extract", "partial": {...}}
`;

    const response = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: prompt }],
      response_format: { type: 'json_object' },
      temperature: 0
    });

    try {
      const data = JSON.parse(response.choices[0].message.content);
      if (data.error) {
        return { 
          success: false, 
          error: data.error, 
          partial: data.partial,
          strategy: 'llm' 
        };
      }
      return { success: true, data, strategy: 'llm' };
    } catch (e) {
      return { success: false, error: e.message, strategy: 'llm' };
    }
  }
}