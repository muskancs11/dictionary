from django.shortcuts import render, redirect
from django.views import View
import requests
from .models import SearchHistory
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import random

class SearchWordView(View):
    def get(self, request):
        search_history = self.get_search_history(request.user) if request.user.is_authenticated else []
        return render(request, 'search.html', {'search_history': search_history})

    def post(self, request):
        search_term = request.POST.get('search_term')
        word_data = self.fetch_word_data(search_term)
        
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, word=search_term)
        
        context = {
            'word_data': word_data,
            'search_term': search_term,
            'search_history': self.get_search_history(request.user)
        }
        return render(request, 'result.html', context)

    def fetch_word_data(self, search_term):
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{search_term}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            meanings = data[0]['meanings']
            definitions = []
            synonyms = []
            antonyms = []
            examples = []
            for meaning in meanings:
                definitions.extend(meaning['definitions'])
                synonyms.extend(meaning.get('synonyms', []))
                antonyms.extend(meaning.get('antonyms', []))
                for definition in meaning['definitions']:
                    if 'example' in definition:
                        examples.append(definition['example'])
            return {
                'definitions': definitions,
                'synonyms': synonyms,
                'antonyms': antonyms,
                'examples': examples,
            }
        return {'error': 'Word not found'}

    def get_search_history(self, user):
        if user.is_authenticated:
            return SearchHistory.objects.filter(user=user).order_by('-timestamp')[:10]
        return []

def get_random_word():
    url = "https://random-word-api.herokuapp.com/word"
    max_attempts = 5  # Maximum number of attempts to fetch a valid word
    attempts = 0
    
    while attempts < max_attempts:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            random_word = data[0]  # Assuming API returns a list with at least one word
            if random_word:
                return random_word
        # Increment attempts counter
        attempts += 1
    
    # If no valid word is found after max_attempts, return a default word or handle as needed
    return "example"  # Example fallback to a default word or handle error in your application

def index(request):
    search_history = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')[:10] if request.user.is_authenticated else []
    word = request.GET.get('word')
    is_searched = bool(word)
    if not word:
        word = get_random_word()
    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
    response = requests.get(url)
    context = {}
    if response.status_code == 200:
        data = response.json()
        meanings = data[0]['meanings']
        definitions = []
        synonyms = []
        antonyms = []
        examples = []
        for meaning in meanings:
            definitions.extend(meaning['definitions'])
            synonyms.extend(meaning.get('synonyms', []))
            antonyms.extend(meaning.get('antonyms', []))
            for definition in meaning['definitions']:
                if 'example' in definition:
                    examples.append(definition['example'])
        context = {
            'word': word,
            'definitions': definitions,
            'synonyms': synonyms,
            'antonyms': antonyms,
            'examples': examples,
            'is_searched': is_searched,
            'search_history': search_history
        }
    else:
        context = {'error': 'Word not found'}
    return render(request, 'index.html', context)