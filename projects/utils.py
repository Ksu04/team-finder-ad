from django.core.paginator import Paginator


def paginate_queryset(queryset, request, items_per_page=12):
    """
    Универсальная функция для пагинации queryset.

    Args:
        queryset: QuerySet для пагинации
        request: HTTP request объект (для получения page из GET)
        items_per_page: Количество элементов на странице (по умолчанию 12)

    Returns:
        page_obj: Объект страницы с пагинированными данными
    """
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj
