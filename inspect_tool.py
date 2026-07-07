from agent.tools import research_company

print('type', type(research_company))
print('callable', callable(research_company))
print('has func', hasattr(research_company, 'func'))
print('func', getattr(research_company, 'func', None))
print('has _run', hasattr(research_company, '_run'))
print('has _acall', hasattr(research_company, '_acall'))
print('has run', hasattr(research_company, 'run'))
print([a for a in dir(research_company) if 'func' in a.lower() or 'run' in a.lower() or 'call' in a.lower()][:60])
