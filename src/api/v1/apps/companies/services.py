def company_logo_upload_location(obj, logo):
    return f'companies/{obj.name[:200]}/logos/{logo}'


def text_normalize(text):
    return ' '.join(str(text).split())
