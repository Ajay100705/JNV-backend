from django.utils import timezone

def get_current_academic_year():
    now = timezone.now()
    year = now.year

    # Academic year starts in April
    if now.month < 4:
        return f"{year-1}-{str(year)[-2:]}"
    
    return f"{year}-{str(year+1)[-2:]}"