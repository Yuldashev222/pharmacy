def firm_logo_upload_location(obj, logo):
    return f'firms/{obj.name[:200]}/logos/{logo}'
