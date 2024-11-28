class RawMarkdownSplitter:
    def __repr__(self) -> str:
        return 'RawMarkdownSplitter'
    
    def split(self, text):
        chunks = text.split('\n\n\n')
        i = 0
        while i < len(chunks):
            chunk = chunks[i].replace('\n', ' ')
            if len(chunk) > 512:
                del chunks[i]  # Remove the oversized chunk
                sub_chunks = self.split_into_sub_chunks(chunk)
                for sub_chunk in reversed(sub_chunks):
                    chunks.insert(i, sub_chunk)  # Insert each sub-chunk back at the original index
            else:
                i += 1  # Only increment if no deletion occurred
        return chunks

    def split_into_sub_chunks(self, chunk):
        paragraphs = chunk.split('.')
        sub_chunks = []
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                figures = self.extract_figures(paragraph)
                sub_chunks.append({
                    'text': paragraph,
                    'figures': figures
                })
        if not sub_chunks:
            return [{'text': chunk, 'figures': []}]
        start = 0
        while start < len(chunk):
            # End is start plus chunk size or end of string, whichever is smaller
            end = min(start + 512, len(chunk))
            sub_chunks.append(chunk[start:end])
            if end == len(chunk):
                break
            start = end - 128  # Move start for overlap
        return sub_chunks
    
    
def RegexSplitter(pattern):
    def split(self, text):
        return re.split(pattern, text)
    return split