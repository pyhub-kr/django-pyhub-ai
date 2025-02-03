=======================
Document 추상화 모델
=======================


여러 Document 모델을 둘려면?
=================================

``PaikdabangMenuDocument`` 모델은 빽다방 메뉴 데이터를 저장하고 임베딩하는 모델입니다.
그런데, ``page_content``, ``metadata``, ``embedding`` 필드 등
여러 Document 모델에서 공통적으로 사용되는 필드로만 구성되어있습니다.
빽다방 관련된 부분은 모델명 밖에 없죠.
추가로 ``StarbucksMenuDocument`` 모델을 만들려면 ``PaikdabangMenuDocument``
모델 코드를 복사&붙여넣기 하기보다, 장고의 추상화 모델 클래스를 상속받아 구현하시면
코드 중복없이 간결하게 여러 ``Document`` 모델을 정의하실 수 있게 됩니다.

기존 ``PaikdabangMenuDocument`` 클래스의 이름은 ``Document``\로 변경하고,
``PaikdabangMenuDocumentQuerySet`` 클래스의 이름은 ``DocumentQuerySet``\로 변경합니다.
그리고 ``Document`` 클래스는 ``Meta.abstract = True`` 설정으로 추상화 클래스로 선언하고
``Meta.indexes`` 속성은 제거합니다.
인덱스 정책은 모델마다 달라질 수 있고, 각 인덱스 ``name``\은
유일한 이름으로 지정되어야 하기에 추상화 클래스에서는 지정할 수 없고,
상속받은 모델에서 인덱스를 직접 정의하도록 하겠습니다.

.. code-block:: python
    :linenos:
    :caption: ``chat/models.py``
    :emphasize-lines: 2,5,9,12-13,15-24

    # class PaikdabangMenuDocumentQuerySet(models.QuerySet):
    class DocumentQuerySet(models.QuerySet):
        ...

        async def search(self, question: str, k: int = 4) -> List["Document"]:
            ...

    # class PaikdabangMenuDocument(LifecycleModelMixin, models.Model):
    class Document(LifecycleModelMixin, models.Model):
        ...

        class Meta:
            abstract = True

            # 인덱스는 추상화 클래스가 아닌 실제 모델에서 정의해야만 합니다.
            # indexes = [
            #     HnswIndex(
            #         name="paikdabang_menu_doc_idx",
            #         fields=["embedding"],
            #         m=16,
            #         ef_construction=64,
            #         opclasses=["vector_cosine_ops"],
            #     ),
            # ]

이제 ``PaikdabangMenuDocument`` 모델과 ``StarbucksMenuDocument`` 모델은 ``Document`` 모델 상속 만으로 아래와 같이 손쉽게 정의할 수 있게 됩니다.
``PaikdabangMenuDocument`` 모델의 인덱스를 복사해서 인덱스명만 변경해주겠습니다.

.. code-block:: python
    :linenos:
    :caption: ``chat/models.py``
    :emphasize-lines: 1,5,13,17

    class PaikdabangMenuDocument(Document):
        class Meta:
            indexes = [
                HnswIndex(
                    name="paikdabang_menu_doc_idx",
                    fields=["embedding"],
                    m=16,
                    ef_construction=64,
                    opclasses=["vector_cosine_ops"],
                ),
            ]

    class StarbucksMenuDocument(Document):
        class Meta:
            indexes = [
                HnswIndex(
                    name="starbucks_menu_doc_idx",
                    fields=["embedding"],
                    m=16,
                    ef_construction=64,
                    opclasses=["vector_cosine_ops"],
                ),
            ]

마이그레이션을 해주시면 ``StarbucksMenuDocument`` 모델에 대한 테이블도 생성되고,
``DocumentQuerySet`` 클래스에서 정의한 ``search`` 메서드를 통해
질문과 유사한 문서 검색을 할 수 있게 됩니다.



모델 인덱스에 맞춰 검색하기
================================

인덱스를 정의할 때, 인덱스 생성 시에 사용할 벡터 연산 클래스를 지정합니다.
``pgvector`` 확장에서 지원하는 벡터 연산 목록은 :doc:`/rag-02/pgvector-model` 문서에 정리되어있습니다.

.. code-block:: python
    :caption: ``chat/models.py``
    :linenos:
    :emphasize-lines: 9

    class PaikdabangMenuDocument(Document):
        class Meta:
            indexes = [
                HnswIndex(
                    name="paikdabang_menu_doc_idx",
                    fields=["embedding"],
                    m=16,
                    ef_construction=64,
                    opclasses=["vector_cosine_ops"],
                ),
            ]

코사인 거리 연산 클래스는 ``vector_cosine_ops``\이고 ``DocumentQuerySet``\에서 ``search`` 메서드에서는
인덱스를 활용할 수 있도록 ``CosineDistance`` 데이터베이스 함수를 통해 쿼리를 작성해야만 합니다.

인덱스 정의는 ``Document`` 모델 클래스에서 이뤄지고, 검색 쿼리는 ``DocumentQuerySet.search`` 메서드에서 이뤄집니다.
``search`` 메서드를 개선하여 ``Document`` 모델의 인덱스 선언에 맞춰 쿼리를 작성할 수 있도록 하겠습니다.
``pgvector`` 확장을 통해 여러 벡터 연산 클래스가 지원되지만, 본 튜토리얼에서는
코사인 거리와 L2 거리 연산 클래스만 구현했습니다.

