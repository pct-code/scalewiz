from tomlkit import document, nl, table, loads, dumps
from tomlkit.api import comment

def init_config(path: str):

    doc = document()
    doc.add(comment('This is a TOML document, made according to the spec at https://toml.io/en/'))
    doc.add(comment('If it behaves unexpectantly, try using https://www.toml-lint.com/ to check your edits'))
    doc.add(comment("If valid TOML is behaving unexpectantly in ScaleWiz, please open an issue at https://github.com/teauxfu/scalewiz/issues"))
    doc.add(nl())
    doc.add('title', 'a configuration file for ScaleWiz')
    doc.add(nl())
    # these will get updated between user sessions
    recents = table()
    for field in ('analyst', 'project'):
        recents.add(field)
    doc.add('recents', recents)
    # general defaults    
    params = table()
    fields = [
        'baseline',
        'time limit (min.)',
        'pressure limit (psi)',
        'reading interval (s)',
        'uptake time (s)',
        'flowrate (mL/min)',
        'output format'
    ]
    for field in fields:
        params.add(field)
    params['output format'] = 'CSV'
    doc.add('default parameters', params)

    with open(path, 'w') as file:
        file.write(dumps(doc))