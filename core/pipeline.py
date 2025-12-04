# nlp/pipeline.py

from core.entity_normalizer import EntityNormalizer


class NLPPipeline:
    def __init__(self):
        self.normalizer = EntityNormalizer()

    async def run(self, text: str):
        """
        أهم دالة:
        ترجع JSON فيه كل الكيانات المستخرجة
        """
        return await self.normalizer.parse_all(text)