.. code-block:: python
    :linenos:
    :caption: ``chat/models.py``
    :emphasize-lines: 12,14-18,19-23

    from django.core.exceptions import ImproperlyConfigured
    from django.db.models import Index
    from pgvector.django import CosineDistance, L2Distance

    class DocumentQuerySet(models.QuerySet):
        # ...

        async def search(self, question: str, k: int = 4) -> List["Document"]:
            question_embedding: List[float] = await self.model.aembed(question)

            qs = None
            index: Index
            for index in self.model._meta.indexes:
                if "embedding" in index.fields:
                    if "vector_cosine_ops" in index.opclasses:
                        qs = (qs or self).annotate(
                            distance=CosineDistance("embedding", question_embedding)
                        )
                        qs = qs.order_by("distance")
                    elif "vector_l2_ops" in index.opclasses:
                        qs = (qs or self).annotate(
                            distance=L2Distance("embedding", question_embedding)
                        )
                        qs = qs.order_by("distance")
                    else:
                        raise NotImplementedError(f"{index.opclasses}에 대한 검색 구현이 필요합니다.")

            if qs is None:
                raise ImproperlyConfigured(f"{self.model.__name__} 모델에 embedding 필드에 대한 인덱스를 추가해주세요.")

            return await sync_to_async(list)(qs[:k])


make_vector_store 명령 개선
================================

기존의 ``make_vector_store`` 명령은 ``PaikdabangMenuDocument`` 모델에 대한 벡터 저장소를 생성하는 명령이었습니다.
이제 ``Document`` 모델 상속 만으로 손쉽게 새로운 문서 모델을 만들 수 있으니,
``make_vector_store`` 명령도 다양한 문서 모델을 지원하도록 개선해보겠습니다.

#. ``model`` 인자로 저장할 Document 모델 경로를 ``앱이름.모델명`` 포맷으로 지정합니다.
#. ``get_model_class`` 메서드는 모델 경로를 받아 모델 클래스를 임포트하고, 모델 클래스의 유효성을 검증한 뒤에, 모델 클래스를 반환합니다.
#. ``handle`` 메서드에서는 ``model`` 문자열 인자로 모델 클래스를 조회하고, 이를 활용합니다.

.. code-block:: python
    :caption: ``chat/management/commands/make_vector_store.py``
    :linenos:
    :emphasize-lines: 16-20,31-44,47,50,58,64

    import sys
    from pathlib import Path
    from typing import Type

    from django.core.management import BaseCommand
    from django.db.models import Model
    from django.utils.module_loading import import_string
    from tqdm import tqdm

    from chat import rag
    from chat.models import Document


    class Command(BaseCommand):
        def add_arguments(self, parser):
            parser.add_argument(
                "model",
                type=str,
                help="저장할 Document 모델 경로 (예: 'chat.PaikdabangMenuDocument')",
            )
            parser.add_argument(
                "txt_file_path",
                type=str,
                help="VectorStore로 저장할 원본 텍스트 파일 경로",
            )

        def print_error(self, msg: str) -> None:
            self.stdout.write(self.style.ERROR(msg))
            sys.exit(1)

        def get_model_class(self, model_path: str) -> Type[Model]:
            try:
                module_name, class_name = model_path.rsplit(".", 1)
                dotted_path = ".".join((module_name, "models", class_name))
                ModelClass: Type[Model] = import_string(dotted_path)
            except ImportError as e:
                self.print_error(f"{model_path} 경로의 모델을 임포트할 수 없습니다. ({e})")

            if not issubclass(ModelClass, Document):
                self.print_error("Document 모델을 상속받은 모델이 아닙니다.")
            elif ModelClass._meta.abstract:
                self.print_error("추상화 모델은 사용할 수 없습니다.")

            return ModelClass

        def handle(self, *args, **options):
            model_name = options["model"]
            txt_file_path = Path(options["txt_file_path"])

            ModelClass = self.get_model_class(model_name)

            doc_list = rag.load(txt_file_path)
            print(f"loaded {len(doc_list)} documents")
            doc_list = rag.split(doc_list)
            print(f"split into {len(doc_list)} documents")

            new_doc_list = [
                ModelClass(
                    page_content=doc.page_content,
                    metadata=doc.metadata,
                )
                for doc in tqdm(doc_list)
            ]
            ModelClass.objects.bulk_create(new_doc_list)

이제 ``make_vector_store`` 명령에서 지식 데이터 파일 경로와 함께 모델 클래스 경로를 지정하여 벡터 저장소에 지식을 저장할 수 있게 됩니다.

.. code-block:: bash

    uv run python manage.py make_vector_store chat.PaikdabangMenuDocument  ./chat/assets/빽다방.txt


이후 튜토리얼에서는
=====================

``Document`` 모델마다 지식을 load/split하는 과정이 다를 텐데요.
이에 대해서는 이후 튜토리얼에서 다뤄보겠습니다.
