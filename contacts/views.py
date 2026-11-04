from django.forms import modelform_factory
from django.http import HttpResponse, HttpResponseBadRequest, QueryDict
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from main.models import Contact

ContactForm = modelform_factory(Contact, fields=("name", "email", "phone"))


@require_GET
def contact_list(request):
    return render(request, "contacts/index.html", {"contacts": Contact.objects.order_by("pk")})


@require_GET
def contact_search(request):
    contacts = Contact.objects.filter(name__icontains=request.GET.get("q", "")).order_by("pk")
    return render(request, "contacts/_contact_rows.html", {"contacts": contacts})


@require_POST
def contact_add(request):
    form = ContactForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest(form.errors.as_text(), content_type="text/plain")
    return render(request, "contacts/_contact_added.html", {"contact": form.save()})


@require_GET
def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, "contacts/_contact_edit_row.html", {"contact": contact})


@require_GET
def contact_row(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, "contacts/_contact_row.html", {"contact": contact})


@require_http_methods(["PUT"])
def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    form = ContactForm(QueryDict(request.body), instance=contact)
    if not form.is_valid():
        return HttpResponseBadRequest(form.errors.as_text(), content_type="text/plain")
    return render(request, "contacts/_contact_row.html", {"contact": form.save()})


@require_http_methods(["DELETE"])
def contact_delete(request, pk):
    get_object_or_404(Contact, pk=pk).delete()
    return HttpResponse("")
