from django.shortcuts import render, HttpResponse, redirect
from django import forms 
from . import util
import secrets

class NewTaskForm(forms.Form):
    content=forms.CharField(label="New Content")
    title=forms.CharField(label="Title")


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request,title):
    markdown_content= util.get_entry(title)
    html_content = util.convert_markdown_to_html(markdown_content)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })

def search(request):
    entries= util.list_entries()
    if request.method == "POST":
        query = request.POST.get('query', '').strip()
        matching_entries = [entry for entry in entries if query.lower() in entry.lower()]
        
        for entry in entries:
            if query == entry.lower() or query==entry:
                return redirect('entry', title=query)
            
        if matching_entries:
            return render(request, "encyclopedia/search.html", {
                "query": query,
                "entries": matching_entries
            })
        else:
            return render(request, "encyclopedia/search.html", {
                "query": query
            })
    return redirect('index')

def new(request):
    return render(request, "encyclopedia/new.html")

def create(request):
    if request.method == "POST":
        form = NewTaskForm(request.POST)
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        if not title or not content:
            return render(request, "encyclopedia/new.html", {
                "error": "Both title and content are required!",
                "title": title,
                "content": content
            })
        
        if util.get_entry(title):
            return render(request, "encyclopedia/new.html", {
                "error": "An entry with this title already exists!",
                "title": title,
                "content": content
            })

        util.save_entry(title, content)
        
        return redirect('entry', title=title)
    
    return render(request, "encyclopedia/new.html" )

def edit(request, title):

    content = util.get_entry(title)

    if request.method == "POST":
        form = NewTaskForm(request.POST)
        updated_content = request.POST.get('content', '').strip()

        if not updated_content:
            return render(request, "encyclopedia/edit.html", {
                "error": "Content cannot be empty!",
                "content": content
            })
        
        util.save_entry(title, updated_content)
        
        return redirect('entry', title=title)
    
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content
    } )

def random(request):
    entries= util.list_entries()
    random_title= secrets.choice(entries)
    return redirect('entry', title= random_title )