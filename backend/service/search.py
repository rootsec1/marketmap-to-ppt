from googlesearch import search


def search_google_and_return_company_url(company_name):
    results = list(search(f"{company_name} website homepage", num_results=1))
    if results:
        return results[0]
    return None
