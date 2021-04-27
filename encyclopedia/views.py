import random
from django import forms
from django.shortcuts import render
from . import util
import markdown2

class Search(forms.Form):
    search = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Search Encyclopedia'}))

class NewPage(forms.Form):
    pagetitle = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Enter Markdown Content.'}))
    
class EditPage(forms.Form):
    content = forms.CharField(widget=forms.Textarea())

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(), "form": Search()
    })

def entry(request, title):
    entries = util.list_entries()
    if title in entries:
        page = util.get_entry(title)
        pageconvert = markdown2.markdown(page)
        return render(request, "encyclopedia/title.html", {
            "title": title, "content": pageconvert, "form": Search()
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })

def search(request):
    if request.method == "GET":
        form = Search(request.GET)
        entries_found = []
        all_entries = util.list_entries()  
        if form.is_valid():
            search = form.cleaned_data["search"].lower()
    
            for i in all_entries:
                if search.lower() == i.lower():
                    page = util.get_entry(i)
                    pageconvert = markdown2.markdown(page)
                    return render(request, "encyclopedia/title.html", {
                        "title": i, "content": pageconvert, "form": Search()
                    })
                if search.lower() in i.lower():
                    entries_found.append(i)
            return render(request, "encyclopedia/search.html", {
                "results" : entries_found, "search": search, "form": Search()
            })
    return render(request, "encyclopedia/search.html", {
        "results": "", "search":"","form": Search()
    })
    
def new(request):
    if request.method == "GET":
        createpage = NewPage(request.GET)
        return render(request, "encyclopedia/new.html", {
            "newpage": NewPage(), "form":Search()
        } )
    else:
        createpage = NewPage(request.POST)
        if createpage.is_valid():
            title = createpage.cleaned_data["pagetitle"]
            body = createpage.cleaned_data["content"]

            entries = util.list_entries()
            for name in entries:
                if title.lower() == name.lower():
                    return render(request, "encyclopedia/error.html", {
                    "message": f"Page with title {title} already exists."
                })
                else:
                    util.save_entry(title, body)
                    return entry(request,title)
        else:
            return render(request, "encyclopedia/new.html", {
                "newpage": NewPage(), "form": Search()
            })

def edit(request, title):
    if request.method == "GET":
        page = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": title, "edit": EditPage(initial={'textarea':page})
        })
    else:
        form = EditPage(request.POST)
        if form.is_valid():
            textarea = form.cleaned_data["textarea"]
            util.save_entry(title,textarea)
            return entry(request,title)


def randompage(request):
    return entry(request, random.choice(util.list_entries()))