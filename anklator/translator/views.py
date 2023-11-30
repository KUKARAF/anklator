
# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from .models import Language, Word, Definition
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

def add_language_form(request):
    with open('lang_codes/language-codes.json', 'r') as file:
        language_codes = json.load(file)
    return render(request, 'add_language_form.html', {'language_codes': language_codes})

def index(request):
    langs = Language.objects.all()  # Or any other method you have defined
    return render(request, 'index.html', {'languages': langs})

@csrf_exempt
@require_http_methods(["POST"])
def add_language(request):
    try:
        data = json.loads(request.body)
        language, created = Language.objects.get_or_create(
            language=data['language'],
            defaults={
                'language_code': data['language_code'],
                'spacy_corpus': data['spacy_corpus']
            }
        )
        return JsonResponse({'language_id': language.id, 'created': created}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def add_word(request):
    try:
        data = json.loads(request.body)
        language = Language.objects.get(id=data['language_id'])
        definition, _ = Definition.objects.get_or_create(definition_text=data['definition'])
        word, created = Word.objects.get_or_create(
            lemmatized_word=data['lemmatized_word'],
            language=language,
            defaults={'definition': definition}
        )
        return JsonResponse({'word_id': word.id, 'created': created}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def add_translation(request):
    try:
        data = json.loads(request.body)
        source_word = Word.objects.get(id=data['source_word_id'])
        target_language = Language.objects.get(language_code=data['target_language_code'])
        translation_text = data['translation_text']  # This should come from a translation service
        translation, _ = Translation.objects.get_or_create(translation_text=translation_text)
        target_word, created = Word.objects.get_or_create(
            lemmatized_word=translation_text,
            language=target_language,
            defaults={'translation': translation}
        )
        WordRelationship.objects.create(word1=source_word, word2=target_word)
        return JsonResponse({'translation_id': translation.id, 'created': created}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def get_all_languages(request):
    try:
        languages = Language.objects.all().values('language', 'language_code', 'spacy_corpus')
        return JsonResponse(list(languages), safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Add more views as needed for other operations
