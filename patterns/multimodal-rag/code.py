from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain.retrievers.multi_vector import MultiVectorRetriever
from PIL import Image
import os
from typing import List, Union

class MultimodalRAG:
    def __init__(
        self,
        text_model="text-embedding-3-small",
        vision_model="openai/clip-vit-large-patch14"
    ):
        self.text_embeddings = OpenAIEmbeddings(model=text_model)
        self.vectorstore = Chroma(collection_name="multimodal", embedding_function=self.text_embeddings)
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

        try:
            from transformers import CLIPProcessor, CLIPModel
            self.clip_model = CLIPModel.from_pretrained(vision_model)
            self.clip_processor = CLIPProcessor.from_pretrained(vision_model)
        except ImportError:
            self.clip_model = None
            print("CLIP not available, installing transformers...")

    def load_image(self, image_path: str) -> Image.Image:
        return Image.open(image_path).convert("RGB")

    def embed_image(self, image_path: str) -> List[float]:
        image = self.load_image(image_path)
        inputs = self.clip_processor(images=image, return_tensors="pt")
        with Image.open(image_path) as img:
            vision_features = self.clip_model.get_image_features(**inputs)
        return vision_features.detach().numpy().flatten().tolist()

    def embed_text(self, text: str) -> List[float]:
        return self.text_embeddings.embed_query(text)

    def embed_audio(self, audio_path: str) -> List[float]:
        import torch
        from transformers import Wav2Vec2Processor, Wav2Vec2Model

        processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
        model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")

        import libros
        audio, sr = libros.load(audio_path, sr=16000)
        inputs = processor(audio, return_tensors="pt", sampling_rate=sr)
        features = model(**inputs).last_hidden_state.mean(dim=1)

        return features.detach().numpy().flatten().tolist()

    def transcribe_audio(self, audio_path: str) -> str:
        from transformers import WhisperProcessor, WhisperForConditionalGeneration
        import libros

        processor = WhisperProcessor.from_pretrained("openai/whisper-small")
        model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

        audio, sr = libros.load(audio_path, sr=16000)
        inputs = processor(audio, return_tensors="pt", sampling_rate=sr)
        forced_decoder_ids = processor.get_decoder_prompt_ids(language="en", task="transcribe")
        generated_ids = model.generate(inputs, forced_decoder_ids=forced_decoder_ids)
        transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)

        return transcription[0]

    def index_document(
        self,
        content: str,
        modality: str,
        source_path: str = None,
        metadata: dict = None
    ):
        if modality == "text":
            embedding = self.embed_text(content)
        elif modality == "image":
            embedding = self.embed_image(source_path) if source_path else self.embed_text(content)
        elif modality == "audio":
            transcription = self.transcribe_audio(source_path) if source_path else content
            embedding = self.embed_text(transcription)
        else:
            embedding = self.embed_text(content)

        doc_metadata = {
            "modality": modality,
            "source_path": source_path,
            **(metadata or {})
        }

        doc = Document(page_content=content, metadata=doc_metadata)
        self.vectorstore.add_documents([doc], embeddings=[embedding])

    def index_multimodal_folder(self, folder_path: str):
        for root, _, files in os.walk(folder_path):
            for file in files:
                filepath = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()

                if ext in [".txt", ".md", ".pdf", ".docx"]:
                    with open(filepath) as f:
                        content = f.read()
                    self.index_document(content, "text", filepath)

                elif ext in [".jpg", ".jpeg", ".png", ".gif"]:
                    from PIL import Image
                    img = Image.open(filepath)
                    self.index_document(
                        f"Image: {file} (size: {img.size})",
                        "image",
                        filepath,
                        {"description": f"Image file {file}"}
                    )

                elif ext in [".mp3", ".wav", ".m4a"]:
                    transcription = self.transcribe_audio(filepath)
                    self.index_document(transcription, "audio", filepath)

    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        query_embedding = self.embed_text(query)
        results = self.vectorstore.similarity_search_by_vector(query_embedding, k=k)
        return results

    async def answer_multimodal(self, query: str) -> str:
        docs = self.retrieve(query, k=5)

        context = "Retrieved Context:\n\n"
        for i, doc in enumerate(docs, 1):
            modality = doc.metadata.get("modality", "unknown")
            context += f"[{i}] {modality.upper()}:\n{doc.page_content}\n"
            if doc.metadata.get("source_path"):
                context += f"Source: {doc.metadata['source_path']}\n"
            context += "\n"

        prompt = f"""Based on the following retrieved context from multiple modalities,
answer the question thoroughly. Reference specific sources and modalities.

Context:
{context}

Question: {query}

Answer:"""

        response = await self.llm.ainvoke(prompt)
        return response.content

mmrag = MultimodalRAG()
mmrag.index_multimodal_folder("./multimodal_knowledge_base")
answer = await mmrag.answer_multimodal(
    "What safety equipment is required in the factory floor?"
)