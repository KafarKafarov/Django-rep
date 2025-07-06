import os
import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UploadForm
from .models import Docs, UserToDocs, Cart, Price
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST

FASTAPI_URL = settings.FASTAPI_URL


@login_required
def list_docs(request):
    docs = []
    error = None
    try:
        resp = requests.get(f"{settings.FASTAPI_URL}/documents/", timeout=10)
        resp.raise_for_status()
        docs = resp.json()
    except Exception as e:
        error = f"Ошибка загрузки документов: {e}"

    return render(request, 'docs_app/list.html', {
        'docs': docs,
        'error': error,
        'fastapi_url': settings.FASTAPI_URL
    })


@login_required
def upload_doc(request):
    error = None
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            content = file.read()
            file.seek(0)

            try:
                resp = requests.post(
                    f"{FASTAPI_URL}/upload_doc",
                    files={'file': (file.name, content, file.content_type)},
                    timeout=10
                )
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        file_path = data.get('path')
                        if not file_path:
                            raise ValueError("Отсутствует путь к файлу в ответе")

                        file_name = os.path.basename(file_path)
                        doc = Docs.objects.create(
                            file_path=f'documents/{file_name}',
                            size_file=len(content) / 1024
                        )
                        UserToDocs.objects.create(user=request.user, doc=doc)

                        return redirect('docs_app:list_docs')
                    except Exception as e:
                        error = f"Ошибка обработки ответа: {e}"
                else:
                    try:
                        detail = resp.json().get('detail', resp.text)
                    except ValueError:
                        detail = resp.text
                    error = f"FastAPI error {resp.status_code}: {detail}"
            except requests.RequestException as e:
                error = f"Connection error: {e}"
        else:
            error = "Неверный формат данных."
    else:
        form = UploadForm()

    return render(request, 'docs_app/upload.html', {
        'form': form,
        'error': error
    })


@login_required
def analyse_doc(request):
    result = None
    error = None

    if request.method == 'POST':
        doc_id = request.POST.get('doc_id')
        if doc_id:
            try:
                resp = requests.post(f"{FASTAPI_URL}/doc_analyse/{doc_id}", timeout=10)
                if resp.status_code == 200:
                    try:
                        result = resp.json()
                    except ValueError:
                        result = resp.text
                else:
                    try:
                        detail = resp.json().get('detail', resp.text)
                    except ValueError:
                        detail = resp.text
                    error = f"FastAPI error {resp.status_code}: {detail}"
            except requests.RequestException as e:
                error = f"Connection error: {e}"
        else:
            error = "Введите корректный ID документа."

    return render(request, 'docs_app/analyse.html', {
        'result': result,
        'error': error
    })

@login_required
def get_text(request):
    text = None
    error = None
    if request.method == 'POST':
        doc_id = request.POST.get('doc_id')
        try:
            resp = requests.get(f"{FASTAPI_URL}/documents/{doc_id}/", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            text = data.get('text')
        except Exception as e:
            error = f"Ошибка получения текста: {e}"
    return render(request, 'docs_app/get_text.html', {'text': text, 'error': error})

@staff_member_required
def delete_doc(request):
    result = None
    error = None
    if request.method == 'POST':
        doc_id = request.POST.get('doc_id')
        try:
            resp = requests.delete(f"{FASTAPI_URL}/documents/{doc_id}", timeout=10)
            if resp.status_code in (200, 204):
                result = f"Документ {doc_id} удалён"
            else:
                error = f"Ошибка удаления: {resp.status_code} – {resp.text}"
        except Exception as e:
            error = f"Ошибка подключения: {e}"
    return render(request, 'docs_app/delete_doc.html', {'result': result, 'error': error})


@login_required
def cart_list(request):
    orders = Cart.objects.filter(user=request.user).order_by('-id')
    return render(request, 'docs_app/cart.html', {'orders': orders})


@require_POST
@login_required
def cart_add(request):
    doc_id = request.POST.get('doc_id')
    doc = get_object_or_404(Docs, pk=doc_id)

    ext = doc.file_path.name.split('.')[-1].lower()
    try:
        price_obj = Price.objects.get(file_type=ext)
        price = price_obj.price
    except Price.DoesNotExist:
        price = 1

    order_price = doc.size_file * price

    Cart.objects.create(user=request.user, doc=doc, order_price=order_price)
    return redirect('docs_app:cart_list')


@login_required
def cart_pay(request, pk):
    order = get_object_or_404(Cart, pk=pk, user=request.user)
    if not order.payment:
        order.payment = True
        order.save()
    return redirect('docs_app:cart_list')
