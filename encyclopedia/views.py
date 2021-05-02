from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from . import util
from django import forms
import re
import markdown2
from markdown2 import Markdown
import random
from django.shortcuts import redirect
from django.urls import reverse, resolve


class SearchForm(forms.Form):
    search = forms.CharField(label="")


class NewForm(forms.Form):
    title = forms.CharField(label="Title of Page")
    textarea = forms.CharField(widget=forms.Textarea, label="")


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": SearchForm()
    })


def get_page(request, name):
    page_details = util.get_entry(name)
    if not page_details:
        return render(request, "encyclopedia/apology.html", {
            "name": name
        })
    return render(request, "encyclopedia/wiki_page.html", {
        "name": name,
        "page_details": page_details,
        "search_form": SearchForm()
    })


def search(request):
    if request.method == "POST":
        print("inside search ")
        form = SearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data["search"]
            page_details = util.get_entry(data)
            if page_details:
                return render(request, "encyclopedia/wiki_page.html", {
                    "name": data,
                    "page_details": page_details,
                    "search_form": SearchForm()
                })
            if not page_details:
                regex = data
                matched_patterns = []
                entries = util.list_entries()
                for entry in entries:
                    match = re.search(regex, entry)
                    print(match)
                    if match != None:
                        print(entry)
                        print(match.group(0))
                        matched_patterns.append(entry)
                if len(matched_patterns) == 0:
                    return render(request, "encyclopedia/apology.html", {
                        "name": data,
                        "search_form": SearchForm()
                    })
                else:
                    return render(request, "encyclopedia/index.html", {
                        "entries": matched_patterns,
                        "search_form": SearchForm()
                    })


def new_page(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new_page.html", {
            "new_page_form": NewForm(),
            "search_form": SearchForm(),

        })
    elif request.method == "POST":
        form = NewForm(request.POST)
        if form.is_valid():
            found_page = False
            print("this is inside post")
            title = form.cleaned_data["title"]
            content = form.cleaned_data["textarea"]
            print(title)
            print(type(title))
            title_entries = util.list_entries()
            print(title_entries)
            for entry in title_entries:
                print(type(entry))
                print(entry)
                if title.lower() == entry.lower():
                    found_page = True
                    return render(request, "encyclopedia/new_page.html", {
                        "message": found_page,
                        "search_form": SearchForm(),
                        "page_name": title,
                        "new_page_form": NewForm(initial={'title': title, 'textarea': content})
                    })
            if found_page == False:
                markdown_content = markdown2.markdown(content)
                util.save_entry(title, markdown_content)
                return HttpResponseRedirect(reverse("wikis:get_page", kwargs={'name': title}))


def edit_page(request, name):
    if request.method == "GET":
        page_details = util.get_entry(name)
        edit_form = NewForm(initial={'title': name, 'textarea': page_details})
        print(edit_form)

        return render(request, "encyclopedia/edit_page.html", {
            "name": name,
            "edit_form": edit_form,
            "search_form": SearchForm()
        })
    if request.method == "POST":
        form = NewForm(request.POST)
        if form.is_valid():
            found_page = False
            title = form.cleaned_data["title"]
            content = form.cleaned_data["textarea"]

            title_entries = util.list_entries()
            for entry in title_entries:
                if title.lower() == entry.lower():
                    found_page = True
                    markdown_content = markdown2.markdown(content)
                    util.save_entry(title, markdown_content)
                    return HttpResponseRedirect(reverse("wikis:get_page", kwargs={'name': title}))


def random_page(request):
    get_pages_list = util.list_entries()
    n = random.randint(0, len(get_pages_list))
    page = get_pages_list[n-1]
    return HttpResponseRedirect(reverse("wikis:get_page", kwargs={'name': page}))
