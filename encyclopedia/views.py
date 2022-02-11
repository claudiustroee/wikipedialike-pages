from django.forms import fields
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

from . import util
import markdown2
import secrets

class NewEntryForm(forms.Form):
    title = forms.CharField(label = "Entry title", widget = forms.TextInput(attrs={'class' : 'form-control col-md-8 col-lg-8'}))
    content = forms.CharField(widget = forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows' : 10}))
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/notfound.html", {
            "entrytitle": entry
        })
    else:
        html = markdown2.markdown(entryPage)
        return render(request, "encyclopedia/entry.html", {
            "entrytitle": entry,
            "entry": html
        })

def newentry(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if(util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry':title}))
            else:
                return render(request, "encyclopedia/new_entry.html",{
                    "form": form,
                    "existing": True,
                    "entry": title
                })
        else:
            return render(request, "encyclopedia/new_entry.html",{
                "form": form,
                "existing": False
            })
    else:
        return render(request, "encyclopedia/new_entry.html",{
            "form": NewEntryForm(),
            "existing": False
        })

def edit(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/notfound.html", {
            "entrytitle": entry
        })
    else:
        form = NewEntryForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entryPage
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/new_entry.html", {
            "form": form,
            "edit": form.fields["edit"].initial,
            "entrytitle": form.fields["title"].initial
        })

def random(request):
    entries = util.list_entries()
    random_entry = secrets.choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={'entry':random_entry}))

def search(request):
    value = request.GET.get('q', '')
    entryPage = util.get_entry(value)
    if entryPage is not None:
        return HttpResponseRedirect(reverse("entry", kwargs={'entry':value}))
    else:
        subString_entries = []
        for entry in util.list_entries():
            if value.upper() in entry.upper():
                subString_entries.append(entry)
            

        return render(request, "encyclopedia/index.html",{
            "entries": subString_entries,
            "search": True,
            "value": value
        })