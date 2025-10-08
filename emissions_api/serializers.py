def serialize_emission(result):
    """Map database result to response format."""
    return {
        'year': result['year'],
        'anzsic': result['anzsic'],
        'anzwi': result['anzwi'],
        'description': result['anzsic_descriptor'],
        'category': result['category'],
        'variable': result['variable'],
        'units': result['units'],
        'magnitude': result['magnitude'],
        'source': result['source'],
        'data_value': result['data_value']
    }