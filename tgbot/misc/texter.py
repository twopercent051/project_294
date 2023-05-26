def texter(text_list, subject):
    for item in text_list:
        if item['subject'].split('|')[-1].split(':')[1] == subject:
            return item['text']
    return 'Текст не задан'
