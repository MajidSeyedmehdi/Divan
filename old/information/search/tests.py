from django.shortcuts import render
from .forms import SearchForm
from django.conf import settings
import pyodbc

def search_input(request):
    results = []
    form = SearchForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        db_settings = settings.DATABASES['default']

        conn_str = (
            f"DRIVER={db_settings['OPTIONS']['driver']};"
            f"SERVER={db_settings['HOST']};"
            f"DATABASE={db_settings['NAME']};"
            f"Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        query = """
            SELECT p.First_name, p.Last_name, p.National_code, p.Gender_status, p.Marital_status, o.Employment_id
            FROM Tbl_Personally p
            LEFT JOIN Tbl_Official o ON p.id_personal = o.id_personal
            WHERE 1=1
        """
        params = []

        if form.cleaned_data['name']:
            query += " AND p.First_name LIKE ?"
            params.append(f"%{form.cleaned_data['name']}%")
        if form.cleaned_data['family']:
            query += " AND p.Last_Name LIKE ?"
            params.append(f"%{form.cleaned_data['family']}%")
        if form.cleaned_data['national_code']:
            query += " AND p.National_code LIKE ?"
            params.append(f"%{form.cleaned_data['national_code']}%")
        if form.cleaned_data['personel_code']:
            query += " AND o.Employment_id LIKE ?"
            params.append(f"%{form.cleaned_data['personel_code']}%")
        if form.cleaned_data['gender']:
            query += " AND p.Gender_status = ?"
            params.append(form.cleaned_data['gender'])
        if form.cleaned_data['marital_status']:
            query += " AND p.Marital_status = ?"
            params.append(form.cleaned_data['marital_status'])

        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        cursor.close()
        conn.close()
        form = SearchForm()     #برای اینکه فرم دوباره خالی شود
    return render(request, 'main/includes/search/search.html', {'form': form, 'results': results})
