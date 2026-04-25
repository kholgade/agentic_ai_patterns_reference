from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class SelfRAGSystem:
    def __init__(self, model_name="togethercomputer/Reflector-7B"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.model.eval()

        self.special_tokens = {
            "retrieve": self.tokenizer.convert_tokens_to_ids("[RETRIEVE]"),
            "relevant": self.tokenizer.convert_tokens_to_ids("[ISREL]"),
            "supported": self.tokenizer.convert_tokens_to_ids("[ISSUP]"),
            "utility": self.tokenizer.convert_tokens_to_ids("[UTILITY]")
        }

    def format_instruction(self, query, documents=None):
        instruction = f"Question: {query}\n\n"
        if documents:
            for i, doc in enumerate(documents):
                instruction += f"Document [{i}]: {doc}\n"
        instruction += "Answer:"
        return instruction

    @torch.no_grad()
    def generate_with_reflection(self, query, retriever=None, max_new_tokens=500):
        text = self.format_instruction(query)
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

        output_tokens = []
        current_retriever = retriever

        for _ in range(max_new_tokens):
            outputs = self.model(**inputs)
            next_token = torch.argmax(outputs.logits[:, -1, :])

            token_str = self.tokenizer.decode([next_token.item()])
            output_tokens.append(next_token.item())

            if next_token.item() == self.special_tokens["retrieve"]:
                retrieved_docs = current_retriever.get_relevant_documents(
                    self.tokenizer.decode(inputs["input_ids"][0])
                )
                doc_context = " ".join([d.page_content for d in retrieved_docs])
                new_text = text + "".join(output_tokens) + f"\nRetrieved: {doc_context}\n"
                inputs = self.tokenizer(new_text, return_tensors="pt").to(self.model.device)
                output_tokens = []
                continue

            inputs = torch.cat([
                inputs["input_ids"],
                next_token.unsqueeze(0).unsqueeze(0)
            ], dim=1)

            if next_token.item() in [self.tokenizer.eos_token_id, self.tokenizer.pad_token_id]:
                break

        return self.tokenizer.decode(output_tokens)

    def parse_reflection_tokens(self, output_text):
        reflections = {
            "retrievals": [],
            "relevance": [],
            "support": [],
            "utilities": []
        }

        tokens_map = {
            "[RETRIEVE]": "retrievals",
            "[ISREL]": "relevance",
            "[ISSUP]": "support",
            "[UTILITY]": "utilities"
        }

        import re
        for match in re.finditer(r'\[(RETRIEVE|ISREL|ISSUP|UTILITY)[^\]]*\]', output_text):
            token_type = match.group(1).lower()
            if token_type in reflections:
                reflections[token_type].append(match.group(0))

        return reflections

rag = SelfRAGSystem()
result = rag.generate_with_reflection(
    "Explain quantum entanglement",
    retriever=vectorstore.as_retriever()
)
reflections = rag.parse_reflection_tokens(result)
print(f"Response: {result}")
print(f"Retrievals triggered: {len(reflections['retrievals'])}")