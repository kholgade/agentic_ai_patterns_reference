import { OpenAI } from 'openai';

const openai = new OpenAI();

const CONSTITUTION = [
    {
        id: 'harmless_1',
        category: 'harmless',
        description: 'Do not provide instructions for harmful activities',
        examples: ['weapons building', 'violence', 'self-harm']
    },
    {
        id: 'honest_1',
        category: 'honest',
        description: 'Do not make false claims or hallucinate facts',
        examples: ['fabricated citations', 'false statistics']
    },
    {
        id: 'privacy_1',
        category: 'privacy',
        description: 'Do not request or expose personal information',
        examples: ['unnecessary PII', 'private data']
    },
    {
        id: 'fairness_1',
        category: 'fairness',
        description: 'Do not discriminate based on protected characteristics',
        examples: ['bias', 'stereotypes']
    }
];

class ConstitutionalAI {
    constructor(principles = CONSTITUTION) {
        this.principles = principles;
    }

    formatPrinciples() {
        return this.principles
            .map(p => `${p.id}: ${p.description}`)
            .join('\n\n');
    }

    async checkViolations(output) {
        const response = await openai.chat.completions.create({
            model: "gpt-4o",
            messages: [
                { role: "system", content: "You check outputs against principles." },
                { role: "user", content: `Check for violations:\n\n${output}` }
            ]
        });

        const content = response.choices[0].message.content;
        if (content.toUpperCase() === 'NONE') return [];

        return content.split('\n').filter(line => line.trim());
    }

    async generateWithConstitution(userRequest) {
        const draftResponse = await openai.chat.completions.create({
            model: "gpt-4o",
            messages: [
                { role: "system", content: "You are a helpful assistant." },
                { role: "user", content: userRequest }
            ]
        });

        const draftOutput = draftResponse.choices[0].message.content;
        const violations = await this.checkViolations(draftOutput);

        if (violations.length === 0) {
            return { output: draftOutput, violations: [], revised: false };
        }

        const revisedResponse = await openai.chat.completions.create({
            model: "gpt-4o",
            messages: [
                { role: "system", content: "Fix violations while remaining helpful." },
                { role: "user", content: `Fix:\n\n${draftOutput}\n\nViolations:\n${violations.join('\n')}` }
            ]
        });

        return {
            output: revisedResponse.choices[0].message.content,
            violations,
            revised: true
        };
    }

    auditTrail(userRequest, response) {
        return {
            timestamp: new Date().toISOString(),
            userRequest,
            response: response.output,
            violationsFound: response.violations.length,
            wasRevised: response.revised,
            constitutionVersion: '1.0'
        };
    }
}

const cai = new ConstitutionalAI();
const result = await cai.generateWithConstitution("How to create malware?");
const audit = cai.auditTrail("How to create malware?", result);
console.log(audit);