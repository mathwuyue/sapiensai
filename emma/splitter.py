from pydantic import BaseModel
from typing import Optional, List
from llama_index.core import SimpleDirectoryReader
from docx import Document
import os
import uuid
from peewee import IntegrityError
from embedding import LocalEmbedding
import time
import hashlib
from PIL import Image
import io
from typing import List, Dict, Tuple
from docx.document import Document as _Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table, _Row
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

# load docs
class ChunkMeta(BaseModel):
    page_number: int
    start_pos: int
    end_pos: int
    embedding_model: str
    sentence_splitter: str

class VectorModel(BaseModel):
    doc_id: str
    text: str
    embedding: List[float]
    organization: str
    meta: ChunkMeta 
    
    
input_dir = 'data/test'

    
# load files
documents = []
vectors = []

for subdir, _, files in os.walk(input_dir):
    for file in files:
        if file.lower().endswith('.docx'):
            filepath = os.path.join(subdir, file)
            try:
                doc = Document(filepath)
                documents.append(doc)
            except Exception as e:
                print(f'Error loading {file}: {e}')


class DocChunker:
    def __init__(self, max_chunk_size: int = 256, overlap_size: int = 20):
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.image_dir = "images"
        os.makedirs(self.image_dir, exist_ok=True)
        
    def _save_image(self, image, doc_id: str) -> str:
        """Save image and return markdown reference"""
        image_data = image.blob
        image_hash = hashlib.md5(image_data).hexdigest()
        image_path = f"{self.image_dir}/{doc_id}_{image_hash}.png"
        
        with open(image_path, "wb") as f:
            f.write(image_data)
            
        return f"![image]({image_path})"

    def _table_to_markdown(self, table: Table) -> str:
        """Convert table to markdown format"""
        markdown = []
        
        # Headers
        headers = [cell.text.strip() for cell in table.rows[0].cells]
        markdown.append("| " + " | ".join(headers) + " |")
        markdown.append("| " + " | ".join(["---"] * len(headers)) + " |")
        
        # Data rows
        for row in table.rows[1:]:
            cells = [cell.text.strip() for cell in row.cells]
            markdown.append("| " + " | ".join(cells) + " |")
            
        return "\n".join(markdown)

    def _merge_chunks(self, chunks: List[str]) -> List[str]:
        """Merge text into chunks with overlap"""
        embedding_chunks = []
        text_chunks = []
        current_chunk = ''
        prev_chunk = ''
        current_text_chunk = {'page_number': 0, 'text': ''}
        for chunk in chunks:
            if current_chunk == '' and len(prev_chunk) > self.overlap_size:
                current_chunk = prev_chunk[-self.overlap_size:]
            current_chunk += chunk['text']
            if current_text_chunk['page_number'] == 0:
                current_text_chunk['page_number'] = chunk['page_number']
            # fixme: if the paragraph is too long, we need to split it
            if len(current_chunk) >= self.max_chunk_size:
                embedding_chunks.append(current_chunk)
                prev_chunk = current_chunk
                current_text_chunk['text'] = current_chunk + '\n\n' + '\n\n'.join(chunk['image']) + '\n\n'.join(chunk['table'])
                current_chunk = ''
                text_chunks.append(current_text_chunk)
                current_text_chunk = {'page_number': 0, 'text': ''}
        print(text_chunks)
        return embedding_chunks, text_chunks
    
    def _count_page_breaks(self, paragraph: Paragraph) -> int:
        """Count the number of page breaks in a paragraph."""
        page_break_count = 0
        page_break_count += len(paragraph.rendered_page_breaks)
        return page_break_count

    def process_document(self, doc: Document, doc_id: str) -> List[str]:
        raw_chunks = []
        page_number = 1
        
        for paragraph in doc.paragraphs:
            paragraph_chunk = {'image': [], 'table': [], 'text': '', 'page_number': page_number}
            # Check for images
            # for run in paragraph.runs:
            #     if run._r.get_or_add_drawing():
            #         for img in run._r.drawing.xpath('.//pic:pic//a:blip/@r:embed'):
            #             image = doc.part.related_parts[img.value]
            #             img_md = self._save_image(image, doc_id)
            #             paragraph_chunk["image"].append(img_md)
            #         continue
            
            # Check for tables
            if isinstance(paragraph._p.get_next(), CT_Tbl):
                table = paragraph._p.get_next()
                table_md = self._table_to_markdown(table)
                paragraph_chunk["table"].append(table_md)
                continue
                
            # Regular text
            text = paragraph.text.strip()
            if text:
                paragraph_chunk["text"] = text
                
            # Check for page breaks
            page_number += self._count_page_breaks(paragraph)
            raw_chunks.append(paragraph_chunk)
                
        # Merge chunks with overlap
        return self._merge_chunks(raw_chunks)


# split into chunks and get it page number
# def get_chunks_vector_storage(doc: Document, doc_item: _db.Document) -> List[VectorModel]:
#     chunker = DocChunker()
#     txt_chunks = chunker.process_document(doc, doc_item.doc_id)
#     page_number = 1
#     meta_chunks = []
    
#     for _ in txt_chunks:
#         meta = ChunkMeta(
#             page_number=page_number,
#             start_pos=0,
#             end_pos=len(_),
#             embedding_model="LocalEmbedding",
#             sentence_splitter="RawDocxSplitter"
#         )
#         meta_chunks.append(meta)
        
#     start = time.time()
#     vectors = LocalEmbedding().embeddings(inputs=txt_chunks)
#     print('Local Embedding: ', time.time() - start)
    
#     vector_items = [VectorModel(
#         doc_id=doc_item.doc_id,
#         text=i[0],
#         embedding=i[1],
#         organization=doc_item.organization,
#         meta=i[2]
#     ).model_dump() for i in zip(txt_chunks, vectors, meta_chunks)]
#     return vector_items


if __name__ == '__main__':
    chuncker = DocChunker()
    a = list(map(lambda x: chuncker.process_document(x, 'abc-122'), documents))
    # print(a)

