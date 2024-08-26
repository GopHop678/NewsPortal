from django import template

register = template.Library()


@register.filter
def censor(string_to_check):

    bad_words = {
        'редиска': 'р******',
        'морковка': 'м*******',
        'капуста': 'к******'
    }

    list_string = string_to_check.split()
    formated_string = []
    for word in list_string:
        if word in bad_words.keys():
            formated_string.append(bad_words[word])
        else:
            formated_string.append(word)

    return ' '.join(formated_string)
