from django import template
import string

register = template.Library()

BAD_WORDS = [
   "ipsum",
   "duis",
   "laborum",
   "mistaken",
   "except",
   "avoids",
   "ipsam",
   "bonorum"
]

# Регистрируем наш фильтр под именем currency, чтоб Django понимал,
# что это именно фильтр для шаблонов, а не простая функция.
@register.filter()
def censor(value):
   def isbad(word: str):
      return True if word in BAD_WORDS else False

   def replace(word: str):
      str_ = word[0]
      for i in range(1, len(word)):
         if word[i] not in string.punctuation:
            str_ += '*'
         else:
            str_ += word[i]
      return str_

   list = value.split()
   for n, word in enumerate(list):
      word2check = ""
      word = word.strip().lower()
      for i in range(len(word)):
         if word[i] not in string.punctuation:
            word2check += word[i]
      if isbad(word2check):
         list[n] = replace(list[n])
   return f'{" ".join(list)}'
